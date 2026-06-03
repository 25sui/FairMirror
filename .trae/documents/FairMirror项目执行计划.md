# FairMirror AI反偏见招聘镜像 - 执行计划

## 一、项目概述

**项目名称**: AI反偏见招聘镜像（FairMirror）
**项目定位**: 全链路招聘公平性审计平台
**核心目标**: 实现JD审计、简历防御、AI面试监控三大核心功能，提供可交付、可演示的完整系统

## 二、技术架构

### 2.1 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 前端 | React 18 + TypeScript + Ant Design 5 | 企业级SaaS界面 |
| 后端 | FastAPI + Python 3.10+ | 高性能API服务 |
| 数据库 | PostgreSQL 15 + Milvus 2.x | 关系数据 + 向量检索 |
| AI框架 | PyTorch + Transformers | 模型训练与推理 |
| 可解释AI | SHAP + LIME | 偏见归因解释 |
| 部署 | Docker + Docker Compose | 一键部署 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (React/TS)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ JD审计模块 │ │ 简历防御  │ │ 面试监控  │ │ Dashboard│   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   API网关层 (FastAPI)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ JD审计API │ │ 简历检测API│ │ 面试监控API│ │ 合规报告API│  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
│ 偏见检测引擎    │ │ XAI解释引擎 │ │ 对抗去偏模块 │
│ (RoBERTa-wwm)  │ │ (SHAP/LIME) │ │ (Adversarial)│
└─────────────────┘ └─────────────┘ └─────────────┘
              │            │            │
              └────────────┼────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│              数据层 (PostgreSQL + Milvus)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ JD语料库 │ │ 简历库   │ │ 合规规则库│ │ 偏见模式库│    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 三、模块划分与实施计划

### 3.1 项目结构

```
FairMirror/
├── frontend/                      # 前端项目
│   ├── src/
│   │   ├── components/            # 公共组件
│   │   │   ├── BiasTag/          # 偏见标签组件
│   │   │   ├── ScoreCard/        # 评分卡片
│   │   │   ├── ReportViewer/     # 报告查看器
│   │   │   └── RiskMeter/        # 风险仪表盘
│   │   ├── pages/               # 页面
│   │   │   ├── JDAudit/          # JD审计页面
│   │   │   ├── ResumeShield/     # 简历防御页面
│   │   │   ├── InterviewMonitor/ # 面试监控页面
│   │   │   ├── Dashboard/        # 数据看板
│   │   │   └── Login/            # 登录页面
│   │   ├── services/             # API服务
│   │   ├── stores/               # 状态管理
│   │   ├── utils/                # 工具函数
│   │   └── types/                # TypeScript类型
│   └── package.json
├── backend/                       # 后端项目
│   ├── app/
│   │   ├── api/                  # API路由
│   │   │   ├── v1/
│   │   │   │   ├── jd/           # JD审计接口
│   │   │   │   ├── resume/      # 简历检测接口
│   │   │   │   ├── interview/    # 面试监控接口
│   │   │   │   └── compliance/  # 合规报告接口
│   │   ├── models/               # 数据模型
│   │   ├── services/             # 业务逻辑
│   │   │   ├── bias_detector/   # 偏见检测服务
│   │   │   ├── xai_explainer/   # XAI解释服务
│   │   │   ├── resume_shield/   # 简历防御服务
│   │   │   └── compliance/      # 合规服务
│   │   ├── core/                 # 核心配置
│   │   └── main.py               # 应用入口
│   ├── models/                   # AI模型
│   │   ├── bias_classifier/     # 偏见分类模型
│   │   ├── adversarial_debias/  # 对抗去偏模型
│   │   └── requirements.txt
│   └── Dockerfile
├── docker-compose.yml            # Docker编排
├── data/                         # 演示数据
│   ├── sample_jds/               # 示例JD
│   ├── sample_resumes/           # 示例简历
│   └── reports/                  # 示例报告
└── docs/                         # 文档
    ├── PRD.md
    ├── TechDesign.md
    └── API.md                    # 接口文档
```

### 3.2 实施阶段

#### **阶段一：基础架构搭建** (第1-3天)

| 序号 | 任务 | 说明 | 交付物 |
|------|------|------|--------|
| 1.1 | 项目初始化 | 创建前后端项目结构，配置开发环境 | 项目骨架代码 |
| 1.2 | Docker环境配置 | 编写Dockerfile和docker-compose.yml | 容器化配置 |
| 1.3 | 数据库设计 | 设计PostgreSQL表结构、Milvus向量索引 | 数据模型SQL |
| 1.4 | API框架搭建 | FastAPI路由结构、认证体系、中间件 | API基础框架 |
| 1.5 | 前端框架搭建 | React路由配置、状态管理、UI组件库 | 前端基础架构 |

#### **阶段二：核心AI模型开发** (第4-8天)

