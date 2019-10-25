from flask import current_app
import pytest
from core.constants import REGISTERED_CANDIDATE
from computable.helpers.transaction import call, transact

def test_has_ethertoken(w3, ether_token):
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

def test_has_cmt(w3, ether_token, market_token, reserve):
    user = w3.eth.defaultAccount
    # Approve the spend
    user_bal = call(ether_token.balance_of(user))
    old_allowance = call(ether_token.allowance(user, reserve.address))
    assert old_allowance == 0
    tx= transact(ether_token.approve(reserve.address, w3.toWei(10, 'ether'), opts={'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    new_allowance = call(ether_token.allowance(user, reserve.address))
    assert new_allowance == w3.toWei(10, 'ether')

    # Perform pre-checks for support
    support_price = call(reserve.get_support_price())
    assert user_bal >= support_price
    assert new_allowance >= user_bal
    minted = (user_bal // support_price) * 10**9
    assert minted == 10**7 * w3.toWei(1, 'gwei')
    priv = call(market_token.has_privilege(reserve.address))
    assert priv == True
    total_supply = call(market_token.total_supply())
    assert total_supply == w3.toWei(4, 'ether')

    # Call support
    tx = transact(reserve.support(user_bal, opts={'gas': 1000000, 'from': user}))
    rct = w3.eth.waitForTransactionReceipt(tx)
    assert rct['status'] == 1
    cmt_user_bal = call(market_token.balance_of(user))
    # There is the creator already
    assert cmt_user_bal >= w3.toWei(10, 'milliether')
    new_supply = call(market_token.total_supply())
    assert new_supply == total_supply + w3.toWei(10, 'milliether')

def test_register(w3, ctx):
    runner = current_app.test_cli_runner()
    result = runner.invoke(args=['admin', 'registration_test'])
    assert REGISTERED_CANDIDATE in result.output

def test_registered_candidate(w3, voting, ctx):
    hash = w3.keccak(text=current_app.config['DNS_NAME'])
    candidate = call(voting.is_candidate(hash))
    assert candidate == True
