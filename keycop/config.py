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
# This section is now dynamically handled by the provider modules.

# --- Storage Configuration ---
# Defines the paths for our JSON-based storage files.
STORAGE_PATHS = {
    'leaked_keys': os.path.join(DATA_DIR, 'leaked_keys.json'),
    'valid_keys': os.path.join(DATA_DIR, 'valid_keys.json'),
}

# --- Notifier Configuration ---
# Template for the GitHub issue that will be created.
ISSUE_TITLE = "Exposed API Key Found"
ISSUE_BODY_TEMPLATE = """Hello @{repo_owner} 👋,

🚨 Our trusty bot **KeyCop** has sniffed out what looks like a leaked API key in your repository.

![He’s not mad, just *disappointed*... and a little concerned.](https://raw.githubusercontent.com/2511zzZ/KeyCop/main/docs/CatCop.jpeg)

---

### 🔍 **Leak Details**
- **Repository:** `{repo_full_name}`
- **File:** `{file_path}`
- **Key Type:** `{key_type}`

---

### 📚 **Why This Matters**

API keys are like passwords — they grant access to services such as OpenAI’s API.  
If someone finds your key on GitHub, they could use it to:
- Run up unexpected charges on your account 💸
- Abuse the API under your name 🕵️
- Get your account suspended due to misuse ⚠️

Even if it’s accidental, **publishing API keys on GitHub is a security risk** and may violate the service’s terms of use.

---

### 🛠️ **What to Do (Right Meow 😼)**

1. **Remove the key from your repository** — even if it's been revoked, leaving it in the commit history may pose risks.
2. **Revoke the leaked key** immediately via the provider console. For example: [OpenAI API Keys dashboard](https://platform.openai.com/account/api-keys).
3. **Rotate the key** if you're still using it in production.
4. For future safety, use **environment variables** or a **secrets management tool** to avoid committing sensitive credentials.

---

If this little nudge from KeyCop helped you, consider giving the project a ⭐ on GitHub:  
👉 [github.com/2511zzZ/KeyCop](https://github.com/2511zzZ/KeyCop)  
It helps us keep the internet a little safer — one key at a time. 😼🔐

---

Thanks for keeping your codebase clean and secure!  
Stay safe,  
**KeyCop Cat**
"""