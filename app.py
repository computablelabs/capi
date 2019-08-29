from flask import Flask
from apis import api
from core.protocol import set_w3

# create and config the app
app = Flask(__name__, instance_relative_config=True)
# default first
app.config.from_object('config.default')
# instance dir...
app.config.from_pyfile('config.py')
# whatever the makefile says...
app.config.from_envvar('ENV_CONFIG_FILE')

# init the api and its namespaces
api.init_app(app)

# setup any global before-request type calls
# NOTE if restplus gets these per-namespace -> move them. currently not avail...
@app.before_request
def set_w3_before_request():
    set_w3()
