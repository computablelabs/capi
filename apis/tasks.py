"""
Asyncronous tasks that may be used by more than one namespace
"""
from time import sleep
from flask import current_app, g
from web3.exceptions import TransactionNotFound
from app import celery
from core.protocol import set_w3
import core.constants as C
from core.helpers import get_gas_price_and_wait_time

@celery.task
def wait_for_mining(tx_hash):
    """
    Wait for the given tx_hash to be mined, then record the result to be fetched later
    """

    # must be set in a worker (which runs in its own app)
    set_w3()

    current_app.logger.info(C.WAITING_FOR_RECEIPT, tx_hash)
    try:
        price_and_time = get_gas_price_and_wait_time() # just default to avg times
    except Exception:
        price_and_time = [C.MAINNET_GAS_DEFAULT, C.EVM_TIMEOUT] # a fairly high gas price and timeout that should not fail in the near future

    slept = 0
    tx_rcpt = None

    # NOTE that price_and_time[1] is 2x what the ethGasStation estimate is
    while slept < price_and_time[1]:
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
