"""
Asyncronous tasks that may be used by more than one namespace
"""
from flask import current_app, g
from app import celery
from core.protocol import set_w3
import core.constants as C

@celery.task
def wait_for_mining(tx_hash):
    """
    Wait for the given tx_hash to be mined, then record the result to be fetched later
    """

    # will likely need to be set in a worker (which runs in its own app)
    set_w3()

    current_app.logger.info(C.WAITING_FOR_RECEIPT, tx_hash)
    # TODO handle timeout via web3.exceptions.TimeExhausted
    tx_rcpt = g.w3.eth.waitForTransactionReceipt(tx_hash, C.EVM_TIMEOUT)
    current_app.logger.info(C.TRANSACTION_MINED, tx_rcpt['transactionHash'])
    return g.w3.toHex(tx_rcpt['transactionHash'])
