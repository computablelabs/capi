from flask_restplus import reqparse

delivery_parser = reqparse.RequestParser(bundle_errors=True)
delivery_parser.add_argument('listing_hash', type=str, required=True, location='args', help='The listing hash requested for this delivery')
