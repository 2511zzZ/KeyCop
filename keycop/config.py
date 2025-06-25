import os

# --- General Configuration ---
# Get the root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the data directory
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# --- GitHub API Configuration ---
# Your GitHub Personal Access Token. It's recommended to use environment variables.
GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN')

# --- Key-specific Configurations ---
# A dictionary defining the types of keys to search for.
# Each key type has a pattern, a search query for GitHub, and a verification endpoint.
KEY_TYPES = {
    'OPENAI': {
        'pattern': 'sk-[a-zA-Z0-9]{48}',
        'search_query': '"OPENAI_API_KEY=sk-" filename:*.py filename:*.js filename:*.ts filename:*.env',
        'verification_endpoint': 'https://api.openai.com/v1/models'
    },
    'GEMINI': {
        # This is a placeholder pattern and endpoint for Gemini.
        'pattern': 'AIzaSy[a-zA-Z0-9_-]{33}',
        'search_query': '"GEMINI_API_KEY="',
        'verification_endpoint': 'https://generativelanguage.googleapis.com/v1beta/models'
    }
    # Add other key types here in the future.
}

# --- Storage Configuration ---
# Defines the paths for our JSON-based storage files.
STORAGE_PATHS = {
    'leaked_keys': os.path.join(DATA_DIR, 'leaked_keys.json'),
    'processed_repos': os.path.join(DATA_DIR, 'processed_repos.json'),
    'scan_history': os.path.join(DATA_DIR, 'scan_history.json')
}

# --- Notifier Configuration ---
# Template for the GitHub issue that will be created.
ISSUE_TITLE = "[Security Alert] Leaked API Key Found in Repository"
ISSUE_BODY_TEMPLATE = """
Hello @{repo_owner},

Our automated scanner, KeyCop, has detected a potentially leaked API key in your repository.

**Details:**
- **Repository:** `{repo_full_name}`
- **File:** `{file_path}`
- **Line Number:** `{line_number}`
- **Key Type:** `{key_type}`

**Recommendation:**
We strongly advise you to immediately revoke this key and replace it. Please also review your commit history to ensure the key is fully removed.

To prevent this in the future, consider using environment variables or a secret management service.

Best,
KeyCop Bot
"""