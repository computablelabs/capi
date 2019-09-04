export
PYTHONPATH := .

test:
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/testing.py python -m pytest -s

development:
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/development.py python run.py
