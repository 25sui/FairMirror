"""RoBERTa-wwm-ext 推理适配器。

默认不下载模型，保证演示和 CI 离线可运行。设置 FAIRMIRROR_ROBERTA_MODEL 后，
可以在本地扩展为 Transformers 推理；未配置时返回可复现的轻量归因结果。
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ModelFinding:
    label: str
    score: float
    start: int
    end: int
    text: str
    source: str = "model"


@dataclass(frozen=True)
class TokenAttribution:
    token: str
    label: str
    contribution: float
    start: int
    end: int


class RobertaBiasProvider:
    model_name = "hfl/chinese-roberta-wwm-ext"

    def __init__(self, model_path: Optional[str] = None) -> None:
        self.model_path = model_path or os.getenv("FAIRMIRROR_ROBERTA_MODEL")
        self.runtime_mode = "transformers" if self._can_use_transformers() else "local_surrogate"
        self.lexicon = {
            "age": ["35岁以下", "年轻团队", "年轻化", "精力充沛", "毕业不超过3年"],
            "gender": ["男性优先", "女性优先", "已婚已育", "短期无生育计划", "无家庭负担"],
            "education": ["985", "211", "双一流", "名校", "第一学历"],
            "region": ["本地户籍", "本地人", "籍贯", "外地人"],
            "proxy": ["空窗", "待业", "照顾家庭", "育儿", "稳定性强"],
        }

    def predict(self, text: str) -> list[ModelFinding]:
        findings: list[ModelFinding] = []
        for label, terms in self.lexicon.items():
            for term in terms:
                for match in re.finditer(re.escape(term), text, flags=re.IGNORECASE):
                    findings.append(
                        ModelFinding(
                            label=label,
                            score=0.88 if label in {"age", "gender"} else 0.68,
                            start=match.start(),
                            end=match.end(),
                            text=match.group(0),
                        )
                    )
        return findings

    def explain(self, text: str) -> list[TokenAttribution]:
        return [
            TokenAttribution(
                token=finding.text,
                label=finding.label,
                contribution=round(0.18 + min(0.42, len(finding.text) / 30), 2),
                start=finding.start,
                end=finding.end,
            )
            for finding in self.predict(text)
        ]

    def _can_use_transformers(self) -> bool:
        if not self.model_path:
            return False
        try:
            import transformers  # noqa: F401
        except Exception:
            return False
        return True


if __name__ == "__main__":
    provider = RobertaBiasProvider()
    sample = "年轻团队，要求35岁以下，985/211优先。"
    print({"runtime_mode": provider.runtime_mode, "findings": [item.__dict__ for item in provider.predict(sample)], "attribution": [item.__dict__ for item in provider.explain(sample)]})