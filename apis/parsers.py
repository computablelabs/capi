from flask_restplus import reqparse

from_to_owner = reqparse.RequestParser()
from_to_owner.add_argument('from-block', type=int, location='args', help='Block number to begin scanning from')
from_to_owner.add_argument('to-block', type=int, location='args', help='Block number (inclusive) to end scanning at')
from_to_owner.add_argument('owner', location='args', help='Ethereum account which owns this candidate')

def parse_from_to_owner(args):
    """
    return a dict of the from-block and owner args if present,
    setting defaults if not
    """
    fb = args['from-block'] if args['from-block'] != None else 0
    tb = args['to-block'] if args['to-block'] != None else None
    f = {'owner': args['owner']} if args['owner'] != None else None

    return dict(from_block=fb, to_block=tb, filters=f)
