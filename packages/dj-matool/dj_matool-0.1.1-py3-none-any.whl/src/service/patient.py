from peewee import DoesNotExist, IntegrityError, InternalError, DataError

import settings
from dosepack.error_handling.error_handler import error, create_response
from dosepack.validation.validate import validate
from src.dao.patient_dao import get_patient_data_dao, patient_note_update_or_create_dao, get_patients_dao

logger = settings.logger


def get_patient_note(patient_id):
    """
    Return patient note if present
    :param patient_id: Patient ID
    :return: str
    """
    try:
        note = get_patient_data_dao(patient_id=patient_id)

    except DoesNotExist:
        note = {}

    except (InternalError, IntegrityError, ValueError, DataError) as e:
        logger.error("error in get_patient_note {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in get_patient_note {}".format(e))
        return error(1000, "Error in v: " + str(e))

    return create_response(note)


@validate(required_fields=["patient_id", "note", "user_id"])
def create_patient_note(patient_info):
    """
    Creates patient note, updates if already present
    :param patient_info: dict
    :return: str
    """
    try:
        record = patient_note_update_or_create_dao(patient_id=patient_info["patient_id"],
                                                   patient_note=patient_info["note"],
                                                   user_id=patient_info["user_id"])


        return create_response(record.id)

    except (InternalError, IntegrityError, ValueError, DataError) as e:
        logger.error("error in create_patient_note {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in create_patient_note {}".format(e))
        return error(1000, "Error in v: " + str(e))


@validate(required_fields=['company_id'])
def get_patients(request_params):
    try:
        company_id = request_params['company_id']
        filter_fields = request_params.get('filters', None)
        sort_fields = request_params.get('sort_fields', None)
        paginate = request_params.get('paginate', None)

        if paginate and ("number_of_rows" not in paginate or "page_number" not in paginate):
            return error(1020, 'Missing key(s) in paginate.')

        count, results = get_patients_dao(company_id, filter_fields, paginate, sort_fields)
        return create_response({"patient_list": results, "number_of_records": count})

    except (InternalError, IntegrityError, ValueError, DataError) as e:
        logger.error("error in get_patients {}".format(e))
        return error(2001)

    except Exception as e:
        logger.error("Error in get_patients {}".format(e))
        return error(1000, "Error in v: " + str(e))

