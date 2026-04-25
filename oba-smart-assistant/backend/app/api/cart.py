from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel
from app.database import get_db
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter()


# Pydantic schemas
class CartItemCreate(BaseModel):
    product_id: UUID
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str
    product_image: str
    unit_price: float
    discount_price: float | None
    quantity: int
    subtotal: float
    in_stock: bool
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: UUID
    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    
    class Config:
        from_attributes = True


def get_or_create_cart(user_id: UUID, db: Session) -> Cart:
    """Get user's cart or create one if it doesn't exist."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.get("/", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart."""
    cart = get_or_create_cart(current_user.id, db)
    
    items = []
    subtotal = 0
    total_items = 0
    
    for item in cart.items:
        product = item.product
        price = product.discount_price if product.discount_price else product.price
        item_subtotal = price * item.quantity
        
        items.append(CartItemResponse(
            id=item.id,
            product_id=product.id,
            product_name=product.name,
            product_image=product.image_urls[0] if product.image_urls else "",
            unit_price=product.price,
            discount_price=product.discount_price,
            quantity=item.quantity,
            subtotal=item_subtotal,
            in_stock=product.stock_quantity >= item.quantity
        ))
        
        subtotal += item_subtotal
        total_items += item.quantity
    
    return CartResponse(
        id=cart.id,
        items=items,
        total_items=total_items,
        subtotal=round(subtotal, 2)
    )


@router.post("/items", response_model=CartResponse)
def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an item to cart."""
    # Check product exists and is active
    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check stock
    if product.stock_quantity < item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Only {product.stock_quantity} available."
        )
    
    cart = get_or_create_cart(current_user.id, db)
    
    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + item.quantity
        if product.stock_quantity < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add more. Only {product.stock_quantity} available."
            )
        existing_item.quantity = new_quantity
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    
    return get_cart(current_user, db)


@router.put("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: UUID,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity."""
    cart = get_or_create_cart(current_user.id, db)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    if item_update.quantity <= 0:
        # Remove item if quantity is 0 or less
        db.delete(cart_item)
    else:
        # Check stock
        if cart_item.product.stock_quantity < item_update.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Only {cart_item.product.stock_quantity} available."
            )
        cart_item.quantity = item_update.quantity
    
    db.commit()
    
    return get_cart(current_user, db)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_from_cart(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an item from cart."""
    cart = get_or_create_cart(current_user.id, db)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    db.delete(cart_item)
    db.commit()
    
    return get_cart(current_user, db)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart."""
    cart = get_or_create_cart(current_user.id, db)
    
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
