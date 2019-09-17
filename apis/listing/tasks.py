from flask import current_app, g
from app import celery
from core.protocol import get_datatrust, is_registered
from core.helpers import set_gas_prices
from core.constants import SEND_DATA_HASH
from computable.helpers.transaction import call, transact, send

@celery.task(name=SEND_DATA_HASH)
def send_data_hash_after_mining(tx_hash, listing, data_hash):
    """
    Wait for the transaction to be mined, then set the data_hash
    for the uploaded file in protocol.
    """

    # TODO else?
    if is_registered() == True:
        # TODO timeout length?
        current_app.logger.info('Waiting for initial transaction receipt: %s', g.w3.toHex(tx_hash))
        tx_rcpt = g.w3.eth.waitForTransactionReceipt(tx_hash)
        current_app.logger.info('Initial transaction mined: %s', g.w3.toHex(tx_rcpt['transactionHash']))
        # TODO handle failure here
        dt = get_datatrust()
        t = dt.set_data_hash(listing, data_hash)
        gwei = 2 # TODO use get_gas_price ethgasstation call
        t = set_gas_prices(t, gwei)
        # TODO send_or_transact
        current_app.logger.info('Sending data hash to protocol: %s', g.w3.toHex(data_hash))
        if current_app.config['TESTING'] == True:
            send_tx = transact(t)
        else:
            send_tx = send(g.w3, current_app.config['PRIVATE_KEY'], t)

        # TODO timeout length?
        current_app.logger.info('Waiting for send data hash transaction receipt: %s', g.w3.toHex(send_tx))
        send_rcpt = g.w3.eth.waitForTransactionReceipt(send_tx)
        current_app.logger.info('Send data hash transaction mined: %s', g.w3.toHex(send_rcpt['transactionHash']))
