from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster


def add_template_delete_status_due_to_change_rx_code_master():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if CodeMaster.table_exists():
            # codes for canister testing
            CodeMaster.insert(id=settings.TEMPLATE_DELETED_DRUE_TO_CHANGE_RX,
                              group_id=settings.GROUP_MASTER_TEMPLATE,
                              value="Deleted Due To ChangeRx").execute()

            print("Data inserted in the CodeMaster table.")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))


if __name__ == "__main__":
    add_template_delete_status_due_to_change_rx_code_master()
