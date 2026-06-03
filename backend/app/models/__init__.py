try:
    from .bias_classifier import BiasClassifier, BiasDetector
    from .adversarial_debiasing import AdversarialDebiasingModel, FairnessTrainer
    from .xai_explainer import XAIExplainer
    AI_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI models not available: {e}")
    print("Using simple mode for bias detection")
    AI_MODELS_AVAILABLE = False
    BiasClassifier = None
    BiasDetector = None
    AdversarialDebiasingModel = None
    FairnessTrainer = None
    XAIExplainer = None

__all__ = [
    "BiasClassifier",
    "BiasDetector",
    "AdversarialDebiasingModel",
    "FairnessTrainer",
    "XAIExplainer",
    "AI_MODELS_AVAILABLE",
]
