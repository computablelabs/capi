"""
Some serializer models will be useful to multiple namespaces
"""
from flask_restplus import Model, fields

Listing = Model('Listing', {
    'description': fields.String(required=True, description='Description of listing item'),
    'title': fields.String(required=True, description='Title of the listing'),
    'license': fields.String(required=True, description='Usage license'),
    'listing_hash': fields.String(required=True, description='The listing this upload belongs to'),
    'file_type': fields.String(required=True, description='File content: video, image, audio, etc'),
    'tags': fields.List(fields.String, required=False, description='Tags to categorize and describe the listing file')
    })

Listings = Model('Listings', {
    'items': fields.List(fields.Nested(Listing)),
    'from_block': fields.Integer(required=True, description='Block number where scanning began'),
    'to_block': fields.Integer(required=True, description='Highest block number scanned')
    })
