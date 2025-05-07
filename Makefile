PKG_VERSION = $(shell python -c "import importlib.metadata; print(importlib.metadata.version('felipper_client'))")

.PHONY: help install install-dev clean version publish hooks mypy

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/^([a-zA-Z0-9_-]+):.*## (.*)/\1\t\2/' | sort

install: ## Install the package
	uv pip install .

install-dev: ## Install development dependencies
	uv pip install .[dev]

clean: ## Clean up build artifacts
	@rm -rf build
	@rm -rf dist

version: ## Show the package version
	@echo ${PKG_VERSION}

publish: ## Publish the package
	uv publish .

hooks: ## Run pre-commit hooks
	pre-commit run --all-files

mypy: ## Run type checks with mypy
	@mypy --follow-imports=silent --ignore-missing-imports flipper
