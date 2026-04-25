from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CategoryBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    slug: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: UUID
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    discount_percent: Optional[int] = None
    stock_quantity: int = 0
    unit: str = "ədəd"
    weight: Optional[float] = None
    image_urls: List[str] = []


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    discount_percent: Optional[int] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class ProductResponse(ProductBase):
    id: UUID
    is_active: bool = True
    is_featured: bool = False
    view_count: int = 0
    sold_count: int = 0
    avg_rating: float = 0.0
    review_count: int = 0
    created_at: datetime
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ProductSearchRequest(BaseModel):
    query: str
    category_id: Optional[UUID] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    sort_by: str = "relevance"  # relevance, price_asc, price_desc, rating, newest
    page: int = 1
    per_page: int = 20
