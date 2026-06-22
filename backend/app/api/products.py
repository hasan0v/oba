from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models.product import Product, Category
from app.models.user import User
from app.schemas.product import (
    ProductResponse, 
    ProductListResponse, 
    CategoryResponse,
    ProductCreate,
    ProductUpdate
)
from app.utils.dependencies import get_current_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[UUID] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    sort_by: str = Query("newest", regex="^(newest|price_asc|price_desc|rating|popular)$"),
    db: Session = Depends(get_db)
):
    """Get products with filtering and pagination."""
    query = db.query(Product).filter(Product.is_active == True)
    
    # Filter by category
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.name_en.ilike(search_term),
                Product.description.ilike(search_term),
                Product.brand.ilike(search_term)
            )
        )
    
    # Price range
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Stock filter
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock_quantity > 0)
        else:
            query = query.filter(Product.stock_quantity == 0)
    
    # Featured filter
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    
    # Sorting
    if sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    elif sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "rating":
        query = query.order_by(Product.avg_rating.desc())
    elif sort_by == "popular":
        query = query.order_by(Product.sold_count.desc())
    
    # Total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * per_page
    products = query.offset(offset).limit(per_page).all()
    
    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )


@router.get("/featured", response_model=List[ProductResponse])
def get_featured_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured products."""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.is_featured == True
    ).order_by(Product.created_at.desc()).limit(limit).all()
    
    return products


@router.get("/deals", response_model=List[ProductResponse])
def get_deals(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get products with discounts."""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.discount_price.isnot(None),
        Product.discount_price < Product.price
    ).order_by(Product.discount_percent.desc()).limit(limit).all()
    
    return products


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    parent_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """Get all categories or subcategories."""
    query = db.query(Category).filter(Category.is_active == True)
    
    if parent_id:
        query = query.filter(Category.parent_id == parent_id)
    else:
        query = query.filter(Category.parent_id.is_(None))
    
    categories = query.order_by(Category.sort_order).all()
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: UUID, db: Session = Depends(get_db)):
    """Get a specific category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Get a specific product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Increment view count
    product.view_count += 1
    db.commit()
    
    return product


@router.get("/{product_id}/similar", response_model=List[ProductResponse])
def get_similar_products(
    product_id: UUID,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get similar products based on category."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    similar = db.query(Product).filter(
        Product.id != product_id,
        Product.is_active == True,
        Product.category_id == product.category_id
    ).order_by(func.random()).limit(limit).all()
    
    return similar


@router.post("/voice-search", response_model=List[ProductResponse])
def voice_search(
    query: str,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search products using voice-transcribed text."""
    search_term = f"%{query}%"
    
    products = db.query(Product).filter(
        Product.is_active == True,
        or_(
            Product.name.ilike(search_term),
            Product.name_en.ilike(search_term),
            Product.brand.ilike(search_term)
        )
    ).limit(limit).all()
    
    return products


# Admin endpoints
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new product (admin only)."""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    for key, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a product (admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    product.is_active = False
    db.commit()