| 序号 | 任务 | 说明 | 交付物 |
|------|------|------|--------|
| 2.1 | 偏见检测模型 | 基于RoBERTa的多标签分类模型 | bias_classifier.pt |
| 2.2 | XAI解释引擎 | 集成SHAP/LIME，生成可解释报告 | xai_service.py |
| 2.3 | 对抗去偏模块 | 实现预测器-对抗者架构 | adversarial_model.py |
| 2.4 | 模型API封装 | 将模型推理封装为REST API | inference_api.py |
| 2.5 | 模型测试验证 | 偏见检测准确率≥93%验证 | 测试报告 |

#### **阶段三：功能模块开发** (第9-14天)

**模块A：JD智能审计官**
| 序号 | 任务 | 说明 | 交付物 |
|------|------|------|--------|
| 3.1 | JD上传解析 | 支持文本/文件上传，文本切片 | jd_parser.py |
| 3.2 | 偏见检测实现 | 性别/年龄/学历/地域偏见检测 | bias_detector.py |
| 3.3 | 报告生成 | 问题定位、严重等级、修改建议 | audit_report.html |
| 3.4 | 前端UI开发 | JD输入框、结果展示、改写建议 | JDAuditPage.tsx |

**模块B：简历防御盾**
| 序号 | 任务 | 说明 | 交付物 |
|------|------|------|--------|
| 3.5 | 简历解析 | 提取关键信息，敏感字段识别 | resume_parser.py |
| 3.6 | ATS仿真 | 模拟主流ATS系统筛选逻辑 | ats_simulator.py |
| 3.7 | 魔法改写 | 生成偏见免疫版本简历 | resume_rewriter.py |
| 3.8 | 前端UI开发 | 简历上传、风险提示、改写结果 | ResumeShieldPage.tsx |

**模块C：AI面试公平性监控**
| 序号 | 任务 | 说明 | 交付物 |
|------|------|------|--------|
| 3.9 | 数据接入 | 面试评分数据导入接口 | interview_api.py |
| 3.10 | 4/5法则校验 | 不同群体通过率差异计算 | four_fifths_check.py |
| 3.11 | 差异影响分析 | 代理变量识别、风险评估 | disparate_impact.py |
| 3.12 | 前端UI开发 | 公平性仪表盘、趋势图 | InterviewMonitorPage.tsx |

#### **阶段四：通用能力与合规** (第15-18天)

| 序号 | 任务 | 说明 | 交付物 |
|------|------|------|--------|
| 4.1 | 合规规则引擎 | EU AI Act、中国AI伦理检查清单 | compliance_rules.py |
| 4.2 | Dashboard可视化 | 偏见热力图、通过率对比、趋势曲线 | DashboardPage.tsx |
| 4.3 | 候选人申诉通道 | 申诉提交、人工复核流程 | appeal_api.py |
| 4.4 | 招聘公平性指数 | 企业公平性榜单计算 | fairness_index.py |
| 4.5 | 权限体系 | 多角色系统（管理员/HR/求职者/审计员） | auth_system.py |

#### **阶段五：集成测试与演示准备** (第19-21天)

| 序号 | 任务 | 说明 | 交付物 |
|------|------|------|--------|
| 5.1 | 前后端联调 | API联调、数据流转验证 | 联调测试报告 |
| 5.2 | 演示数据准备 | 准备演示用的JD、简历、面试数据 | sample_data/ |
| 5.3 | 演示流程设计 | 设计完整演示流程 | demo_script.md |
| 5.4 | 性能优化 | 并发测试、响应时间优化 | 性能测试报告 |
| 5.5 | 部署验证 | 一键部署脚本、Docker启动验证 | 部署验证文档 |

## 四、AI模型详细设计

### 4.1 偏见检测模型

**模型架构**: RoBERTa-wwm-ext + Multi-Label Classification Head

**输入**: 文本序列（JD/简历片段）
**输出**: 多标签偏见分类
- 性别偏见 (gender): 0-1
- 年龄偏见 (age): 0-1
- 学历偏见 (education): 0-1
- 地域偏见 (region): 0-1
- 种族偏见 (race): 0-1

**训练数据**: 标注数据集 10,000+ 条
**评估指标**: Precision≥93%, Recall≥91%, F1≥91%

### 4.2 对抗去偏框架

**架构**: 双塔对抗网络
- 预测器 (Predictor): 预测工作能力
- 对抗者 (Adversary): 尝试从表征推断敏感属性

**损失函数**:
```
L_total = L_pred - λ * L_adv
```

**目标**: 最小化预测误差，最大化对抗损失（使敏感属性无法被推断）

### 4.3 XAI解释模块

**SHAP应用**:
- 全局特征重要性分析
- 偏见归因可视化

**LIME应用**:
- 单样本自然语言解释
- "为什么这份简历被拒绝"的解释

## 五、前端UI设计

### 5.1 页面清单

1. **登录页** - 用户认证、角色选择
2. **JD审计页** - JD输入/上传、偏见检测、报告展示、改写建议
3. **简历防御页** - 简历上传、敏感信息扫描、ATS仿真、改写输出
4. **面试监控页** - 数据导入、公平性指标、4/5法则校验、趋势图
5. **Dashboard** - 偏见热力图、通过率对比、合规状态、预警信息
6. **申诉管理页** - 候选人申诉、状态追踪、人工复核
7. **合规报告页** - EU AI Act检查清单、中国AI伦理审查
8. **管理后台** - 用户管理、角色权限、系统配置

