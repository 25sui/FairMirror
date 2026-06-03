from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
import re

from app.models.database import get_db
from app.models.entities import UserDB
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str = "hr"

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 2:
            raise ValueError('用户名至少2个字符')
        if len(v) > 20:
            raise ValueError('用户名最多20个字符')
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码至少8个字符')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含数字')
        if not re.search(r'[^a-zA-Z0-9]', v):
            raise ValueError('密码必须包含特殊字符')
        return v

    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['admin', 'hr', 'candidate', 'auditor']
        if v not in valid_roles:
            raise ValueError(f'无效的角色类型，可选值: {", ".join(valid_roles)}')
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    company_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    success: bool = False


class ValidationErrorResponse(BaseModel):
    detail: List[dict]
    success: bool = False


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口

    参数:
    - email: 邮箱地址（必填，有效的邮箱格式）
    - username: 用户名（必填，2-20个字符）
    - password: 密码（必填，至少8个字符，包含大小写字母、数字和特殊字符）
    - role: 角色类型（可选，默认为hr，可选值: admin, hr, candidate, auditor）

    返回:
    - success: 是否成功
    - message: 提示信息
    - user: 用户信息
    """
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    existing_username = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用"
        )

    hashed_password = get_password_hash(user.password)

    db_user = UserDB(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

    return RegisterResponse(
        message="注册成功！",
        user=UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            role=db_user.role,
            company_id=db_user.company_id,
            is_active=db_user.is_active
        ),
        success=True
    )


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口

    参数（Form Data）:
    - username: 邮箱地址
    - password: 密码

    返回:
    - access_token: JWT访问令牌
    - token_type: 令牌类型
    - user: 用户信息
    """
    user = db.query(UserDB).filter(UserDB.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号已被禁用，请联系管理员"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "company_id": user.company_id},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "company_id": user.company_id,
            "is_active": user.is_active
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    """
    获取当前登录用户信息

    需要Bearer Token认证
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        company_id=current_user.company_id,
        is_active=current_user.is_active
    )


@router.get("/validate/email/{email}")
async def validate_email_availability(email: str, db: Session = Depends(get_db)):
    """
    检查邮箱是否可用

    参数:
    - email: 邮箱地址

    返回:
    - available: 是否可用
    """
    existing_user = db.query(UserDB).filter(UserDB.email == email).first()
    return {
        "available": existing_user is None,
        "email": email
    }


@router.get("/validate/username/{username}")
async def validate_username_availability(username: str, db: Session = Depends(get_db)):
    """
    检查用户名是否可用

    参数:
    - username: 用户名

    返回:
    - available: 是否可用
    """
    existing_user = db.query(UserDB).filter(UserDB.username == username).first()
    return {
        "available": existing_user is None,
        "username": username
    }
