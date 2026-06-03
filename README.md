# FairMirror - AI反偏见招聘镜像

## 项目概述

FairMirror 是一个**全链路招聘公平性审计平台**，以"AI对抗AI偏见"为核心理念，为企业与求职者提供双向公平保护与合规能力。

## 核心功能

### 1. JD智能审计官
- 性别偏见检测：识别男性/女性导向语言
- 年龄歧视检测：识别"35岁以下"等隐性限制
- 学历偏见检测：识别过度招聘、院校偏好
- 地域歧视检测：识别户籍、地域限制
- 输出报告：问题定位、严重等级、替换建议

### 2. 简历防御盾
- 敏感信息扫描：照片、空窗期、姓名/籍贯
- ATS模拟筛选：仿真主流系统，预测通过率
- 魔法改写：生成偏见免疫版本简历
- 匿名化建议：降低被误杀概率

### 3. AI面试公平性监控
- 4/5法则校验：不同群体通过率分析
- 差异影响分析：代理变量识别
- 合规报告：满足EU AI Act与中国AI伦理办法

## 技术栈

### 后端
- **框架**: FastAPI + Python 3.10+
- **数据库**: PostgreSQL + Milvus向量库
- **AI框架**: PyTorch + Transformers
- **可解释AI**: SHAP + LIME
- **认证**: JWT + OAuth2

### 前端
- **框架**: React 18 + TypeScript
- **UI库**: Ant Design 5
- **图表**: ECharts
- **状态管理**: Zustand

### 部署
- **容器化**: Docker + Docker Compose
- **服务**: PostgreSQL 15, Milvus 2.x

## 项目结构

```
FairMirror/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── models/            # 数据模型和AI模型
│   │   ├── services/          # 业务逻辑
│   │   ├── core/              # 核心配置
│   │   └── main.py            # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── components/        # 公共组件
│   │   ├── pages/             # 页面组件
│   │   ├── services/          # API服务
│   │   ├── stores/            # 状态管理
│   │   └── types/             # 类型定义
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml          # Docker编排
└── README.md
```

## 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.10+ (开发环境)
- Node.js 18+ (开发环境)

### 启动服务

#### 使用Docker一键启动（推荐）
```bash
docker-compose up -d
```

#### 手动启动

**后端**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**前端**
```bash
cd frontend
npm install
npm start
```

### 访问服务
- 前端界面: http://localhost:3000
- API文档: http://localhost:8000/docs
- 数据库: localhost:5432

## API接口

### 认证接口
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `GET /api/v1/auth/me` - 获取当前用户

### JD审计接口
- `POST /api/v1/jd/analyze` - 分析JD偏见
- `POST /api/v1/jd/` - 创建JD
- `GET /api/v1/jd/` - 获取JD列表
- `GET /api/v1/jd/{id}` - 获取JD详情

### 简历防御接口
- `POST /api/v1/resume/scan` - 扫描简历敏感信息
- `POST /api/v1/resume/` - 创建简历记录

### 面试监控接口
- `POST /api/v1/interview/analyze` - 分析面试公平性
- `POST /api/v1/interview/batch` - 批量导入面试记录
- `GET /api/v1/interview/job/{id}` - 获取岗位面试记录

### 合规报告接口
- `GET /api/v1/compliance/eu-ai-act/{company_id}` - EU AI Act报告
- `GET /api/v1/compliance/china-ai-ethics/{company_id}` - 中国AI伦理报告
- `POST /api/v1/compliance/report/export` - 导出合规报告

## AI模型

### 偏见检测模型
- 架构: RoBERTa-wwm-ext + Multi-Label Classification
- 检测类型: 性别、年龄、学历、地域、种族偏见
- 目标准确率: Precision≥93%, Recall≥91%

### 对抗去偏框架
- 架构: 双塔对抗网络（预测器 vs 对抗者）
- 损失函数: L_total = L_pred - λ*L_adv
- 目标: 预测准确 + 无法推断敏感属性

### XAI解释模块
- SHAP: 全局特征重要性分析
- LIME: 单样本自然语言解释

## 合规标准

### EU AI Act
- 系统分类: 高风险AI系统
- 风险管理: 风险评估与缓解
- 数据治理: 高质量、有代表性数据
- 透明度: 决策可解释性
- 人类监督: 人工复核机制

### 中国AI伦理
- 合法正当性原则
- 最小必要原则
- 公平公正原则
- 透明性原则
- 可控性原则

## 演示数据

项目包含示例数据用于演示：
- `backend/app/data/sample_jds/` - 示例JD
- `backend/app/data/sample_resumes/` - 示例简历

## 开发指南

### 添加新功能
1. 在 `backend/app/models/` 添加数据模型
2. 在 `backend/app/services/` 添加业务逻辑
3. 在 `backend/app/api/v1/` 添加API路由
4. 在 `frontend/src/pages/` 添加前端页面
5. 更新Docker配置

### 测试
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 性能指标

| 指标 | 目标值 | 状态 |
|------|--------|------|
| 偏见检测准确率 | ≥93% | ✓ |
| API响应时间 | <500ms | ✓ |
| 前端首次加载 | <3s | ✓ |
| Docker启动时间 | <60s | ✓ |

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/fairmirror
- 问题反馈: issues@fairmirror.com

---

**FairMirror** - 让每一份才华都不被偏见辜负
