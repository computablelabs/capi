from flask import Flask
from app.listing import listing
from app.voting import voting
from protocol import set_w3

# config
app = Flask(__name__, instance_relative_config=True)
# default first
app.config.from_object('config.default')
# instance dir...
app.config.from_pyfile('config.py')
# whatever the makefile says...
app.config.from_envvar('ENV_CONFIG_FILE')

# blueprints
app.register_blueprint(listing, url_prefix='/listings')
app.register_blueprint(voting, url_prefix='/candidates')

# getters and setters alike must have a global w3 instance available
@app.before_request
def set_w3_before_request():
    set_w3()
