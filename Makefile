#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = INEQMX-ENCO-2022
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	
## Download raw data
.PHONY: download_data
download_data:
	@echo ">>> Downloading raw data..."
	$(PYTHON_INTERPRETER) modules/dataset_modules/data_downloader.py

## Transform raw data into interim data
.PHONY: transform_data
transform_data:
	@echo ">>> Transforming raw data..."
	$(PYTHON_INTERPRETER) modules/dataset_modules/data_transform_enco.py
	$(PYTHON_INTERPRETER) modules/dataset_modules/data_transform_engih.py
	$(PYTHON_INTERPRETER) modules/dataset_modules/data_transform_shp.py
	$(PYTHON_INTERPRETER) modules/dataset_modules/data_transform_ageb.py

## Clean intermediate and processed files
.PHONY: clean_data
clean_data:
	@echo ">>> Cleaning up intermediate files..."
	rm -rf data/interim/*
	rm -rf data/processed/*

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 proyecto_ic_mcd
	isort --check --diff --profile black proyecto_ic_mcd
	black --check --config pyproject.toml proyecto_ic_mcd

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml proyecto_ic_mcd


## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	@bash -c "if [ ! -z `which virtualenvwrapper.sh` ]; then source `which virtualenvwrapper.sh`; mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); else mkvirtualenv.bat $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); fi"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
	

## Generate profiling report with ydata-profiling
.PHONY: generate_profiling_report
generate_profiling_report:
	@echo ">>> Generating profiling report with ydata-profiling..."
	$(PYTHON_INTERPRETER) scripts/generate_ydata_profiling_report.py
#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## Full data pipeline (download, transform, visualize)
.PHONY: full_pipeline
full_pipeline: download_data transform_data generate_visualizations

## Deploy documentation pipeline (MkDocs)
.PHONY: deploy
deploy: generate_visualizations deploy_docs


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)

