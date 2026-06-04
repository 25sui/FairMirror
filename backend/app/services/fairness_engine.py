from __future__ import annotations

import re
import uuid
from collections import defaultdict
from statistics import mean

from app.schemas.audit import (
    AtsScore,
    AuditJobSummary,
    AuditReportSummary,
    BiasFinding,
    ComplianceItem,
    ComplianceReport,
    DashboardSummary,
    ExplanationFactor,
    FairnessMetric,
    GroupMetric,
    InterviewAuditResponse,
    InterviewRecord,
    JDAuditResponse,
    ResumeAuditResponse,
    RoleProfile,
    UserRole,
)

Rule = dict[str, object]

JD_RULES: list[Rule] = [
    {"pattern": "35岁以下|年轻化|年轻人", "type": "age", "level": "high", "score": 88, "reason": "年龄门槛会排除具备能力但年龄不匹配的候选人。", "suggestion": "改为说明岗位所需经验、体力或出差条件，避免直接年龄限制。", "compliance": "高风险招聘 AI 应避免年龄歧视与不可解释筛除。"},
    {"pattern": "985|211|双一流|名校", "type": "education", "level": "medium", "score": 68, "reason": "院校标签可能成为能力以外的代理变量。", "suggestion": "改为列出必要知识、项目经验和能力证明方式。", "compliance": "招聘筛选条件应与岗位必要能力直接相关。"},
    {"pattern": "狼性|抗压能力强|高强度加班|长期加班", "type": "workstyle", "level": "medium", "score": 64, "reason": "表达可能强化单一工作风格，影响照护者或特定群体机会。", "suggestion": "改为描述明确工作节奏、资源支持和绩效目标。", "compliance": "工作条件应透明且避免间接排斥。"},
    {"pattern": "男性优先|女性优先|已婚已育|未婚", "type": "gender", "level": "high", "score": 92, "reason": "性别或婚育状态与岗位能力无直接关系。", "suggestion": "删除性别/婚育相关限制，改用能力与职责描述。", "compliance": "直接触发性别平等与就业公平风险。"},
    {"pattern": "本地户籍|本地人|籍贯|外地人", "type": "region", "level": "medium", "score": 70, "reason": "地域信息可能造成与能力无关的机会差异。", "suggestion": "改为说明通勤、驻场或服务区域要求。", "compliance": "地域限制需证明与岗位履约必要性相关。"},
]

RESUME_RULES: list[Rule] = [
    {"pattern": "照片|头像", "type": "appearance", "level": "medium", "score": 62, "reason": "照片可能引入外貌、年龄和性别判断。", "suggestion": "投递版本可移除照片，保留作品集或能力证明。", "compliance": "简历筛选应降低非能力变量影响。"},
    {"pattern": "女|男|已婚|已育|未婚", "type": "gender", "level": "high", "score": 86, "reason": "性别与婚育状态容易触发不公平筛选。", "suggestion": "匿名化版本移除性别与婚育状态。", "compliance": "敏感属性不应作为自动筛选依据。"},
    {"pattern": "籍|户籍|河南|东北|外地", "type": "region", "level": "medium", "score": 66, "reason": "籍贯可能成为地域歧视代理变量。", "suggestion": "保留工作地点偏好即可，不展示籍贯。", "compliance": "候选人画像应限制敏感属性采集。"},
    {"pattern": "空窗|间隔|待业", "type": "proxy", "level": "medium", "score": 58, "reason": "职业空窗可能被系统误判为能力下降。", "suggestion": "补充空窗期间学习、照护、项目或证书产出。", "compliance": "自动化评估应允许候选人补充解释。"},
    {"pattern": r"32岁|35岁|年龄|\d{4}年毕业", "type": "age", "level": "medium", "score": 60, "reason": "年龄与毕业年份可能成为年龄代理变量。", "suggestion": "突出年限、技能栈和成果，弱化年龄标识。", "compliance": "代理变量也需要纳入公平性审计。"},
]


