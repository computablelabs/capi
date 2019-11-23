from core.protocol import get_listing

def filter_listed(from_block, to_block, arg_filters=None):
    """
    given filter args and the current request g context create a listing contract
    and execute the filter for listed event, returning the results
    """
    listing = get_listing()
    if arg_filters != None:
        filter = listing.deployed.events.Listed.createFilter(fromBlock=from_block, toBlock=to_block, argument_filters=arg_filters)
    else:
        filter = listing.deployed.events.Listed.createFilter(fromBlock=from_block, toBlock=to_block)

    return filter.get_all_entries()

def filter_listing_removed(from_block, to_block):
    """
    given filter args and the current request g context create a listing contract
    and execute the filter for listed event, returning the results
    """
    listing = get_listing()
    filter = listing.deployed.events.ListingRemoved.createFilter(fromBlock=from_block, toBlock=to_block)

    return filter.get_all_entries()
