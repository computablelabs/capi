export
PYTHONPATH := .

test:
	ENV_CONFIG_FILE=/home/rob/github/capi/config/testing.py python -m pytest -s

development:
	ENV_CONFIG_FILE=/home/rob/github/capi/config/development.py python run.py
