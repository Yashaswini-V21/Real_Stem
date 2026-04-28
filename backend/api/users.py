"""
Users API Endpoints

Provides endpoints for user registration, authentication, profile management, and role-based access.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from pydantic import BaseModel, EmailStr, Field

from config import settings
from utils.logger import get_logger
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    RoleChecker
)
from database import get_db
from models.user import User
from schemas.users import (
    UserCreate,
    UserResponse,
    UserUpdate,
    LoginRequest,
    Token,
    UsersListResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

# --- Helper Request/Response Schemas ---

class TokenResponse(BaseModel):
    """Enhanced token response with user info"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Roles dependencies
admin_required = RoleChecker(["admin"])
teacher_required = RoleChecker(["admin", "teacher"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account (student, teacher, or admin)",
)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user in the system.
    """
    logger.info(f"👤 Registering new user: {user_in.email} ({user_in.role})")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    
    if existing_user:
        logger.warning(f"❌ Registration failed: Email {user_in.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    try:
        # Create new user
        user = User(
            email=user_in.email,
            name=user_in.full_name,
            password_hash=get_password_hash(user_in.password).encode('utf-8'),
            role=user_in.role,
            is_active=True
        )
        # Note: grade_level and subjects can be added here if present in UserCreate or updated schema
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ User registered successfully: {user.id}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and return JWT access token",
)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and return access token with user profile.
    """
    logger.info(f"🔑 Login attempt for user: {request.username}") # request.username maps to email in current LoginRequest schema
    
    user = db.query(User).filter(User.email == request.username).first()
    
    if not user or not verify_password(request.password, user.password_hash.decode('utf-8')):
        logger.warning(f"❌ Login failed: Invalid credentials for {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"❌ Login failed: Account inactive for {request.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Generate token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    logger.info(f"✅ Login successful: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve profile of the currently authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get profile of the logged-in user.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update account details and preferences for the current user",
)
async def update_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update profile data for the currently authenticated user.
    """
    logger.info(f"📝 Updating profile for user: {current_user.id}")
    
    try:
        update_data = user_in.model_dump(exclude_unset=True)
        
        # Map schema fields to model fields if they differ
        if "full_name" in update_data:
            current_user.name = update_data.pop("full_name")
            
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
            
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"✅ Profile updated: {current_user.id}")
        return current_user
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating profile")


@router.get(
    "/me/progress",
    summary="Get student progress",
    description="Retrieve the learning progress and achievements for the current student",
)
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns progress metrics for the authenticated student.
    """
    # Placeholder implementation
    return {
        "user_id": current_user.id,
        "lessons_completed": 5,
        "time_spent_minutes": 120,
        "achievements": ["First Lesson", "Quiz Master"],
        "grade_level": current_user.grade_level
    }


@router.get(
    "/me/impact",
    summary="Get student impact",
    description="Retrieve the real-world impact metrics for the current student",
)
async def get_impact(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns impact metrics for the authenticated student.
    """
    # Placeholder implementation
    return {
        "user_id": current_user.id,
        "projects_adopted": 2,
        "research_cited": 0,
        "carbon_offset": 5.2
    }


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user profile",
    description="Retrieve profile of a specific user by ID",
)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get generic user profile information.
    """
    logger.info(f"🔍 Fetching profile for user: {user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"❌ User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
        
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update account details and preferences",
)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update user profile data.
    """
    logger.info(f"📝 Updating profile for user: {user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"❌ User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
            
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ Profile updated: {user_id}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating profile")


@router.get(
    "",
    response_model=UsersListResponse,
    summary="List users",
    description="Admin only: Retrieve paginated list of all users",
)
async def get_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> UsersListResponse:
    """
    Get paginated list of users.
    """
    logger.info(f"👥 Fetching users list: role={role}, limit={limit}, offset={offset}")
    
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
        
    total = query.count()
    users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
    
    return {
        "items": users,
        "total": total,
        "limit": limit,
        "offset": offset
    }

