from flask import g, current_app
from flask_restplus import Namespace, Resource
from apis.helpers import extract_listing_hashes, extract_listing_hashes_to_block, listing_hash_join
from apis.serializers import Listing, Listings
from apis.parsers import from_to_owner, parse_from_to_owner
from .parsers import parse_candidates_by_kind
from .serializers import Candidates
from .helpers import filter_candidate_added, filter_candidate_removed
from core.dynamo import get_listings

api = Namespace('Candidates', description='Operations pertaining to the Computable Protocol Candidate Object')

api.models['Candidates'] = Candidates
api.models['Listing'] = Listing
api.models['Listings'] = Listings

@api.route('/', methods=['GET'])
class CandidatesRoute(Resource):
    @api.expect(from_to_owner)
    @api.marshal_with(Candidates)
    # TODO errors...
    def get(self):
        """
        Fetch and return all candidates, optionally filtered by given block number(s).
        """
        args = parse_from_to_owner(from_to_owner.parse_args())
        current_app.logger.info(f'Fetching candidates from block {args["from_block"]} to block {args["to_block"]}')

        # use this list to filter by so that we only return live candidates. ...removed has no filters
        removed = filter_candidate_removed(args['from_block'], args['to_block'])
        removed_hashes = extract_listing_hashes(removed) # not using the to_block on removed

        added  = filter_candidate_added(args['from_block'], args['to_block'], args['filters'])
        added_hashes, tb = extract_listing_hashes_to_block(added, removed_hashes)

        # /candidates simply returns the filtered list. NOTE we return the to_block from the added event
        return dict(items=added_hashes, from_block=args['from_block'], to_block=tb), 200

@api.route('/application', methods=['GET'])
class ListingCandidatesRoute(Resource):
    @api.expect(from_to_owner)
    @api.doc(params={'type': 'One of the Voting Contract Candidate kinds, excluding application [challenge, reparam, registration]'})
    @api.marshal_with(Listings)
    # TODO errors
    def get(self):
        """
        Fetch and return all listing candidates, optionally filtered from a given block number.
        """
        # TODO implement paging?
        args = parse_candidates_by_kind(from_to_owner.parse_args(), 'application')

        # TODO handle blockchain reverts
        current_app.logger.info(f'Fetching applications from block {args["from_block"]} to block {args["to_block"]}')

        # listing_hash_join can take a list to filter by (exclusionary). ...removed has no filters
        removed = filter_candidate_removed(args['from_block'], args['to_block'])
        removed_hashes = extract_listing_hashes(removed)

        added = filter_candidate_added(args['from_block'], args['to_block'], args['filters'])
        all_the_dynamo = get_listings()
        current_app.logger.debug('retrieved candidates from db')
        # now reduce everything to the actual result (use removed to filter)
        it, tb = listing_hash_join(added, all_the_dynamo, removed_hashes)

        return dict(items=it, from_block=args['from_block'], to_block=tb), 200

# NOTE: type and kind used interchangeably as reserved keywords are dumb...
@api.route('/<string:type>', methods=['GET'])
class CandidatesByKindRoute(Resource):
    @api.expect(from_to_owner)
    @api.doc(params={'type': 'One of the Voting Contract Candidate kinds, excluding application [challenge, reparam, registration]'})
    @api.marshal_with(Candidates)
    # TODO errors
    def get(self, type):
        """
        Fetch and return all candidates of the given kind, optionally filtered from a given block number.
        """

        # TODO implement paging?
        args = parse_candidates_by_kind(from_to_owner.parse_args(), type)
        # TODO handle blockchain reverts
        current_app.logger.info(f'Fetching candidates of type {type} from block {args["from_block"]} to block {args["to_block"]}')

        removed = filter_candidate_removed(args['from_block'], args['to_block'])
        removed_hashes = extract_listing_hashes(removed) # not using the to_block on removed

        added  = filter_candidate_added(args['from_block'], args['to_block'], args['filters'])
        added_hashes, tb = extract_listing_hashes_to_block(added, removed_hashes)

        return dict(items=added_hashes, from_block=args['from_block'], to_block=tb), 200
