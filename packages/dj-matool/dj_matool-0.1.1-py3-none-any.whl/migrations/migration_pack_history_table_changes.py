import logging

from peewee import *

import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_pack_details import PackDetails

# get the logger for the pack from global configuration file logging.json
logger = logging.getLogger("root")


class GroupMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class PackHistory(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_history"


class PackHistoryDetails(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_history_details"


class NewPackHistory(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    action_id = ForeignKeyField(ActionMaster)
    action_taken_by = IntegerField()
    action_date_time = DateTimeField(default=get_current_date_time)
    old_value = CharField(null=True)
    new_value = CharField(null=True)
    from_ips = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_history"


def pack_history_table_changes():
    """
    To create new PackHistoryDetail table and updating ActionMaster with new Actions
    @return: Success Message
    """
    init_db(db, "database_migration")
    if ActionMaster.table_exists():
        ActionMaster.create(group_id=1, key=21, value="Pack reassigned")
        print("Data inserted in the Action Master table.")

    if PackHistoryDetails.table_exists():
        db.drop_tables([PackHistoryDetails])
        print("Table dropped: PackHistoryDetails")

    if PackHistory.table_exists():
        db.drop_tables([PackHistory])
        print("Table dropped: PackHistory")

    db.create_tables([NewPackHistory], safe=True)
    print("Table created:PackHistory")


if __name__ == '__main__':
    pack_history_table_changes()
