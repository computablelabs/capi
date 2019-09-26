from datetime import timedelta
from flask import request, g, current_app
from flask_restplus import Namespace, Resource
from flask_jwt_extended import create_access_token
from core import constants as C
from .serializers import JWTToken
from .parsers import auth_parser

api = Namespace('Authorize', description='Authorization and authentication')

api.models['JWTToken'] = JWTToken

@api.route('/', methods=['POST'])
class Login(Resource):
    @api.expect(auth_parser)
    @api.response(200, C.LOGIN_SUCCESS)
    @api.response(401, C.LOGIN_FAILED)
    @api.marshal_with(JWTToken)
    def post(self):
        """
        Return a jwt when supplied with a public key and verifiable signed message
        """
        payload = request.get_json()
        if payload is not None:
            expires = timedelta(days=current_app.config['EXPIRES_IN_DAYS'])
            token = create_access_token(identity=payload['public_key'], expires_delta=expires)
            # TODO: call is_authorized from api/helpers
            return dict(message= C.LOGIN_SUCCESS, jwt=token), 200
        else:
            current_app.logger.warning(C.MISSING_PAYLOAD_DATA)
            api.abort(400, C.MISSING_PAYLOAD_DATA)
