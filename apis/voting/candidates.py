from flask import g, current_app
from flask_restplus import Namespace, Resource
from apis.helpers import extract_listing_hashes, listing_hash_join
from apis.serializers import Listing, Listings
from apis.parsers import from_block_owner, parse_from_block_owner
from .parsers import parse_candidates_by_kind
from .serializers import Candidates
from .helpers import filter_candidate_added
from core.dynamo import get_listings

api = Namespace('Candidates', description='Operations pertaining to the Computable Protocol Candidate Object')

api.models['Candidates'] = Candidates
api.models['Listing'] = Listing
api.models['Listings'] = Listings

@api.route('/', methods=['GET'])
class CandidatesRoute(Resource):
    @api.expect(from_block_owner)
    @api.marshal_with(Candidates)
    # TODO errors...
    def get(self):
        """
        Fetch and return all candidates, optionally filtered from a given block number.
        """
        # TODO implement paging?
        args = parse_from_block_owner(from_block_owner.parse_args())
        # TODO handle blockchain reverts
        events = filter_candidate_added(args['from_block'], args['filters'])
        # /candidates simply returns the hashes as a list
        it, tb = extract_listing_hashes(events)

        return dict(items=it, from_block=args['from_block'], to_block=tb), 200

@api.route('/application', methods=['GET'])
class ListingCandidatesRoute(Resource):
    @api.expect(from_block_owner)
    @api.doc(params={'type': 'One of the Voting Contract Candidate kinds, excluding application [challenge, reparam, registration]'})
    @api.marshal_with(Listings)
    # TODO errors
    def get(self):
        """
        Fetch and return all listing candidates, optionally filtered from a given block number.
        """
        # TODO implement paging?
        args = parse_candidates_by_kind(from_block_owner.parse_args(), 'application')
        # TODO handle blockchain reverts
        events = filter_candidate_added(args['from_block'], args['filters'])
        everything = get_listings()
        current_app.logger.debug('retrieved candidates from db')
        # now filter everything by the actual hashes...
        it, tb = listing_hash_join(events, everything)

        current_app.logger.info(f'Returning candidates from block {args["from_block"]} to {tb}')
        return dict(items=it, from_block=args['from_block'], to_block=tb), 200

# NOTE: type and kind used interchangeably as reserved keywords are dumb...
@api.route('/<string:type>', methods=['GET'])
class CandidatesByKindRoute(Resource):
    @api.expect(from_block_owner)
    @api.doc(params={'type': 'One of the Voting Contract Candidate kinds, excluding application [challenge, reparam, registration]'})
    @api.marshal_with(Candidates)
    # TODO errors
    def get(self, type):
        """
        Fetch and return all candidates of the given kind, optionally filtered from a given block number.
        """
        # TODO implement paging?
        args = parse_candidates_by_kind(from_block_owner.parse_args(), type)
        # TODO handle blockchain reverts
        events = filter_candidate_added(args['from_block'], args['filters'])
        everything = get_listings()
        current_app.logger.debug('retrieved candidates from db')
        # simply returns the hashes as a list
        it, tb = extract_listing_hashes(events)

        current_app.logger.info(f'Returning candidates of type {type} from block {args["from_block"]} to {tb}')

        return dict(items=it, from_block=args['from_block'], to_block=tb), 200
