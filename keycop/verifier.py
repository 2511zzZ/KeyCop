import openai
from keycop.storage.json_store import leaked_keys_store, JSONStore
from datetime import datetime
from keycop.config import STORAGE_PATHS

# Create a new store for valid keys
valid_keys_store = JSONStore(STORAGE_PATHS['valid_keys'])

class KeyVerifier:
    """Verifies if a given key is active."""

    def verify_key(self, key_info: dict) -> str:
        """Verifies a key based on its type and returns the new status."""
        api_key = key_info.get('extracted_key')
        if not api_key:
            return 'EXTRACTION_FAILED'

        key_type = key_info.get('key_type', '').lower()
        if key_type != 'openai':
            # For now, we only support OpenAI key verification
            return 'UNSUPPORTED_KEY_TYPE'

        try:
            client = openai.OpenAI(api_key=api_key)
            # Make a lightweight API call to check for validity
            client.models.list()
            return 'VALID_ACTIVE'
        except openai.AuthenticationError:
            # This indicates the key is invalid or inactive
            return 'VALID_INACTIVE'
        except Exception as e:
            print(f"An unexpected error occurred during verification: {e}")
            return 'VERIFICATION_FAILED'

    def run_verification(self):
        """Iterates through 'FOUND' keys, verifies them, and saves valid keys separately."""
        all_keys = leaked_keys_store.read_all()
        keys_to_verify = [key for key in all_keys if key.get('status') == 'FOUND']
        total_to_verify = len(keys_to_verify)
        
        updated_keys = all_keys.copy()
        newly_validated_count = 0

        for i, key in enumerate(updated_keys):
            if key.get('status') == 'FOUND':
                progress = f"({i + 1}/{total_to_verify})"
                new_status = self.verify_key(key)
                print(f"{progress} {new_status} key in {key['repo_full_name']}")
                key['status'] = new_status
                key['last_checked_at'] = datetime.utcnow().isoformat()

                if new_status == 'VALID_ACTIVE':
                    valid_keys_store.append(key)
                    newly_validated_count += 1

        # Overwrite the main log with updated statuses
        leaked_keys_store.write_all(updated_keys)

        if newly_validated_count > 0:
            print(f"Appended {newly_validated_count} new valid keys to valid_keys.json.")

        print("Verification run complete.")