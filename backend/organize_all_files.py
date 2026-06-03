import os
import shutil

base_dir = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta\models--hfl--chinese-roberta-wwm-ext"
blobs_dir = os.path.join(base_dir, "blobs")
snapshot_dir = os.path.join(base_dir, "snapshots", "5c58d0b8ec1d9014354d691c538661bf00bfdb44")

print("Analyzing all blob files...\n")

files_info = []

for filename in os.listdir(blobs_dir):
    filepath = os.path.join(blobs_dir, filename)
    size = os.path.getsize(filepath)
    size_mb = size / (1024 * 1024)
    size_kb = size / 1024
    
    file_type = "unknown"
    target_name = None
    
    if size_mb > 100:
        if size_mb > 392:
            file_type = "pytorch_model.bin"
        elif size_mb > 388:
            file_type = "tf_model.h5 (version 1)"
        else:
            file_type = "flax_model.msgpack"
        target_name = file_type.split(' (')[0]
    elif size_kb > 100:
        if size_kb > 200:
            file_type = "tokenizer.json"
            target_name = "tokenizer.json"
        else:
            file_type = "tokenizer_config.json"
            target_name = "tokenizer_config.json"
    elif size_kb > 10:
        if size_kb > 50:
            file_type = "config.json"
            target_name = "config.json"
        else:
            file_type = "unknown (need check)"
    else:
        with open(filepath, 'rb') as f:
            header = f.read(500)
        
        try:
            text = header.decode('utf-8', errors='ignore')
            
            if '"bos_token"' in text or '"eos_token"' in text:
                file_type = "tokenizer_config.json"
                target_name = "tokenizer_config.json"
            elif '"added_tokens"' in text:
                file_type = "added_tokens.json"
                target_name = "added_tokens.json"
            elif '"version"' in text.lower() and ('oid' in text or 'sha' in text.lower()):
                file_type = ".gitattributes"
                target_name = ".gitattributes"
            elif '# ' in text[:100] or 'README' in text[:100]:
                file_type = "README.md"
                target_name = "README.md"
            elif 'special_tokens_map' in text:
                file_type = "special_tokens_map.json"
                target_name = "special_tokens_map.json"
            elif header.startswith(b'RIFF'):
                file_type = "vocab.txt"
                target_name = "vocab.txt"
        except:
            pass
    
    files_info.append({
        'hash': filename,
        'size': size_mb,
        'size_kb': size_kb,
        'type': file_type,
        'target': target_name
    })
    
    print(f"{filename[:8]}... {size_kb:8.1f} KB -> {file_type}")

print("\n" + "="*70)
print("Copying files to snapshot directory...\n")

for info in files_info:
    if info['target']:
        src = os.path.join(blobs_dir, info['hash'])
        dst = os.path.join(snapshot_dir, info['target'])
        
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            if info['size'] > 0.1:
                print(f"  Copied: {info['target']} ({info['size']:.2f} MB)")
            else:
                print(f"  Copied: {info['target']} ({info['size_kb']:.1f} KB)")
        else:
            print(f"  Exists: {info['target']}")

print("\n" + "="*70)
print("Final files in snapshot directory:")
for f in sorted(os.listdir(snapshot_dir)):
    size = os.path.getsize(os.path.join(snapshot_dir, f))
    if size > 1024 * 1024:
        print(f"  {f:30s} ({size / (1024*1024):.1f} MB)")
    else:
        print(f"  {f:30s} ({size / 1024:.1f} KB)")

print("\n" + "="*70)
print(f"Model path: {snapshot_dir}")
