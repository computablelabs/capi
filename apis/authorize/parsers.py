from flask_restplus import reqparse

auth_parser = reqparse.RequestParser(bundle_errors=True)
auth_parser.add_argument('public_key', type=str, required=True, location='json', help='Public key from the authorizing client')
auth_parser.add_argument('message', type=str, required=True, location='json', help='Signed message from the client')
