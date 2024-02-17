from typing import List

from peewee import InternalError, IntegrityError, DataError, DoesNotExist

from dosepack.base_model.base_model import db
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate
from settings import logger
from src.dao.canister_testing_dao import logger
from src.model.model_unit_conversion import UnitConversion
from src.model.model_unit_master import UnitMaster


@validate(required_fields=["name", "symbol", "type"])
@log_args_and_response
def insert_unit_data_dao(unit_data):
    """
    Insert units data into unit_master.

    :param unit_data:
    :return: json
    """
    try:
        unit_data_dict = unit_data.copy()

        with db.transaction():
            response = UnitMaster.insert_unit(unit_data=unit_data_dict)

        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("Error in insert_unit_data_dao {}".format(e), exc_info=True)
        raise


@log_args_and_response
def get_units_by_type_dao(unit_data):
    """
    Gets the details of units by type.
    @param unit_data:
    :return: json
    """
    try:
        unit_type = unit_data['unit_type']

        response = UnitMaster.get_units_by_type(unit_type=unit_type)
        response_dict = dict()
        response_dict['dimensions_list'] = response

        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("Error in get_units_by_type_dao {}".format(e), exc_info=True)
        raise


@log_args_and_response
@validate(required_fields=["conversion_from_unit", "conversion_to_unit", "ratio"])
def insert_conversion_data_dao(unit_data):
    """
    Inserts unit conversion data.

    :param unit_data:
    :return: json
    """
    try:
        ratio_data_dict = dict()
        ratio_data_dict['convert_from_id'] = unit_data['conversion_from_unit']
        ratio_data_dict['convert_to_id'] = unit_data['conversion_to_unit']
        ratio_data_dict['conversion_ratio'] = unit_data['ratio']

        with db.transaction():
            response = UnitConversion.insert_conversion_ratio(ratio_data=ratio_data_dict)

        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("Error in insert_conversion_data_dao {}".format(e), exc_info=True)
        raise


@log_args_and_response
def get_conversion_ratio_dao(unit_data):
    """
    Gets the conversion ratio of two units.
    @param unit_data:
    :return: json
    """
    try:
        convert_from = unit_data['convert_from']
        convert_into = unit_data['convert_into']

        response = UnitConversion.get_conversion_ratio_for_a_unit(convert_from=convert_from, convert_into=convert_into)

        return response

    except (InternalError, IntegrityError, DataError, DoesNotExist, Exception) as e:
        logger.error("Error in get_conversion_ratio_dao {}".format(e), exc_info=True)
        raise


@log_args_and_response
def get_conversion_ratio_for_a_unit_dao(convert_from, convert_into) -> List[int]:
    """
     To get the conversion ratio of two units.
     @param convert_from:
     @param convert_into:
     @return:
    """
    try:
        conversion_ratio = UnitConversion.get_conversion_ratio_for_a_unit(convert_from=convert_from,
                                                                          convert_into=convert_into)

        return conversion_ratio

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_conversion_ratio_for_a_unit_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_conversion_ratio_for_a_unit_dao {}".format(e))
        raise e


@log_args_and_response
def get_unit_data_by_name_dao(unit_name):
    """
     to get the unit data by the unit name.
     @param unit_name:
     @return:
    """
    try:
        data = UnitMaster.get_unit_data_by_name(unit_name=unit_name)

        return data

    except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
        logger.error("error in get_unit_data_by_name_dao {}".format(e))
        raise e
    except Exception as e:
        logger.error("error in get_unit_data_by_name_dao {}".format(e))
        raise e
