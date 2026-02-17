import time
print("Starting import of model.py...")
start = time.time()
try:
    import model
    print(f"Import successful in {time.time() - start:.2f} seconds.")
except Exception as e:
    print(f"Import failed: {e}")
