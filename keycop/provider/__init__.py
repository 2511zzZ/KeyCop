import os
import importlib

# A dictionary to hold all loaded provider modules
PROVIDERS = {}

# Discover and load all provider modules in this directory
provider_dir = os.path.dirname(__file__)
for filename in os.listdir(provider_dir):
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f'keycop.provider.{module_name}')
            PROVIDERS[module_name.upper()] = module
            print(f"Successfully loaded provider: {module_name}")
        except ImportError as e:
            print(f"Failed to load provider {module_name}: {e}")