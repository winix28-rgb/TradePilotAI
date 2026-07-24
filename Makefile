# ==========================================================
# TradePilotAI Makefile
# ==========================================================

PYTHON = python

.PHONY: help run test lint format clean docs

help:
	@echo ""
	@echo "TradePilotAI Commands"
	@echo "====================="
	@echo "make run      - Run TradePilotAI"
	@echo "make test     - Run unit tests"
	@echo "make lint     - Run Ruff linter"
	@echo "make format   - Format code with Black"
	@echo "make clean    - Remove cache files"
	@echo "make docs     - Rebuild documentation"

run:
	$(PYTHON) main.py

test:
	pytest

lint:
	ruff check .

format:
	black .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	$(PYTHON) create_docs.py