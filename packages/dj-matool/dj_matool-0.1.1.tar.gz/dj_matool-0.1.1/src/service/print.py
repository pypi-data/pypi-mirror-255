import settings
from dosepack.error_handling.error_handler import error, create_response
from src import constants
from src.dao.print_dao import get_associated_printers_dao, add_printer_in_db, db_get_by_printer_type, \
    db_get_by_printer_code, add_printers_in_couch_db

logger = settings.logger


def get_associated_printers(system_id):
    try:
        data = get_associated_printers_dao(system_id)
        return data
    except Exception as e:
        logger.exception("Exception in get_associated_printers: {}".format(e))
        raise e


def add_printer(printer_name, ip_address, system_id, printer_type=None):
    """
    Adds printer in printer table and updates it in real_time DB
    :param printer_name:
    :param ip_address:
    :param system_id:
    :param printer_type:
    :return: json
    """
    try:
        printer_type = int(printer_type) if printer_type else None
        # check if printer already exists
        unique_code = str(printer_name).replace(" ", '') + "@" + str(system_id)

        response = add_printer_in_db(printer_name, printer_type, unique_code, ip_address, system_id)

        if response and response["added"]:
            printer = {
                "id": response["id"],
                "printer_name": printer_name,
                "ip_address": ip_address,
                "unique_code": unique_code,
                "printer_type_id": printer_type
            }
            add_printers_in_couch_db(system_id, printer)

    except Exception as e:
        logger.exception("Exception in add_printer {}".format(e))
        return error(2005)
    return create_response(response)


def db_get_printer(unique_code, system_id):
    printer = None
    try:
        if not unique_code:  # If printer code is not available get printer using default printer type
            printer = db_get_by_printer_type(constants.DEFAULT_PRINTER_TYPE, system_id)
        else:
            printer = db_get_by_printer_code(unique_code, system_id)

    except Exception as e:
        logger.exception("Exception in db_get_printer {}".format(e))
        return error(2005)
    return printer
