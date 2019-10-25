"""
Blueprint containing the 'admin' CLI for datatrust operators
"""
import click
from flask import Blueprint
from flask import current_app, g
from .protocol import set_w3, get_market_token, get_voting, get_parameterizer, get_datatrust, is_registered
from .helpers import set_gas_prices, send_or_transact
import core.constants as C # TODO why can't i use .constants?
from computable.helpers.transaction import call

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
        # the operator will need to approve the voting contract to spend the stake
        click.echo('Checking for the ability to stake...')
        p11r = get_parameterizer()
        stake = call(p11r.get_stake())

        mt = get_market_token()

        # the datatrust operator must have CMT in order to stake
        mt_bal = call(mt.balance_of(mt.account))

        if mt_bal < stake:
            click.echo(C.NEED_CMT_TO_STAKE)
        else:
            # the 'account' of any HOC is the public key set in our env
            allowed = call(mt.allowance(mt.account, current_app.config['VOTING_CONTRACT_ADDRESS']))

            if allowed < stake:
                click.echo('Approving the Voting contract to withdraw the stake for this registration')
                # rather than fuss with getting deltas, just set the approval to the stake
                app = mt.approve(current_app.config['VOTING_CONTRACT_ADDRESS'], stake)
                app_args = set_gas_prices(app, gas_price)
                app_tx = send_or_transact(app_args)
                rct = g.w3.eth.waitForTransactionReceipt(app_tx)

            click.echo('Registering...')
            dt = get_datatrust()
            # comp.py HOC methods produce a tuple -> (tx, opts)
            t = dt.register(current_app.config['DNS_NAME'])
            # we use an abstracted helper to estimate gas, and set the given gas price
            args = set_gas_prices(t, gas_price) # omit gas arg and it will be estimated
            tx = send_or_transact(args)
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
    tx = send_or_transact(args)
    rct = g.w3.eth.waitForTransactionReceipt(tx)

    click.echo(C.RESOLVED % hash)
