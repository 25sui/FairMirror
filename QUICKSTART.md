# FairMirror 快速开始指南

## 🚀 最快启动方式（推荐）

### 方式一：Docker一键启动（无需安装任何依赖）

```bash
# 在项目根目录执行
cp .env.example .env
# Windows PowerShell 可使用：Copy-Item .env.example .env

# 按需修改 .env 中的 SECRET_KEY、DATABASE_URL、POSTGRES_PASSWORD、CORS_ORIGINS
docker compose up -d

# 等待服务启动...
# 访问地址：
# 前端：http://localhost:3000
# 后端API：http://localhost:8000
# API文档：http://localhost:8000/docs
```

### 方式二：Python直接启动（需要Python环境）

#### 步骤1：安装基础依赖

```bash
cd backend

# 如果在 Windows 系统
install.bat

# 或者在 Linux/Mac 系统
chmod +x install.sh
./install.sh
```

#### 步骤2：启动服务

```bash
# 使用智能启动脚本（自动检测依赖）
python run.py

# 或者直接启动
uvicorn app.main:app --reload
```

#### 步骤3：访问服务

打开浏览器访问：
- API文档：http://localhost:8000/docs
- 交互式文档：http://localhost:8000/redoc

## 📦 依赖说明

### 核心依赖（必须）
- fastapi: Web框架
- uvicorn: ASGI服务器
- pydantic: 数据验证
- sqlalchemy: 数据库ORM

### AI模型依赖（可选）
- transformers: 预训练模型
- torch: 深度学习框架
- shap: 模型解释

**重要**：系统设计了自动降级机制。如果没有安装AI模型依赖，系统会自动使用基于规则的简化偏见检测，功能完全可用！

## 🔧 常见问题解决

### 问题1：transformers 安装失败

**原因**：网络问题或版本冲突

**解决方案**：

```bash
# 使用国内镜像
pip install transformers -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用豆瓣镜像
pip install transformers -i https://pypi.doubanio.com/simple/
```

### 问题2：PyTorch 下载太慢

**解决方案**：

```bash
# CPU版本（较小）
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 使用国内镜像
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：端口被占用

**解决方案**：

```bash
# 查看8000端口占用
netstat -ano | findstr :8000

# 或使用其他端口启动
uvicorn app.main:app --port 8001 --reload
```

### 问题4：模块导入错误

**原因**：缺少依赖包

**解决方案**：

```bash
# 重新安装基础依赖
pip install -r requirements_base.txt

# 检查是否安装成功
python -c "import fastapi; print('✓ FastAPI')"
```

### 问题5：数据库连接错误

**解决方案**：

系统会自动创建SQLite数据库，无需配置。如果使用PostgreSQL：

```bash
# 创建数据库
createdb fairmirror

# 或修改环境变量
set DATABASE_URL=postgresql://user:pass@localhost:5432/fairmirror
```

## 🎯 功能验证

启动服务后，可以测试以下功能：

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

预期输出：
```json
{
  "status": "healthy",
  "service": "FairMirror API",
  "mode": "simple"  // 或 "full"
}
```

### 2. JD偏见检测

```bash
curl -X POST http://localhost:8000/api/v1/jd/analyze \
  -H "Content-Type: application/json" \
  -d '{"jd_text": "招聘男性工程师，要求35岁以下，985优先"}'
```

预期输出：
```json
{
  "bias_results": [
    {
      "type": "gender",
      "score": 0.9,
      "level": "high",
      "text": "男性",
      "suggestion": "使用性别中性语言"
    },
    ...
  ],
  "overall_score": 0.75,
  "overall_level": "high"
}
```

## 🐳 Docker相关问题

### Docker未安装

访问 https://docs.docker.com/get-docker/ 安装Docker Desktop

### Docker启动失败

```bash
# 检查Docker状态
docker --version
docker compose version

# 重新构建镜像
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 访问被拒绝

```bash
# 检查容器状态
docker ps

# 查看日志
docker compose logs -f
```

## 📝 前端连接

前端开发模式访问后端：

1. 确保后端在 localhost:8000 运行
2. 前端会自动连接到后端API
3. 如果前端在 Docker 中运行，已配置正确的网络

## 🎨 自定义配置

### 修改端口

```bash
# 修改后端端口
uvicorn app.main:app --port 8080

# 修改前端端口（修改 frontend/package.json）
"scripts": {
  "start": "PORT=8081 react-scripts start"
}
```

### 修改数据库

```bash
# 环境变量
export DATABASE_URL=postgresql://user:pass@localhost:5432/fairmirror

# 或修改 backend/.env
DATABASE_URL=postgresql://user:pass@localhost:5432/fairmirror
```

### 启用调试模式

```bash
# 后端
uvicorn app.main:app --reload --log-level debug

# 前端
REACT_APP_DEBUG=true npm start
```

## 🎓 学习资源

### 文档链接
- FastAPI文档：https://fastapi.tiangolo.com/
- React文档：https://reactjs.org/
- Transformers文档：https://huggingface.co/docs/transformers/

### 视频教程
- FastAPI入门：搜索"B站 FastAPI教程"
- React + TypeScript：搜索"B站 React教程"

## 🆘 获取帮助

如果遇到其他问题：

1. 查看控制台错误信息
2. 检查日志输出
3. 查看项目文档
4. 提交Issue

## ✅ 快速检查清单

启动前请确认：

- [ ] Python 3.10+ 已安装
- [ ] pip 已更新到最新版本
- [ ] 已安装基础依赖（requirements_base.txt）
- [ ] 端口 8000 未被占用
- [ ] （可选）已安装 Docker Desktop

## 🎉 成功标志

看到以下输出表示启动成功：

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

然后访问 http://localhost:8000/docs 应该看到API文档页面。

---

**祝您使用愉快！** 🚀

如有问题，欢迎提交Issue或联系团队。
