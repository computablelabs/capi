from flask import Flask
from flask_cors import CORS
from apis import api
from core.cli import admin
from core.protocol import set_w3
from core.dynamo import set_dynamo_table
from core.s3 import set_s3_client
from core.celery import set_celery
from logging.config import fileConfig

# create and config the app
app = Flask(__name__, instance_relative_config=True)
# default first
app.config.from_object('config.default')
# whatever the makefile says...
app.config.from_envvar('ENV_CONFIG_FILE')

# setup logging
fileConfig('config/logging.config')
app.logger.setLevel(app.config['LOG_LEVEL'])

# init the api and its namespaces
api.init_app(app)

# register the CLI admin blueprint
app.register_blueprint(admin)

# Allow CORS
CORS(app, origins='*')

# setup any global before-request type calls
# NOTE if restplus gets these per-namespace -> move them. currently not avail...
@app.before_request
def set_all_the_things():
    """
    by setting these outside of the actual endpoint logic we can easily
    manipulate them in testing environments
    """
    set_w3()
    set_dynamo_table()
    set_s3_client()
    set_celery()
