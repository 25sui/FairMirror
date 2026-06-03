import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional


class AdversarialDebiasingModel(nn.Module):
    def __init__(
        self,
        input_dim: int = 768,
        hidden_dim: int = 256,
        num_sensitive_attrs: int = 5,
        lambda_adv: float = 1.0
    ):
        super(AdversarialDebiasingModel, self).__init__()

        self.lambda_adv = lambda_adv

        self.predictor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, 1)
        )

        self.adversary = nn.Sequential(
            nn.Linear(input_dim + 1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, num_sensitive_attrs)
        )

    def forward_predictor(self, x: torch.Tensor) -> torch.Tensor:
        return self.predictor(x)

    def forward_adversary(self, x: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        combined = torch.cat([x, y_pred], dim=1)
        return self.adversary(combined)

    def compute_fairness_loss(
        self,
        features: torch.Tensor,
        y_true: torch.Tensor,
        sensitive_attrs: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        y_pred = self.forward_predictor(features)

        pred_loss = nn.BCEWithLogitsLoss()(y_pred.squeeze(), y_true)

        sensitive_pred = self.forward_adversary(features, y_pred.detach())
        adv_loss = nn.CrossEntropyLoss()(sensitive_pred, sensitive_attrs)

        total_loss = pred_loss - self.lambda_adv * adv_loss

        return total_loss, pred_loss, adv_loss

    def get_fair_representation(self, x: torch.Tensor) -> torch.Tensor:
        self.eval()
        with torch.no_grad():
            features = x
            y_pred = self.forward_predictor(features)
            adv_pred = self.forward_adversary(features, y_pred)

            adversary_gradients = torch.autograd.grad(
                adv_pred.sum(),
                features,
                retain_graph=True
            )[0]

            fair_features = features - 0.1 * adversary_gradients

        return fair_features

    def evaluate_fairness(
        self,
        features: torch.Tensor,
        y_true: torch.Tensor,
        sensitive_attrs: torch.Tensor
    ) -> Dict[str, float]:
        self.eval()
        with torch.no_grad():
            y_pred = torch.sigmoid(self.forward_predictor(features)).squeeze()

            sensitive_pred = self.forward_adversary(features, y_pred.unsqueeze(1))
            sensitive_probs = torch.softmax(sensitive_pred, dim=1)

            accuracy = ((y_pred > 0.5).float() == y_true).float().mean().item()

            fairness_metrics = {}
            for i in range(sensitive_attrs.max().item() + 1):
                mask = sensitive_attrs == i
                if mask.sum() > 0:
                    group_acc = ((y_pred[mask] > 0.5).float() == y_true[mask]).float().mean().item()
                    fairness_metrics[f'group_{i}_acc'] = group_acc

            disparate_impact = min(fairness_metrics.values()) / max(fairness_metrics.values()) if fairness_metrics else 1.0
            fairness_metrics['disparate_impact'] = disparate_impact

        return {
            'accuracy': accuracy,
            **fairness_metrics
        }


class FairnessTrainer:
    def __init__(
        self,
        model: AdversarialDebiasingModel,
        lr: float = 0.001,
        lambda_adv: float = 1.0
    ):
        self.model = model
        self.lambda_adv = lambda_adv

        self.optimizer_pred = torch.optim.Adam(model.predictor.parameters(), lr=lr)
        self.optimizer_adv = torch.optim.Adam(model.adversary.parameters(), lr=lr * 0.5)

    def train_step(
        self,
        features: torch.Tensor,
        y_true: torch.Tensor,
        sensitive_attrs: torch.Tensor
    ) -> Dict[str, float]:
        self.model.train()

        y_pred = self.model.forward_predictor(features)
        pred_loss = nn.BCEWithLogitsLoss()(y_pred.squeeze(), y_true)

        self.optimizer_pred.zero_grad()
        pred_loss.backward(retain_graph=True)
        self.optimizer_pred.step()

        sensitive_pred = self.model.forward_adversary(features, y_pred.detach())
        adv_loss = nn.CrossEntropyLoss()(sensitive_pred, sensitive_attrs)

        self.optimizer_adv.zero_grad()
        adv_loss.backward()
        self.optimizer_adv.step()

        return {
            'pred_loss': pred_loss.item(),
            'adv_loss': adv_loss.item()
        }

    def train(
        self,
        train_loader,
        val_loader=None,
        epochs: int = 100,
        save_path: str = 'adversarial_model.pt'
    ) -> Dict[str, List[float]]:
        history = {'pred_loss': [], 'adv_loss': [], 'val_fairness': []}

        for epoch in range(epochs):
            epoch_pred_loss = 0
            epoch_adv_loss = 0

            for features, y_true, sensitive_attrs in train_loader:
                losses = self.train_step(features, y_true, sensitive_attrs)
                epoch_pred_loss += losses['pred_loss']
                epoch_adv_loss += losses['adv_loss']

            avg_pred_loss = epoch_pred_loss / len(train_loader)
            avg_adv_loss = epoch_adv_loss / len(train_loader)

            history['pred_loss'].append(avg_pred_loss)
            history['adv_loss'].append(avg_adv_loss)

            if val_loader and epoch % 10 == 0:
                val_metrics = self.evaluate(val_loader)
                history['val_fairness'].append(val_metrics['accuracy'])
                print(f"Epoch {epoch}: pred_loss={avg_pred_loss:.4f}, adv_loss={avg_adv_loss:.4f}, val_acc={val_metrics['accuracy']:.4f}")
            else:
                print(f"Epoch {epoch}: pred_loss={avg_pred_loss:.4f}, adv_loss={avg_adv_loss:.4f}")

        torch.save(self.model.state_dict(), save_path)
        return history

    def evaluate(self, val_loader) -> Dict[str, float]:
        all_features = []
        all_y_true = []
        all_sensitive = []

        self.model.eval()
        with torch.no_grad():
            for features, y_true, sensitive_attrs in val_loader:
                all_features.append(features)
                all_y_true.append(y_true)
                all_sensitive.append(sensitive_attrs)

        all_features = torch.cat(all_features, dim=0)
        all_y_true = torch.cat(all_y_true, dim=0)
        all_sensitive = torch.cat(all_sensitive, dim=0)

        metrics = self.model.evaluate_fairness(all_features, all_y_true, all_sensitive)
        return metrics
