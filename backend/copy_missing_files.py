import os
import shutil

snapshot_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\snapshots\5c58d0b8ec1d9014354d691c538661bf00bfdb44"
blobs_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\blobs"

files_to_copy = {
    "config.json": "78282c2ccf3682fc74ae985fb0d8a1e6f122a455",
    ".gitattributes": "ae8c63daedbd4206d7d40126955d4e6ab1c80f8f",
    "special_tokens_map.json": "e7b0375001f109a6b8873d756ad4f7bbb15fbaa5",
    "added_tokens.json": "9e26dfeeb6e641a33dae4961196235bdb965b21b"
}

print("Copying missing files...\n")

for filename, hash_name in files_to_copy.items():
    src = os.path.join(blobs_dir, hash_name)
    dst = os.path.join(snapshot_dir, filename)
    
    if os.path.exists(src):
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        print(f"  Copied: {filename} ({size} bytes)")
    else:
        print(f"  Not found: {filename}")

# 检查vocab.txt
vocab_files = [f for f in os.listdir(blobs_dir) if 'vocab' in f.lower() or os.path.getsize(os.path.join(blobs_dir, f)) > 100000]
print(f"\nLooking for vocab.txt...")
for f in os.listdir(blobs_dir):
    size = os.path.getsize(os.path.join(blobs_dir, f))
    if size > 100000 and size < 200000:
        with open(os.path.join(blobs_dir, f), 'rb') as file:
            header = file.read(50)
        if header.startswith(b'RIFF'):
            shutil.copy2(os.path.join(blobs_dir, f), os.path.join(snapshot_dir, "vocab.txt"))
            print(f"  Found vocab.txt: {f} ({size} bytes)")

print("\n" + "="*70)
print("Final files in snapshot directory:")
for f in sorted(os.listdir(snapshot_dir)):
    size = os.path.getsize(os.path.join(snapshot_dir, f))
    if size > 1024 * 1024:
        print(f"  {f:30s} ({size / (1024*1024):.1f} MB)")
    else:
        print(f"  {f:30s} ({size / 1024:.1f} KB)")

print("\n" + "="*70)
print("SUCCESS: All model files are now in place!")
print(f"\nModel path: {snapshot_dir}")
