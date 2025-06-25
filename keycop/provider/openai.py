import re

# Configuration for OpenAI key searching
CONFIG = {
    'pattern': r'sk-(?:proj-)?[a-zA-Z0-9_\-]{48,}',
    'search_query': '"OPENAI_API_KEY=sk-" "T3BlbkFJ"',
    'verification_endpoint': 'https://api.openai.com/v1/models'
}

def extract_key(fragment: str) -> str | None:
    """Extracts an OpenAI API key from a given fragment."""
    match = re.search(CONFIG['pattern'], fragment)
    if match:
        return match.group(0)
    return None