#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import logging
import os

from lambda_helper import (assemble_tx,
                           get_params,
                           calc_eth_address,
                           get_kms_public_key)

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
LOG_FORMAT = "%(levelname)s:%(lineno)s:%(message)s"
handler = logging.StreamHandler()

_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)


def lambda_handler(event, context):
    _logger.debug("incoming event: {}".format(event))

    try:
        params = get_params()
    except Exception as e:
        raise e

    operation = event.get('operation')
    key_id = os.getenv('KMS_KEY_ID')
    if not operation:
        raise ValueError('operation needs to be specified in request and needs to be eigher "status" or "sign_bulk_payout"')

    # {"operation": "status"}
    if operation == 'status':
        pub_key = get_kms_public_key(key_id)
        eth_checksum_address = calc_eth_address(pub_key)

        return {'eth_checksum_address': eth_checksum_address}

    elif operation == "sign_bulk_payout":
        del event["operation"]
        # download public key from KMS
        pub_key = get_kms_public_key(key_id)

        # calculate the Ethereum public address from public key
        eth_checksum_addr = calc_eth_address(pub_key)

        # assemble Ethereum transaction and sign it offline
        return {"signed_tx": assemble_tx(tx_params=event, params=params, eth_checksum_addr=eth_checksum_addr)}
