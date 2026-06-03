import os
from typing import List, Dict, Any, Optional
import re
import torch
from app.models.schemas import BiasType, BiasLevel, BiasCheckResult, JDAuditResponse
from app.core.config import settings
from datetime import datetime

MODEL_PATH = os.getenv(
    "BIAS_MODEL_PATH",
    os.path.join(settings.MODEL_PATH, "chinese-roberta")
)

class BiasDetector:
    def __init__(self):
        self.patterns = self._load_bias_patterns()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.tokenizer = None
        self._model_initialized = False
        
        print("BiasDetector initialized.")

    def _load_bias_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "gender": [
                {
                    "pattern": r"(男性|女[性人]|先生|女士|帅哥|美女)",
                    "type": "explicit_gender",
                    "severity": 5,
                    "suggestion": "使用性别中性语言"
                },
                {
                    "pattern": r"(阳刚|柔弱|坚强|细心体贴|领导能力|数理逻辑)",
                    "type": "implicit_gender",
                    "severity": 3,
                    "suggestion": "避免使用与性别相关的刻板印象描述"
                },
            ],
            "age": [
                {
                    "pattern": r"(35岁以[上下内]|40岁以[上下内]|30岁以下|25岁以下)",
                    "type": "explicit_age",
                    "severity": 5,
                    "suggestion": "删除年龄限制要求"
                },
                {
                    "pattern": r"(年轻人|有活力|精力充沛|成熟稳重|老年)",
                    "type": "implicit_age",
                    "severity": 3,
                    "suggestion": "避免使用暗示年龄的描述"
                },
            ],
            "education": [
                {
                    "pattern": r"(985|211|清华|北大|复旦|浙大|必须985|优先985)",
                    "type": "explicit_education",
                    "severity": 4,
                    "suggestion": "改为'本科及以上学历'或'具备相关经验'"
                },
                {
                    "pattern": r"(名校|第一学历|全日制|统招)",
                    "type": "implicit_education",
                    "severity": 2,
                    "suggestion": "考虑能力导向而非院校导向"
                },
            ],
            "region": [
                {
                    "pattern": r"(北京|上海|广州|深圳)户籍|本地户口",
                    "type": "explicit_region",
                    "severity": 5,
                    "suggestion": "删除户籍要求，人才能力不应受地域限制"
                },
                {
                    "pattern": r"(北方人|南方人|本省人|外地人)",
                    "type": "implicit_region",
                    "severity": 4,
                    "suggestion": "避免使用地域偏见语言"
                },
            ],
        }

    def _resolve_model_path(self) -> Optional[str]:
        if os.path.exists(os.path.join(MODEL_PATH, "config.json")):
            return MODEL_PATH

        snapshots_dir = os.path.join(
            MODEL_PATH,
            "models--hfl--chinese-roberta-wwm-ext",
            "snapshots",
        )
        if os.path.isdir(snapshots_dir):
            snapshots = [
                os.path.join(snapshots_dir, item)
                for item in os.listdir(snapshots_dir)
                if os.path.isdir(os.path.join(snapshots_dir, item))
            ]
            if snapshots:
                return sorted(snapshots)[-1]

        return None

    def _try_load_deep_learning_model(self):
        if self._model_initialized:
            return
        
        try:
            model_path = self._resolve_model_path()
            if model_path:
                print("Loading Deep Learning Model from local directory...")
                from transformers import RobertaTokenizer, RobertaForSequenceClassification
                
                self.tokenizer = RobertaTokenizer.from_pretrained(
                    model_path,
                    local_files_only=True
                )
                
                self.model = RobertaForSequenceClassification.from_pretrained(
                    model_path,
                    num_labels=5,
                    local_files_only=True
                )
                self.model.to(self.device)
                self.model.eval()
                
                print("Deep Learning Model loaded successfully!")
                self._model_initialized = True
            else:
                print("Deep Learning Model not found. Using rule-based detection.")
        except Exception as e:
            print(f"Failed to load Deep Learning Model: {e}")
            print("Using rule-based detection instead.")

    def detect_bias_rules(self, text: str) -> List[BiasCheckResult]:
        results = []

        for bias_type, patterns in self.patterns.items():
            for pattern_info in patterns:
                matches = list(re.finditer(pattern_info["pattern"], text))
                for match in matches:
                    start, end = match.start(), match.end()
                    matched_text = text[start:end]

                    score = self._calculate_bias_score(bias_type, pattern_info["severity"])
                    level = self._determine_level(score)

                    results.append(BiasCheckResult(
                        type=BiasType(bias_type),
                        score=score,
                        level=level,
                        text=matched_text,
                        position=[start, end],
                        suggestion=pattern_info["suggestion"],
                        severity=pattern_info["severity"]
                    ))

        return results

    def detect_bias_deep_learning(self, text: str) -> List[BiasCheckResult]:
        if not self.model or not self.tokenizer:
            return []

        try:
            encoding = self.tokenizer(
                text,
                max_length=512,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )

            input_ids = encoding['input_ids'].to(self.device)
            attention_mask = encoding['attention_mask'].to(self.device)

            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                probs = torch.sigmoid(logits).squeeze()

            bias_labels = ['gender', 'age', 'education', 'region', 'race']
            results = []

            for i, bias_type in enumerate(bias_labels):
                if i < len(probs):
                    prob = probs[i].item()
                    if prob > 0.5:
                        score = prob
                        level = BiasLevel.HIGH if prob > 0.7 else BiasLevel.MEDIUM

                        results.append(BiasCheckResult(
                            type=BiasType(bias_type),
                            score=score,
                            level=level,
                            text=f"DL检测:{bias_type}偏见",
                            position=[0, 0],
                            suggestion=f"建议检查{bias_type}相关表述",
                            severity=int(prob * 5)
                        ))

            return results

        except Exception as e:
            print(f"Deep learning detection failed: {e}")
            return []

    def _calculate_bias_score(self, bias_type: str, severity: int) -> float:
        base_scores = {
            "gender": 0.25,
            "age": 0.30,
            "education": 0.20,
            "region": 0.25,
        }
        base = base_scores.get(bias_type, 0.2)
        return min(base * severity / 5, 1.0)

    def _determine_level(self, score: float) -> BiasLevel:
        if score >= 0.7:
            return BiasLevel.HIGH
        elif score >= 0.4:
            return BiasLevel.MEDIUM
        else:
            return BiasLevel.LOW

    def calculate_overall_score(self, bias_results: List[BiasCheckResult]) -> tuple[float, BiasLevel]:
        if not bias_results:
            return 0.0, BiasLevel.LOW

        total_score = sum(result.score for result in bias_results)
        overall = total_score / len(bias_results)

        max_severity = max(result.severity for result in bias_results)
        if max_severity >= 5:
            overall = max(overall, 0.8)
        elif max_severity >= 4:
            overall = max(overall, 0.6)

        level = self._determine_level(overall)
        return round(overall, 2), level

    def generate_suggestions(self, bias_results: List[BiasCheckResult], use_deep_learning: bool = False) -> List[str]:
        suggestions = []
        seen_types = set()

        for result in bias_results:
            if result.type.value not in seen_types:
                method_tag = "[DL] " if "DL检测" in result.text else ""
                suggestions.append(
                    f"{method_tag}[{result.type.value}偏见]{result.suggestion}(严重程度:{result.severity}/5)"
                )
                seen_types.add(result.type.value)

        if not suggestions:
            suggestions.append("恭喜！您的内容未检测到明显的偏见内容")
            suggestions.append("建议持续关注语言的包容性")
        else:
            if use_deep_learning and self._model_initialized:
                suggestions.append("以上结果由深度学习模型辅助检测")
            suggestions.append("建议对上述偏见内容进行修改，以提高招聘的公平性")

        return suggestions

    async def analyze_jd(self, jd_text: str, job_title: str = None, use_deep_learning: bool = False) -> JDAuditResponse:
        # 规则检测总是运行
        bias_results = self.detect_bias_rules(jd_text)
        
        # 如果启用深度学习，尝试加载模型并进行检测
        dl_used = False
        if use_deep_learning:
            self._try_load_deep_learning_model()
            if self._model_initialized:
                print("Using Deep Learning Model for additional detection...")
                dl_results = self.detect_bias_deep_learning(jd_text)
                bias_results.extend(dl_results)
                dl_used = True

        overall_score, overall_level = self.calculate_overall_score(bias_results)
        suggestions = self.generate_suggestions(bias_results, dl_used)

        return JDAuditResponse(
            bias_results=bias_results,
            overall_score=overall_score,
            overall_level=overall_level,
            suggestions=suggestions,
            report_url=None,
            audit_timestamp=datetime.utcnow()
        )

bias_detector = BiasDetector()
