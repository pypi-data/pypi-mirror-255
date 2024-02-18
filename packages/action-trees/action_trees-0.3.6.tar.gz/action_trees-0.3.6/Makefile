.PHONY: install_pkg, clean, build, lint, list, test, uml

SHELL := /bin/bash

UID := $(shell id -u)
GID := $(shell id -g)
USERNAME := $(shell id -u -n)

MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MKFILE_DIR := $(dir $(MKFILE_PATH))

list:
	@cat Makefile

clean:
	rm -rf src/*.egg-info dist venv public public docs/uml

lint:
	pylint -E src
	pylint -E examples
	mypy src
	mypy examples

test:
	pytest --cov=action_trees --cov-report term-missing tests


install_pkg:
	@echo "Installing package..."
	pip install .


uml: install_pkg
	# generage uml files
	mkdir -p docs/uml/action_trees
	pyreverse src/action_trees -o png -d docs/uml/action_trees

public: uml
	# build html documentation
	mkdocs build -d public

# used inside mkdocs container to build docs and start serving
serve_docs: uml
	# serve html documentation
	mkdocs serve -a 0.0.0.0:8000

build: clean
	python -m build
	# display package contents
	tar -tzf dist/*.tar.gz
