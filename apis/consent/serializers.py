from flask_restplus import Model, fields

Consent = Model('Consent', {
    'timestamp': fields.Integer(required=True, description='When the consent was agreed upon'),
    'from_us': fields.Boolean(required=True, description='Self identification as a "US Person"'),
    'version': fields.Integer(required=True, description='Version of this consent agreement'),
    })

NewConsent = Model('NewConsent', {
    'message': fields.String(required=True, description='Message returned from the endpoint'),
    'consenter': fields.String(required=True, description='Public key derived from the JWT'),
    })
