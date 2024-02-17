from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db

from model.model_init import init_db

from src import constants
from src.constants import EXTCHANGERXACTIONS_GROUP_ID, EXTCHANGERXACTIONS_ADD, EXTCHANGERXACTIONS_DELETE
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster
from src.model.model_ext_change_rx import ExtChangeRx
from src.model.model_ext_change_rx_details import ExtChangeRxDetails
from src.model.model_ext_changerx_json import ExtChangeRxJson
from src.model.model_ext_pack_details import ExtPackDetails
from src.model.model_group_master import GroupMaster
from src.model.model_pack_header import PackHeader


def add_data():
    if GroupMaster.table_exists():
        GroupMaster.insert(id=EXTCHANGERXACTIONS_GROUP_ID, name='ExtChangeRxActions').execute()
        GroupMaster.insert(id=constants.EXT_PACK_USAGE_STATUS_GROUP_ID,
                           name=constants.EXT_PACK_USAGE_STATUS_DESC).execute()

    print("ChangeRx Flow -- Insertion in Group Master completed.")

    if ActionMaster.table_exists():
        ActionMaster.insert(id=EXTCHANGERXACTIONS_ADD, group_id=EXTCHANGERXACTIONS_GROUP_ID,
                            value="ChangeRx -- Add").execute()
        ActionMaster.insert(id=EXTCHANGERXACTIONS_DELETE, group_id=EXTCHANGERXACTIONS_GROUP_ID,
                            value="Change Rx -- Delete").execute()
    print("ChangeRx Flow -- Insertion in Action Master completed.")

    if CodeMaster.table_exists():
        CodeMaster.insert(id=settings.PACK_STATUS_CHANGE_RX, group_id=settings.GROUP_MASTER_PACK,
                          value=constants.EXT_CHANGE_RX_PACKS_DESC).execute()

        CodeMaster.insert(id=settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_TEMPLATE,
                          group_id=settings.GROUP_MASTER_TEMPLATE,
                          value="Pending ChangeRx From Template").execute()
        CodeMaster.insert(id=settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_PACK, group_id=settings.GROUP_MASTER_TEMPLATE,
                          value="Pending ChangeRx From Pack").execute()

        CodeMaster.insert(id=constants.EXT_PACK_STATUS_CODE_CHANGE_RX_HOLD, group_id=constants.EXT_PACK_STATUS_GROUP_ID,
                          value="Hold Due To ChangeRx").execute()

        CodeMaster.insert(id=constants.EXT_PACK_USAGE_STATUS_NA_ID, group_id=constants.EXT_PACK_USAGE_STATUS_GROUP_ID,
                          value=constants.EXT_PACK_USAGE_STATUS_NA_DESC).execute()
        CodeMaster.insert(id=constants.EXT_PACK_USAGE_STATUS_PENDING_ID,
                          group_id=constants.EXT_PACK_USAGE_STATUS_GROUP_ID,
                          value=constants.EXT_PACK_USAGE_STATUS_PENDING_DESC).execute()
        CodeMaster.insert(id=constants.EXT_PACK_USAGE_STATUS_DONE_ID, group_id=constants.EXT_PACK_USAGE_STATUS_GROUP_ID,
                          value=constants.EXT_PACK_USAGE_STATUS_DONE_DESC).execute()

    print("ChangeRx Flow -- Insertion in Code Master completed.")


def add_tables():
    db.create_tables([ExtChangeRx, ExtChangeRxDetails, ExtChangeRxJson], safe=True)
    print("ChangeRx Flow -- New tables creation completed.")


def add_column(migrator):
    if ExtPackDetails.table_exists():
        migrate(
            migrator.add_column(ExtPackDetails._meta.db_table,
                                ExtPackDetails.ext_change_rx_id.db_column,
                                ExtPackDetails.ext_change_rx_id)
        )
        print("Added column in ExtPackDetails")

    if PackHeader.table_exists():
        migrate(
            migrator.add_column(PackHeader._meta.db_table,
                                PackHeader.change_rx_flag.db_column,
                                PackHeader.change_rx_flag)
        )
        print("Added column in PackHeader")

    if ExtPackDetails.table_exists():
        migrate(
            migrator.add_column(ExtPackDetails._meta.db_table,
                                ExtPackDetails.pack_usage_status_id.db_column,
                                ExtPackDetails.pack_usage_status_id)
        )
        print("Added pack_usage_status_id column in ExtPackDetails")


def update_data():
    if CodeMaster.table_exists():
        update_flag = CodeMaster.update(value=constants.EXT_CHANGE_RX_PACKS_DESC)\
            .where(CodeMaster.id == settings.PACK_STATUS_CHANGE_RX).execute()
    print("Updated value in Code Master table for ID: {}, New Value: {}"
          .format(settings.PACK_STATUS_CHANGE_RX, constants.EXT_CHANGE_RX_PACKS_DESC))


def migrate_new_update_data():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    print("Migration started for Change Rx feature.")

    # Insert Data into Group Master
    # Change Rx Actions for Group and Action Master
    add_data()

    # Create New tables for storing and processing data for Change Rx
    add_tables()

    # Add New column in ext_pack_details table
    add_column(migrator)

    # Update data in code_master table
    # update_data()
    # print("Migration completed for Change Rx feature.")


if __name__ == "__main__":
    migrate_new_update_data()
