import json
import os
import threading
from typing import List, Dict, Any

from keycop.config import STORAGE_PATHS, DATA_DIR

class JSONStore:
    """A thread-safe class to handle reading from and writing to JSON files."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensures the directory and a default file exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            # Create an empty list for key storage, or an empty dict for other files.
            default_content = [] if self.file_path.endswith('_keys.json') else {}
            self.write_all(default_content)

    def read_all(self) -> Any:
        """Reads all content from the JSON file."""
        with self._lock:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return [] if self.file_path.endswith('_keys.json') else {}

    def write_all(self, data: Any):
        """Writes all content to the JSON file, overwriting existing content."""
        with self._lock:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    def append(self, item: Dict[str, Any]):
        """Appends a single item to a list-based JSON store."""
        if not isinstance(self.read_all(), list):
            raise TypeError("Append operation is only supported for list-based stores.")
        
        all_data = self.read_all()
        all_data.append(item)
        self.write_all(all_data)

# Instantiate stores for each data file
leaked_keys_store = JSONStore(STORAGE_PATHS['leaked_keys'])
valid_keys_store = JSONStore(STORAGE_PATHS['valid_keys'])