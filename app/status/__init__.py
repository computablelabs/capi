"""
Blueprint for health and status type API endpoints.
NOTE: Using the url_prefix '/status'
"""
from flask import Blueprint, g
from flask_restplus import Api, Resource
import app.constants as C

status = Blueprint('status', __name__)
api = Api(status, default='status', doc='/documentation',
    title=C.TITLE, version=C.VERSION, description='API abstractions for status and health checks')

