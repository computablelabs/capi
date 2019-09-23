from flask import current_app, g
from computable.helpers.transaction import send, transact

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

def get_gas_price(key='average'):
    """
    Ethgasstation has an api endpoint that will return current estimates for pricing
    GET https://ethgasstation.info/json/ethgasAPI.json
    param optional key should be one of:
        ['safelow','average','fast','fastest']
    TODO this...
    """
    pass

def send_or_transact(args):
    """
    Given a computable.py HOC args tuple (tx, opts), inspect the current app env
    and either send the transaction using the datatrust private key, or
    simply transact it if it test
    """
    if current_app.config['TESTING'] == True:
        tx = transact(args)
    else:
        tx = send(g.w3, current_app.config['PRIVATE_KEY'], args)

    return tx
