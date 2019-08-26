"""
Blueprint for the API endpoints pertaining to the Voting contract
NOTE: Registered with the url_prefix '/candidates'
"""
from flask import Blueprint, g
from flask_restplus import Api, Resource, reqparse
import app.constants as C
from .helpers import filter_candidate_added
from .parsers import req_parser, parse_candidates, parse_candidates_by_kind

voting = Blueprint('voting', __name__)

api = Api(voting, default='candidates', doc='/documentation',
    title=C.TITLE, version=C.VERSION, description='API abstractions pertaining to the Computable Voting contract')

@api.route('/', methods=['GET'])
@api.expect(req_parser)
class Candidates(Resource):
    def get(self):
        """
        Fetch and return all candidates posted from [from_block || 0] until latest.
        """
        # TODO implement paging?

        args = parse_candidates(req_parser.parse_args())

        # protocol stuff... TODO handle blockchain reverts
        events = filter_candidate_added(args['from_block'], args['filters'])
        hashes = []
        to_block = 0

        for event in events:
            # TODO dynamo stuff
            hashes.append(g.w3.toHex(event['args']['hash'])) # byte array not json serializable, convert it
            to_block = max(to_block, event['blockNumber'])

        # TODO marshalling
        return {'items': hashes, 'from_block': args['from_block'], 'to_block': to_block}, 200

# NOTE: We have to use 'type' interchangeably with 'kind' cuz reserved keyword fail...
@api.route('/<string:type>', methods=['GET'])
@api.expect(req_parser)
@api.doc(params={'type': 'One of the Voting Contract Candidate kinds [application, challenge, reparam, registration]'})
class CandidatesByKind(Resource):
    def get(self, type):
        """
        Fetch and return all candidates posted from [from_block || 0] until latest of a given kind.
        """
        # TODO implement paging?

        args = parse_candidates_by_kind(req_parser.parse_args(), type)

        # TODO handle blockchain reverts
        events = filter_candidate_added(args['from_block'], args['filters'])
        hashes = []
        to_block = 0

        for event in events:
            # TODO dynamo stuff
            hashes.append(g.w3.toHex(event['args']['hash'])) # byte array not json serializable, convert it
            to_block = max(to_block, event['blockNumber'])

        # TODO marshalling
        return {'items': hashes, 'from_block': args['from_block'], 'to_block': to_block, 'kind': args['filters']['kind']}, 200