def _findings(text: str, rules: list[Rule]) -> list[BiasFinding]:
    findings: list[BiasFinding] = []
    for rule in rules:
        for match in re.finditer(str(rule["pattern"]), text, flags=re.IGNORECASE):
            findings.append(
                BiasFinding(
                    type=rule["type"],
                    level=rule["level"],
                    score=float(rule["score"]),
                    text=match.group(0),
                    position=(match.start(), match.end()),
                    reason=str(rule["reason"]),
                    suggestion=str(rule["suggestion"]),
                    compliance=str(rule["compliance"]),
                )
            )
    return findings


def _risk_score(findings: list[BiasFinding]) -> float:
    if not findings:
        return 8.0
    weighted = sum(f.score * {"high": 1.15, "medium": 1.0, "low": 0.75}[f.level] for f in findings)
    return round(min(100, weighted / max(1, len(findings)) + len(findings) * 3), 1)


def _explanations(findings: list[BiasFinding]) -> list[ExplanationFactor]:
    if not findings:
        return [ExplanationFactor(feature="能力导向表达", direction="protective", impact=0.18, explanation="文本主要围绕能力、职责和成果，没有明显敏感属性依赖。")]
    grouped: dict[str, float] = defaultdict(float)
    for finding in findings:
        grouped[finding.type] += finding.score / 100
    total = sum(grouped.values()) or 1
    return [
        ExplanationFactor(
            feature=kind,
            direction="risk",
            impact=round(value / total, 2),
            explanation=f"{kind} 相关表达对本次风险评分贡献较高，需要优先整改。",
        )
        for kind, value in sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    ]


def audit_jd(title: str, content: str) -> JDAuditResponse:
    findings = _findings(content, JD_RULES)
    risk = _risk_score(findings)
    rewritten = content
    replacements = {
        "35岁以下": "具备岗位所需经验与交付能力",
        "985/211": "具备相关专业知识或等效项目经验",
        "抗压能力强": "能在明确目标和资源支持下推进复杂任务",
        "高强度加班": "能适应阶段性业务高峰并获得调休支持",
        "狼性": "目标感强、协作推进能力好",
        "本地户籍": "可稳定满足岗位所在城市工作安排",
    }
    for old, new in replacements.items():
        rewritten = rewritten.replace(old, new)
    return JDAuditResponse(
        audit_id=f"jd-{uuid.uuid4().hex[:8]}",
        title=title,
        risk_score=risk,
        inclusive_score=round(100 - risk, 1),
        summary="发现多处可能影响招聘公平性的表达，建议优先移除年龄、院校和地域限制。" if findings else "未发现显著偏见风险。",
        findings=findings,
        explanations=_explanations(findings),
        rewritten=rewritten,
        compliance_flags=sorted({finding.compliance for finding in findings}),
    )


def audit_resume(candidate_name: str, content: str, target_role: str) -> ResumeAuditResponse:
    findings = _findings(content, RESUME_RULES)
    risk = _risk_score(findings)
    ats_scores = [
        AtsScore(system="Keyword ATS", pass_rate=max(30, 86 - risk * 0.34), reason="关键词匹配较好，但敏感信息会降低推荐稳定性。"),
        AtsScore(system="Enterprise ATS", pass_rate=max(25, 78 - risk * 0.42), reason="企业版更关注履历连续性，空窗期需补充解释。"),
        AtsScore(system="LLM Screener", pass_rate=max(35, 82 - risk * 0.28), reason="大模型能理解项目成果，但仍可能受代理变量影响。"),
        AtsScore(system="Campus ATS", pass_rate=max(20, 70 - risk * 0.38), reason="院校与毕业年份权重较高，建议突出能力证据。"),
    ]
    rewritten = re.sub("张敏|男|女|已婚已育|已婚|未婚|河南籍|照片|32岁", "", content)
    rewritten = rewritten.replace("曾因家庭原因有2年职业空窗期", "阶段性完成数据分析课程与增长项目复盘，保持专业能力更新")
    return ResumeAuditResponse(
        audit_id=f"resume-{uuid.uuid4().hex[:8]}",
        candidate_name=candidate_name,
        risk_score=risk,
        ats_scores=[score.model_copy(update={"pass_rate": round(score.pass_rate, 1)}) for score in ats_scores],
        findings=findings,
        rewritten=rewritten.strip(),
        anonymity_tips=["移除照片、性别、婚育、籍贯等非必要字段", "将空窗期改写为能力更新或项目产出", f"围绕 {target_role} 增加成果量化表达"],
        explanations=_explanations(findings),
    )


