# FairMirror 安装指南

## 环境要求

- Python 3.10 或更高版本
- pip 包管理器
- 稳定的网络连接（需要下载大型模型文件）

## 安装步骤

### 1. 安装基础依赖

首先安装基础依赖：

```bash
cd backend
pip install -r requirements_base.txt
```

### 2. 安装 AI/ML 依赖（可选）

安装AI模型相关的依赖：

```bash
# 安装PyTorch（CPU版本，较小）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 安装Transformers和其他AI库
pip install transformers scikit-learn shap sentencepiece
```

**注意**：如果需要GPU加速，请访问 [PyTorch官网](https://pytorch.org/) 安装对应版本的GPU版本。

### 3. 快速安装（推荐）

如果您只需要运行基础功能（不包含AI模型推理），可以使用简化版本：

```bash
# 安装仅包含基础功能的依赖
pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy psycopg2-binary python-jose passlib python-multipart
```

### 4. 验证安装

运行以下命令验证安装：

```bash
python -c "import fastapi; import transformers; import torch; print('✓ 所有依赖安装成功')"
```

## 常见问题

### Q1: transformers 安装失败

**解决方案**：

```bash
# 使用国内镜像
pip install transformers -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者使用豆瓣镜像
pip install transformers -i https://pypi.doubanio.com/simple/
```

### Q2: PyTorch 下载太慢

**解决方案**：

```bash
# 使用国内镜像
pip install torch -i https://download.pytorch.org/whl/cpu

# 或者使用清华镜像
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: shap 安装失败

**解决方案**：

```bash
pip install shap -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q4: 内存不足

**解决方案**：

1. 使用CPU版本的PyTorch
2. 不安装AI模型，直接使用基于规则的偏见检测（已内置）

### Q5: 模型下载失败

**解决方案**：

系统会自动下载预训练模型。如果网络不稳定，可以：

1. 使用代理
2. 设置环境变量：
   ```bash
   export HF_ENDPOINT=https://hf-mirror.com
   ```

## 启动服务

安装完成后，启动服务：

```bash
# 方式一：直接启动（推荐用于开发）
uvicorn app.main:app --reload

# 方式二：指定端口
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问：
- API文档：http://localhost:8000/docs
- 交互式文档：http://localhost:8000/redoc

## Docker 安装（推荐）

使用Docker可以避免所有依赖安装问题：

```bash
# 在项目根目录执行
docker-compose up -d

# 访问应用
# 前端：http://localhost:3000
# 后端：http://localhost:8000
```

## 离线安装

如果需要在离线环境安装，请先在有网络的环境下载所有包：

```bash
# 下载所有依赖到本地目录
pip download -r requirements.txt -d ./packages

# 传输到目标机器后安装
pip install --no-index --find-links=./packages -r requirements.txt
```

## 技术支持

如果遇到其他问题，请：

1. 检查Python版本：`python --version`
2. 检查pip版本：`pip --version`
3. 查看错误日志
4. 查看官方文档

祝您使用愉快！🚀
