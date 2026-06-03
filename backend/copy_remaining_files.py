import os
import shutil

blobs_dir = r"C:\Users\13054\.cache\huggingface\hub\models--hfl--chinese-roberta-wwm-ext\blobs"
snapshot_dir = r"C:\Users\13054\.cache\huggingface\hub\models--hfl--chinese-roberta-wwm-ext\snapshots\5c58d0b8ec1d9014354d691c538661bf00bfdb44"

# 手动识别并复制剩余文件
files = {
    'vocab.txt': None,
    'config.json': None,
    'README.md': None,
    '.gitattributes': None
}

for filename in os.listdir(blobs_dir):
    filepath = os.path.join(blobs_dir, filename)
    size = os.path.getsize(filepath)
    
    if size < 10000:  # 小于10KB
        with open(filepath, 'rb') as f:
            header = f.read(50)
        
        if header.startswith(b'RIFF'):
            files['vocab.txt'] = filename
        elif header.startswith(b'{'):
            content = header.decode('utf-8', errors='ignore')
            if '"model_type"' in content:
                files['config.json'] = filename
            elif '# ' in content or 'README' in content:
                files['README.md'] = filename
            elif 'version' in content.lower():
                files['.gitattributes'] = filename

print("Copying remaining files...")
for name, blob_hash in files.items():
    if blob_hash:
        src = os.path.join(blobs_dir, blob_hash)
        dst = os.path.join(snapshot_dir, name)
        
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            size_mb = os.path.getsize(dst) / 1024
            print(f"  Copied: {name} ({size_mb:.1f} KB)")
        else:
            print(f"  Already exists: {name}")

# 列出最终文件
print("\nFinal files in snapshot directory:")
for f in sorted(os.listdir(snapshot_dir)):
    size = os.path.getsize(os.path.join(snapshot_dir, f))
    if size > 1024 * 1024:
        print(f"  {f:30s} ({size / (1024*1024):.1f} MB)")
    else:
        print(f"  {f:30s} ({size / 1024:.1f} KB)")
