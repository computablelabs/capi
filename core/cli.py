"""
Blueprint containing the 'admin' CLI for datatrust operators
"""
import click
from flask import Blueprint
from flask import current_app, g
from .protocol import set_w3, get_datatrust, is_registered
from .helpers import set_gas_prices
import core.constants as C # TODO why can't i use .constants?
from computable.helpers.transaction import call, transact, send

admin = Blueprint('admin', __name__)

@admin.cli.command('registration_test', with_appcontext=False)
# We will default an omitted gas price to 2 gwei TODO set something else?
@click.option('--gas_price', type=int, default=2, help='An int, representing GWEI, that will be set as gas_price for this transaction')
def registration_test(gas_price):
    do_registration(gas_price)


@admin.cli.command('register')
@click.option('--gas_price', type=int, default=2, help='An int, representing GWEI, that will be set as gas_price for this transaction')
def registration_real(gas_price):
    do_registration(gas_price)

def do_registration(gas_price):
    """
    register as this market's datatrust
    NOTE: we are assuming you have checked that any previous registration
    candidate (can be checked via /candidates/registration), if present,
    has been resolved (via resolve_registration)
    """

    # set_w3 by hand as this is not in a request cycle
    set_w3()

    if is_registered() == True:
        click.echo(C.REGISTERED)
    else:
        dt = get_datatrust()
        # comp.py HOC methods produce a tuple -> (tx, opts)
        t = dt.register(current_app.config['DNS_NAME'])
        # we use an abstracted helper to estimate gas, and set the given gas price
        args = set_gas_prices(t, gas_price) # omit gas arg and it will be estimated
        # TEST env never need use send... TODO implement send_or_transact helper
        if current_app.config['TESTING'] == True:
            tx = transact(args)
        else:
            tx = send(g.w3, current_app.config['PRIVATE_KEY'], args)

        rct = g.w3.eth.waitForTransactionReceipt(tx)
        # TODO if the receipt is wanted we could output it...
        # click.echo(rct)

        click.echo(C.REGISTERED_CANDIDATE)

@admin.cli.command('resolution_test', with_appcontext=False)
@click.option('--hash', type=str, help='The Keccak hash which identifies the candidate to be resolved')
@click.option('--gas_price', type=int, default=2, help='An int, representing GWEI, that will be set as gas_price for this transaction')
def resolution_test(hash, gas_price):
    do_resolution(hash, gas_price)


@admin.cli.command('resolve')
@click.option('--hash', type=str, help='The Keccak hash which identifies the candidate to be resolved')
@click.option('--gas_price', type=int, default=2, help='An int, representing GWEI, that will be set as gas_price for this transaction')
def resolution_real(hash, gas_price):
    do_resolution(hash, gas_price)

def do_resolution(hash, gas_price):
    """
    Allow the datatrust operator to call for the resolution of a given candidate
    """
    # set_w3 by hand as this is not in a request cycle
    set_w3()
    dt = get_datatrust()
    t = dt.resolve_registration(hash)
    args = set_gas_prices(t, gas_price) # omit gas arg and it will be estimated

    # TEST env never need use send... TODO implement send_or_transact helper
    # tx = send_or_transact(args)
    if current_app.config['TESTING'] == True:
        tx = transact(args)
    else:
        tx = send(g.w3, current_app.config['PRIVATE_KEY'], args)

    rct = g.w3.eth.waitForTransactionReceipt(tx)
    click.echo(C.RESOLVED % g.w3.toHex(hash))
