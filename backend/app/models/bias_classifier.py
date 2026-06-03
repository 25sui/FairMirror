import torch
import torch.nn as nn
from transformers import RobertaModel, RobertaTokenizer
from typing import List, Dict, Tuple
import re


class BiasClassifier(nn.Module):
    def __init__(
        self,
        model_name: str = "hfl/chinese-roberta-wwm-ext",
        num_labels: int = 5,
        hidden_size: int = 768,
        dropout: float = 0.1
    ):
        super(BiasClassifier, self).__init__()
        self.roberta = RobertaModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size, num_labels)
        self.num_labels = num_labels

        self.bias_types = ['gender', 'age', 'education', 'region', 'race']

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        token_type_ids: torch.Tensor = None
    ) -> torch.Tensor:
        outputs = self.roberta(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )

        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        return logits

    def predict(self, texts: List[str], tokenizer: RobertaTokenizer, device: str = 'cuda') -> List[Dict[str, float]]:
        self.eval()
        self.to(device)

        predictions = []

        with torch.no_grad():
            for text in texts:
                encoding = tokenizer(
                    text,
                    max_length=512,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )

                input_ids = encoding['input_ids'].to(device)
                attention_mask = encoding['attention_mask'].to(device)

                logits = self.forward(input_ids, attention_mask)
                probs = torch.sigmoid(logits).squeeze()

                result = {
                    bias_type: probs[i].item()
                    for i, bias_type in enumerate(self.bias_types)
                }
                predictions.append(result)

        return predictions


class BiasDetector:
    def __init__(self, model_path: str = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = BiasClassifier()
        if model_path:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        self.tokenizer = RobertaTokenizer.from_pretrained('hfl/chinese-roberta-wwm-ext')

        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, List[Dict]]:
        return {
            'gender': [
                {'pattern': r'男性|女性|先生|女士', 'weight': 0.9},
                {'pattern': r'帅哥|美女|小伙子|小姑娘', 'weight': 0.7},
                {'pattern': r'阳刚|柔弱|坚强|细心', 'weight': 0.5},
            ],
            'age': [
                {'pattern': r'\d{2}岁以下|\d{2}岁以上|\d{2}岁以[上下内]', 'weight': 0.9},
                {'pattern': r'35岁|40岁|30岁|25岁', 'weight': 0.8},
                {'pattern': r'年轻人|精力充沛|成熟稳重', 'weight': 0.5},
            ],
            'education': [
                {'pattern': r'985|211|必须|优先', 'weight': 0.9},
                {'pattern': r'名校|第一学历|全日制', 'weight': 0.7},
                {'pattern': r'本科以上|硕士|博士', 'weight': 0.3},
            ],
            'region': [
                {'pattern': r'北京户籍|上海户籍|本地户口', 'weight': 0.9},
                {'pattern': r'本地人|外地人|北方人|南方人', 'weight': 0.7},
                {'pattern': r'籍贯|出生于', 'weight': 0.4},
            ],
            'race': [
                {'pattern': r'汉族|少数民族|外籍', 'weight': 0.8},
            ],
        }

    def detect_pattern_based(self, text: str) -> Dict[str, float]:
        scores = {bias_type: 0.0 for bias_type in self.patterns.keys()}

        for bias_type, patterns in self.patterns.items():
            for pattern_info in patterns:
                matches = re.findall(pattern_info['pattern'], text)
                if matches:
                    scores[bias_type] = max(scores[bias_type], pattern_info['weight'])

        return scores

    def detect(self, text: str, threshold: float = 0.5) -> Tuple[Dict[str, float], List[Dict]]:
        pattern_scores = self.detect_pattern_based(text)

        bias_results = []
        for bias_type, score in pattern_scores.items():
            if score >= threshold:
                matches = []
                for pattern_info in self.patterns.get(bias_type, []):
                    if re.search(pattern_info['pattern'], text):
                        for match in re.finditer(pattern_info['pattern'], text):
                            matches.append({
                                'text': match.group(),
                                'start': match.start(),
                                'end': match.end(),
                                'confidence': pattern_info['weight']
                            })

                bias_results.append({
                    'type': bias_type,
                    'score': score,
                    'matches': matches
                })

        bias_results.sort(key=lambda x: x['score'], reverse=True)
        return pattern_scores, bias_results

    def explain(self, text: str) -> Dict:
        pattern_scores, bias_results = self.detect(text)

        explanations = {}
        for bias_type, score in pattern_scores.items():
            if score > 0:
                explanations[bias_type] = {
                    'score': score,
                    'risk_level': 'high' if score >= 0.7 else 'medium' if score >= 0.4 else 'low',
                    'matched_patterns': [
                        p['pattern'] for p in self.patterns.get(bias_type, [])
                        if re.search(p['pattern'], text)
                    ]
                }

        return {
            'text': text,
            'scores': pattern_scores,
            'explanations': explanations,
            'bias_results': bias_results
        }
