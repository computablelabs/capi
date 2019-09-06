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
# NOTE when testing pass `with_appconext=False` as a 2nd arg
@admin.cli.command('registration_test', with_appcontext=False)
# We will default an omitted gas price to 2 gwei TODO set something else?
@click.option('--gas_price', type=int, default=2, help='An int, representing GWEI, that will be set as gas_price for this transaction')
def test(gas_price):
    do_register(gas_price)


@admin.cli.command('register')
@click.option('--gas_price', type=int, default=2, help='An int, representing GWEI, that will be set as gas_price for this transaction')
def real(gas_price):
    do_register(gas_price)

def do_register(gas_price):
    """
    register as this market's datatrust
    NOTE: we are assuming you have checked that any previous registration
    candidate (can be checked via /candidates/registration), if present,
    has been resolved (via resolve_registration --tbd)
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
        # TEST env never need use send...
        if current_app.config['TESTING'] == True:
            tx = transact(args)
        else:
            tx = send(g.w3, current_app.config['PRIVATE_KEY'], args)

        rct = g.w3.eth.waitForTransactionReceipt(tx)
        # TODO if the receipt is wanted we could output it...
        # click.echo(rct)

        click.echo(C.REGISTERED_CANDIDATE)
