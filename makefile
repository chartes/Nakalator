# Makefile

# Nom du répertoire pour l'environnement virtuel
VENV_DIR = venv

# Commandes
PYTHON = python3
PIP = pip3

# Venv
VENV_BIN = $(VENV_DIR)/bin
VENV_ACTIVATE = source $(VENV_BIN)/activate

# Vérification de la disponibilité de virtualenv
VENV_CHECK = $(shell $(PYTHON) -m virtualenv --version > /dev/null 2>&1; echo $$?)

.PHONY: all check_venv create_venv install_requirements run_tool success

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
