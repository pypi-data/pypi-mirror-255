from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from src.model.model_group_master import GroupMaster
from playhouse.migrate import *
import settings


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(null=True)
    status = ForeignKeyField(CodeMaster, null=True)
    split_function_id = IntegerField(default=0, null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    imported_date = DateTimeField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


def migrate_72():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_column(
            BatchMaster._meta.db_table,
            BatchMaster.imported_date.db_column,
            BatchMaster.imported_date
        ))
    print("Table Modified: BATCH MASTER")


if __name__ == "__main__":
    migrate_72()
