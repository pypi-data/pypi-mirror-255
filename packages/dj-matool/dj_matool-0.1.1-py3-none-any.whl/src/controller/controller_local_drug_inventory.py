import settings
from dosepack.base_model.base_model import db
from dosepack.utilities.manage_db_connection import use_database
from src.service.local_drug_inventory import local_di_update_brand_flag

logger = settings.logger


class LocalDIBrandFlag(object):
    exposed = True

    @use_database(db, settings.logger)
    def GET(self) -> str:
        """
        To obtain pre_order data using facility_dist_id & company_id.
        """
        logger.debug("In Class LocalDIBrandFlag.GET")

        return local_di_update_brand_flag()
