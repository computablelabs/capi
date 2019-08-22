"""
Blueprint for the API endpoints pertaining to the Voting contract
NOTE: Registered with the url_prefix '/candidates'
"""
from flask import Blueprint
from flask import g
from flask_restplus import Api, Resource, reqparse
import app.constants as C
from .helpers import filter_candidate_added

voting = Blueprint('voting', __name__)

api = Api(voting, default='voting', doc='/documentation',
        title=C.TITLE, version=C.VERSION, description='API abstractions pertaining to the Computable Voting contract')

# argument parsers for this blueprint
reqparser = reqparse.RequestParser()
reqparser.add_argument('from-block', location='args', help='Block number to begin scanning from')



@api.route('/', methods=['GET'])
@api.expect(reqparser)
class Candidates(Resource):
    def get(self):
        """
        Fetch and return all candidates posted from [from_block || 0] until latest.
        """
        # TODO implement paging?

        items = []
        args = reqparser.parse_args()
        from_block = int(args['from-block']) if args['from-block'] != None else 0
        to_block = 0

        # protocol stuff... TODO handle blockchain reverts
        events = filter_candidate_added(g, from_block)
        for event in events:
            # TODO dynamo stuff
            items.append(g.w3.toHex(event['args']['hash'])) # byte array not json serializable, convert it
            to_block = max(to_block, event['blockNumber'])

        return {'items': items, 'from_block': from_block, 'to_block': to_block}, 200

# NOTE: We have to use 'type' interchangeably with 'kind' cuz reserved keyword fail...
@api.route('/<string:type>', methods=['GET'])
@api.expect(reqparser)
@api.doc(params={'type': 'One of the Voting Contract Candidate kinds [application, challenge, reparam, registration]'})
class CandidatesByKind(Resource):
    def get(self, type):
        """
        Fetch and return all candidates posted from [from_block || 0] until latest of a given kind.
        """
        # TODO implement paging?

        items = []
        args = reqparser.parse_args()
        from_block = int(args['from-block']) if args['from-block'] != None else 0
        to_block = 0

        # TODO protocol stuff...
        int_kind = C.candidate_kinds[type]
        events = filter_candidate_added(g, from_block, {'kind': int_kind})
        for event in events:
            # TODO dynamo stuff
            items.append(g.w3.toHex(event['args']['hash'])) # byte array not json serializable, convert it
            to_block = max(to_block, event['blockNumber'])

        return {'items': items, 'from_block': from_block, 'to_block': to_block, 'kind': int_kind}, 200
