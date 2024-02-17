import src.constants
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


def migrate_mfd_rts_actions():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        ACTION_MASTER_DATA = [
            dict(id=settings.DELETE_PACK_ACTION, group_id=settings.GROUP_MASTER_PACK,
                 value="Pack Deleted"),
            dict(id=settings.MANUAL_PACK_ACTION, group_id=settings.GROUP_MASTER_PACK,
                 value="Pack Marked as Manual"),
        ]

        ActionMaster.insert_many(ACTION_MASTER_DATA).execute()

    except Exception as e:
        print(e)
        print('failed')


if __name__ == "__main__":
    migrate_mfd_rts_actions()
