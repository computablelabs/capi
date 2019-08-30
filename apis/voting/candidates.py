from flask import g
from flask_restplus import Namespace, Resource
from .parsers import req_parser, parse_candidates, parse_candidates_by_kind
from .helpers import filter_candidate_added
from core.dynamo import get_listings

api = Namespace('Candidates', description='Operations pertaining to the Computable Protocol Candidate Object')

@api.route('/', methods=['GET'])
@api.expect(req_parser)
class CandidatesRoute(Resource):
    def get(self):
        """
        Fetch and return all candidates, optionally filtered from a given block number.
        """
        # TODO implement paging?

        args = parse_candidates(req_parser.parse_args())

        # TODO handle blockchain reverts
        events = filter_candidate_added(args['from_block'], args['filters'])
        hashes = []
        to_block = 0

        for event in events:
            hashes.append(g.w3.toHex(event['args']['hash'])) # byte array not json serializable, convert it
            to_block = max(to_block, event['blockNumber'])

        # to dynamo a candidate and a listing are the same thing...
        everything = get_listings()

        # now filter everything by the actual hashes...

        # TODO marshalling
        return {'hashes': hashes, 'listings': everything, 'from_block': args['from_block'], 'to_block': to_block}, 200

# NOTE: We have to use 'type' interchangeably with 'kind' cuz reserved keyword fail...
@api.route('/<string:type>', methods=['GET'])
@api.expect(req_parser)
@api.doc(params={'type': 'One of the Voting Contract Candidate kinds [application, challenge, reparam, registration]'})
class CandidatesByKindRoute(Resource):
    def get(self, type):
        """
        Fetch and return all candidates of the given kind, optionally filtered from a given block number.
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
