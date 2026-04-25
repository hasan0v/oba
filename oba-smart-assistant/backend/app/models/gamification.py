from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    description = Column(Text)
    description_en = Column(Text)
    icon_url = Column(String(500))
    category = Column(String(50))  # shopping, loyalty, engagement, special
    requirement_type = Column(String(50))  # orders_count, total_spent, reviews_count, streak
    requirement_value = Column(Integer)
    points_reward = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("UserBadge", back_populates="badge")
    
    def __repr__(self):
        return f"<Badge {self.name}>"


class UserBadge(Base):
    __tablename__ = "user_badges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey('badges.id'), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="users")
    
    def __repr__(self):
        return f"<UserBadge {self.user_id} - {self.badge_id}>"


class PointTransaction(Base):
    __tablename__ = "point_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    points = Column(Integer, nullable=False)  # Positive for earned, negative for spent
    transaction_type = Column(String(50), nullable=False)  # purchase, review, badge, redemption, bonus
    reference_type = Column(String(50), nullable=True)  # order, review, badge
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    description = Column(Text)
    balance_after = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="point_transactions")
    
    def __repr__(self):
        return f"<PointTransaction {self.points} points>"
