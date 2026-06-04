# FairMirror 启动说明

FairMirror 是一个反偏见招聘审计演示平台，覆盖 JD 智能审计、简历防御盾、AI 面试公平监控、合规报告和可视化 Dashboard。

## 一键启动

```bash
docker compose up --build
```

启动后访问：

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 本地开发

后端：

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 演示流程

1. 打开“公平性驾驶舱”，按 5 分钟路演节奏展示业务闭环、技术壁垒和正式报告。
2. 查看总体风险、偏见热力图、通过率趋势、多角色工作台、审计任务流和报告摘要。
3. 进入“JD 智能审计”，使用内置高风险 JD 或上传文件，点击开始审计。
4. 查看命中位置、风险原因、替代表达和偏见免疫版 JD。
5. 进入“简历防御盾”，模拟 ATS 通过率，查看匿名化建议和改写版本。
6. 进入“面试公平监控”，查看 4/5 法则、差异影响比和群体通过率。
7. 进入“算法壁垒”，查看 RoBERTa 适配层、Token 归因和对抗去偏前后指标。
8. 进入“合规报告”，导出正式 PDF/JSON 报告，展示证据链、整改路线图和签核区。

## 核心接口

- `GET /api/v1/health`：服务健康检查。
- `GET /api/v1/demo`：演示输入数据。
- `GET /api/v1/roles`：企业管理员、HR、求职者、审计员四类角色画像。
- `GET /api/v1/audit-jobs`：审计任务流。
- `POST /api/v1/jd/audit`：JD 智能审计。
- `POST /api/v1/resume/audit`：简历防御盾。
- `POST /api/v1/interview/audit`：面试公平性审计。
- `GET /api/v1/interview/demo`：内置面试批次审计。
- `GET /api/v1/compliance/report`：合规检查清单。
- `GET /api/v1/dashboard/summary`：Dashboard 聚合指标。
- `GET /api/v1/reports/summary`：全链路审计报告摘要。
- `POST /api/v1/ai/model-audit`：RoBERTa 适配层文本审计与 Token 归因。
- `GET /api/v1/ai/debiasing-demo`：对抗去偏训练演示指标。

## 验证命令

后端测试：

```bash
pytest
```

前端构建：

```bash
cd frontend
npm run build
```

## 交付物

- `frontend/`：React + TypeScript + Ant Design + Recharts 控制台。
- `backend/`：FastAPI API、角色、审计对象、规则引擎和报告结构。
- `ai/`：RoBERTa-wwm-ext 与对抗去偏接入骨架。
- `infra/postgres/init.sql`：PostgreSQL 初始化结构和演示账号。
- `demo-data/fairmirror-demo.json`：演示输入与合规样例。
- `docs/sample-compliance-report.md`：合规报告样例。
- `docs/demo-script.md`：5 分钟演示脚本。
- `docs/pitch-notes.md`：参赛路讲稿要点。

## 技术边界

当前版本优先保证参赛演示闭环：AI 层以规则库、评分器和解释结构实现。`ai/` 中保留 RoBERTa-wwm-ext、SHAP/LIME、对抗去偏的接入位置，后续可替换为真实模型。