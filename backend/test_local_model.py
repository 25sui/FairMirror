import os
import sys

MODEL_PATH = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\snapshots\5c58d0b8ec1d9014354d691c538661bf00bfdb44"

print("Testing Deep Learning Model Loading from Local Directory...\n")
print("="*70)
print(f"Model Path: {MODEL_PATH}")
print(f"Path exists: {os.path.exists(MODEL_PATH)}")

if os.path.exists(MODEL_PATH):
    print("\nFiles in model directory:")
    for f in sorted(os.listdir(MODEL_PATH)):
        size = os.path.getsize(os.path.join(MODEL_PATH, f))
        if size > 1024 * 1024:
            print(f"  {f:30s} ({size / (1024*1024):.1f} MB)")
        else:
            print(f"  {f:30s} ({size / 1024:.1f} KB)")

print("\n" + "="*70)
print("Loading tokenizer...")

try:
    from transformers import RobertaTokenizer
    
    tokenizer = RobertaTokenizer.from_pretrained(
        MODEL_PATH,
        local_files_only=True
    )
    print("Tokenizer loaded successfully!")
    print(f"  Vocab size: {tokenizer.vocab_size}")
    print(f"  Model max length: {tokenizer.model_max_length}")
    
except Exception as e:
    print(f"Failed to load tokenizer: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("Loading model...")

try:
    from transformers import RobertaForSequenceClassification
    
    model = RobertaForSequenceClassification.from_pretrained(
        MODEL_PATH,
        num_labels=5,
        local_files_only=True
    )
    print("Model loaded successfully!")
    print(f"  Number of labels: {model.num_labels}")
    print(f"  Hidden size: {model.config.hidden_size}")
    
except Exception as e:
    print(f"Failed to load model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("SUCCESS: Deep Learning Model is fully operational!")
print("="*70)
print("\nYou can now use deep learning features in FairMirror.")
