.PHONY: install search verify notify

# Install dependencies
install:
	pip install -r requirements.txt

# Search for leaked keys
# Usage: make search type=OPENAI
search:
	@if [ -z "$(type)" ]; then \
		echo "Usage: make search type=<KEY_TYPE>"; \
		exit 1; \
	fi
	python -m keycop.cli search $(type)

# Verify found keys
verify:
	python -m keycop.cli verify

# Notify repository owners
# Usage: make notify
# Usage (for a specific repo): make notify repo=owner/repo
notify:
	python -m keycop.cli notify $(if $(repo),--repo $(repo),)