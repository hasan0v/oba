from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ARRAY, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    slug = Column(String(100), unique=True, index=True)
    image_url = Column(String(500), nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref="parent", remote_side=[id])
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text)
    description_en = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'))
    brand = Column(String(100))
    sku = Column(String(50), unique=True, index=True)
    barcode = Column(String(50), index=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    discount_percent = Column(Integer, nullable=True)
    cost_price = Column(Float, nullable=True)
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=10)
    unit = Column(String(20), default='ədəd')  # piece, kg, litr
    weight = Column(Float, nullable=True)  # in kg
    image_urls = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    sold_count = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    
    @property
    def effective_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def has_discount(self):
        return self.discount_price is not None and self.discount_price < self.price
    
    @property
    def in_stock(self):
        return self.stock_quantity > 0
    
    def __repr__(self):
        return f"<Product {self.name}>"
