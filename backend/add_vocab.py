import os
import shutil

snapshot_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\snapshots\5c58d0b8ec1d9014354d691c538661bf00bfdb44"
blobs_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\blobs"

# ca4f9781030019ab9b253c6dcb8c7878b6dc87a5 看起来是 vocab.txt
vocab_hash = "ca4f9781030019ab9b253c6dcb8c7878b6dc87a5"
vocab_src = os.path.join(blobs_dir, vocab_hash)
vocab_dst = os.path.join(snapshot_dir, "vocab.txt")

if os.path.exists(vocab_src):
    shutil.copy2(vocab_src, vocab_dst)
    print(f"Copied vocab.txt ({os.path.getsize(vocab_dst) / 1024:.1f} KB)")
else:
    print("vocab.txt not found")

print("\nAll files:")
for f in sorted(os.listdir(snapshot_dir)):
    size = os.path.getsize(os.path.join(snapshot_dir, f))
    if size > 1024 * 1024:
        print(f"  {f:30s} ({size / (1024*1024):.1f} MB)")
    else:
        print(f"  {f:30s} ({size / 1024:.1f} KB)")
