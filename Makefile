# Makefile for running the main application and tests

.PHONY: ev test cli api svelte

dev:
	python3 src/main.py

test:
	pytest tests

cli:
	@echo "Running CLI..."
	python3 gen_podcast/main.py cli

api:
	@echo "Running API Server..."
	uvicorn gen_podcast.main:app --host 127.0.0.1 --port 5432 --reload

svelte:
	@echo "Starting Svelte app..."
	cd web && npm run dev
