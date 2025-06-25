from github import Github, GithubException
from github.PaginatedList import PaginatedList
from github.ContentFile import ContentFile
from keycop.config import GITHUB_API_TOKEN
from keycop.storage.json_store import leaked_keys_store
from keycop.provider import PROVIDERS
import uuid
from datetime import datetime
import time

class CodeSearcher:
    """Handles searching for leaked keys on GitHub."""

    def __init__(self):
        if not GITHUB_API_TOKEN:
            raise ValueError("GitHub API token not found. Please set the GITHUB_API_TOKEN environment variable.")
        self.github = Github(GITHUB_API_TOKEN, per_page=100)

    def _extract_key_from_fragment(self, fragment: str, key_type: str) -> str:
        """Extracts the key from a code fragment using the appropriate provider."""
        provider = PROVIDERS.get(key_type.upper())
        if provider and hasattr(provider, 'extract_key'):
            key = provider.extract_key(fragment)
            if key:
                return key
        return "key-extraction-not-implemented"

    def search_leaked_keys(self, key_type: str):
        """Searches for a specific type of key and saves new findings."""
        provider = PROVIDERS.get(key_type.upper())
        if not provider:
            print(f"Error: Provider for key type '{key_type}' not found.")
            return

        query = provider.CONFIG['search_query']
        print(f"Searching for {key_type} keys with query: {query}")

        try:
            # Manually construct PaginatedList to pass custom headers
            # This is a workaround for PyGithub's search_code not exposing headers parameter
            results = PaginatedList(
                ContentFile,
                self.github._Github__requester,
                "/search/code",
                {"q": query},
                headers={"Accept": "application/vnd.github.text-match+json"}
            )
            
            total_count = results.totalCount
            print(f"Found {total_count} total results from GitHub API.")

            existing_keys = leaked_keys_store.read_all()
            # Create a set of existing locations for quick lookup
            existing_locations = { (k['repo_full_name'], k['file_path']) for k in existing_keys }

            page_num = 0
            processed_count = 0
            # GitHub API returns at most 1000 search results (10 pages of 100)
            total_pages = total_count // 100 + 1

            while page_num < total_pages:
                print(f'\n--- Fetching page {page_num + 1}/{total_pages} ---')
                try:
                    page_results = results.get_page(page_num)
                    page_num += 1
                except GithubException as e:
                    if e.status == 403:
                        print("Rate limit likely hit. Sleeping for 60 seconds before retrying...")
                        time.sleep(60)
                        continue # Retry fetching the same page
                    else:
                        raise e # Re-raise other exceptions

                for content_file in page_results:
                    processed_count += 1
                    print(f"\n--- Processing file {processed_count}/{total_count}: {content_file.repository.full_name}/{content_file.path} ---")

                    if (content_file.repository.full_name, content_file.path) in existing_locations:
                        print(f"Skipping already found file: {content_file.repository.full_name}/{content_file.path}")
                        continue # Skip already found file

                    # The text_matches attribute is a list of dictionaries when using the manual PaginatedList approach
                    if hasattr(content_file, 'text_matches') and content_file.text_matches:
                        print(f"[Debug] text_matches found: {content_file.text_matches}")
                        # Use fragments from text match metadata
                        code_snippet = "\n---\n".join([match['fragment'] for match in content_file.text_matches])
                        # Extract key from the first fragment for simplicity
                        extracted_key = self._extract_key_from_fragment(content_file.text_matches[0]['fragment'], key_type)
                    else:
                        print("[Debug] No text_matches found. Falling back to decoded_content.")
                        # Fallback to decoded content if no text matches
                        decoded_content_str = content_file.decoded_content.decode('utf-8', 'ignore')
                        code_snippet = decoded_content_str
                        extracted_key = self._extract_key_from_fragment(code_snippet, key_type)

                    key_data = {
                        'id': str(uuid.uuid4()),
                        'repo_full_name': content_file.repository.full_name,
                        'file_path': content_file.path,
                        'html_url': content_file.html_url,
                        'code_snippet': code_snippet, # Now stores fragments
                        'extracted_key': extracted_key, # New field
                        'key_type': key_type,
                        'status': 'FOUND',
                        'found_at': datetime.utcnow().isoformat(),
                        'last_checked_at': None
                    }
                    print(f"[Debug] Storing key_data: {key_data}")
                    leaked_keys_store.append(key_data)
                    print(f"Found new potential key in {key_data['repo_full_name']}/{key_data['file_path']}")

                if page_num < total_pages:
                    # Wait 6 seconds to stay under 10 requests/minute for the search API.
                    print("Waiting 6 seconds to avoid rate limiting...")
                    time.sleep(6)
        except GithubException as e:
            print(f"An error occurred while searching GitHub: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")