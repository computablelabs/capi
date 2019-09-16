from flask_restplus import Model, fields

Candidates = Model('Candidates', {
    'items': fields.List(fields.String(required=True, description='Hash identifier of the candidate')),
    'from_block': fields.Integer(required=True, description='Block number where scanning began'),
    'to_block': fields.Integer(required=True, description='Highest block number scanned')
    })
