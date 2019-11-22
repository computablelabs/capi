"""
Asyncronous tasks that may be used by more than one namespace
"""
from flask import current_app, g
from web3.exceptions import TimeExhausted
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

    # as an attempt to mitigate false positive tx failures, check for a successful TX after a timeout
    try:
        tx_rcpt = g.w3.eth.waitForTransactionReceipt(tx_hash, price_and_time[1])
    except TimeExhausted:
        current_app.logger.info(C.TRANSACTION_TIMEOUT_TRY_GET % price_and_time[1])
        tx_rcpt = g.w3.eth.getTransactionReceipt(tx_hash)

    if tx_rcpt == None:
        current_app.logger.info(C.TRANSACTION_TIMEOUT % price_and_time[1])
        raise Exception(C.TRANSACTION_TIMEOUT % price_and_time[1])
    else:
        current_app.logger.info(C.TRANSACTION_MINED, tx_rcpt['transactionHash'])
        return g.w3.toHex(tx_rcpt['transactionHash'])
