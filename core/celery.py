"""
Abstractions for celery and asynchronous tasks handled by celery workers
"""
from flask import current_app, g
from celery import Celery
from .protocol import get_datatrust, is_registered
from .helpers import set_gas_prices
from .constants import SEND_DATA_HASH
from computable.helpers.transaction import call, transact, send

def set_celery(celery=None):
    """
    create a celery app at the request level to be used by our async tasks
    """
    if 'celery' not in g:
        if celery == None:
            celery = Celery(
                backend=current_app.config['CELERY_RESULT_BACKEND'],
                broker=current_app.config['CELERY_BROKER_URL'])
        g.celery = celery

def get_uuid():
    return uuid()

def get_send_data_hash_after_mining():
    """
    Return the async task itself from here, as we must lazily declare its task status
    """
    @g.celery.task(name=SEND_DATA_HASH)
    def send_data_hash(tx_hash, listing, data_hash):
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

    return send_data_hash
