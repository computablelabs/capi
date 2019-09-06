export
PYTHONPATH := .

test:
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/testing.py python -m pytest -s

development:
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/development.py python run.py

local_docker:
	docker build -t capi:local . -f Dockerfile_local.dockerfile \
		--build-arg accesskey=$(shell aws configure get aws_access_key_id) \
		--build-arg secretkey=$(shell aws configure get aws_secret_access_key)

register_development:
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/development.py FLASK_APP=run.py flask admin register
