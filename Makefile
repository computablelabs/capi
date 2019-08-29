export
PYTHONPATH := .

test:
	ENV_CONFIG_FILE=/home/rob/github/capi/config/testing.py AWS_ACCESS_KEY_ID=testing AWS_SECRET_ACCESS_KEY_ID=testing AWS_SECURITY_TOKEN=testing AWS_SESSION_TOKEN=testing python -m pytest -s

development:
	ENV_CONFIG_FILE=/home/rob/github/capi/config/development.py python run.py
