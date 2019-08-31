from flask import g
from flask_restplus import Namespace, Resource
from apis.helpers import listing_hash_join
from apis.serializers import Listing, Listings
from .parsers import req_parser, parse_candidates, parse_candidates_by_kind
from .helpers import filter_candidate_added
from core.dynamo import get_listings

api = Namespace('Candidates', description='Operations pertaining to the Computable Protocol Candidate Object')

api.models['Listing'] = Listing
api.models['Listings'] = Listings

@api.route('/', methods=['GET'])
class CandidatesRoute(Resource):
    @api.expect(req_parser)
    @api.marshal_with(Listings)
    def get(self):
        """
        Fetch and return all candidates, optionally filtered from a given block number.
        """
        # TODO implement paging?
        args = parse_candidates(req_parser.parse_args())
        # TODO handle blockchain reverts
        events = filter_candidate_added(args['from_block'], args['filters'])
        # to dynamo a candidate and a listing are the same thing... TODO wut?
        everything = get_listings()
        # now filter everything by the actual hashes...
        it, tb = listing_hash_join(events, everything)

        return dict(items=it, from_block=args['from_block'], to_block=tb), 200

# NOTE: We have to use 'type' interchangeably with 'kind' cuz reserved keyword fail...
@api.route('/<string:type>', methods=['GET'])
class CandidatesByKindRoute(Resource):
    @api.expect(req_parser)
    @api.doc(params={'type': 'One of the Voting Contract Candidate kinds [application, challenge, reparam, registration]'})
    @api.marshal_with(Listings)
    def get(self, type):
        """
        Fetch and return all candidates of the given kind, optionally filtered from a given block number.
        """
        # TODO implement paging?
        args = parse_candidates_by_kind(req_parser.parse_args(), type)
        # TODO handle blockchain reverts
        events = filter_candidate_added(args['from_block'], args['filters'])
        everything = get_listings()
        # now filter everything by the actual hashes...
        it, tb = listing_hash_join(events, everything)

        return dict(items=it, from_block=args['from_block'], to_block=tb), 200
