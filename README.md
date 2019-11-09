# CAPI
### Computable Protocol APIs... They all look the same.
[![Build Status](https://travis-ci.org/computablelabs/capi.svg?branch=v3)](https://travis-ci.org/computablelabs/capi)

This repo is the first implementation of the Computable API,
[CAPI](https://computablelabs.github.io/compspec/docs/capi/), the core
set of APIs which govern access to a datatrust in the Computable
protocol. A datatrust is any piece of software which implements CAPI.

This repo hosts an implementation of CAPI in Python. The setup is
fairly straightforward. There's a Flask server which connects to AWS.
The actual data is stored in Dynamo DB. (The choice of storage will be
abstracted further in future versions.) This codebase also
communicates extensively with a deployed set of Computable smart
contracts through `web3.py` and `computable.py`.

## Installation

First set up a virtual environment with Python 3.6. (Python 3.7
and `web3.py` have some issues with each other). See
[here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
for a guide. The cheatsheet version is to run the following commands

```
python -m pip install --user virtualenv
git clone https://github.com/computablelabs/capi.git
cd capi
python3 -m venv env
source env/bin/activate
```

This clones `capi` and creates a virtual environment hosted in the local folder
`capi/env`. Once you have the repo closed and the virtual environment setup,
you only need to run

```
source env/bin/activate
```

each time you start developing. To complete the installation of `capi`, run the
following commands in your activated virtual environment

```
pip install awscli
pip install boto3
pip install -r requirements.txt
```
You'll also need to run one additional command:
```
pip install web3[tester]
```
(The awkward format of this command doesn't mesh well with the
automatic pip installation, so needs to be done manually). You should
now be set up.

## Running the tests

The tests are specified in the `Makefile`. To run tests, simply do
```
make test
```

## Configuration

Three supported environments: skynet, rinkeby, mainnet
Services run as ECS Fargate services on AWS. Provisioning is done by `scripts/provision.py`.  This script takes one argument as a parameter: the CloudFormation Stack Name (`capi-skynet`, `capi-rinkeby`, and `capi-mainnet`). 

Running the script with any one of these names will update the environment using the stack definition in `scripts/cf_stack.yml`. To update a running environment, make the desired changes to the CF template and run the provision script.

Running the provisioning script with any other argument will create a stack with the name supplied by the argument _if_ you add the new stack name to argparse (this is to minimize typos/errors from not doing what you wanted).

The following resources are built by the CF template:
- DNS name: points to the load balancer for this service
- Application Load Balancer: provides load distribution across containers
- Target Group: logical grouping of running containers (target for the load balancer)
- Automatic redirection of HTTP to HTTPS on the load balancer
- SSL cert for HTTPS
- ECS Service: service definition
- Cloudwatch Log Group: collection point for logs from the docker containers

### Config and Security
Config and secure variables are stored in AWS Secrets Manager. The name of the secrets store in Secrets Manager is the same as the stack name (see above). On provisioning, the provision script grabs the values from Secrets Manager and uses them to deploy the stack. 

### IAM Roles
On startup, the docker container will also access Secrets Manager to get environment variables needed for operation. Each stack has its own IAM role configured with only the permissions needed for that environment. I.e. - the skynet stack cannot access resources assigned to rinkeby or mainnet, etc...

Permissions are defined in the IAM roles. IAM roles are named after the stack: `capi_skynet_role`, `capi_rinkeby_role`, `capi_mainnet_role`.

Each role has the following IAM policies attached:
- `capi_{stack}_dynamo`: provides access to the dynamodb table for that environment
- `capi_{stack}_s3`: provides access to the s3 bucket used by that stack
- `capi_{stack}_secrets`: provides access to Secrets Manager for variables used by that stack
- `datatrust-cloudwatch-metrics-write`: permits writing performance metrics to Cloudwatch
- `AmazonECSTaskExecutionRolePolicy`: allows access to ECS resources needed to launch the task

## Deployment
Deployment is handled by Travis-CI
After successfully running tests, Travis will build the docker image and tag it with the branch name (`skynet`, `rinkeby`, or `mainnet`). The resulting docker image is pushed to the CAPI docker repository and a service restart command is issued. The service restart command will force new docker containers to launch, picking up the docker image tagged for their environment.

Rolling restarts are done by default: i.e. the currently running container remains up and serving requests until the new container passes the health check. The current container is then idled out to complete any in-flight requests and new traffic is sent to the new container. After the idle timeout, the original container is terminated. In the event the new container never passes the health check, the original container will remain online serving requests indefinitely.