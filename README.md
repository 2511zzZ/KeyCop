# KeyCop 👮

KeyCop is an automated tool to find leaked API keys on GitHub and notify repository owners.

## Features

- **Search**: Finds potentially leaked keys using GitHub's code search.
- **Verify**: Checks if the found keys are active.
- **Notify**: Automatically creates a GitHub issue to alert the owner.
- **Extensible**: Easily add new key types to search for.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/2511zzZ/KeyCop.git
    cd KeyCop
    ```

2.  Install dependencies:
    ```bash
    make install
    ```

3.  Set your GitHub API Token:
    ```bash
    export GITHUB_API_TOKEN='your_github_personal_access_token'
    ```

## Usage

KeyCop is run from the command line using Make.

1.  **Search for keys:**
    ```bash
    # Search for OpenAI keys
    make search type=OPENAI
    ```

2.  **Verify found keys:**
    ```bash
    make verify
    ```

3.  **Notify owners:**
    ```bash
    # Notify all found repositories
    make notify

    # Notify a specific repository
    make notify repo=owner/repo
    ```

## Disclaimer

This tool is for educational and security research purposes only. Use it responsibly. The creators are not responsible for any misuse.