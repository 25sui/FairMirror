# FairMirror API 文档

基础地址：`http://localhost:8000/api/v1`

## 认证

- `POST /auth/register`：注册用户。
- `POST /auth/login`：登录，返回 Bearer Token。
- `GET /auth/me`：获取当前用户。

## JD 审计

- `POST /jd/analyze`：检测 JD 偏见。
- `POST /jd/`：创建 JD，仅 `admin/hr` 可用。
- `GET /jd/`：查看当前公司 JD，`admin` 可跨公司筛选。
- `GET /jd/{job_id}`：查看 JD 详情，按公司隔离。

## 简历防御

- `POST /resume/scan`：扫描简历敏感信息。
- `POST /resume/`：创建简历记录，本人或 `admin/hr` 可用。
- `GET /resume/{resume_id}`：查看简历扫描记录。

## 面试监控

- `POST /interview/analyze`：执行 4/5 法则与差异影响分析。
- `POST /interview/`：创建面试记录，仅 `admin/hr` 可用。
- `POST /interview/batch`：批量创建面试记录。
- `GET /interview/job/{job_id}`：查看岗位面试记录。

## 合规报告

- `GET /compliance/eu-ai-act/{company_id}`：EU AI Act 检查。
- `GET /compliance/china-ai-ethics/{company_id}`：中国 AI 伦理检查。
- `POST /compliance/report/export`：导出并保存合规检查结果。

## 数据看板

- `GET /dashboard/metrics?company_id=1`：返回 JD、简历、面试、合规聚合指标。

## 认证头

```bash
Authorization: Bearer <access_token>
```