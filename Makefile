export
PYTHONPATH := .

test:
	ENV_CONFIG_FILE=/home/rob/github/capi/config/testing.py python -m pytest

development:
	ENV_CONFIG_FILE=config/development.py python run.py
