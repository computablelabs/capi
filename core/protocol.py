"""
Methods that deal with the Computable Protocol aspects of operating a Datatrust API,
Ideally, these functions are "pan-blueprint" as blueprint specific functionality can be
placed in its own helper file.
TODO: implement celery for blockchain methods?
"""
from flask import current_app, g
from web3 import Web3
from web3.middleware import geth_poa_middleware
from computable.contracts import Voting, Datatrust, Listing
from computable.helpers.transaction import call, transact, send

def set_w3(w3=None):
    """
    NOTE: test env will pass a web3 instance here
    An instance of Web3. NOTE: it is expected that .eth.defaultAccount is set with the datatrust's public key
    """
    if 'w3' not in g: # we check here as test cases will stub before the request cycle begins
        if w3 != None:
            current_app.logger.debug('Setting w3 in global environment')
            g.w3 = w3
        else:
            current_app.logger.info(f'Setting default eth account {current_app.config["PUBLIC_KEY"]} using provider {current_app.config["RPC_PATH"]}')
            provider = Web3.HTTPProvider(current_app.config['RPC_PATH'])
            g.w3 = Web3(provider)
            g.w3.eth.defaultAccount = current_app.config['PUBLIC_KEY']
            # If in DEV mode, setup w3 to talk to SKYNET POA
            if current_app.config['DEVELOPMENT'] == True:
                g.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def get_voting():
    v = Voting(g.w3.eth.defaultAccount)
    v.at(g.w3, current_app.config['VOTING_CONTRACT_ADDRESS'])
    return v

def get_datatrust():
    d = Datatrust(g.w3.eth.defaultAccount)
    d.at(g.w3, current_app.config['DATATRUST_CONTRACT_ADDRESS'])
    return d

def get_listing():
    l = Listing(g.w3.eth.defaultAccount)
    l.at(g.w3, current_app.config['LISTING_CONTRACT_ADDRESS'])
    return l

def get_backend_address():
    d = get_datatrust()
    address = call(d.get_backend_address())
    current_app.logger.info(f'backend address from protocol is {address}')
    return address

def get_backend_url():
    d = get_datatrust()
    url = call(d.get_backend_url())
    current_app.logger.info(f'backend url from protocol is {url}')
    return url

def is_registered():
    """
    Check that this API is registered as the datatrust for a given market by
    comparing the on-chain backend address with this API's wallet addr
    """
    address = get_backend_address()
    return address == current_app.config['PUBLIC_KEY']
