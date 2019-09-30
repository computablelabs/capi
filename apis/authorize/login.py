from datetime import timedelta
from flask import request, g, current_app
from flask_restplus import Namespace, Resource
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from core import constants as C
from .serializers import JWTToken
from .parsers import auth_parser, refresh_parser

api = Namespace('Authorize', description='Authorization and authentication')

api.models['JWTToken'] = JWTToken

@api.route('/', methods=['GET','POST'])
class Login(Resource):
    @api.expect(refresh_parser)
    @api.response(200, C.LOGIN_SUCCESS)
    @api.response(401, C.LOGIN_FAILED)
    @api.marshal_with(JWTToken)
    def get(self):
        """
        Return a new token when a refresh token is presented for renewal
        """
        args = refresh_parser.parse_args()
        expires = timedelta(days=current_app.config['EXPIRES_IN_DAYS'])
        if args['refresh']:
            # client is attempting to get a new token using the refresh token
            client = get_jwt_identity()
            access_token = create_access_token(identity=client, expires_delta=expires)
            refresh_token = create_refresh_token(identity=client)
            return dict(message=C.LOGIN_SUCCESS, access_token=access_token, refresh_token=refresh_token), 200

    @api.expect(auth_parser)
    @api.response(200, C.LOGIN_SUCCESS)
    @api.response(401, C.LOGIN_FAILED)
    @api.marshal_with(JWTToken)
    def post(self):
        """
        Return a jwt when supplied with a public key and verifiable signed message
        """
        args = auth_parser.parse_args()
        expires = timedelta(days=current_app.config['EXPIRES_IN_DAYS'])
        if args['public_key'] is not None and args['message'] is not None:
            access_token = create_access_token(identity=args['public_key'], expires_delta=expires)
            refresh_token = create_refresh_token(identity=args['public_key'])
            # TODO: call is_authorized from api/helpers
            return dict(message=C.LOGIN_SUCCESS, access_token=access_token, refresh_token=refresh_token), 200
        else:
            current_app.logger.warning(C.MISSING_PAYLOAD_DATA)
            api.abort(400, C.MISSING_PAYLOAD_DATA)
