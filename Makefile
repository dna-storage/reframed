
.PHONY: help init develop install test lint clean

help:
	@echo "Available targets:"
	@echo "  init     - Set up full conda + MPI environment (requires config/init.sh)"
	@echo "  develop  - Install package in editable mode"
	@echo "  install  - Install package"
	@echo "  test     - Run the test suite"
	@echo "  lint     - Run flake8 linter"
	@echo "  clean    - Remove build artifacts"

init:
	bash config/init.sh

test:
	python -m pytest tests

lint:
	flake8 dnastorage/ tests/

clean:
	rm -rf build
	rm -rf dist
	rm -rf dnastorage.egg-info
	rm -rf generate.egg-info


install:
	pip3 install --user .

develop:
	pip3 install -e .
