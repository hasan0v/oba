from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
import random
import string
from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.models.gamification import PointTransaction
from app.utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()


# Pydantic schemas
class OrderItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: float
    discount_price: Optional[float]
    subtotal: float
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    subtotal: float
    discount_amount: float
    delivery_fee: float
    total_amount: float
    status: str
    payment_status: str
    payment_method: Optional[str]
    delivery_type: str
    delivery_address: Optional[str]
    points_earned: int
    points_used: int
    items: List[OrderItemResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    payment_method: str = "cash"
    delivery_type: str = "delivery"
    delivery_address: Optional[str] = None
    delivery_notes: Optional[str] = None
    points_to_use: int = 0


class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    per_page: int


def generate_order_number() -> str:
    """Generate unique order number."""
    prefix = "OBA"
    timestamp = datetime.now().strftime("%y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_suffix}"


@router.get("/", response_model=OrderListResponse)
def get_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's orders."""
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    
    orders = query.order_by(Order.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    return OrderListResponse(
        items=orders,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific order."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order from cart."""
    # Get user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Validate delivery address for delivery orders
    if order_data.delivery_type == "delivery" and not order_data.delivery_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery address is required"
        )
    
    # Calculate totals
    subtotal = 0
    order_items = []
    
    for cart_item in cart.items:
        product = cart_item.product
        
        # Check stock
        if product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}"
            )
        
        price = product.discount_price if product.discount_price else product.price
        item_subtotal = price * cart_item.quantity
        subtotal += item_subtotal
        
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": cart_item.quantity,
            "unit_price": product.price,
            "discount_price": product.discount_price,
            "subtotal": item_subtotal
        })
    
    # Calculate points usage
    points_to_use = min(order_data.points_to_use, current_user.points)
    points_discount = points_to_use / 100  # 100 points = 1 AZN
    
    # Calculate delivery fee
    delivery_fee = 3.0 if order_data.delivery_type == "delivery" and subtotal < 30 else 0
    
    # Calculate total
    total_amount = subtotal - points_discount + delivery_fee
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id,
        subtotal=round(subtotal, 2),
        discount_amount=round(points_discount, 2),
        delivery_fee=delivery_fee,
        total_amount=round(total_amount, 2),
        payment_method=order_data.payment_method,
        delivery_type=order_data.delivery_type,
        delivery_address=order_data.delivery_address,
        delivery_notes=order_data.delivery_notes,
        points_used=points_to_use
    )
    
    db.add(order)
    db.flush()  # Get order ID
    
    # Create order items and update stock
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            **item_data
        )
        db.add(order_item)
        
        # Update product stock and sold count
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        product.stock_quantity -= item_data["quantity"]
        product.sold_count += item_data["quantity"]
    
    # Deduct points from user
    if points_to_use > 0:
        current_user.points -= points_to_use
        
        # Record point transaction
        point_transaction = PointTransaction(
            user_id=current_user.id,
            points=-points_to_use,
            transaction_type="redemption",
            reference_type="order",
            reference_id=order.id,
            description=f"Points redeemed for order {order.order_number}",
            balance_after=current_user.points
        )
        db.add(point_transaction)
    
    # Calculate and add earned points (1 point per 1 AZN)
    points_earned = int(total_amount)
    if points_earned > 0:
        order.points_earned = points_earned
        current_user.points += points_earned
        
        # Record point transaction
        point_transaction = PointTransaction(
            user_id=current_user.id,
            points=points_earned,
            transaction_type="purchase",
            reference_type="order",
            reference_id=order.id,
            description=f"Points earned from order {order.order_number}",
            balance_after=current_user.points
        )
        db.add(point_transaction)
    
    # Clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.put("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: UUID,
    reason: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an order (only if pending or confirmed)."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order in current status"
        )
    
    # Restore product stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity
            product.sold_count -= item.quantity
    
    # Restore used points
    if order.points_used > 0:
        current_user.points += order.points_used
        
        point_transaction = PointTransaction(
            user_id=current_user.id,
            points=order.points_used,
            transaction_type="refund",
            reference_type="order",
            reference_id=order.id,
            description=f"Points refunded for cancelled order {order.order_number}",
            balance_after=current_user.points
        )
        db.add(point_transaction)
    
    # Deduct earned points
    if order.points_earned > 0:
        current_user.points = max(0, current_user.points - order.points_earned)
        
        point_transaction = PointTransaction(
            user_id=current_user.id,
            points=-order.points_earned,
            transaction_type="refund",
            reference_type="order",
            reference_id=order.id,
            description=f"Points revoked for cancelled order {order.order_number}",
            balance_after=current_user.points
        )
        db.add(point_transaction)
    
    order.status = "cancelled"
    order.cancelled_at = datetime.utcnow()
    order.cancel_reason = reason
    
    db.commit()
    db.refresh(order)
    
    return order


# Admin endpoints
@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: UUID,
    status: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)."""
    valid_statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = status
    
    if status == "delivered":
        order.delivered_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order
