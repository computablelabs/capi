from flask_restplus import Model, fields

NewListing = Model('NewListing', {
    'message': fields.String(required=True, description='Server response for a new Listing when POSTed')
    })
