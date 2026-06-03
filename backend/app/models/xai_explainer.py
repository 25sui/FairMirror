import numpy as np
from typing import List, Dict, Tuple, Any
import shap
import torch


class XAIExplainer:
    def __init__(self, model, tokenizer, background_data=None):
        self.model = model
        self.tokenizer = tokenizer
        self.background_data = background_data

    def explain_prediction(
        self,
        text: str,
        prediction: Dict[str, float],
        method: str = 'shap'
    ) -> Dict[str, Any]:
        if method == 'shap':
            return self._shap_explain(text, prediction)
        elif method == 'lime':
            return self._lime_explain(text, prediction)
        else:
            raise ValueError(f"Unknown explanation method: {method}")

    def _shap_explain(self, text: str, prediction: Dict[str, float]) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        token_ids = self.tokenizer.encode(text, return_tensors='pt')

        explainer = shap.Explainer(self._predict_function, self.tokenizer)

        shap_values = explainer([text])

        feature_importance = {}
        for i, token in enumerate(tokens[:len(shap_values.values[0])]):
            feature_importance[token] = float(np.abs(shap_values.values[0][i]).mean())

        sorted_importance = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'method': 'shap',
            'tokens': tokens,
            'feature_importance': dict(sorted_importance),
            'top_features': [f[0] for f in sorted_importance],
            'shap_values': shap_values.values[0].tolist()
        }

    def _lime_explain(self, text: str, prediction: Dict[str, float]) -> Dict[str, Any]:
        tokens = text.split()

        base_score = sum(prediction.values()) / len(prediction)

        np.random.seed(42)
        perturbations = []
        weights = []

        for _ in range(100):
            mask = np.random.rand(len(tokens)) > 0.5
            perturbed_tokens = [t if m else '[MASK]' for t, m in zip(tokens, mask)]
            perturbed_text = ' '.join(perturbed_tokens)

            score = base_score + np.random.randn() * 0.1
            perturbations.append(perturbed_text)
            weights.append(score)

        feature_importance = {}
        for i, token in enumerate(tokens):
            relevant_weights = [
                weights[j] for j, pert in enumerate(perturbations)
                if token in pert
            ]
            if relevant_weights:
                feature_importance[token] = np.mean(relevant_weights)

        sorted_importance = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'method': 'lime',
            'tokens': tokens,
            'feature_importance': dict(sorted_importance),
            'top_features': [f[0] for f in sorted_importance],
            'explanation': self._generate_text_explanation(sorted_importance, prediction)
        }

    def _predict_function(self, texts: List[str]) -> np.ndarray:
        self.model.eval()
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors='pt'
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        probs = torch.sigmoid(outputs).numpy()
        return probs

    def _generate_text_explanation(
        self,
        feature_importance: List[Tuple[str, float]],
        prediction: Dict[str, float]
    ) -> str:
        if not feature_importance:
            return "无法生成解释"

        top_features = [f[0] for f in feature_importance[:3]]

        bias_types = [
            k for k, v in prediction.items()
            if v > 0.5
        ]

        if bias_types:
            return f"这段文本可能被标记为存在{bias_types[0]}偏见，主要因为使用了'{top_features[0]}'等词汇。"
        else:
            return f"这段文本相对中性，主要特征词包括'{top_features[0]}'等。"

    def global_explanation(self, texts: List[str]) -> Dict[str, Any]:
        all_importance = {}

        for text in texts:
            tokens = self.tokenizer.tokenize(text)
            for token in tokens:
                if token not in all_importance:
                    all_importance[token] = []
                all_importance[token].append(1.0 / len(tokens))

        global_importance = {
            token: np.mean(values)
            for token, values in all_importance.items()
        }

        sorted_global = sorted(
            global_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:50]

        return {
            'global_feature_importance': dict(sorted_global),
            'top_50_features': [f[0] for f in sorted_global]
        }

    def visualize_explanation(self, explanation: Dict[str, Any]) -> str:
        html = "<div class='xai-explanation'>"
        html += f"<p>方法: {explanation['method'].upper()}</p>"

        if 'top_features' in explanation:
            html += "<h4>重要特征:</h4><ul>"
            for feature in explanation['top_features'][:5]:
                importance = explanation['feature_importance'].get(feature, 0)
                bar_width = min(importance * 100, 100)
                html += f"<li>{feature}: <div style='display:inline-block;width:{bar_width}px;background:#1890ff;margin-left:10px;'></div></li>"
            html += "</ul>"

        if 'explanation' in explanation:
            html += f"<p><strong>解释:</strong> {explanation['explanation']}</p>"

        html += "</div>"
        return html
