from github import Github, GithubException
from keycop.config import GITHUB_API_TOKEN, KEY_TYPES
from keycop.storage.json_store import leaked_keys_store
import uuid
from datetime import datetime

class CodeSearcher:
    """Handles searching for leaked keys on GitHub."""

    def __init__(self):
        if not GITHUB_API_TOKEN:
            raise ValueError("GitHub API token not found. Please set the GITHUB_API_TOKEN environment variable.")
        self.github = Github(GITHUB_API_TOKEN)

    def search_leaked_keys(self, key_type: str):
        """Searches for a specific type of key and saves new findings."""
        query = KEY_TYPES[key_type]['search_query']
        print(f"Searching for {key_type} keys with query: {query}")

        try:
            results = self.github.search_code(query)
            existing_keys = leaked_keys_store.read_all()
            # Create a set of existing locations for quick lookup
            existing_locations = { (k['repo_full_name'], k['file_path'], k['line_number']) for k in existing_keys }

            for content_file in results:
                location = (content_file.repository.full_name, content_file.path, content_file.decoded_content.decode('utf-8').splitlines().index(next(l for l in content_file.decoded_content.decode('utf-8').splitlines() if KEY_TYPES[key_type]['pattern'] in l)) + 1)
                if location in existing_locations:
                    continue # Skip already found key

                key_data = {
                    'id': str(uuid.uuid4()),
                    'repo_full_name': content_file.repository.full_name,
                    'file_path': content_file.path,
                    'line_number': location[2],
                    'key_type': key_type,
                    'status': 'FOUND',
                    'found_at': datetime.utcnow().isoformat(),
                    'last_checked_at': datetime.utcnow().isoformat()
                }
                leaked_keys_store.append(key_data)
                print(f"Found new potential key in {key_data['repo_full_name']}")

        except GithubException as e:
            print(f"An error occurred while searching GitHub: {e}")