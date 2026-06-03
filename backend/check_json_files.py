import os

snapshot_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\snapshots\5c58d0b8ec1d9014354d691c538661bf00bfdb44"

print("Checking tokenizer_config.json...\n")

filepath = os.path.join(snapshot_dir, "tokenizer_config.json")
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} bytes")
print(f"First 500 chars:\n{content[:500]}")
print("\n" + "="*70)
print("Checking config.json...\n")

filepath = os.path.join(snapshot_dir, "config.json")
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} bytes")
print(f"First 500 chars:\n{content[:500]}")
