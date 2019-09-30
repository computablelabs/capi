from flask_restplus import Model, fields

JWTToken = Model('JWTToken', {
    'message': fields.String(required=True, description='Server response for a new Listing when POSTed'),
    'access_token': fields.String(required=True, description='JWT token representing an authenticated client'),
    'refresh_token': fields.String(required=True, description='Refresh token used to retrieve new token after expiration')
})