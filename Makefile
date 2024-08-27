# Makefile for running the main application and tests

.PHONY: ev test cli web

dev:
	python3 src/main.py

test:
	pytest tests

cli:
	@echo "Running CLI..."
	python3 src/main.py cli

web:
	@echo "Running Web Server..."
	python3 src/main.py web
