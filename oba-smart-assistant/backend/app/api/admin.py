from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.product import Product, Category
from app.models.order import Order, OrderItem
from app.models.review import Review
from app.models.complaint import Complaint
from app.utils.dependencies import get_current_admin_user

router = APIRouter()


# Pydantic schemas
class DashboardStats(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_revenue: float
    orders_today: int
    revenue_today: float
    pending_orders: int
    pending_complaints: int


class SalesData(BaseModel):
    date: str
    orders: int
    revenue: float


class CategorySales(BaseModel):
    category: str
    sales: float
    percentage: float


class TopProduct(BaseModel):
    id: str
    name: str
    sold_count: int
    revenue: float


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    today = datetime.utcnow().date()
    
    # Total counts
    total_users = db.query(User).filter(User.is_active == True).count()
    total_products = db.query(Product).filter(Product.is_active == True).count()
    total_orders = db.query(Order).count()
    
    # Total revenue
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status == "delivered"
    ).scalar() or 0
    
    # Today's stats
    orders_today = db.query(Order).filter(
        func.date(Order.created_at) == today
    ).count()
    
    revenue_today = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) == today,
        Order.status != "cancelled"
    ).scalar() or 0
    
    # Pending counts
    pending_orders = db.query(Order).filter(
        Order.status.in_(["pending", "confirmed", "processing"])
    ).count()
    
    pending_complaints = db.query(Complaint).filter(
        Complaint.status.in_(["pending", "in_progress"])
    ).count()
    
    return DashboardStats(
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2),
        orders_today=orders_today,
        revenue_today=round(revenue_today, 2),
        pending_orders=pending_orders,
        pending_complaints=pending_complaints
    )


@router.get("/sales-trend", response_model=List[SalesData])
def get_sales_trend(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get sales trend for the last N days."""
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    # Query daily sales
    results = db.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('orders'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        func.date(Order.created_at) >= start_date,
        Order.status != "cancelled"
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at)
    ).all()
    
    # Convert to dict for easy lookup
    sales_dict = {
        r.date.strftime('%Y-%m-%d'): {'orders': r.orders, 'revenue': float(r.revenue or 0)}
        for r in results
    }
    
    # Fill in missing dates with zeros
    sales_data = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        data = sales_dict.get(date_str, {'orders': 0, 'revenue': 0})
        sales_data.append(SalesData(
            date=date_str,
            orders=data['orders'],
            revenue=round(data['revenue'], 2)
        ))
        current += timedelta(days=1)
    
    return sales_data


@router.get("/category-sales", response_model=List[CategorySales])
def get_category_sales(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get sales by category."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        Category.name,
        func.sum(OrderItem.subtotal).label('sales')
    ).join(
        Product, Product.category_id == Category.id
    ).join(
        OrderItem, OrderItem.product_id == Product.id
    ).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        Order.created_at >= start_date,
        Order.status != "cancelled"
    ).group_by(
        Category.name
    ).order_by(
        func.sum(OrderItem.subtotal).desc()
    ).all()
    
    total_sales = sum(r.sales or 0 for r in results)
    
    return [
        CategorySales(
            category=r.name,
            sales=round(float(r.sales or 0), 2),
            percentage=round((r.sales or 0) / total_sales * 100, 1) if total_sales > 0 else 0
        )
        for r in results
    ]


@router.get("/top-products", response_model=List[TopProduct])
def get_top_products(
    limit: int = Query(10, ge=5, le=50),
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get top selling products."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        Product.id,
        Product.name,
        func.sum(OrderItem.quantity).label('sold_count'),
        func.sum(OrderItem.subtotal).label('revenue')
    ).join(
        OrderItem, OrderItem.product_id == Product.id
    ).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        Order.created_at >= start_date,
        Order.status != "cancelled"
    ).group_by(
        Product.id, Product.name
    ).order_by(
        func.sum(OrderItem.subtotal).desc()
    ).limit(limit).all()
    
    return [
        TopProduct(
            id=str(r.id),
            name=r.name,
            sold_count=int(r.sold_count or 0),
            revenue=round(float(r.revenue or 0), 2)
        )
        for r in results
    ]


@router.get("/users", response_model=dict)
def get_users_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of users."""
    query = db.query(User)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            User.email.ilike(search_term) |
            User.full_name.ilike(search_term) |
            User.phone.ilike(search_term)
        )
    
    total = query.count()
    
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    return {
        "items": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "phone": u.phone,
                "points": u.points,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/complaints", response_model=dict)
def get_complaints_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of complaints."""
    query = db.query(Complaint)
    
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)
    
    total = query.count()
    
    complaints = query.order_by(Complaint.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    return {
        "items": [
            {
                "id": str(c.id),
                "ticket_number": c.ticket_number,
                "category": c.category,
                "priority": c.priority,
                "subject": c.subject,
                "status": c.status,
                "user_id": str(c.user_id),
                "created_at": c.created_at.isoformat()
            }
            for c in complaints
        ],
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.put("/complaints/{complaint_id}/assign")
def assign_complaint(
    complaint_id: UUID,
    assignee_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Assign complaint to staff member."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    complaint.assigned_to = assignee_id
    complaint.status = "in_progress"
    
    if not complaint.first_response_at:
        complaint.first_response_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Complaint assigned successfully"}


@router.put("/complaints/{complaint_id}/resolve")
def resolve_complaint(
    complaint_id: UUID,
    resolution: str,
    resolution_type: str = "apology",
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Resolve a complaint."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    complaint.status = "resolved"
    complaint.resolution = resolution
    complaint.resolution_type = resolution_type
    complaint.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Complaint resolved successfully"}
