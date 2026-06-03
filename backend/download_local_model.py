import os
import shutil

# 设置代理
PROXY_PORT = "7897"
PROXY_URL = f"http://127.0.0.1:{PROXY_PORT}"
os.environ['HTTP_PROXY'] = PROXY_URL
os.environ['HTTPS_PROXY'] = PROXY_URL

print(f"Using proxy: {PROXY_URL}")

# 本地模型目录
MODEL_DIR = r"e:\vibe coding学习\AI 反偏见招聘镜像（FairMirror）\backend\models\chinese-roberta"
os.makedirs(MODEL_DIR, exist_ok=True)

print("\nDownloading model to local directory...")
print(f"Model will be saved to: {MODEL_DIR}")
print("\nThis may take a few minutes...")

try:
    from huggingface_hub import snapshot_download
    
    print("\nDownloading all model files...")
    path = snapshot_download(
        'hfl/chinese-roberta-wwm-ext',
        cache_dir=MODEL_DIR,
        force_download=True
    )
    
    print(f"\nModel downloaded successfully to: {path}")
    print("\nFiles in model directory:")
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, path)
            size = os.path.getsize(filepath)
            if size > 1024 * 1024:
                print(f"  {rel_path:40s} ({size / (1024*1024):.1f} MB)")
            else:
                print(f"  {rel_path:40s} ({size / 1024:.1f} KB)")
    
    print("\n" + "="*70)
    print("SUCCESS: Model downloaded to local directory!")
    print("="*70)
    print(f"\nModel path for code: {path}")

except Exception as e:
    print(f"\nDownload failed: {e}")
    import traceback
    traceback.print_exc()
