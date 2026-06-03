import uvicorn
import sys

print("=" * 60)
print("FairMirror - AI Anti-Bias Recruitment Platform")
print("=" * 60)
print()
print("Starting in FULL MODE...")
print()

try:
    from app.main import app
    print("[OK] Full mode loaded successfully")
    print()
    print("Access addresses:")
    print("  API Documentation: http://localhost:8000/docs")
    print("  Interactive Docs: http://localhost:8000/redoc")
    print()
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
except Exception as e:
    print(f"[ERROR] Failed to start in full mode: {e}")
    print()
    print("Please install required dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
