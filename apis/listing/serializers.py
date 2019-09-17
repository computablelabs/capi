from flask_restplus import Model, fields

NewListing = Model('NewListing', {
    'message': fields.String(required=True, description='Server response for a new Listing when POSTed'),
    'task_id': fields.String(required=True, description='UUID for the asynchronous mining task')
    })
