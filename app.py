from flask import Flask
from apis import api
from core.protocol import set_w3
from core.dynamo import set_dynamo_table
from core.s3 import set_s3_client
from core.cli import admin

# create and config the app
app = Flask(__name__, instance_relative_config=True)
# default first
app.config.from_object('config.default')
# whatever the makefile says...
app.config.from_envvar('ENV_CONFIG_FILE')

# init the api and its namespaces
api.init_app(app)

# register the CLI admin blueprint
app.register_blueprint(admin)

# setup any global before-request type calls
# NOTE if restplus gets these per-namespace -> move them. currently not avail...
@app.before_request
def set_w3_and_dynamo_table_and_s3():
    set_w3()
    set_dynamo_table()
    set_s3_client()
