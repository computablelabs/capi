from flask_restplus import reqparse

req_parser = reqparse.RequestParser()
req_parser.add_argument('from-block', type=int, location='args', help='Block number to begin scanning from')
req_parser.add_argument('owner', location='args', help='Ethereum account which owns this listing')

# res_parser TODO

def parse_listings(args):
    """
    return a dict of the input items required by the '/' route
    """
    b = args['from-block'] if args['from-block'] != None else 0
    f = {'owner': args['owner']} if args['owner'] != None else None

    return dict(from_block=b, filters=f)
