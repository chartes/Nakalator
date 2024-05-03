# Makefile

VENV_DIR = venv

PYTHON = python3
PIP = pip3

VENV_BIN = $(VENV_DIR)/bin
VENV_ACTIVATE = source $(VENV_BIN)/activate
VENV_CHECK = $(shell $(PYTHON) -m virtualenv --version > /dev/null 2>&1; echo $$?)

.PHONY: all check_venv create_venv install_requirements run_tool success build_go

all: check_venv create_venv install_requirements run_tool success

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
	@echo "Build Go binary..."
	@go build -o lib/go_scripts/nakala_request.so -buildmode=c-shared lib/go_scripts/nakala_request.go
	@echo "Go binary built successfully!"