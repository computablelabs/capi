from flask import current_app
import pytest
from core.constants import RESOLVED
from computable.helpers.transaction import call, transact
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_approval, time_travel

# voter, datatrust owner = accounts 2 and 3

def test_setup_registration_candidate(w3, market_token, voting, parameterizer_opts, datatrust, ctx):
    dt = w3.eth.accounts[3]
    tx = transact(datatrust.register(current_app.config['DNS_NAME'], {'from': dt, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    rct = w3.eth.waitForTransactionReceipt(tx)

    reg_hash = w3.keccak(text=current_app.config['DNS_NAME'])

    # should see the candidate now
    is_candidate = call(voting.is_candidate(reg_hash))
    assert is_candidate == True

    # we'll use acct 2 as voter, will likely need market token...
    voter = w3.eth.accounts[2]
    stake = parameterizer_opts['stake']
    trans_rct = maybe_transfer_market_token(w3, market_token, voter, stake)
    # will likely need to approve voting
    app_rct = maybe_increase_market_token_approval(w3, market_token, voter, voting.address, stake)
    # should be able to vote now
    vote_tx = transact(voting.vote(reg_hash, 1,
        {'from': voter, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
    vote_rct = w3.eth.waitForTransactionReceipt(vote_tx)
    # check that the vote registered
    candidate = call(voting.get_candidate(reg_hash))
    assert candidate[4] == 1

def test_resolve(w3, voting, parameterizer_opts, datatrust, ctx):
    reg_hash = w3.keccak(text=current_app.config['DNS_NAME'])
    #before we can resolve the candidate, move past the voteby
    time_travel(w3, parameterizer_opts['vote_by'])
    did_pass = call(voting.did_pass(reg_hash, parameterizer_opts['plurality']))
    assert did_pass == True

    # now resolve it
    runner = current_app.test_cli_runner()

    #pass a string like cli does
    result = runner.invoke(args=['admin', 'resolution_test', '--hash', w3.toHex(reg_hash)])
    assert (RESOLVED % w3.toHex(reg_hash)) in result.output

def test_was_actually_resolved(w3, voting, ctx):
    reg_hash = w3.keccak(text=current_app.config['DNS_NAME'])
    is_candidate = call(voting.is_candidate(reg_hash))
    assert is_candidate != True
