"""RoBERTa-wwm-ext 推理适配骨架。

MVP 阶段由后端规则引擎提供稳定演示结果。真实模型接入时，只需要让该 Provider 输出同样的审计结构。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelFinding:
    label: str
    score: float
    start: int
    end: int
    text: str


class RobertaBiasProvider:
    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path

    def predict(self, text: str) -> list[ModelFinding]:
        raise NotImplementedError("请在准备好 RoBERTa-wwm-ext 权重后接入 Transformers 推理。")