import settings
from peewee import InternalError
from dosepack.error_handling.error_handler import create_response
from dosepack.utilities.utils import log_args_and_response
from src.dao.effi_dash_dao import get_batch_preprocess_data_dao, get_pack_details_by_date_resource, \
    get_all_system_packs_data

logger = settings.logger


@log_args_and_response
def get_pack_details_for_efficiency(last_fetch_id):
    """
    Get pack information for pharmacy performance and pharmacy manual dashboards
    @param last_fetch_id: {"last_fetch_id": int}
    @return: dict
    """
    try:
        pack_data = get_pack_details_by_date_resource(last_fetch_id)

        for row in pack_data['records']:
            row.update({'pills': float(row['pills'])})
            row.update({'date': row['date'].strftime('%Y-%m-%d')})
            if row['time'] is not None:
                row.update({'time': int(row['time'])})
        return create_response(pack_data)
    except Exception as e:
        logger.error(e, exc_info=True)
        return e


@log_args_and_response
def get_system_processed_packs_data():
    """
    Pack details of packs that have status done and are filled by system
    @return: dict
    """
    try:
        pack_data = get_all_system_packs_data()

        return create_response(pack_data)
    except InternalError as e:
        logger.error(e)
        return e


@log_args_and_response
def get_batch_preprocess_data():
    """
    Get batch details, process details, and time spent on that screen of the preprocessing module for each batch
    @return: dict
    """

    try:
        session_data = get_batch_preprocess_data_dao()

        return create_response(session_data)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise
