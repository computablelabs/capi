from flask_restplus import reqparse
import core.constants as C

req_parser = reqparse.RequestParser()
req_parser.add_argument('from-block', type=int, location='args', help='Block number to begin scanning from')
req_parser.add_argument('owner', location='args', help='Ethereum account which owns this candidate')

def parse_candidates(args):
    """
    return a dict of the input items required by the '/' route
    """
    b = args['from-block'] if args['from-block'] != None else 0
    f = {'owner': args['owner']} if args['owner'] != None else None

    return dict(from_block=b, filters=f)

def parse_candidates_by_kind(args, type):
    d = parse_candidates(args)
    i = C.candidate_kinds[type]

    if d['filters'] != None:
        d['filters']['kind'] = i
    else:
        d['filters'] = {'kind': i}

    return d
