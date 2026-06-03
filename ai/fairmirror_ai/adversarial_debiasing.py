"""对抗去偏训练骨架。

目标：预测器保留录用相关信息，对抗者难以从表征推断敏感属性。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DebiasingConfig:
    lambda_adv: float = 0.4
    epochs: int = 5
    batch_size: int = 16


def describe_training_objective(config: DebiasingConfig = DebiasingConfig()) -> dict[str, float | str]:
    return {
        "objective": "minimize L_pred - lambda_adv * L_adv",
        "lambda_adv": config.lambda_adv,
        "epochs": config.epochs,
        "batch_size": config.batch_size,
    }