"""
Users API Response Schemas
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=100, description="User full name")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    role: str = Field("student", description="User role (student, teacher, admin)")


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Schema for user profile update"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user profile response"""
    id: UUID
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    avatar_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class UsersListResponse(BaseModel):
    """Schema for paginated users list"""
    items: List[UserResponse]
    total: int
    limit: int
    offset: int
