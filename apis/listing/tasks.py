from flask import current_app, g
from app import celery
from core.protocol import set_w3, get_datatrust, is_registered
from core.helpers import set_gas_prices, send_or_transact
from computable.helpers.transaction import call, transact, send
import core.constants as C

@celery.task
def send_data_hash_after_mining(tx_hash, listing, data_hash):
    """
    Wait for the transaction to be mined, then set the data_hash
    for the uploaded file in protocol.
    """

    # will likely need to be set in a worker (which runs in its own app)
    set_w3()

    # TODO else?
    if is_registered() == True:
        # TODO timeout length?
        current_app.logger.info(C.WAITING_FOR_RECEIPT, tx_hash)
        # TODO handle timeout via web3.exceptions.TimeExhausted
        tx_rcpt = g.w3.eth.waitForTransactionReceipt(tx_hash, timeout=C.EVM_TIMEOUT)
        current_app.logger.info(C.TRANSACTION_MINED, tx_rcpt['transactionHash'])
        # TODO handle failure here
        dt = get_datatrust()
        t = dt.set_data_hash(listing, data_hash)
        gwei = 2 # TODO use get_gas_price ethgasstation call
        args = set_gas_prices(t, gwei)
        # TODO send_or_transact
        current_app.logger.info('Sending data hash to protocol: %s', data_hash)
        send_tx = send_or_transact(args)
        # TODO timeout length?
        current_app.logger.info(C.WAITING_FOR_NAMED_RECEIPT, 'send data hash', send_tx)
        send_rcpt = g.w3.eth.waitForTransactionReceipt(send_tx)
        # return this as the task result as well. use hex...
        send_hash = g.w3.toHex(send_rcpt['transactionHash'])
        current_app.logger.info(C.NAMED_TRANSACTION_MINED, 'Send data hash', send_hash)
        return send_hash
