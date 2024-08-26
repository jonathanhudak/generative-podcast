# Makefile for running the main application and tests

.PHONY: ev test

dev:
	python3 src/main.py

test:
	pytest tests
