"""
    @file: error_handler.py
    @createdBy: Amisha Patel
    @createdDate: 4/22/2015
    @lastModifiedBy: Amisha Patel
    @lastModifiedDate: 4/22/2015
    @type: file
    @desc: Contains global constants for reason code messages
"""

from peewee import InternalError, IntegrityError

from src.dao.reason_master_dao import db_get_reasons_dao
from dosepack.error_handling.error_handler import create_response, error
import logging.config

config_file_path = "logging.json"

# get the logger
logger = logging.getLogger("root")

# declare all the reason codes.
FAILURE = 0
DUPLICATE_RFID = 1
EMPTY_RFID = 2

RFID_ALREADY_ASSOCIATED = 4


def get_reasons(reason_group):
    """
    Returns list of reasons for a given group

    :return: json
    """
    try:
        pack_fill_reasons = db_get_reasons_dao(reason_group)
        return create_response(pack_fill_reasons)
    except (IntegrityError, InternalError) as e:
        logger.error(e, exc_info=True)
        return error(2001)


