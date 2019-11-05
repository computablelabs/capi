from flask_restplus import reqparse
from core.helpers import metrics_collector

from_block_owner = reqparse.RequestParser()
from_block_owner.add_argument('from-block', type=int, location='args', help='Block number to begin scanning from')
from_block_owner.add_argument('owner', location='args', help='Ethereum account which owns this candidate')

@metrics_collector
def parse_from_block_owner(args):
    """
    return a dict of the from-block and owner args if present,
    setting defaults if not
    """
    b = args['from-block'] if args['from-block'] != None else 0
    f = {'owner': args['owner']} if args['owner'] != None else None

    return dict(from_block=b, filters=f)
