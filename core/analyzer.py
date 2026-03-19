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
    Calls Gemini API if GEMINI_API_KEY is set, otherwise returns a mock review.
    """
    system_prompt = build_system_prompt()
    
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    if api_key:
        try:
            from google import genai
            
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[system_prompt, f"Please review this code:\n\n{code_content}"]
            )
            return response.text
        except ImportError as e:
            return f"""
### Error: Missing Dependency
The `google-generativeai` package could not be imported on this server.

**Error:** `{str(e)}`

**Fix:** Ensure `google-generativeai` is in `requirements.txt` and the server has been redeployed.
            """
        except Exception as e:
            return f"""
### Error: Gemini API Call Failed
The AI engine encountered an error while processing your code review.

**Error:** `{str(e)}`

**File:** `{file_name}`

### Suggestions
- Verify your `GEMINI_API_KEY` environment variable is set correctly.
- Check that the API key has access to `gemini-2.5-flash`.
            """
    
    # Fallback mock review when no API key is available
    return f"""
### Summary
**Needs Work**: Simulated evaluation of `{file_name}` complete. The Code Review Agent requires a valid LLM API key to perform semantic analysis.

### Critical Issues
- **API Key Missing**: No `GEMINI_API_KEY` environment variable detected. You must supply a valid key to transition from mock testing to live intelligent analysis.

### Suggestions
- **Environment**: Set your environment variable `GEMINI_API_KEY` in your Render dashboard.

### Refactored Snippet
```python
# Coming soon: AI-generated refactored logic via Gemini Flash 2.5!
```
    """

