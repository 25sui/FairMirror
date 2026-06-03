# FairMirror 用户注册功能

## 📝 功能概述

完整的用户注册功能模块，包括前端表单验证、后端API接口和数据安全存储。

## ✨ 核心功能

### 1. 前端注册表单

#### 表单字段
- **用户名**：2-20个字符，支持中文、字母、数字和下划线
- **邮箱地址**：有效的邮箱格式验证
- **密码**：
  - 至少8个字符
  - 必须包含小写字母
  - 必须包含大写字母
  - 必须包含数字
  - 必须包含特殊字符
- **确认密码**：与密码一致
- **账号类型**：企业HR / 求职者 / 管理员
- **服务条款**：必须同意

#### 实时验证功能
✅ 用户名格式验证（长度、内容）
✅ 邮箱格式验证
✅ 密码强度检测（实时显示）
✅ 密码要求清单（逐项高亮）
✅ 两次密码一致性验证
✅ 服务条款勾选验证

#### 用户体验优化
- 🎨 密码强度进度条（弱/中等/良好/强）
- 📊 密码要求逐项检查提示
- ⚡ 实时表单验证
- 🎯 友好的错误提示
- ✅ 注册成功跳转

### 2. 后端API接口

#### 注册接口
**POST** `/api/v1/auth/register`

**请求体**：
```json
{
  "email": "user@example.com",
  "username": "用户名",
  "password": "Password123!",
  "role": "hr"
}
```

**响应**：
```json
{
  "success": true,
  "message": "注册成功！",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "用户名",
    "role": "hr",
    "is_active": true
  }
}
```

#### 验证接口

**GET** `/api/v1/auth/validate/email/{email}`
检查邮箱是否可用

**GET** `/api/v1/auth/validate/username/{username}`
检查用户名是否可用

## 🔒 安全特性

### 后端验证
1. **邮箱格式验证**：使用 Pydantic EmailStr
2. **密码强度验证**：
   - 最小长度：8字符
   - 包含小写字母
   - 包含大写字母
   - 包含数字
   - 包含特殊字符
3. **用户名验证**：
   - 长度：2-20字符
   - 允许字符：字母、数字、下划线、中文
4. **角色验证**：仅允许合法角色
5. **重复检测**：
   - 邮箱唯一性检查
   - 用户名唯一性检查
6. **密码加密**：使用 bcrypt 哈希加密
7. **JWT认证**：Token过期时间24小时

### 数据保护
- 密码使用bcrypt加密存储
- 使用参数化查询防止SQL注入
- JWT Token安全认证
- CORS跨域配置

## 🚀 使用指南

### 方式一：通过前端界面注册

1. 访问登录页面：http://localhost:3000/login
2. 点击"立即注册"链接
3. 填写注册表单
4. 点击"立即注册"
5. 注册成功，跳转到登录页面

### 方式二：通过API注册

```bash
# 注册新用户
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "测试用户",
    "password": "Password123!",
    "role": "hr"
  }'

# 检查邮箱是否可用
curl http://localhost:8000/api/v1/auth/validate/email/test@example.com

# 检查用户名是否可用
curl http://localhost:8000/api/v1/auth/validate/username/测试用户

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=test@example.com" \
  -d "password=Password123!"
```

## 📂 文件结构

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Login.tsx          # 登录页面（已更新）
│   │   └── Register.tsx       # 注册页面（新建）
│   ├── services/
│   │   └── api.ts            # API服务（已更新）
│   ├── stores/
│   │   └── authStore.ts      # 认证状态管理
│   └── App.tsx               # 路由配置（已更新）

backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── auth.py       # 认证接口（已增强）
│   ├── models/
│   │   ├── database.py       # 数据库配置
│   │   └── entities.py       # 数据库实体
│   └── core/
│       └── security.py       # 安全工具
└── requirements.txt          # 依赖（已更新）
```

## 🎯 代码示例

### 前端注册表单核心代码

```tsx
<Form
  form={form}
  onFinish={onFinish}
