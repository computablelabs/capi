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
