from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
import settings
import logging

logger = logging.getLogger("root")


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


def migrate_55():
    init_db(db, "database_migration")
    with db.transaction():
        partial_fill_dict = {
            'id': 51,
            'key': 51,
            'group_id': 1,
            'value': 'Filled Partially'
        }
        try:
            CodeMaster.insert(**partial_fill_dict).execute()
            record, created = CodeMaster.get_or_create(id=50, defaults=dict(key=50, group_id=1, value='Fill Manually'))
            if not created:
                CodeMaster.update(value='Fill Manually').where(CodeMaster.id == record.id).execute()
            print('Table(s) Updated: CodeMaster')
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)


if __name__ == '__main__':
    migrate_55()
