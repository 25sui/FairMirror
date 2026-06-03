# AI反偏见招聘镜像（FairMirror）- 技术设计文档
版本：V1.0 | 日期：2026-05-15

## 1. 技术栈总览
- 前端：React + TypeScript + Ant Design + 数据可视化
- 后端：FastAPI + Docker + 微服务
- 数据库：PostgreSQL + Milvus向量库
- AI框架：PyTorch、Transformers、Fairlearn、AIF360
- 可解释AI：SHAP + LIME
- 部署：云原生、CI/CD、容器编排

## 2. 系统架构（分层）
1. 数据层：JD语料库、匿名简历库、合规规则库、向量库
2. 模型层：偏见分类、对抗去偏、XAI、多模态解析
3. 服务层：JD审计API、简历检测API、面试监控API、合规API
4. 应用层：企业SaaS、求职者端、管理后台、dashboard
5. 合规层：EU AI Act、中国AI伦理审查规则引擎

## 3. 核心AI模块设计
### 3.1 偏见检测引擎
- 模型：RoBERTa-wwm-ext 微调多标签分类
- 检测类型：性别、年龄、学历、地域、种族、外貌偏见
- 能力：200+偏见模式、召回率91%、准确率93%
- 输出：位置、等级、原因、修改建议

### 3.2 可解释AI（XAI）
- SHAP：全局特征重要性、偏见归因
- LIME：单样本自然语言解释（为何被拒/为何有偏见）
- 代理变量挖掘：识别间接歧视特征（毕业年份→年龄等）

### 3.3 对抗去偏见框架（核心创新）
- 双模型对抗架构：预测器 vs 对抗者
- 目标：预测准确 + 无法推断敏感属性（性别/年龄/种族）
- 损失函数：min L_pred - λ*L_adv
- 输出：公平表征、公平性评分、审计报告

### 3.4 多Agent协同系统
- 搜索Agent：爬取公开JD、面试评价
- 分析Agent：偏见检测、公平性计算
- 报告Agent：生成合规报告、整改建议
- 监控Agent：实时告警、趋势追踪

## 4. 数据模型（核心）
```typescript
// 笔记结构（示例）
interface Note {
  id: string;
  title: string;
  content: string;
  createdAt: number;
  updatedAt: number;
}

// 偏见检测结果
interface BiasCheckResult {
  type: 'gender'|'age'|'education'|'region'|'appearance';
  score: number;
  level: 'high'|'medium'|'low';
  text: string;
  position: [number,number];
  suggestion: string;
}

// 面试公平性指标
interface InterviewFairnessMetric {
  groupPassRate: Record<string, number>;
  fourFifthsRule: boolean;
  shapKeyFeatures: string[];
  biasRiskLevel: string;
}
```
## 5. 关键流程
### 5.1 岗位描述审核
- JD 上传 → 文本切片 → 偏见模型推理 → 报告生成
### 5.2 简历检测
- 简历上传 → 脱敏解析 → ATS 仿真 → 风险扫描 → 改写输出
### 5.3 面试监控
- 面试数据接入 → 多模态解析 → 公平性计算 → XAI 解释 → 合规报告
### 5.4 实时监控 → 指标异常 → 自动告警 → 溯源定位 → 整改建议
## 6. 部署与运维
### 6.1 容器化：Docker + Compose
### 6.2 可扩展：支持私有化部署与云托管
### 6.3 安全：数据脱敏、加密、审计日志、权限体系
### 6.4 监控：服务健康、模型性能、公平性指标
