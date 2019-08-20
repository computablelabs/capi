from flask import Flask

app = Flask(__name__, instance_relative_config=True)
# default first
app.config.from_object('config.default')
# instance dir...
app.config.from_pyfile('config.py')
# whatever the makefile says...
app.config.from_envvar('ENV_CONFIG_FILE')