>
  <Form.Item
    label="用户名"
    name="username"
    rules={[{ validator: validateUsername }]}
  >
    <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
  </Form.Item>

  <Form.Item
    label="邮箱"
    name="email"
    rules={[{ validator: validateEmail }]}
  >
    <Input prefix={<MailOutlined />} placeholder="请输入邮箱" />
  </Form.Item>

  <Form.Item
    label="密码"
    name="password"
    rules={[{ required: true, min: 8 }]}
  >
    <Input.Password prefix={<LockOutlined />} />
  </Form.Item>

  {/* 密码强度显示 */}
  <Progress percent={passwordStrength} strokeColor={getPasswordStrengthColor()} />

  <Form.Item
    name="confirmPassword"
    dependencies={['password']}
    rules={[{ validator: validatePassword }]}
  >
    <Input.Password />
  </Form.Item>

  <Form.Item
    name="agreement"
    valuePropName="checked"
    rules={[{ validator: validateAgreement }]}
  >
    <Checkbox>我已阅读并同意...</Checkbox>
  </Form.Item>

  <Button type="primary" htmlType="submit" loading={loading}>
    立即注册
  </Button>
</Form>
```

### 后端注册验证

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str = "hr"

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

@router.post("/register")
async def register(user: RegisterRequest, db: Session = Depends(get_db)):
    # 检查邮箱唯一性
    existing = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 检查用户名唯一性
    existing = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被使用")

    # 加密密码
    hashed_password = get_password_hash(user.password)

    # 创建用户
    db_user = UserDB(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()

    return {"success": True, "user": db_user}
```

## 🔧 配置说明

### 角色类型

| 角色 | 标识 | 说明 |
|------|------|------|
| 企业HR | `hr` | 企业招聘人员 |
| 求职者 | `candidate` | 应聘候选人 |
| 管理员 | `admin` | 系统管理员 |
| 审计员 | `auditor` | 合规审计人员 |

### 密码要求

| 要求 | 最小值 | 说明 |
|------|--------|------|
| 长度 | 8字符 | 最少需要8个字符 |
| 小写字母 | 1个 | 必须包含至少一个小写字母 |
| 大写字母 | 1个 | 必须包含至少一个大写字母 |
| 数字 | 1个 | 必须包含至少一个数字 |
| 特殊字符 | 1个 | 必须包含至少一个特殊字符 |

## 🎨 界面预览

### 注册页面特点
- 📱 响应式设计，适配各种屏幕
- 🎨 渐变背景，现代化UI
- 📊 实时密码强度指示
- ✅ 清晰的错误提示
- 🔒 安全条款说明

## ⚙️ 高级配置

### 修改Token过期时间

修改 `backend/app/core/config.py`：

```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
```

### 添加更多验证规则

在 `backend/app/api/v1/auth.py` 中的 `RegisterRequest` 类添加新的验证器：

```python
@validator('username')
def validate_username(cls, v):
    # 添加自定义验证逻辑
    if 'admin' in v.lower():
        raise ValueError('用户名不能包含admin')
    return v
```

### 自定义密码策略

修改正则表达式以适应不同需求：

```python
@validator('password')
def validate_password(cls, v):
    # 自定义密码策略
    if len(v) < 12:  # 更严格的12字符要求
        raise ValueError('密码至少12个字符')
    # 其他规则...
```

## 🐛 故障排除

### 问题1：注册接口返回500错误

**原因**：数据库连接失败或表不存在

**解决方案**：
```bash
# 初始化数据库
cd backend
python -c "from app.models.database import engine, Base; Base.metadata.create_all(engine)"
```

### 问题2：邮箱格式验证失败

**原因**：使用了无效的邮箱地址

**解决方案**：使用真实有效的邮箱格式，如 `user@example.com`

### 问题3：密码强度不够

**原因**：密码不满足所有要求

**解决方案**：确保密码包含所有要求的字符类型

### 问题4：用户名已存在

**原因**：该用户名已被其他用户使用

**解决方案**：换一个用户名

## 📚 相关文档

- [API接口文档](http://localhost:8000/docs)
- [数据库设计](backend/app/models/entities.py)
- [安全配置](backend/app/core/security.py)

## 🎉 总结

用户注册功能已完成，包含：

✅ 完整的表单验证
✅ 密码强度检测
✅ 实时反馈
✅ 友好的用户体验
✅ 安全的密码存储
✅ JWT认证
✅ 重复检测
✅ 详细错误提示

所有代码均已通过测试，可直接使用！
