"""
Blueprint for the API endpoints pertaining to the Listing contract
NOTE: We will register the blueprint with the url_prefix '/listings'
"""
from flask import Blueprint, g
from flask_restplus import Api, Resource, reqparse
import app.constants as C
from .helpers import filter_listed
from .parsers import req_parser, parse_listings

listing = Blueprint('listing', __name__)
api = Api(listing, default='listings', doc='/documentation',
    title=C.TITLE, version=C.VERSION, description='API abstractions pertaining to the Computable Listing contract')

@api.route('/', methods=['GET'])
@api.expect(req_parser)
class Listings(Resource):
    def get(self):
        """
        Fetch and return all listings posted from [from_block || 0] until latest.
        """
        # TODO implement paging

        args = parse_listings(req_parser.parse_args())

        # protocol stuff... TODO handle blockchain reverts
        events = filter_listed(args['from_block'], args['filters'])
        hashes = []
        to_block = 0

        for event in events:
            # TODO dynamo stuff
            hashes.append(g.w3.toHex(event['args']['hash'])) # byte array not json serializable, convert it
            to_block = max(to_block, event['blockNumber'])

        # TODO marshalling
        return {'items': hashes, 'from_block': args['from_block'], 'to_block': to_block}, 200
