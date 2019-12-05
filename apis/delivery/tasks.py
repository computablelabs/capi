from flask import current_app, g
from app import celery
from core.protocol import set_w3, delivered
import core.constants as C
from core.helpers import wait_for_receipt

@celery.task
def delivered_async(delivery_hash, delivery_url, accessed_tx, price_and_time):
    """
    async celery task used by the datatrust to report that a delivery was made.

    @param delivery_hash
    @param delivery_url
    @param accessed_tx The unmined transaction given from reporting listing_accessed
    @param price a gas price to pass to delivered()
    @param duration a timeout duration to pass wait_for_receipt()
    """

    # must be set in a worker (which runs in its own app)
    set_w3()

    # before we can call delivered we must make sure the accessed tx has mined
    current_app.logger.info(C.WAITING_FOR_RECEIPT, accessed_tx)
    accessed_rct_hash = wait_for_receipt(accessed_tx, price_and_time[1])
    current_app.logger.info(f'listing_accessed transaction {accessed_rct_hash} mined, calling for delivery completion')
    # now see if we can get paid
    del_tx = delivered(delivery_hash, delivery_url, price_and_time[0])
    current_app.logger.info(C.WAITING_FOR_RECEIPT, del_tx)
    # return the transaction hash as a hex
    return wait_for_receipt(del_tx, price_and_time[1])