def audit_interview(batch_name: str, records: list[InterviewRecord]) -> InterviewAuditResponse:
    by_group: dict[str, list[InterviewRecord]] = defaultdict(list)
    for record in records:
        by_group[record.group].append(record)

    metrics: list[GroupMetric] = []
    for group, group_records in by_group.items():
        passed = sum(1 for item in group_records if item.passed)
        metrics.append(
            GroupMetric(
                group=group,
                total=len(group_records),
                passed=passed,
                pass_rate=round(passed / len(group_records), 3),
                average_score=round(mean(item.score for item in group_records), 1),
                average_question_depth=round(mean(item.question_depth for item in group_records), 1),
            )
        )

    rates = [metric.pass_rate for metric in metrics if metric.total]
    max_rate = max(rates) if rates else 0
    min_rate = min(rates) if rates else 0
    ratio = round((min_rate / max_rate) if max_rate else 1, 3)
    demographic_parity_difference = round(max_rate - min_rate, 3)
    average_score_gap = round(max((metric.average_score for metric in metrics), default=0) - min((metric.average_score for metric in metrics), default=0), 1)
    question_depth_gap = round(max((metric.average_question_depth for metric in metrics), default=0) - min((metric.average_question_depth for metric in metrics), default=0), 1)
    overall_selection_rate = round(sum(metric.passed for metric in metrics) / sum(metric.total for metric in metrics), 3) if metrics else 0

    passes_rule = ratio >= 0.8
    risk_level = "low" if passes_rule and demographic_parity_difference <= 0.1 else "high" if ratio < 0.6 or demographic_parity_difference >= 0.35 else "medium"
    fairness_metrics = _interview_fairness_metrics(
        overall_selection_rate=overall_selection_rate,
        disparate_impact_ratio=ratio,
        demographic_parity_difference=demographic_parity_difference,
        average_score_gap=average_score_gap,
        question_depth_gap=question_depth_gap,
    )
    calculation_notes = _interview_calculation_notes(metrics, ratio, demographic_parity_difference)

    return InterviewAuditResponse(
        audit_id=f"interview-{uuid.uuid4().hex[:8]}",
        batch_name=batch_name,
        four_fifths_rule=passes_rule,
        disparate_impact_ratio=ratio,
        risk_level=risk_level,
        metrics=metrics,
        fairness_metrics=fairness_metrics,
        calculation_notes=calculation_notes,
        explanations=[
            ExplanationFactor(feature="差异影响比", direction="risk", impact=round(1 - min(1, ratio), 2), explanation="最低通过率群体与最高通过率群体的比值越低，代表潜在不公平影响越高。"),
            ExplanationFactor(feature="Demographic Parity Difference", direction="risk", impact=round(min(1, demographic_parity_difference), 2), explanation="不同群体通过率绝对差异越大，越需要人工复核。"),
            ExplanationFactor(feature="追问深度差异", direction="risk", impact=round(min(1, question_depth_gap / 5), 2), explanation="不同群体获得的追问深度不一致，可能影响最终评分。"),
        ],
        recommendations=["复核低通过率群体的评分样本", "统一面试追问策略与评分锚点", "对历史面试数据运行代理变量检测", "在报告中保留指标计算口径和批次样本量"],
    )


