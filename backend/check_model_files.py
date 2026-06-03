import os

blobs_dir = r"C:\Users\13054\.cache\huggingface\hub\models--hfl--chinese-roberta-wwm-ext\blobs"

print("Checking downloaded model files:\n")
print("="*70)

for filename in sorted(os.listdir(blobs_dir)):
    filepath = os.path.join(blobs_dir, filename)
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    if size_mb > 100:
        file_type = "Model weights (pytorch_model.bin)"
    elif size_mb > 10:
        file_type = "Model weights (tf_model.h5 or flax_model.msgpack)"
    elif size_mb > 0.1:
        file_type = "Config or tokenizer file"
    else:
        file_type = "Small config file"
    
    print(f"{filename}")
    print(f"  Size: {size_mb:.2f} MB")
    print(f"  Type: {file_type}")
    print()

print("="*70)
print("\nThese files are the actual model weights and config files!")
print("We need to organize them into the correct directory structure.")
