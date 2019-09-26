from flask_restplus import Model, fields

JWTToken = Model('JWTToken', {
    'message': fields.String(required=True, description='Server response for a new Listing when POSTed'),
    'jwt': fields.String(required=True, description='JWT token representing an authenticated client')
})