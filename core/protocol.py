"""
Methods that deal with the Computable Protocol aspects of operating a Datatrust API,
Ideally, these functions are "pan-blueprint" as blueprint specific functionality can be
placed in its own helper file.
TODO: implement celery for blockchain methods?
"""
from flask import current_app, g
from web3 import Web3
from web3.middleware import geth_poa_middleware
from computable.contracts import MarketToken, Voting, Parameterizer, Datatrust, Listing
from computable.helpers.transaction import call
from .helpers import metrics_collector


@metrics_collector
def set_w3(w3=None):
    """
    NOTE: test env will pass a web3 instance here
    An instance of Web3. NOTE: it is expected that .eth.defaultAccount is set with the datatrust's public key
    """
    if 'w3' not in g:  # we check here as test cases will stub before the request cycle begins
        if w3 is not None:
            current_app.logger.debug('Setting w3 in global environment')
            g.w3 = w3
        else:
            current_app.logger.info(
                f'Set default account {current_app.config["PUBLIC_KEY"]}, provider {current_app.config["RPC_PATH"]}')
            provider = Web3.HTTPProvider(current_app.config['RPC_PATH'])
            g.w3 = Web3(provider)
            g.w3.eth.defaultAccount = current_app.config['PUBLIC_KEY']
            # If in DEV mode, setup w3 to talk to SKYNET POA
            if current_app.config['DEVELOPMENT'] is True:
                g.w3.middleware_onion.inject(geth_poa_middleware, layer=0)


@metrics_collector
def get_market_token():
    mt = MarketToken(g.w3.eth.defaultAccount)
    mt.at(g.w3, current_app.config['MARKET_TOKEN_CONTRACT_ADDRESS'])
    return mt


@metrics_collector
def get_voting():
    v = Voting(g.w3.eth.defaultAccount)
    v.at(g.w3, current_app.config['VOTING_CONTRACT_ADDRESS'])
    return v


@metrics_collector
def get_application(hash):
    """
    given a hash for a listing applicant, return its candidate if it
    is an applicant, none otherwise
    """
    v = get_voting()
    b = g.w3.toBytes(hexstr=hash)
    if call(v.candidate_is(b, 1)):
        return call(v.get_candidate(b))
    else:
        return None


@metrics_collector
def get_parameterizer():
    p = Parameterizer(g.w3.eth.defaultAccount)
    p.at(g.w3, current_app.config['PARAMETERIZER_CONTRACT_ADDRESS'])
    return p


@metrics_collector
def get_datatrust():
    d = Datatrust(g.w3.eth.defaultAccount)
    d.at(g.w3, current_app.config['DATATRUST_CONTRACT_ADDRESS'])
    return d


@metrics_collector
def get_listing():
    lg = Listing(g.w3.eth.defaultAccount)
    lg.at(g.w3, current_app.config['LISTING_CONTRACT_ADDRESS'])
    return lg


@metrics_collector
def get_single_listing(listing_hash):
    lg = get_listing()
    # the provided listing_hash needs to be converted to a byte array
    b = g.w3.toBytes(hexstr=listing_hash)
    if call(lg.is_listed(b)):
        return call(lg.get_listing(b))
    else:
        return None


@metrics_collector
def get_backend_address():
    d = get_datatrust()
    address = call(d.get_backend_address())
    current_app.logger.info(f'backend address from protocol is {address}')
    return address


@metrics_collector
def get_backend_url():
    d = get_datatrust()
    url = call(d.get_backend_url())
    current_app.logger.info(f'backend url from protocol is {url}')
    return url


@metrics_collector
def is_registered():
    """
    Check that this API is registered as the datatrust for a given market by
    comparing the on-chain backend address with this API's wallet addr
    """
    address = get_backend_address()
    return address == current_app.config['PUBLIC_KEY']


@metrics_collector
def get_bytes_purchased(address):
    """
    Return the number of bytes purchased by the address
    """
    d = get_datatrust()
    return call(d.get_bytes_purchased(address))


def has_stake(address):
    """
    Given an account address, check to see if there is sufficient CMT balance to pay current market stake
    """
    p = get_parameterizer()
    stake = call(p.get_stake())

    t = get_market_token()
    bal = call(t.balance_of(address))

    return bal >= stake
