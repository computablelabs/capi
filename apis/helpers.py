from flask import g
from core.helpers import metrics_collector

"""
Some helpers are useful to more than one namespace.
"""
@metrics_collector
def extract_listing_hashes(logs):
    """
    Return only the listing hashes present in a given collection of logs
    """
    return list(map(lambda log: g.w3.toHex(log['args']['hash']), logs))

@metrics_collector
def extract_listing_hashes_to_block(logs, filter_by=None):
    """
    Return both a list of hashes present in the given logs as well as the highest block number seen
    If filter_by (list) is present, exclude results found in it
    """
    to_block = 0
    hashes = []

    # TODO there may be a better itertools way to do this, but there may not...
    for log in logs:
        target = g.w3.toHex(log['args']['hash']) # byte array not json serializable, convert it
        if filter_by != None:
            if target not in filter_by:
                hashes.append(target)
        else:
            hashes.append(target)

        to_block = max(to_block, log['blockNumber'])

    return hashes, to_block

@metrics_collector
def listing_hash_join(logs, candidates, filter_by=None):
    """
    given a list of evm logs and an array of dynamo 'listings' (or any object with a 'listing_hash' attribute)
    return the 'listings' whose hash appears in the logs, and the highetst block number encountered
    Optionally further filter the result by passing filter_by (list)
    """
    hashes, to_block = extract_listing_hashes_to_block(logs, filter_by)
    actual = list(filter(lambda candidate: candidate['listing_hash'] in hashes, candidates))

    return actual, to_block
