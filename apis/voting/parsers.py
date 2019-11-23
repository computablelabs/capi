from apis.parsers import parse_from_to_owner
import core.constants as C

def parse_candidates_by_kind(args, type):
    d = parse_from_to_owner(args)
    i = C.candidate_kinds[type]

    if d['filters'] != None:
        d['filters']['kind'] = i
    else:
        d['filters'] = {'kind': i}

    return d
