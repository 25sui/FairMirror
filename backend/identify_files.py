import os

blobs_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext\blobs"

print("Reading small files to identify their types...\n")

files_to_check = [
    "66051e65c65b3ec5e0b437496d1e545c5d8934b4",
    "78282c2ccf3682fc74ae985fb0d8a1e6f122a455",
    "9e26dfeeb6e641a33dae4961196235bdb965b21b",
    "ae8c63daedbd4206d7d40126955d4e6ab1c80f8f",
    "e7b0375001f109a6b8873d756ad4f7bbb15fbaa5"
]

for filename in files_to_check:
    filepath = os.path.join(blobs_dir, filename)
    size = os.path.getsize(filepath)
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    print(f"\n{filename[:8]}... ({size} bytes):")
    print(f"  Hex: {content[:20].hex()}")
    
    try:
        text = content.decode('utf-8', errors='ignore')
        print(f"  Text preview: {text[:100]}")
    except:
        print(f"  Text preview: (binary)")
