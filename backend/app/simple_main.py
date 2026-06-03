from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
from jose import JWTError, jwt
from passlib.context import CryptContext
import re
import uuid

print("使用简化模式启动（无需AI模型）...")

SECRET_KEY = "fairmirror-simple-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

app = FastAPI(
    title="FairMirror",
    version="1.0.0",
    description="AI反偏见招聘镜像 - 简化模式",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_db: Dict[str, dict] = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = fake_db.get(user_id)
    if user is None:
        raise credentials_exception
    return user


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
    id: str
    email: str
    username: str
    role: str
    is_active: bool


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
    success: bool = True


@app.post("/api/v1/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user: RegisterRequest):
    for existing_user in fake_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
        if existing_user["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )

    hashed_password = get_password_hash(user.password)
    user_id = str(uuid.uuid4())

    new_user = {
        "id": user_id,
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password,
        "role": user.role,
        "is_active": True,
        "created_at": datetime.utcnow()
    }

    fake_db[user_id] = new_user

    return RegisterResponse(
        message="注册成功！",
        user=UserResponse(
            id=new_user["id"],
            email=new_user["email"],
            username=new_user["username"],
            role=new_user["role"],
            is_active=new_user["is_active"]
        ),
        success=True
    )


@app.post("/api/v1/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    for u in fake_db.values():
        if u["email"] == form_data.username:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号已被禁用，请联系管理员"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"], "role": user["role"]},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "role": user["role"],
            "is_active": user["is_active"]
        }
    }


@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        role=current_user["role"],
        is_active=current_user["is_active"]
    )


@app.get("/api/v1/auth/validate/email/{email}")
async def validate_email_availability(email: str):
    for user in fake_db.values():
        if user["email"] == email:
            return {"available": False, "email": email}
    return {"available": True, "email": email}


@app.get("/api/v1/auth/validate/username/{username}")
async def validate_username_availability(username: str):
    for user in fake_db.values():
        if user["username"] == username:
            return {"available": False, "username": username}
    return {"available": True, "username": username}


class BiasLevel(str, Enum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class BiasType(str, Enum):
    GENDER = 'gender'
    AGE = 'age'
    EDUCATION = 'education'
    REGION = 'region'
    RACE = 'race'


class BiasCheckResult(BaseModel):
    type: BiasType
    score: float
    level: BiasLevel
    text: str
    position: List[int]
    suggestion: str
    severity: int


class JDAuditRequest(BaseModel):
    jd_text: str
    job_title: Optional[str] = None


class JDAuditResponse(BaseModel):
    bias_results: List[BiasCheckResult]
    overall_score: float
    overall_level: BiasLevel
    suggestions: List[str]
    report_url: Optional[str] = None
    audit_timestamp: datetime


class SimpleBiasDetector:
    def __init__(self):
        self.patterns = {
            "gender": [
                {"pattern": r"男性|女性|先生|女士|帅哥|美女", "weight": 0.9, "suggestion": "使用性别中性语言"},
                {"pattern": r"阳刚|柔弱|坚强|细心体贴", "weight": 0.7, "suggestion": "避免使用与性别相关的刻板印象描述"},
            ],
            "age": [
                {"pattern": r"35岁以[上下内]|40岁以[上下内]|30岁以下", "weight": 0.9, "suggestion": "删除年龄限制要求"},
                {"pattern": r"年轻人|精力充沛|成熟稳重", "weight": 0.5, "suggestion": "避免使用暗示年龄的描述"},
            ],
            "education": [
                {"pattern": r"985|211|必须985|优先985", "weight": 0.9, "suggestion": "改为'本科及以上学历'或'具备相关经验'"},
                {"pattern": r"名校|第一学历|全日制", "weight": 0.6, "suggestion": "考虑能力导向而非院校导向"},
            ],
            "region": [
                {"pattern": r"北京户籍|上海户籍|本地户口", "weight": 0.9, "suggestion": "删除户籍要求"},
                {"pattern": r"本地人|外地人|北方人|南方人", "weight": 0.7, "suggestion": "避免使用地域偏见语言"},
            ],
        }

    def detect(self, text: str) -> List[BiasCheckResult]:
        results = []

        for bias_type, patterns in self.patterns.items():
            for pattern_info in patterns:
                matches = list(re.finditer(pattern_info["pattern"], text))
                for match in matches:
                    start, end = match.start(), match.end()
                    score = pattern_info["weight"]

                    if score >= 0.8:
                        level = BiasLevel.HIGH
                    elif score >= 0.6:
                        level = BiasLevel.MEDIUM
                    else:
                        level = BiasLevel.LOW

                    results.append(BiasCheckResult(
                        type=BiasType(bias_type),
                        score=score,
                        level=level,
                        text=match.group(),
                        position=[start, end],
                        suggestion=pattern_info["suggestion"],
                        severity=int(score * 5)
                    ))

        return results

    def calculate_overall(self, results: List[BiasCheckResult]) -> tuple[float, BiasLevel]:
        if not results:
            return 0.0, BiasLevel.LOW

        total_score = sum(r.score for r in results) / len(results)
        overall = round(total_score, 2)

        if overall >= 0.7:
            level = BiasLevel.HIGH
        elif overall >= 0.4:
            level = BiasLevel.MEDIUM
        else:
            level = BiasLevel.LOW

        return overall, level


simple_detector = SimpleBiasDetector()


@app.post("/api/v1/jd/analyze", response_model=JDAuditResponse)
async def analyze_jd(request: JDAuditRequest):
    bias_results = simple_detector.detect(request.jd_text)
    overall_score, overall_level = simple_detector.calculate_overall(bias_results)

    suggestions = []
    seen_types = set()
    for result in bias_results:
        if result.type.value not in seen_types:
            suggestions.append(
                f"【{result.type.value.upper()}偏见】{result.suggestion} (严重程度: {result.severity}/5)"
            )
            seen_types.add(result.type.value)

    if not suggestions:
        suggestions.append("恭喜！您的JD未检测到明显的偏见内容")

    return JDAuditResponse(
        bias_results=bias_results,
        overall_score=overall_score,
        overall_level=overall_level,
        suggestions=suggestions,
        audit_timestamp=datetime.utcnow()
    )


@app.get("/")
async def root():
    return {
        "message": "Welcome to FairMirror API (Simple Mode)",
        "version": "1.0.0",
        "mode": "simple",
        "docs": "/docs",
        "note": "简化模式无需安装AI模型依赖"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FairMirror API",
        "mode": "simple"
    }
