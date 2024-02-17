import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.utilities.utils import log_args
from src.dao.unit_dao import *

logger = settings.logger


@validate(required_fields=["name", "symbol", "type"])
@log_args
def insert_unit_data(unit_data):
    """
    Insert units data into unit_master.

    :param unit_data:
    :return: json
    """
    try:
        response = insert_unit_data_dao(unit_data)
        logger.info("Response of insert_unit_data {}".format(response))
        return create_response(response)

    except Exception as e:
        logger.error("Error in insert_unit_data {}".format(e))
        return error(0)


@log_args
def get_units_by_type(unit_data):
    """
    Gets the details of units by type.

    @param unit_data:
    :return: json
    """
    try:
        response_dict = dict()

        response = get_units_by_type_dao(unit_data=unit_data)
        response_dict['dimensions_list'] = response
        logger.info("Response of get_units_by_type {}".format(response))

        return create_response(response_dict)

    except Exception as e:
        logger.error("Error in get_units_by_type {}".format(e))
        return error(0)


@validate(required_fields=["conversion_from_unit", "conversion_to_unit", "ratio"])
@log_args
def insert_conversion_data(unit_data):
    """
    Inserts unit conversion data.

    :param unit_data:
    :return: json
    """
    try:
        response = insert_conversion_data_dao(ratio_data=unit_data)
        logger.info("Response of insert_conversion_data {}".format(response))

        return create_response(response)

    except Exception as e:
        logger.error("Error in insert_conversion_data {}".format(e))
        return error(0)


@log_args
def get_conversion_ratio(unit_data):
    """
    Gets the conversion ratio of two units.

    @param unit_data:
    :return: json
    """
    try:
        response = get_conversion_ratio_dao(unit_data=unit_data)
        logger.info("Response of get_conversion_ratio {}".format(response))

        return create_response(response)

    except Exception as e:
        logger.error("Error in get_conversion_ratio {}".format(e))
        return error(0)
