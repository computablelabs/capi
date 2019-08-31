from flask import g
"""
Some helpers are useful to more than one namespace.
"""
def listing_hash_join(logs, candidates):
    """
    given a list of evm logs and an array of dynamo 'listings' (or any object with a 'listing_hash' attribute)
    return the 'listings' whose hash appears in the logs, and the highetst block number encountered
    """
    to_block = 0
    hashes = []

    # we need to create a proper list for takewhile to work with (and we need the block)
    # TODO there may be a better itertools way to do this, but there may not...
    for log in logs:
        hashes.append(g.w3.toHex(log['args']['hash'])) # byte array not json serializable, convert it
        to_block = max(to_block, log['blockNumber'])

    actual = list(filter(lambda candidate: candidate['listing_hash'] in hashes, candidates))

    return actual, to_block
