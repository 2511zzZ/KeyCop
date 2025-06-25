import requests
from keycop.config import KEY_TYPES
from keycop.storage.json_store import leaked_keys_store
from datetime import datetime

class KeyVerifier:
    """Verifies if a given key is active."""

    def verify_key(self, key_info: dict) -> str:
        """Verifies a key based on its type and returns the new status."""
        key_type = key_info['key_type']
        api_key = "..." # This needs logic to extract the actual key from the file content
        endpoint = KEY_TYPES[key_type]['verification_endpoint']
        headers = {'Authorization': f'Bearer {api_key}'}

        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                return 'VALID_ACTIVE'
            elif response.status_code in [401, 403]:
                return 'VALID_INACTIVE'
            else:
                return 'VERIFICATION_FAILED'
        except requests.RequestException:
            return 'ERROR'

    def run_verification(self):
        """Iterates through 'FOUND' keys and verifies them."""
        all_keys = leaked_keys_store.read_all()
        updated_keys = []
        for key in all_keys:
            if key['status'] == 'FOUND':
                print(f"Verifying key in {key['repo_full_name']}...")
                # NOTE: The logic to get the actual key string is missing.
                # This is a placeholder for the verification logic.
                # In a real scenario, you would fetch the file content and extract the key.
                key['status'] = 'VALID_INACTIVE' # Placeholder
                key['last_checked_at'] = datetime.utcnow().isoformat()
            updated_keys.append(key)
        leaked_keys_store.write_all(updated_keys)
        print("Verification run complete.")