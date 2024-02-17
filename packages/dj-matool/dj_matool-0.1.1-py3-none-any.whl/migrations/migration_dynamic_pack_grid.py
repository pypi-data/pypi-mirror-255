from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_group_master import GroupMaster
from src.model.model_pack_details import PackDetails


def migration_dynamic_pack_grid():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.PACK_GRID_TYPE,
                               name="PackGridType").execute()

            print("Data inserted in GroupMaster table.")

        if CodeMaster.table_exists():
            CodeMaster.insert(id=constants.PACK_GRID_ROW_7x4,
                              group_id=constants.PACK_GRID_TYPE,
                              value="7x4 Pack Grid").execute()
            CodeMaster.insert(id=constants.PACK_GRID_ROW_8x4,
                              group_id=constants.PACK_GRID_TYPE,
                              value="8x4 Pack Grid").execute()

            print("Data inserted in the CodeMaster table.")

    except Exception as e:
        settings.logger.error("Error while adding Code Master ", str(e))

    try:
        migrate(
            migrator.add_column(PackDetails._meta.db_table,
                                PackDetails.grid_type.db_column,
                                PackDetails.grid_type)
        )
        print("add column grid_type in PackDetail")
    except Exception as e:
        print("Error while adding column in PackDetail: ", str(e))


if __name__ == "__main__":
    migration_dynamic_pack_grid()
