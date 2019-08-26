from flask import current_app, g
from web3 import Web3
from web3.middleware import geth_poa_middleware
from computable.contracts import Datatrust

def set_w3(w3=None):
    """
    NOTE: test env will pass a web3 instance here
    An instance of Web3. NOTE: it is expected that .eth.defaultAccount is set with the datatrust's public key
    """
    if 'w3' not in g:
        if w3 != None:
            g.w3 = w3
        else:
            provider = Web3.HTTPProvider(current_app.config['WEB3_PROVIDER'])
            g.w3 = Web3(provider)
            g.w3.eth.defaultAccount = current_app.config['API_PUBLIC_KEY']
            # If in DEV mode, setup w3 to talk to SKYNET POA
            if current_app.config['DEVELOPMENT'] == True:
                g.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def set_contract_addresses(addresses):
    """
    NOTE: used in test env as these cannot be known in advance.
    given a dict of addresses update the config
    """
    current_app.config['ETHER_TOKEN_CONTRACT_ADDRESS'] = addresses['ether_token']
    current_app.config['VOTING_CONTRACT_ADDRESS'] = addresses['voting']
    current_app.config['DATATRUST_CONTRACT_ADDRESS'] = addresses['datatrust']
    current_app.config['LISTING_CONTRACT_ADDRESS'] = addresses['listing']

def is_registered():
    """
    Check that this API is registered as the datatrust for a given market.
    If so, proceed normally. If not, intercept the request then:
    * Call to register if not already a registration candidate
    * Resolve any closed registration poll if appropriate
    * Return a message relating the status
    """
    pass
