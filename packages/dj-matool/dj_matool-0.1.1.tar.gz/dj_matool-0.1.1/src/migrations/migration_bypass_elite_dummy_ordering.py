from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_facility_distribution_master import FacilityDistributionMaster


def migration_add_codes_for_elite_bypass():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if CodeMaster.table_exists():
            # codes for canister testing
            CodeMaster.insert(id=constants.DRUG_INVENTORY_MANAGEMENT_BYPASSED,
                              group_id=constants.DRUG_INVENTORY_MANAGEMENT_GROUP_ID,
                              value=constants.DRUG_INVENTORY_MANAGEMENT_BYPASSED_NAME).execute()

            print("Data inserted in the CodeMaster table.")

        if FacilityDistributionMaster.table_exists():
            migrate(
                migrator.add_column(FacilityDistributionMaster._meta.db_table,
                                    FacilityDistributionMaster.ordering_bypass.db_column,
                                    FacilityDistributionMaster.ordering_bypass)
            )
            print("Added column in FacilityDistributionMaster")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    migration_add_codes_for_elite_bypass()
