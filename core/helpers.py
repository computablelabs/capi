from math import ceil
from flask import current_app, g
import requests
from computable.helpers.transaction import send, transact
from .constants import POA_GAS_PRICE, EVM_TIMEOUT

def set_gas_prices(t, gas_price, gas=None):
    """
    Given a Computable.py HOC tuple, a gas price (int representing gwei) and an optional gas amount,
    set them into the 'txOpts' (t[1])
    """
    if gas == None:
        est = t[0].estimateGas()
    # just in case its lower, defer to anything there...
    t[1]['gas'] = max(t[1]['gas'], est)
    t[1]['gasPrice'] = g.w3.toWei(gas_price, 'gwei')
    return t

def fetch_gas_pricing():
    req = requests.get('https://ethgasstation.info/json/ethgasAPI.json')
    return req.json()

def get_gas_price_and_wait_time(price_key='average', wait_key='avgWait'):
    """
    Ethgasstation has an api endpoint that will return current estimates for pricing
    GET https://ethgasstation.info/json/ethgasAPI.json
    param optional price and wait keys should be among (will default to avg...)
        price_key: ['safelow','average','fast','fastest']
        wait_key: ['safeLowWait','avgWait','fastWait','fastestWait']
    We'll return exceptions in the failed call cases so that the caller can decide what to show the client
    """
    if current_app.config.get('MAINNET') == True:
        try:
            payload = fetch_gas_pricing()
        except Exception:
            raise Exception('Error fetching JSON from EthGasStation API')
        # our json will include an avg price and an avg wait time. we'll 2x the wait just in case...
        price = payload.get(price_key)
        wait = payload.get(wait_key)
        if price and wait:
            # assure these are ints...
            if not isinstance(price, int):
                price = ceil(price)
            if not isinstance(wait, int):
                wait = ceil(wait)
            # return (price_in_gwei, doubled_wait_time_seconds) NOTE that we only use the wait as a max timeout
            return (ceil(price / 10), (wait * 2) * 60)
        else:
            raise Exception('Error fetching values from EthGasStation API')
    else:
        return(POA_GAS_PRICE, EVM_TIMEOUT)

def send_or_transact(args):
    """
    Given a computable.py HOC args tuple (tx, opts), inspect the current app env
    and either send the transaction using the datatrust private key, or
    simply transact it if it test
    """
    if current_app.config.get('TESTING') == True:
        tx = transact(args)
    else:
        tx = send(g.w3, current_app.config['PRIVATE_KEY'], args)

    return tx
