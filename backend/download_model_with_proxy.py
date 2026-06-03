import os
import sys
import shutil

# 设置代理环境变量
PROXY_PORT = "7897"
PROXY_URL = f"http://127.0.0.1:{PROXY_PORT}"

os.environ['HTTP_PROXY'] = PROXY_URL
os.environ['HTTPS_PROXY'] = PROXY_URL
os.environ['http_proxy'] = PROXY_URL
os.environ['https_proxy'] = PROXY_URL

print(f"Using proxy: {PROXY_URL}")

# 清理旧缓存
cache_dir = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'hub')
model_cache_dir = os.path.join(cache_dir, 'models--hfl--chinese-roberta-wwm-ext')

if os.path.exists(model_cache_dir):
    print(f"\nCleaning old cache: {model_cache_dir}")
    try:
        shutil.rmtree(model_cache_dir)
        print("   Old cache removed!")
    except Exception as e:
        print(f"   Could not clean cache: {e}")

try:
    from huggingface_hub import snapshot_download
    from transformers import RobertaTokenizer, RobertaForSequenceClassification
    import torch

    print("\n" + "="*60)
    print("Downloading Chinese RoBERTa Model (hfl/chinese-roberta-wwm-ext)")
    print("="*60)
    print("\nThis may take a few minutes (around 400MB)...")

    # 使用 snapshot_download 下载整个模型
    print("\n1. Downloading model files (using snapshot)...")
    model_path = snapshot_download(
        'hfl/chinese-roberta-wwm-ext',
        force_download=True
    )
    print(f"   Model downloaded to: {model_path}")

    # 验证下载的内容
    print("\n2. Verifying download...")
    tokenizer = RobertaTokenizer.from_pretrained(model_path)
    model = RobertaForSequenceClassification.from_pretrained(
        model_path,
        num_labels=5
    )
    print("   Model loaded successfully!")

    print("\n" + "="*60)
    print("SUCCESS: Deep Learning Model Download Complete!")
    print("="*60)

    print(f"\nModel cached at: {cache_dir}")
    print("\nYou can now use deep learning features!")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("\nPlease check your proxy connection.")
    print("Ensure your proxy software (SakuraCat) is running on port 7897.")
    print("\nIf the problem persists, you can try:")
    print("  1. Open your proxy software and make sure it's connected")
    print("  2. Try changing the proxy port in the script if 7897 is not correct")
    print("  3. Continue using rule-based detection (it's still effective!)")
    import traceback
    traceback.print_exc()
    sys.exit(1)
