from math import ceil
import functools
from time import perf_counter, sleep
import requests
from flask import current_app, g
from web3.exceptions import TransactionNotFound
from computable.helpers.transaction import send, transact
import core.constants as C

def set_gas_prices(t, gas_price, gas=None):
    """
    Given a Computable.py HOC tuple, a gas price (int representing gwei) and an optional gas amount,
    set them into the 'txOpts' (t[1])
    """
    if gas == None:
        est = t[0].estimateGas()
    # just in case its lower, defer to anything there...
    t[1]['gas'] = max(t[1]['gas'], est)
    t[1]['gasPrice'] = g.w3.toWei(gas_price, 'gwei')
    return t

def fetch_gas_pricing():
    req = requests.get('https://ethgasstation.info/json/ethgasAPI.json')
    return req.json()

def get_gas_price_and_wait_time(price_key='average', wait_key='avgWait'):
    """
    Ethgasstation has an api endpoint that will return current estimates for pricing
    GET https://ethgasstation.info/json/ethgasAPI.json
    param optional price and wait keys should be among (will default to avg...)
        price_key: ['safelow','average','fast','fastest']
        wait_key: ['safeLowWait','avgWait','fastWait','fastestWait']
    We'll return exceptions in the failed call cases so that the caller can decide what to show the client
    """
    if current_app.config.get('MAINNET') == True:
        try:
            payload = fetch_gas_pricing()
        except Exception:
            raise Exception('Error fetching JSON from EthGasStation API')
        # our json will include an avg price and an avg wait time. we'll 2x the wait just in case...
        price = payload.get(price_key)
        wait = payload.get(wait_key)
        if price and wait:
            # assure these are ints...
            if not isinstance(price, int):
                price = ceil(price)
            if not isinstance(wait, int):
                wait = ceil(wait)
            # return (price_in_gwei, doubled_wait_time_seconds) NOTE that we only use the wait as a max timeout
            return (ceil(price / 10), (wait * 2) * 60)
        else:
            raise Exception('Error fetching values from EthGasStation API')
    else:
        return(C.POA_GAS_PRICE, C.EVM_TIMEOUT)

def send_or_transact(args):
    """
    Given a computable.py HOC args tuple (tx, opts), inspect the current app env
    and either send the transaction using the datatrust private key, or
    simply transact it if it test
    """
    if current_app.config.get('TESTING') == True:
        tx = transact(args)
    else:
        tx = send(g.w3, current_app.config['PRIVATE_KEY'], args)

    return tx

def wait_for_receipt(tx_hash, duration=C.EVM_TIMEOUT):
    """
    A hand rolled solution to our waitForTransactionReceipt issues, given a transaction
    hash and an amount of time, check for transaction mining in increments of
    constants.TRANSACTION_RETRY for that duration. Return the hash of the mined tx
    if completed, raise an exception if not

    @parm tx_hash An unmined transaction hash
    @param duration Amount of time, in seconds, to wait. Likely from the
    get_gas_price_and_wait_time method (will default to constant)
    """
    slept = 0
    tx_rcpt = None

    while slept < duration:
        # because web3 throws if not present vs returning None (like the docs say)
        try:
            tx_rcpt = g.w3.eth.getTransactionReceipt(tx_hash)
        except TransactionNotFound:
            tx_rcpt = None
            current_app.logger.info(f'Transaction Receipt not ready after {slept} seconds, sleeping...')
        except:
            tx_rcpt = None
            current_app.logger.info(f'Unexpected error looking up transaction after {slept} seconds, sleeping...')

        if tx_rcpt != None:
            break
        slept = slept + C.TRANSACTION_RETRY
        sleep(C.TRANSACTION_RETRY)

    if tx_rcpt == None:
        current_app.logger.info(C.TRANSACTION_TIMEOUT % price_and_time[1])
        raise Exception(C.TRANSACTION_TIMEOUT % price_and_time[1])
    else:
        current_app.logger.info(C.TRANSACTION_MINED, tx_rcpt['transactionHash'])
        return g.w3.toHex(tx_rcpt['transactionHash'])

def metrics_collector(func):
    """
    Decorator to time function and store timing results in the global env
    """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = perf_counter()
        value = func(*args, **kwargs)
        end_time = perf_counter()
        run_time = (end_time - start_time) * 1000 # convert to milliseconds
        run_time = int(run_time) # we'll lose some accuracy here, but I think it's negligible
        if 'metrics' not in g:
            g.metrics = []
        g.metrics.append({
            func.__name__: run_time
        })
        return value
    return wrapper_timer
