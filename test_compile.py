import sys
sys.path.insert(0, '/home/67070309/eak_project/SAX-NeRF')
print("Attempting to compile hash encoder...")
try:
    from src.encoder.hashencoder import HashEncoder
    print("✓ Hash encoder compiled successfully!")
except Exception as e:
    print(f"✗ Compilation failed: {e}")
    import traceback
    traceback.print_exc()