def _interview_fairness_metrics(
    *,
    overall_selection_rate: float,
    disparate_impact_ratio: float,
    demographic_parity_difference: float,
    average_score_gap: float,
    question_depth_gap: float,
) -> list[FairnessMetric]:
    return [
        FairnessMetric(
            code="selection_rate",
            label="整体通过率",
            value=overall_selection_rate,
            threshold="仅作批次基线",
            status="pass",
            explanation="全部候选人的平均通过率，用于判断本批次筛选强度。",
        ),
        FairnessMetric(
            code="disparate_impact_ratio",
            label="差异影响比",
            value=disparate_impact_ratio,
            threshold=">= 0.8",
            status="pass" if disparate_impact_ratio >= 0.8 else "fail" if disparate_impact_ratio < 0.6 else "warning",
            explanation="最低群体通过率 / 最高群体通过率，低于 0.8 触发 4/5 法则复核。",
        ),
        FairnessMetric(
            code="demographic_parity_difference",
            label="人口统计均等差异",
            value=demographic_parity_difference,
            threshold="<= 0.1 建议通过，>= 0.35 高风险",
            status="pass" if demographic_parity_difference <= 0.1 else "fail" if demographic_parity_difference >= 0.35 else "warning",
            explanation="最高群体通过率 - 最低群体通过率，衡量群体机会差异。",
        ),
        FairnessMetric(
            code="average_score_gap",
            label="平均评分差异",
            value=average_score_gap,
            threshold="<= 8 分建议通过",
            status="pass" if average_score_gap <= 8 else "warning" if average_score_gap <= 15 else "fail",
            explanation="不同群体平均面试分差，用于辅助判断评分锚点是否一致。",
        ),
        FairnessMetric(
            code="question_depth_gap",
            label="追问深度差异",
            value=question_depth_gap,
            threshold="<= 1 建议通过",
            status="pass" if question_depth_gap <= 1 else "warning" if question_depth_gap <= 2 else "fail",
            explanation="不同群体平均追问深度差异，用于观察面试过程一致性。",
        ),
    ]


def _interview_calculation_notes(metrics: list[GroupMetric], ratio: float, demographic_parity_difference: float) -> list[str]:
    if not metrics:
        return ["本批次没有可计算的面试记录。"]

    highest = max(metrics, key=lambda item: item.pass_rate)
    lowest = min(metrics, key=lambda item: item.pass_rate)
    return [
        f"最高通过率群体：{highest.group}，通过率 {highest.pass_rate}。",
        f"最低通过率群体：{lowest.group}，通过率 {lowest.pass_rate}。",
        f"差异影响比 = {lowest.pass_rate} / {highest.pass_rate} = {ratio}。",
        f"人口统计均等差异 = {highest.pass_rate} - {lowest.pass_rate} = {demographic_parity_difference}。",
    ]


def compliance_report() -> ComplianceReport:
    items = [
        ComplianceItem(code="EU-HRA-01", title="高风险 AI 招聘系统登记", jurisdiction="EU AI Act", status="warning", evidence="已生成审计报告，但缺少定期复核计划。", remediation="建立季度公平性复核和留痕机制。"),
        ComplianceItem(code="EU-XAI-02", title="候选人可理解解释", jurisdiction="EU AI Act", status="pass", evidence="JD、简历、面试链路均输出解释因子。", remediation="保持解释模板与模型版本同步。"),
        ComplianceItem(code="CN-ETH-01", title="公平公正与非歧视", jurisdiction="中国AI伦理", status="warning", evidence="部分招聘条件存在年龄和地域风险。", remediation="删除非必要敏感属性，补充人工复核。"),
        ComplianceItem(code="CN-PRIV-02", title="最小必要数据采集", jurisdiction="中国AI伦理", status="pass", evidence="简历防御盾提供匿名化建议。", remediation="将匿名化作为默认投递版本。"),
    ]
    return ComplianceReport(
        report_id=f"compliance-{uuid.uuid4().hex[:8]}",
        organization="FairMirror Demo Corp",
        readiness_score=76.5,
        items=items,
        roadmap=["30天内完成 JD 模板整改", "60天内建立候选人申诉与人工复核通道", "90天内完成面试批次公平性复审"],
    )




