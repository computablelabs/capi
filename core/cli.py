"""
Blueprint containing the 'admin' CLI for datatrust operators
"""
from flask import Blueprint
from flask import current_app, g
from .protocol import set_w3, get_datatrust
from .helpers import set_gas_prices
from computable.helpers.transaction import call, transact, send

admin = Blueprint('admin', __name__)

@admin.cli.command('register')
@click.argument('gas_price')
def register(gas_price):
    """
    register as this market's datatrust
    """
    # set_w3 by hand as this is not in a request cycle
    set_w3()
    dt = get_datatrust()
    # comp.py HOC methods produce a tuple -> (tx, opts)
    t = dt.register(current_app.config['DNS_NAME'])
    # we use an abstracted helper to estimate gas, and set the given gas price
    args = set_gas_prices(t, gas_price) # omit gas arg and it will be estimated
    # TEST env never need use send...
    if current_app.config['TESTING'] == True:
        tx = transact(args)
    else:
        tx = send(g.w3, current_app.config['PRIVATE_KEY'], args)

    rct = g.w3.waitForTransactionReceipt(tx)
    return rct

@admin.cli.command('get_candidate')
def get_candidate():
    """
    fetch the voting client for this datatrust's registration
    """
    pass

@admin.cli.command('resolve_registration')
def resolve_registration():
    """
    if the registration candidacy period has ended, and no one else has, resolve said candidate
    """
    pass

@admin.cli.command('withdraw')
def withdraw():
    """
    transfer any funds from the ethertoken owed to the datatrust owner
    """
    pass
