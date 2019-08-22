"""
Blueprint for the API endpoints pertaining to the Listing contract
NOTE: We will register the blueprint with the url_prefix '/listings'
"""
from flask import Blueprint
from flask_restplus import Api, Resource, reqparse
import app.constants as C

listing = Blueprint('listing', __name__)
api = Api(listing, default='listings', doc='/documentation',
        title=C.TITLE, version=C.VERSION, description='API abstractions pertaining to the Computable Listing contract')

# argument parsers for this blueprint
reqparser = reqparse.RequestParser()
reqparser.add_argument('from-block', location='args', help='Block number to begin scanning from')

@api.route('/', methods=['GET'])
@api.expect(reqparser)
class Listings(Resource):
    def get(self):
        """
        Fetch and return all listings posted from [from_block || 0] until latest.
        """
        # TODO implement paging

        # TODO can likely abstract out this from_block bit as will be omnipresent
        args = reqparser.parse_args()
        from_block = 0
        if args['from-block'] != None:
            from_block = args['from-block']

        # TODO protocol stuff...
        to_block = 0

        # TODO database stuff

        return {'items': [], 'from_block': from_block, 'to_block': to_block}, 200