def role_profiles() -> list[RoleProfile]:
    return [
        RoleProfile(
            role=UserRole.enterprise_admin,
            label="企业管理员",
            scope="组织级公平性治理、合规准备度和审计闭环",
            permissions=["查看全局 Dashboard", "导出合规报告", "配置角色权限", "跟踪整改路线图"],
            default_view="dashboard",
        ),
        RoleProfile(
            role=UserRole.hr,
            label="HR",
            scope="JD 发布前审计、候选人筛选质量和面试批次复核",
            permissions=["发起 JD 审计", "查看面试公平指标", "创建整改任务"],
            default_view="jd",
        ),
        RoleProfile(
            role=UserRole.candidate,
            label="求职者",
            scope="个人简历偏见防御、ATS 通过率模拟和匿名化建议",
            permissions=["运行简历防御盾", "查看 ATS 预测", "生成偏见免疫版本"],
            default_view="resume",
        ),
        RoleProfile(
            role=UserRole.auditor,
            label="审计员",
            scope="独立审计、证据链复核和监管报告准备",
            permissions=["查看审计证据", "复核 4/5 法则", "生成合规检查清单"],
            default_view="compliance",
        ),
    ]


def audit_job_summaries() -> list[AuditJobSummary]:
    return [
        AuditJobSummary(audit_id="jd-demo-001", kind="jd", title="高级增长产品经理 JD 审计", owner_role=UserRole.hr, status="warning", risk_score=82.6, created_at="2026-05-15T10:12:00Z"),
        AuditJobSummary(audit_id="resume-demo-001", kind="resume", title="增长产品经理简历防御盾", owner_role=UserRole.candidate, status="warning", risk_score=68.2, created_at="2026-05-15T10:18:00Z"),
        AuditJobSummary(audit_id="interview-demo-001", kind="interview", title="2026春招增长岗位批次", owner_role=UserRole.auditor, status="warning", risk_score=74.0, created_at="2026-05-15T10:26:00Z"),
        AuditJobSummary(audit_id="compliance-demo-001", kind="compliance", title="EU AI Act + 中国AI伦理合规报告", owner_role=UserRole.enterprise_admin, status="completed", risk_score=23.5, created_at="2026-05-15T10:32:00Z"),
    ]


def audit_report_summary() -> AuditReportSummary:
    return AuditReportSummary(
        report_id="report-fairmirror-demo",
        title="FairMirror 全链路招聘公平性审计报告",
        organization="FairMirror Demo Corp",
        coverage=["JD 智能审计", "简历防御盾", "AI 面试公平监控", "EU AI Act", "中国 AI 伦理"],
        risk_score=71.8,
        key_findings=[
            "JD 中年龄、院校和工作风格限制构成主要风险来源。",
            "简历中照片、籍贯、婚育和毕业年份属于敏感或代理变量。",
            "面试批次中最低通过率群体与最高通过率群体的差异影响比低于 0.8。",
        ],
        next_actions=[
            "统一 JD 能力描述模板，删除非必要敏感条件。",
            "默认启用匿名化简历版本，并保留候选人补充解释入口。",
            "对面试评分锚点和追问深度进行人工复核。",
        ],
    )


def dashboard_summary() -> DashboardSummary:
    return DashboardSummary(
        fairness_index=82.4,
        open_risks=7,
        audits_completed=128,
        compliance_readiness=76.5,
        bias_heatmap=[
            {"type": "年龄", "jd": 86, "resume": 60, "interview": 74},
            {"type": "学历", "jd": 68, "resume": 42, "interview": 30},
            {"type": "地域", "jd": 70, "resume": 66, "interview": 35},
            {"type": "性别", "jd": 42, "resume": 86, "interview": 58},
        ],
        pass_rate_trend=[
            {"month": "1月", "majority": 0.76, "protected": 0.58},
            {"month": "2月", "majority": 0.74, "protected": 0.61},
            {"month": "3月", "majority": 0.72, "protected": 0.65},
            {"month": "4月", "majority": 0.70, "protected": 0.67},
        ],
        role_distribution=[
            {"role": "企业管理员", "value": 18},
            {"role": "HR", "value": 46},
            {"role": "求职者", "value": 31},
            {"role": "审计员", "value": 5},
        ],
    )
