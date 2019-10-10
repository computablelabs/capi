from flask_restplus import reqparse

delivery_parser = reqparse.RequestParser(bundle_errors=True)
delivery_parser.add_argument('delivery_hash', type=str, required=True, location='args', help='The delivery hash for the request to fulfill')
delivery_parser.add_argument('listing_hash', type=str, required=True, location='args', help='The listing hash requested for this delivery')
