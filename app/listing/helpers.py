from flask import g, current_app
from computable.contracts import Listing

def filter_listed(from_block, arg_filters=None):
    """
    given filter args and the current request g context create a listing contract
    and execute the filter for listed event, returning the results
    """

    listing = Listing(g.w3.eth.defaultAccount)
    listing.at(g.w3, current_app.config['LISTING_CONTRACT_ADDRESS'])
    if arg_filters != None:
        filter = listing.deployed.events.Listed.createFilter(fromBlock=from_block, argument_filters=arg_filters)
    else:
        filter = listing.deployed.events.Listed.createFilter(fromBlock=from_block)

    return filter.get_all_entries()
