from github import Github
from keycop.config import GITHUB_API_TOKEN, ISSUE_TITLE, ISSUE_BODY_TEMPLATE
from keycop.storage.json_store import leaked_keys_store
from datetime import datetime

class Notifier:
    """Handles creating GitHub issues to notify repository owners."""

    def __init__(self):
        if not GITHUB_API_TOKEN:
            raise ValueError("GitHub API token not found.")
        self.github = Github(GITHUB_API_TOKEN)

    def run_notification(self):
        """Finds active keys and creates issues for them."""
        all_keys = leaked_keys_store.read_all()
        updated_keys = []
        for key in all_keys:
            if key['status'] == 'VALID_ACTIVE':
                print(f"Notifying for key in {key['repo_full_name']}")
                try:
                    repo = self.github.get_repo(key['repo_full_name'])
                    owner = repo.owner.login
                    body = ISSUE_BODY_TEMPLATE.format(
                        repo_owner=owner,
                        repo_full_name=key['repo_full_name'],
                        file_path=key['file_path'],
                        line_number=key['line_number'],
                        key_type=key['key_type']
                    )
                    repo.create_issue(title=ISSUE_TITLE, body=body)
                    key['status'] = 'NOTIFIED'
                except Exception as e:
                    print(f"Failed to create issue for {key['repo_full_name']}: {e}")
                    key['status'] = 'ERROR'
                key['last_checked_at'] = datetime.utcnow().isoformat()
            updated_keys.append(key)
        leaked_keys_store.write_all(updated_keys)
        print("Notification run complete.")