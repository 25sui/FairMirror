from typing import List, Dict, Any
import re
from app.models.schemas import (
    BiasLevel,
    SensitiveField,
    ATSResult,
    ResumeScanResponse,
    ResumeScanRequest
)
from datetime import datetime


class ResumeShield:
    def __init__(self):
        self.sensitive_patterns = self._load_sensitive_patterns()
        self.ats_systems = self._load_ats_systems()

    def _load_sensitive_patterns(self) -> Dict[str, Dict[str, Any]]:
        return {
            "photo": {
                "pattern": r"(照片|头像|image|photo)",
                "field_name": "照片/头像",
                "risk": "可能引入外貌偏见",
                "suggestion": "建议删除简历中的照片"
            },
            "age": {
                "pattern": r"(\d{2}岁|\d{4}年\d{1,2}月出生|生于\d{4})",
                "field_name": "年龄信息",
                "risk": "可能导致年龄偏见",
                "suggestion": "建议删除出生年月信息"
            },
            "gender": {
                "pattern": r"(男|女|先生|女士)",
                "field_name": "性别信息",
                "risk": "可能导致性别偏见",
                "suggestion": "建议使用名字而非性别标识"
            },
            "hometown": {
                "pattern": r"(籍贯|出生于|老家|来自.*省)",
                "field_name": "籍贯/出生地",
                "risk": "可能导致地域偏见",
                "suggestion": "建议删除籍贯信息"
            },
            "marital": {
                "pattern": r"(已婚|未婚|离异|子女)",
                "field_name": "婚姻状况",
                "risk": "可能导致婚姻状态偏见",
                "suggestion": "建议删除婚姻状况信息"
            },
            "employment_gap": {
                "pattern": r"(待业|空窗期|离职|gap)",
                "field_name": "职业空窗期",
                "risk": "可能影响简历通过率",
                "suggestion": "可标注为'个人发展期'或'家庭原因'"
            },
        }

    def _load_ats_systems(self) -> List[str]:
        return [
            "Workday",
            "Greenhouse",
            "Lever",
            "Ashby",
            "BambooHR",
            "JazzHR",
            "ZipRecruiter",
            "LinkedIn Recruiter"
        ]

    def scan_sensitive_fields(self, resume_text: str) -> List[SensitiveField]:
        sensitive_fields = []

        for field_key, field_info in self.sensitive_patterns.items():
            matches = list(re.finditer(field_info["pattern"], resume_text))
            if matches:
                for match in matches:
                    start, end = match.start(), match.end()
                    matched_text = resume_text[max(0, start-10):min(len(resume_text), end+10)]

                    risk_level = self._determine_risk_level(field_key)

                    sensitive_fields.append(SensitiveField(
                        field_name=field_info["field_name"],
                        content=f"...{matched_text}...",
                        risk_level=risk_level,
                        suggestion=field_info["suggestion"]
                    ))

        return sensitive_fields

    def _determine_risk_level(self, field_key: str) -> BiasLevel:
        high_risk_fields = ["photo", "gender", "hometown"]
        medium_risk_fields = ["age", "marital"]

        if field_key in high_risk_fields:
            return BiasLevel.HIGH
        elif field_key in medium_risk_fields:
            return BiasLevel.MEDIUM
        else:
            return BiasLevel.LOW

    def simulate_ats(self, resume_text: str, job_id: str = None) -> List[ATSResult]:
        results = []
        sensitive_fields = self.scan_sensitive_fields(resume_text)

        base_pass_rate = 0.75
        risk_penalty = 0
        key_factors = []

        for field in sensitive_fields:
            if field.risk_level == BiasLevel.HIGH:
                risk_penalty += 0.15
                key_factors.append(f"高风险字段: {field.field_name}")
            elif field.risk_level == BiasLevel.MEDIUM:
                risk_penalty += 0.08
                key_factors.append(f"中风险字段: {field.field_name}")
            else:
                risk_penalty += 0.03

        if "年龄" in resume_text:
            key_factors.append("年龄信息可能触发ATS年龄筛选")
        if "照片" in resume_text:
            key_factors.append("照片可能影响ATS评分")

        for system in self.ats_systems:
            pass_prob = max(0.1, base_pass_rate - risk_penalty + (hash(system) % 10) * 0.01)
            results.append(ATSResult(
                system_name=system,
                pass_probability=round(pass_prob, 2),
                key_factors=key_factors[:3] if key_factors else ["简历基本符合要求"]
            ))

        return results

    def rewrite_resume(self, resume_text: str, sensitive_fields: List[SensitiveField]) -> str:
        rewritten = resume_text

        replacements = {
            "photo": "[照片已删除]",
            "age": "[年龄信息已删除]",
            "gender": "[性别标识已删除]",
            "hometown": "[籍贯信息已删除]",
            "marital": "[婚姻状况已删除]",
            "employment_gap": "[职业发展期已标注]"
        }

        for field in sensitive_fields:
            if field.risk_level == BiasLevel.HIGH:
                pattern_key = None
                for key, info in self.sensitive_patterns.items():
                    if info["field_name"] == field.field_name:
                        pattern_key = key
                        break

                if pattern_key and pattern_key in replacements:
                    pattern = self.sensitive_patterns[pattern_key]["pattern"]
                    rewritten = re.sub(pattern, replacements[pattern_key], rewritten)

        if len(rewritten) < len(resume_text) * 0.9:
            rewritten += "\n\n【偏见免疫版本】\n上述敏感信息已脱敏处理，以降低被AI筛选误判的风险。"

        return rewritten

    def determine_overall_risk(self, sensitive_fields: List[SensitiveField]) -> BiasLevel:
        if not sensitive_fields:
            return BiasLevel.LOW

        high_count = sum(1 for f in sensitive_fields if f.risk_level == BiasLevel.HIGH)
        medium_count = sum(1 for f in sensitive_fields if f.risk_level == BiasLevel.MEDIUM)

        if high_count >= 2:
            return BiasLevel.HIGH
        elif high_count >= 1 or medium_count >= 2:
            return BiasLevel.MEDIUM
        else:
            return BiasLevel.LOW

    async def scan_resume(self, request: ResumeScanRequest) -> ResumeScanResponse:
        sensitive_fields = self.scan_sensitive_fields(request.resume_text)
        ats_results = self.simulate_ats(request.resume_text, request.job_id)
        overall_risk = self.determine_overall_risk(sensitive_fields)

        rewritten = None
        if sensitive_fields and overall_risk != BiasLevel.LOW:
            rewritten = self.rewrite_resume(request.resume_text, sensitive_fields)

        return ResumeScanResponse(
            sensitive_fields=sensitive_fields,
            ats_results=ats_results,
            overall_risk_level=overall_risk,
            rewritten_resume=rewritten,
            scan_timestamp=datetime.utcnow()
        )


resume_shield = ResumeShield()
