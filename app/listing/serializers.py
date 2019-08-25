from flask_restplus import fields
from app.listing import api

listing = api.model('Listing', {})

list_of_listings = api.inherit('List of listings', {
    'items': fields.List(fields.Nested(listing))
    })
