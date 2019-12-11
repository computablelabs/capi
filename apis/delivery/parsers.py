from flask_restplus import reqparse
from core.s3 import get_listing_and_meta

delivery_parser = reqparse.RequestParser(bundle_errors=True)
delivery_parser.add_argument(
    'delivery_hash', type=str, required=True, location='args',
    help='The delivery hash for the request to fulfill'
)
delivery_parser.add_argument(
    'query', type=str, required=True, location='args',
    help='The query to execute for this delivery'
)


# Leaving this as a pass-thru for get_listing_and_meta as `query` is the correct term for deliveries...
def parse_query(query):
    """
    Execute the query for the delivery and return the payload for the client
    using our s3 listing utils
    """
    return get_listing_and_meta(query)
