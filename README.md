# KeyCop 👮

KeyCop is an automated tool to find leaked API keys on GitHub and notify repository owners.

## Features

- **Search**: Finds potentially leaked keys using GitHub's code search.
- **Verify**: Checks if the found keys are active (work in progress).
- **Notify**: Automatically creates a GitHub issue to alert the owner.
- **Extensible**: Easily add new key types to search for.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/KeyCop.git
    cd KeyCop
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Set your GitHub API Token:
    ```bash
    export GITHUB_API_TOKEN='your_github_personal_access_token'
    ```

## Usage

KeyCop is run from the command line.

1.  **Search for keys:**
    ```bash
    python -m keycop.cli search OPENAI
    ```

2.  **Verify found keys:**
    ```bash
    python -m keycop.cli verify
    ```

3.  **Notify owners:**
    ```bash
    python -m keycop.cli notify
    ```

## Disclaimer

This tool is for educational and security research purposes only. Use it responsibly. The creators are not responsible for any misuse.