from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(20), unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=True)
    category = Column(String(50), nullable=False)  # product, service, delivery, pricing, other
    subcategory = Column(String(50), nullable=True)
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    priority_score = Column(Integer, nullable=True)  # AI calculated 0-100
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    image_urls = Column(Text, nullable=True)  # JSON array
    status = Column(String(50), default='pending')  # pending, in_progress, waiting_customer, resolved, closed
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    resolution = Column(Text, nullable=True)
    resolution_type = Column(String(50), nullable=True)  # refund, replacement, apology, compensation
    customer_satisfaction = Column(Integer, nullable=True)  # 1-5 rating
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="complaints", foreign_keys=[user_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    messages = relationship("ComplaintMessage", back_populates="complaint", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Complaint {self.ticket_number}>"


class ComplaintMessage(Base):
    __tablename__ = "complaint_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey('complaints.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    is_internal = Column(String(10), default='false')  # Internal notes visible only to staff
    attachment_urls = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    complaint = relationship("Complaint", back_populates="messages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ComplaintMessage {self.id}>"
