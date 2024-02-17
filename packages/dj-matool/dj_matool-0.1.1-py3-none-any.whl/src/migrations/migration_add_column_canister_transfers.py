from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'group_master'


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'code_master'


class LocationMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class DeviceMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "device_master"


class CanisterTxMeta(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    cycle_id = IntegerField()
    device_id = ForeignKeyField(DeviceMaster)
    status_id = ForeignKeyField(CodeMaster)
    to_cart_transfer_count = IntegerField()
    from_cart_transfer_count = IntegerField()
    normal_cart_count = IntegerField()
    elevator_cart_count = IntegerField()
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tx_meta"


class CanisterTransfers(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    canister_id = ForeignKeyField(CanisterMaster)
    dest_device_id = ForeignKeyField(DeviceMaster, null=True)
    dest_location_number = SmallIntegerField(null=True)
    dest_quadrant = SmallIntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    trolley_loc_id = ForeignKeyField(LocationMaster, null=True)
    to_ct_meta_id = ForeignKeyField(CanisterTxMeta, null=True, related_name="to_cart_meta_id")
    from_ct_meta_id = ForeignKeyField(CanisterTxMeta, null=True, related_name="from_cart_meta_id")
    transfer_status = ForeignKeyField(CodeMaster, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_transfers"


def add_column_canister_transfer():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:

        if GroupMaster.table_exists():
            GroupMaster.insert(id=constants.CANISTER_TX_STATUS_GROUP_ID, name="CanisterTxStatus").execute()

        print("Added codes in GroupMaster")

        if CodeMaster.table_exists():
            # codes for guided tracker
            CodeMaster.insert(id=constants.CANISTER_TRANSFER_TO_CSR_DONE,
                              group_id=constants.CANISTER_TRANSFER_GROUP_ID,
                              value="Canister Transfer To CSR Done").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_PENDING,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx Pending").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_TROLLEY_DONE,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Trolley Done").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_TROLLEY_TRANSFERRED_MANUALLY,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Trolley Transferred Manually").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_TROLLEY_SKIPPED,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Trolley Skipped").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_TROLLEY_SKIPPED_AND_ALTERNATE,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Trolley SKipped and Alternate").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_TROLLEY_ALTERNATE,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Trolley Alternate").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_TROLLEY_ALTERNATE_TRANSFER_LATER,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Trolley Alternate Transfer Later").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_ROBOT_DONE,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Robot Done").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_ROBOT_SKIPPED,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Robot Skipped").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_ROBOT_SKIPPED_AND_ALTERNATE,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Robot Skipped and Alternate").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_ROBOT_ALTERNATE,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Robot Alternate").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_LATER,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Robot Alternate Transfer Later").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_CSR_DONE,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To CSR Done").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_CSR_SKIPPED,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To CSR Skipped").execute()
            CodeMaster.insert(id=constants.CANISTER_TX_TO_ROBOT_ALTERNATE_TRANSFER_AT_PPP,
                              group_id=constants.CANISTER_TX_STATUS_GROUP_ID,
                              value="Canister Tx To Robot Alternate Transfer at PPP").execute()

            print("Added codes in Code Master")
            CodeMaster.update(value="Canister Transfer To Robot Done").where(CodeMaster.id == constants.CANISTER_TRANSFER_TO_ROBOT_DONE)

        if CanisterTransfers.table_exists():
            migrate(
                migrator.add_column(CanisterTransfers._meta.db_table,
                                    CanisterTransfers.transfer_status.db_column,
                                    CanisterTransfers.transfer_status)
            )
            print("Added column in CanisterTransfer")

        if ActionMaster.table_exists():
            ActionMaster.create(id=23, group_id=constants.CANISTER_TX_STATUS_GROUP_ID, value="Canister Transfer")
            ActionMaster.create(id=24, group_id=constants.CANISTER_TX_STATUS_GROUP_ID, value="Canister Skipped")
            ActionMaster.create(id=25, group_id=constants.CANISTER_TX_STATUS_GROUP_ID, value="Canister Skipped and Deactivated")

            print("Data inserted in the Action Master table.")

    except Exception as e:
        settings.logger.error("Error while adding columns and data in Canister Transfers: ", str(e))


if __name__ == "__main__":
    add_column_canister_transfer()
