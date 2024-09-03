# Makefile

# MEMO
# command : make build_pkg VERSION_PKG=0.0.1-beta

VENV_DIR = venv

PYTHON = python3
PIP = pip3

VENV_BIN = $(VENV_DIR)/bin
VENV_ACTIVATE = source $(VENV_BIN)/activate
VENV_CHECK = $(shell $(PYTHON) -m virtualenv --version > /dev/null 2>&1; echo $$?)

VERSION_PKG ?= 0.0.1-beta

all: check_venv create_venv install_requirements run_tool success


set_version_pkg:
	@echo "Set version package: $(VERSION_PKG)"
	@sed -i.bak "s/__version__ = [\"'].*[\"']/__version__ = '$(VERSION_PKG)'/" setup.py
	@sed -i.bak "s/version=[\"'].*[\"']/version='$(VERSION_PKG)'/" setup.py
	@rm -f setup.py.bak

build_pkg: set_version_pkg build_go
	@echo "Build package..."
	@$(PYTHON) setup.py sdist bdist_wheel
	@echo "Package built successfully!"

clean_pkg:
	@echo "Clean package..."
	@rm -rf build dist nakalator.egg-info
	@echo "Package cleaned successfully!"

upload_pkg_test: build_pkg
	@echo "Upload package to test pypi..."
	@$(VENV_ACTIVATE) && twine upload --repository testpypi dist/*
	@echo "Package uploaded successfully!"

upload_pkg: build_pkg
	@echo "Upload package to pypi..."
	@$(VENV_ACTIVATE) && twine upload dist/*
	@echo "Package uploaded successfully!"

check_venv:
	@if [ $(VENV_CHECK) -eq 1 ]; then \
	    echo "virtualenv setup..."; \
	    $(PIP) install virtualenv; \
	else \
	    echo "virtualenv is already installed..."; \
	fi

create_venv:
	@echo "Create new virtualenv..."
	@$(PYTHON) -m virtualenv $(VENV_DIR)

install_requirements: create_venv
	@echo "Packages setup..."
	@$(VENV_ACTIVATE) && $(PIP) install -r requirements.txt

run_tool:
	@echo "Run tool with help command..."
	@$(VENV_ACTIVATE) && $(PYTHON) nakalator.py --help

success:
	@echo "Success! You can activate the virtual environment by running the following command:"
	@echo "source $(VENV_BIN)/activate"
	@echo "Then you can run the tool with the following command:"
	@echo "$(PYTHON) nakalator.py"

build_go:
	@echo "Initialize Go module if not already initialized..."
	@if [ ! -f lib/bridge/go.mod ]; then \
	    cd lib/bridge && go mod init lib/bridge && \
	    echo "Fetching dependencies..." && \
	    go mod tidy; \
	else \
	    echo "go.mod already exists. Skipping initialization."; \
	    cd lib/bridge && \
	    echo "Fetching dependencies..." && \
	    go mod tidy; \
	fi && \
	echo "Building Go binary..." && \
	go build -o nakala_request.so -buildmode=c-shared nakala_request.go && \
	echo "Go binary built successfully!"



.PHONY: all check_venv create_venv install_requirements run_tool success build_go set_version_pkg build_pkg clean_pkg upload_pkg_test upload_pkg