### 5.2 核心组件

| 组件名 | 功能 | 状态 |
|--------|------|------|
| BiasTag | 偏见类型标签（带颜色） | 待开发 |
| ScoreCard | 偏见评分卡片 | 待开发 |
| ReportViewer | 报告查看器（支持PDF导出） | 待开发 |
| RiskMeter | 风险仪表盘 | 待开发 |
| JDInput | JD输入/上传组件 | 待开发 |
| ResumeUploader | 简历上传组件 | 待开发 |
| FairnessChart | 公平性图表组件 | 待开发 |
| HeatMap | 偏见热力图 | 待开发 |

## 六、后端API设计

### 6.1 核心接口

**JD审计API**
```
POST /api/v1/jd/analyze
Request: { "jd_text": string, "job_title": string }
Response: {
  "bias_results": [...],
  "overall_score": float,
  "suggestions": [...],
  "report_url": string
}
```

**简历检测API**
```
POST /api/v1/resume/scan
Request: { "resume_text": string, "job_id": string }
Response: {
  "sensitive_fields": [...],
  "ats_score": float,
  "risk_level": string,
  "rewritten_resume": string
}
```

**面试监控API**
```
POST /api/v1/interview/analyze
Request: { "interview_data": [...], "groups": [...] }
Response: {
  "pass_rates": {...},
  "four_fifths_passed": boolean,
  "disparate_impact_ratio": float,
  "high_risk_features": [...]
}
```

### 6.2 合规报告API

```
GET /api/v1/compliance/eu-ai-act/{company_id}
GET /api/v1/compliance/china-ai-ethics/{company_id}
POST /api/v1/compliance/report/export
```

## 七、数据库设计

### 7.1 核心表结构

**users**
- id, email, password_hash, role, company_id, created_at

**job_descriptions**
- id, company_id, title, content, bias_score, audit_status, created_at

**resumes**
- id, candidate_id, job_id, sensitive_fields, ats_score, risk_level

**interview_records**
- id, candidate_id, job_id, scores, demographic_group, fairness_metrics

**bias_reports**
- id, report_type, target_id, results, suggestions, created_at

**compliance_logs**
- id, company_id, regulation_type, check_items, passed, created_at

### 7.2 Milvus向量索引

**bias_patterns**
- id, text_embedding, bias_type, severity, description

**合规规则向量库**
- id, rule_embedding, regulation, check_type, description

## 八、部署方案

### 8.1 Docker Compose配置

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - milvus
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: fairmirror
      POSTGRES_USER: fairmirror
      POSTGRES_PASSWORD: ***
    
  milvus:
    image: milvusdb/milvus:v2.2.0
    ports:
      - "19530:19530"
```

### 8.2 环境变量配置

```bash
# .env
DATABASE_URL=postgresql://fairmirror:***@postgres:5432/fairmirror
MILVUS_HOST=milvus
MILVUS_PORT=19530
SECRET_KEY=***
REDIS_URL=redis://redis:6379
```

## 九、测试策略

### 9.1 单元测试
- AI模型偏见检测准确率测试
- API接口功能测试
- 前端组件渲染测试

### 9.2 集成测试
- 前后端API联调测试
- 数据库读写测试
- Docker容器编排测试

### 9.3 性能测试
- 并发请求压力测试
- 模型推理响应时间测试
- 页面加载性能测试

## 十、质量保证

| 指标 | 目标值 | 验证方法 |
|------|--------|----------|
| 偏见检测准确率 | ≥93% | 验证集评估 |
| API响应时间 | <500ms | 性能测试 |
| 前端首次加载 | <3s | Lighthouse测试 |
| Docker启动时间 | <60s | 部署测试 |
| 偏见检测召回率 | ≥91% | 验证集评估 |

## 十一、交付物清单

| 序号 | 交付物 | 状态 |
|------|--------|------|
| 1 | 项目完整源码 | 待实现 |
| 2 | Docker一键部署脚本 | 待实现 |
| 3 | 技术设计文档 | 已完成 |
| 4 | API接口文档 | 待实现 |
| 5 | 演示数据与报告样例 | 待实现 |
| 6 | 用户使用手册 | 待实现 |
| 7 | 参赛路演PPT | 待实现 |

## 十二、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| AI模型准确率不足 | 产品价值 | 迭代优化、规则兜底 |
| 演示数据不足 | 演示效果 | 人工构造典型案例 |
| Docker环境问题 | 部署失败 | 提供conda环境备选 |
| 性能瓶颈 | 用户体验 | 分层加载、缓存优化 |

## 十三、后续优化方向

1. **模型增强**: 更多偏见类型、跨语言支持
2. **实时监控**: 流式数据处理、实时告警
3. **API开放**: 第三方系统集成、SDK
4. **移动端**: 小程序/H5适配
5. **国际化**: 多语言界面、合规标准扩展

---

**计划版本**: V1.0
**制定日期**: 2026-05-28
**计划状态**: 待审批
