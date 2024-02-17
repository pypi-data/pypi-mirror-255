import settings
from dosepack.base_model.base_model import db
from dosepack.error_handling.error_handler import error
from dosepack.utilities.manage_db_connection import use_database
from src.service.effi_dash import get_pack_details_for_efficiency, get_system_processed_packs_data, \
    get_batch_preprocess_data


class GetPharmacyFillData(object):
    """ Controller to get date and resource level info about packs for get pharmacy fill data API """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self, last_fetch_id=None):

        if last_fetch_id is None:
            return error(1001, "Missing Parameter last_fetch_id")
        response = get_pack_details_for_efficiency(last_fetch_id)

        return response


class GetSystemProcessedPacksData(object):
    """ Controller to get details of packs processed and filled by system """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self):
        response = get_system_processed_packs_data()

        return response


class GetSystemPacksPreprocessingData(object):
    """
        @desc: GET method implementation of get system packs preprocessing data API
        @return: json
    """
    exposed = True

    @use_database(db, settings.logger)
    def GET(self):
        try:
            response = get_batch_preprocess_data()

            return response
        except Exception as e:
            return error(1004)
