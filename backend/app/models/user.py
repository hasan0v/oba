from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(String(500), nullable=True)
    language = Column(String(5), default='az')
    points = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    fcm_token = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id")
    reviews = relationship("Review", back_populates="user")
    complaints = relationship("Complaint", back_populates="user", foreign_keys="Complaint.user_id")
    cart = relationship("Cart", back_populates="user", uselist=False)
    badges = relationship("UserBadge", back_populates="user")
    point_transactions = relationship("PointTransaction", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
