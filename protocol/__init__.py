from flask import g

def set_w3(ctx, w3):
    """
    An instance of Web3. NOTE: it is expected that .eth.defaultAccount is set with the datatrust's public key
    """
    with ctx:
        g.w3 = w3

def set_contract_addresses(ctx, addresses):
    """
    given the current_app and a dict of addresses update the config
    """
    with ctx:
        g.ether_token_address = addresses['ether_token_address']
        g.voting_address = addresses['voting_address']
        g.datatrust_address = addresses['datatrust_address']
        g.listing_address = addresses['listing_address']
