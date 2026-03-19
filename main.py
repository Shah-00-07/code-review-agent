import os
import argparse
from core.analyzer import perform_code_review

def main():
    parser = argparse.ArgumentParser(description="Code Review Agent CLI")
    parser.add_argument("file_path", help="Path to the source file or .diff to review")
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: File '{args.file_path}' not found.")
        return
        
    with open(args.file_path, "r", encoding="utf-8") as f:
        code_content = f.read()
        
    print(f"Analyzing {args.file_path} for Logical, Security, and Style issues...")
    
    # Run the analysis logic (calling the AI model or local static tools)
    report = perform_code_review(code_content, file_name=args.file_path)
    
    print("\n" + "="*50)
    print("CODE REVIEW REPORT")
    print("="*50)
    print(report)

if __name__ == "__main__":
    main()

# --- Firebase Cloud Functions Entry Point ---
from firebase_functions import https_fn
from web.app import app as flask_app

@https_fn.on_request(max_instances=10)
def api(req: https_fn.Request) -> https_fn.Response:
    with flask_app.request_context(req.environ):
        return flask_app.full_dispatch_request()
