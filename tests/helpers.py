from computable.helpers.transaction import call, transact

# TODO must change when audit are propagated (*allowance not *approval)
def maybe_increase_market_token_approval(w3, market_token, owner, spender, thresh):
    """
    Inspect the allowance for a given address from msg.sender. If below a
    given threshold, increase the allowance to meet it.
    """
    rct = None
    allowed = call(market_token.allowance(owner, spender))
    if allowed < thresh:
        delta = thresh - allowed
        tx = transact(market_token.increase_approval(spender, delta, {'from': owner}))
        rct = w3.eth.waitForTransactionReceipt(tx)
    return rct

def maybe_transfer_market_token(w3, market_token, to, thresh):
    """
    Inpect the market token balance of a given address, if below a given threshold
    transfer to it, from the defaultAddress, until thresh is met
    """
    rct = None
    bal = call(market_token.balance_of(to))
    if bal < thresh:
        delta = thresh - bal
        tx = transact(market_token.transfer(to, delta))
        rct = w3.eth.waitForTransactionReceipt(tx)
    return rct
