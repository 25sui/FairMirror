from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.database import get_db
from app.models.entities import UserDB, JobDescriptionDB

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_token_from_request(request: Request) -> str:
    """从请求中提取 Token，不依赖 OAuth2PasswordBearer 的自动验证"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header[len("Bearer "):]
    return token


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = await get_token_from_request(request)
        payload = decode_token(token)
        
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception
            
        # 确保 user_id 是整数类型
        user_id = int(user_id_raw)
    except Exception:
        raise credentials_exception

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: UserDB = Depends(get_current_user)
) -> UserDB:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_roles(allowed_roles: List[str]):
    async def role_checker(
        current_user: UserDB = Depends(get_current_active_user)
    ) -> UserDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action"
            )
        return current_user
    return role_checker


def ensure_company_access(current_user: UserDB, company_id: int) -> None:
    if current_user.role == "admin":
        return
    if current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company resource"
        )


def ensure_self_or_roles(current_user: UserDB, owner_id: int, allowed_roles: List[str]) -> None:
    if current_user.id == owner_id:
        return
    if current_user.role in allowed_roles:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have access to this user resource"
    )


def get_accessible_job(db: Session, job_id: int, current_user: UserDB) -> JobDescriptionDB:
    job = db.query(JobDescriptionDB).filter(JobDescriptionDB.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    ensure_company_access(current_user, job.company_id)
    return job
