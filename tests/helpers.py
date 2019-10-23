from computable.helpers.transaction import call, transact

def maybe_increase_market_token_allowance(w3, market_token, owner, spender, thresh):
    """
    Inspect the allowance for a given address from msg.sender. If below a
    given threshold, increase the allowance to meet it.
    """
    rct = None
    allowed = call(market_token.allowance(owner, spender))
    if allowed < thresh:
        delta = thresh - allowed
        tx = transact(market_token.increase_allowance(spender, delta,
            {'from': owner, 'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
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
        tx = transact(market_token.transfer(to, delta, {'gas': 1000000, 'gasPrice': w3.toWei(2, 'gwei')}))
        rct = w3.eth.waitForTransactionReceipt(tx)
    return rct

def time_travel(w3, amount):
    """
    given the current web3 instance and an amount of time, in seconds, to travel adjust the block
    timestamp and mine a new block.
    returns the newly mined block's hash
    """
    # first get the current block timestamp
    block = w3.eth.getBlock(w3.eth.blockNumber)
    current_time = block['timestamp']
    # add to the future and go there...
    future_time = current_time + amount
    w3.provider.ethereum_tester.time_travel(future_time)
    block_hash = w3.provider.ethereum_tester.mine_block()
    return block_hash
