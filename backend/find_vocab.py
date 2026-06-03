import os

snapshot_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\snapshots\5c58d0b8ec1d9014354d691c538661bf00bfdb44"
blobs_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\blobs"

print("Searching for vocab.txt...\n")

for filename in os.listdir(blobs_dir):
    filepath = os.path.join(blobs_dir, filename)
    size = os.path.getsize(filepath)
    size_kb = size / 1024
    
    if size_kb > 100 and size_kb < 200:
        with open(filepath, 'rb') as f:
            header = f.read(100)
        
        print(f"Found candidate: {filename} ({size_kb:.1f} KB)")
        print(f"  Header: {header[:50]}")
        
        if header.startswith(b'RIFF'):
            dst = os.path.join(snapshot_dir, "vocab.txt")
            shutil.copy2(filepath, dst)
            print(f"  -> Copied as vocab.txt!")
        elif b'vocab' in header or b'token' in header:
            print(f"  -> Might be vocab file")

import shutil
for filename in os.listdir(blobs_dir):
    filepath = os.path.join(blobs_dir, filename)
    size = os.path.getsize(filepath)
    size_kb = size / 1024
    
    if size_kb > 100 and size_kb < 200:
        with open(filepath, 'rb') as f:
            header = f.read(100)
        
        if header.startswith(b'RIFF'):
            dst = os.path.join(snapshot_dir, "vocab.txt")
            shutil.copy2(filepath, dst)
            print(f"\nCopied vocab.txt from {filename}")

print("\n" + "="*70)
print("Final files:")
for f in sorted(os.listdir(snapshot_dir)):
    size = os.path.getsize(os.path.join(snapshot_dir, f))
    if size > 1024 * 1024:
        print(f"  {f:30s} ({size / (1024*1024):.1f} MB)")
    else:
        print(f"  {f:30s} ({size / 1024:.1f} KB)")
