from flask_restplus import Model, fields
from apis.serializers import Listing

Candidate = Model('Candidate', {
    'kind': fields.Integer(required=True, description='Type of this candidate'),
    'owner': fields.String(required=True, description='Proposer of this candidate'),
    'stake': fields.Integer(required=True, description='Amount of CMT Wei staked by the owner of this candidate'),
    'vote_by': fields.Integer(required=True, description='When the poll for this candidate closes'), # leaving as int as not to convert
    'yea': fields.Integer(required=True, description='Votes in support of this candidate'),
    'nay': fields.Integer(required=True, description='Votes opposed to this candidate')
    })

Candidates = Model('Candidates', {
    'items': fields.List(fields.String(required=True, description='Hash identifier of the candidate')),
    'from_block': fields.Integer(required=True, description='Block number where scanning began'),
    'to_block': fields.Integer(required=True, description='Highest block number scanned')
    })

Applicant = Listing.inherit('Candidate', Candidate)
