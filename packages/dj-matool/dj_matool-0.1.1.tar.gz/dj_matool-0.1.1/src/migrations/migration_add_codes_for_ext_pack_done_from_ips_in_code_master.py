from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster


def migration_add_codes_for_ips_done_sync():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if CodeMaster.table_exists():
            # codes for canister testing
            CodeMaster.insert(id=constants.EXT_PACK_STATUS_CODE_DONE,
                              group_id=constants.EXT_PACK_STATUS_GROUP_ID,
                              value="Done from IPS").execute()

            print("Data inserted in the CodeMaster table.")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    migration_add_codes_for_ips_done_sync()
