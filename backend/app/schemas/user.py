from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language: str = "az"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None
    fcm_token: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    avatar_url: Optional[str] = None
    points: int = 0
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    password_hash: str
    is_admin: bool = False


class UserProfile(UserResponse):
    total_orders: int = 0
    total_spent: float = 0.0
    badges_count: int = 0
