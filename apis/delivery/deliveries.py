from flask import request, g, current_app
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, decode_token
from core import constants as C

api = Namespace('Delivery', description='Delivery endpoint for requesting purchased payloads')

@api.route('/', methods=['GET','POST'])
class Delivery(Resource):
    @jwt_required
    def get(self):
        """
        Stub to verify required JWT tokens
        """
        return dict(message="Huzzah!"), 200