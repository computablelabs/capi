from flask import current_app
import pytest
from core.constants import RESOLVED
from computable.helpers.transaction import call, transact
from tests.helpers import maybe_transfer_market_token, maybe_increase_market_token_allowance, time_travel

def test_setup_registration_candidate(w3, ether_token, market_token, voting, parameterizer_opts, parameterizer, reserve, datatrust, ctx):
    user = w3.eth.defaultAccount 
    user_bal = call(ether_token.balance_of(user))
    assert user_bal == 0

    # Deposit ETH in EtherToken
    tx = transact(ether_token.deposit(
        w3.toWei(10, 'ether'), {'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    new_user_bal = call(ether_token.balance_of(user))
    assert new_user_bal == w3.toWei(10, 'ether')
    assert rct['status'] == 1

    # Approve the spend
    old_allowance = call(ether_token.allowance(user, reserve.address))
    assert old_allowance == 0
    tx= transact(ether_token.approve(reserve.address, w3.toWei(10, 'ether'), opts={'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    new_allowance = call(ether_token.allowance(user, reserve.address))
    assert new_allowance == w3.toWei(10, 'ether')

    # Perform pre-checks for support 
    support_price = call(reserve.get_support_price())
    assert new_user_bal >= support_price
    assert new_allowance >= new_user_bal
    minted = (new_user_bal // support_price) * 10**9
    assert minted == 10**7 * w3.toWei(1, 'gwei')
    priv = call(market_token.has_privilege(reserve.address))
    assert priv == True
    total_supply = call(market_token.total_supply())
    assert total_supply == w3.toWei(4, 'ether')

    # Call support
    tx = transact(reserve.support(new_user_bal, opts={'gas': 1000000, 'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    logs = reserve.deployed.events.Supported().processReceipt(rct)
    cmt_user_bal = call(market_token.balance_of(user))
    assert cmt_user_bal >= w3.toWei(10, 'milliether')
    new_supply = call(market_token.total_supply())
    assert new_supply == total_supply + w3.toWei(10, 'milliether')

    stake = call(parameterizer.get_stake())
    assert stake <= cmt_user_bal

    # Approve the market token allowance
    old_mkt_allowance = call(market_token.allowance(user, voting.address))
    assert old_mkt_allowance == 0
    tx = transact(market_token.approve(voting.address, w3.toWei(10, 'milliether'), opts={'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    new_mkt_allowance = call(market_token.allowance(user, voting.address))
    assert new_mkt_allowance == w3.toWei(10, 'milliether')
    assert stake <= new_mkt_allowance
 
    tx = transact(datatrust.register(current_app.config['DNS_NAME'], {'from': user, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
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
    app_rct = maybe_increase_market_token_allowance(w3, market_token, voter, voting.address, stake)
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
