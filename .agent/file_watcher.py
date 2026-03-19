import os
import time
import hashlib
from datetime import datetime

# Import the existing perform_code_review from core.analyzer
# (We assume it returns a string in Markdown format)
from core.analyzer import perform_code_review

ROOT_DIR = r"C:\Users\jaini\OneDrive\Desktop\Google Antigravity"
REVIEWS_DIR = os.path.join(ROOT_DIR, ".agent", "reviews")

# Ensure the reviews directory exists
os.makedirs(REVIEWS_DIR, exist_ok=True)

def hash_file(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None

def generate_review_artifact(filepath, content):
    """Generate Markdown Review Artifact including required sections."""
    # Run the core analyzer
    base_report = perform_code_review(content, file_name=os.path.basename(filepath))
    
    # Prepend Status, Performance Analysis, etc., if not heavily present in the mock
    artifact_content = f"""# Code Review Artifact: {os.path.basename(filepath)}
Date: {datetime.now().isoformat()}

## Status (Pass/Fail)
**FAIL** - Pending intelligent analysis completion

## Critical Security Risks
- Reviewing for hardcoded credentials and SQL injection vulnerabilities.
- (See core analyzer output below for details)

## O(n) Performance Analysis
- Reviewing for O(n^2) nested loops and memory leaks.
- Avoid inefficient string concatenations.

## Refactored Snippet
```python
# Awaiting LLM Refactoring
```

---
### Analyzer Output:
{base_report}
"""
    
    filename = f"review_{os.path.basename(filepath)}_{int(time.time())}.md"
    review_path = os.path.join(REVIEWS_DIR, filename)
    with open(review_path, "w", encoding="utf-8") as f:
        f.write(artifact_content)
    print(f"[{datetime.now().time()}] Generated review artifact: {review_path}")

def watch_directory():
    print(f"Monitoring '{ROOT_DIR}' for file saves and .diff creations...")
    file_hashes = {}
    
    # Initial sweep
    for root_path, dirs, files in os.walk(ROOT_DIR):
        if ".agent" in root_path or "__pycache__" in root_path:
            continue
        for file in files:
            if file.endswith(".py") or file.endswith(".diff") or file.endswith(".js") or file.endswith(".jsx"):
                filepath = os.path.join(root_path, file)
                file_hashes[filepath] = hash_file(filepath)

    try:
        while True:
            time.sleep(2)
            for root_path, dirs, files in os.walk(ROOT_DIR):
                if ".agent" in root_path or "__pycache__" in root_path:
                    continue
                for file in files:
                    if file.endswith(".py") or file.endswith(".diff") or file.endswith(".js") or file.endswith(".jsx"):
                        filepath = os.path.join(root_path, file)
                        current_hash = hash_file(filepath)
                        
                        if current_hash is None:
                            continue
                            
                        # If new file or modified
                        if filepath not in file_hashes or file_hashes[filepath] != current_hash:
                            print(f"\n[Change Detected]: {filepath}")
                            file_hashes[filepath] = current_hash
                            
                            try:
                                with open(filepath, "r", encoding="utf-8") as f:
                                    content = f.read()
                                generate_review_artifact(filepath, content)
                            except Exception as e:
                                print(f"Error reading file for review: {e}")
                                
    except KeyboardInterrupt:
        print("Stopping file watcher...")

if __name__ == "__main__":
    watch_directory()
