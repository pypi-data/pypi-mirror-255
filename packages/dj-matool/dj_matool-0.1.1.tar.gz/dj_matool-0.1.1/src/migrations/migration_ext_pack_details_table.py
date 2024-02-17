from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel, db
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src import constants


class PackDetails(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    value = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class ActionMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "action_master"


class ExtPackDetails(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, null=True)
    template_id = ForeignKeyField(TemplateMaster, null=True)
    status_id = ForeignKeyField(CodeMaster, null=True)
    ext_pack_display_id = IntegerField()
    ext_status_id = ForeignKeyField(CodeMaster, related_name='ext_status')
    ext_comment = CharField(null=True)
    ext_company_id = IntegerField()
    ext_user_id = IntegerField()
    ext_created_date = DateTimeField(default=get_current_date_time())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ext_pack_details"


def create_table():
    try:
        if ExtPackDetails.table_exists():
            db.drop_tables([ExtPackDetails])
        db.create_tables([ExtPackDetails], safe=True)
        print('migrate_ext_pack_details: Table Created: ExtPackDetails')
    except Exception as e:
        print("migrate_ext_pack_details: Error while creating table- ext_pack_details: " + str(e))


def add_codes():
    try:
        GroupMaster.insert(id=constants.EXT_PACK_STATUS_GROUP_ID, name="ExtPackStatus").execute()
        CodeMaster.insert(id=constants.EXT_PACK_STATUS_CODE_DELETED, value="Deleted",
                          group_id=constants.EXT_PACK_STATUS_GROUP_ID).execute()
        ActionMaster.insert(id=settings.PACK_HISTORY_STATUS_CHANGE_FROM_IPS, group_id=1,
                            value="Status change from IPS").execute()
        print("migrate_ext_pack_details: code added in code master and group master and action master")
    except Exception as e:
        print("migrate_ext_pack_details: Error while adding codes in tables code_master and group_master: " + str(e))


def migrate_ext_pack_details():
    init_db(db, 'database_migration')
    create_table()
    add_codes()


if __name__ == "__main__":
    migrate_ext_pack_details()
