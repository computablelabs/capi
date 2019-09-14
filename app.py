from flask import Flask
from apis import api
from celery import Celery
from core.protocol import set_w3
from core.dynamo import set_dynamo_table
from core.s3 import set_s3_client
from core.cli import admin
from core.celery import make_celery
from flask_cors import CORS
from logging.config import fileConfig

# create and config the app
app = Flask(__name__, instance_relative_config=True)
# default first
app.config.from_object('config.default')
# whatever the makefile says...
app.config.from_envvar('ENV_CONFIG_FILE')

# setup logging
fileConfig('logging.config')
app.logger.setLevel(app.config['LOG_LEVEL'])

# init the api and its namespaces
api.init_app(app)

# register the CLI admin blueprint
app.register_blueprint(admin)

# create celery
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)

# Allow CORS
CORS(app, origins='*')

# setup any global before-request type calls
# NOTE if restplus gets these per-namespace -> move them. currently not avail...
@app.before_request
def set_w3_dynamo_table_s3_and_celery():
    set_w3()
    set_dynamo_table()
    set_s3_client()
