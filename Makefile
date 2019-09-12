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
ifdef gas_price
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/development.py FLASK_APP=run.py flask admin register --gas_price=$(gas_price)
else
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/development.py FLASK_APP=run.py flask admin register
endif

resolve_development:
ifdef gas_price
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/development.py FLASK_APP=run.py flask admin resolve --hash=$(hash) --gas_price=$(gas_price)
else
	ENV_CONFIG_FILE=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))config/development.py FLASK_APP=run.py flask admin resolve --hash=$(hash)
endif
