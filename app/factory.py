import os
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix # cuz https is hard i guess
from apis import api
from core.cli import admin
from core.protocol import set_w3
from core.dynamo import set_dynamo_table
from core.s3 import set_s3_client
from core.celery import initialize
from logging.config import fileConfig
from flask_jwt_extended import JWTManager

# this little dance is so that we can align flask and celery on name
a_name = os.path.dirname(os.path.realpath(__file__)).split('/')[-1]
# make the name overrideable just in case
def create_app(app_name=a_name, **kwargs):
    # create and config the app
    app = Flask(app_name, instance_relative_config=True)
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
    # initialize the celery with this app if present
    if kwargs.get('celery'):
        initialize(kwargs.get('celery'), app)
    # allow swagger to actually work when deployed
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    # Setup the Flask-JWT-Extended extension
    JWTManager(app)

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

    return app
