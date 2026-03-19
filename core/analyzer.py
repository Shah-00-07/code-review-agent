import json
import os

def load_rules():
    """Load the custom ruleset generated earlier."""
    rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ruleset.json')
    if os.path.exists(rules_path):
        with open(rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def build_system_prompt(language="python", target_ruleset="Nirma_University"):
    """
    Constructs the Persona / System Prompt for the LLM.
    You will eventually inject this into a Google Gemini API request.
    """
    rules = load_rules()
    
    prompt = f"""
    Act as a Senior Prompt Engineer and DevOps Specialist.
    Your goal is to act as a Code Review Agent.
    
    Analysis Framework:
    1. Logic & Performance: Detect O(n^2), memory leaks.
    2. Security: Scan for hardcoded credentials, SQL injection.
    3. Readability: Enforce naming conventions.
    
    Custom Rules enforced for {target_ruleset}:
    """
    
    if target_ruleset in rules.get("project_rules", {}):
        custom_rules = rules["project_rules"][target_ruleset]
        prompt += f"- Naming Conventions: {custom_rules.get('naming_conventions')}\n"
        prompt += f"- Architecture Constraints: {custom_rules.get('architecture')}\n"
        
    prompt += """
    Output Specification: Return raw Markdown adhering to:
    - Summary
    - Critical Issues
    - Suggestions
    - Refactored Snippet
    """
    return prompt

def perform_code_review(code_content, file_name="unknown"):
    """
    Core Inference Engine logic.
    Replace the mock payload below with an actual call to `google-genai` package.
    """
    system_prompt = build_system_prompt()
    
    # -------------------------------------------------------------
    # Integrate LLM here (e.g., Gemini API)
    import os
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and api_key.strip():
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[system_prompt, f"Please review this code:\n\n{code_content}"]
            )
            return response.text
        except Exception as e:
            pass # Fallback to mock on error
    # -------------------------------------------------------------
    
    # For now, return a mock Code Review simulating the Agent's response.
    return f"""
### Summary
**Needs Work**: Simulated evaluation of `{file_name}` complete. The Code Review Agent requires a valid LLM API key to perform semantic analysis.

### Critical Issues
- **API Key Missing**: The `google-genai` integration logic is currently commented out in `core/analyzer.py`. You must supply a valid `GEMINI_API_KEY` to transition from mock testing to live intelligent analysis.

### Suggestions
- **Integration**: Un-comment the Google GenAI implementation block in `core/analyzer.py`.
- **Environment**: Set your environment variable `export GEMINI_API_KEY="your_api_key_here"`.

### Refactored Snippet
```python
# Coming soon: AI-generated refactored logic via Gemini Flash 2.5!
```
    """
