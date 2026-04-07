import os
import sys

def check_staging():
    """
    Ensures that the staging/ directory contains the required entity type subdirectories.
    This prevents contributors from accidentally omitting folders required for the workflow.
    """
    required_dirs = [
        "brands", "clubs", "festivals", "frames", "materials",
        "models", "people", "pilots", "shops", "teams", "timeline"
    ]
    staging_path = "staging"
    
    # Check if we are in the Kite-knowledge folder or root
    if not os.path.exists(staging_path) and os.path.exists("Kite-knowledge/staging"):
        staging_path = "Kite-knowledge/staging"
    
    if not os.path.exists(staging_path):
        print(f"ERROR: {staging_path} directory is missing.")
        return 1
    
    missing = []
    for d in required_dirs:
        if not os.path.isdir(os.path.join(staging_path, d)):
            missing.append(d)
            
    if missing:
        print(f"ERROR: Missing staging subdirectories: {', '.join(missing)}")
        return 1
    
    print(f"OK: Staging structure in '{staging_path}' is valid.")
    return 0

if __name__ == "__main__":
    sys.exit(check_staging())
