import os
import shutil

cache_dir = r"C:\Users\13054\.cache\huggingface\hub\models--hfl--chinese-roberta-wwm-ext"
blobs_dir = os.path.join(cache_dir, "blobs")
snapshot_dir = os.path.join(cache_dir, "snapshots", "5c58d0b8ec1d9014354d691c538661bf00bfdb44")

print("Setting up model directory structure...\n")
print("="*70)

# 创建快照目录
os.makedirs(snapshot_dir, exist_ok=True)

# 根据文件大小和内容识别文件
files_to_copy = {
    'config.json': None,
    'pytorch_model.bin': None,
    'tf_model.h5': None,
    'flax_model.msgpack': None,
    'tokenizer_config.json': None,
    'tokenizer.json': None,
    'vocab.txt': None,
    'special_tokens_map.json': None,
    'added_tokens.json': None,
    'README.md': None,
    '.gitattributes': None
}

# 扫描所有blob文件
for filename in os.listdir(blobs_dir):
    filepath = os.path.join(blobs_dir, filename)
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    # 根据大小判断
    if size_mb > 100:
        if size_mb > 390:
            files_to_copy['pytorch_model.bin'] = filename
        elif size_mb > 385:
            files_to_copy['tf_model.h5'] = filename
        else:
            files_to_copy['flax_model.msgpack'] = filename
    elif size_mb > 0.2:
        # 可能是 tokenizer.json 或 vocab.txt
        with open(filepath, 'rb') as f:
            header = f.read(100)
        if b'vocab' in header or b'token_type_ids' in header:
            files_to_copy['vocab.txt'] = filename
        else:
            files_to_copy['tokenizer.json'] = filename
    elif size_mb > 0.01:
        # tokenizer_config.json 或 README.md
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(200)
        if '"model_type"' in content or '"hidden_size"' in content:
            files_to_copy['config.json'] = filename
        elif 'README' in content or '# ' in content:
            files_to_copy['README.md'] = filename
        else:
            files_to_copy['tokenizer_config.json'] = filename
    else:
        # 小文件
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(100)
        if '"bos_token"' in content or '"eos_token"' in content:
            files_to_copy['tokenizer_config.json'] = filename
        elif 'version' in content.lower():
            files_to_copy['.gitattributes'] = filename
        elif 'added_tokens' in content:
            files_to_copy['added_tokens.json'] = filename
        else:
            files_to_copy['special_tokens_map.json'] = filename

# 复制文件
print("\nIdentified files:")
for name, blob_hash in files_to_copy.items():
    if blob_hash:
        print(f"  {name:30s} -> {blob_hash} ({os.path.getsize(os.path.join(blobs_dir, blob_hash)) / 1024:.1f} KB)")

print("\nCopying files to snapshot directory...")
for name, blob_hash in files_to_copy.items():
    if blob_hash:
        src = os.path.join(blobs_dir, blob_hash)
        dst = os.path.join(snapshot_dir, name)
        
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  Copied: {name}")
        else:
            print(f"  Already exists: {name}")

# 创建 refs/main 文件
refs_dir = os.path.join(cache_dir, "refs")
os.makedirs(refs_dir, exist_ok=True)
with open(os.path.join(refs_dir, "main"), 'w') as f:
    f.write("5c58d0b8ec1d9014354d691c538661bf00bfdb44")

print("\n" + "="*70)
print("SUCCESS: Model files organized!")
print(f"\nModel location: {snapshot_dir}")
print(f"\nFiles in snapshot directory:")
for f in os.listdir(snapshot_dir):
    print(f"  - {f}")
