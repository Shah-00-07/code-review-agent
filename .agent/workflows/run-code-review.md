---
description: How to run the Code Review Agent on a file or start the file watcher
---
# Running the Code Review Agent

## Option 1: Review a single file
// turbo
1. Run the CLI reviewer on a target file:
```powershell
cd C:\Users\jaini\OneDrive\Desktop\Google` Antigravity; python main.py <target_file>
```
Replace `<target_file>` with the path to the file you want to review (e.g., `review_sample.py`).

## Option 2: Start the background file watcher
// turbo
2. Launch the file watcher daemon (monitors for `.py`, `.js`, `.jsx`, `.diff` changes):
```powershell
cd C:\Users\jaini\OneDrive\Desktop\Google` Antigravity; python .agent/file_watcher.py
```
Review artifacts are saved to `.agent/reviews/`.

## Option 3: Enable Gemini-powered reviews
3. Set your API key before running either option above:
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```
Without the key, the agent falls back to a mock/static review format.
