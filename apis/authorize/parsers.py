from flask_restplus import reqparse

auth_parser = reqparse.RequestParser(bundle_errors=True)
auth_parser.add_argument('message', type=str, required=True, location='json', help='The message presented to the client to sign (text or hashed)')
auth_parser.add_argument('signature', type=str, required=True, location='json', help='The result of signing the message')
auth_parser.add_argument('public_key', type=str, required=True, location='json', help='Public key from the authorizing client')

refresh_parser = reqparse.RequestParser(bundle_errors=True)
refresh_parser.add_argument('refresh', type=bool, required=False, location='args', help='Use the refresh token to create a new JWT')
