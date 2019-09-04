"""
Blueprint containing the 'admin' CLI for datatrust operators
"""
from flask import Blueprint
from flask import current_app, g
from core.protocol import get_datatrust
from computable.helpers.transaction import call, send

admin = Blueprint('admin', __name__)

@admin.cli.command('register')
def register():
    """
    register as this market's datatrust
    """
    # TODO likely will need to call protocol.set_w3 by hand as this is not in
    # a request cycle
    # dt = get_datatrust()
    # tx = send(dt.register...
    # rct = g.w3.waitForTransactionReceipt(tx)
    # return rct
    # TODO this
    pass

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
