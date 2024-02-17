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


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    name = CharField(null=True)
    status = ForeignKeyField(CodeMaster, null=True)
    created_date = DateTimeField(default=get_current_date_time, null=True)
    modified_date = DateTimeField(default=get_current_date_time, null=True)
    created_by = IntegerField()
    modified_by = IntegerField(null=True)
    split_function_id = IntegerField(null=True)
    scheduled_start_time = DateTimeField(default=get_current_date_time(), null=True)
    estimated_processing_time = FloatField(null=True)
    imported_date = DateTimeField(null=True)
    mfd_status = ForeignKeyField(CodeMaster, null=True, related_name='mfd_status')

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


def migrate_batch_mfd():

    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    migrate(
        migrator.add_column(
            BatchMaster._meta.db_table,
            BatchMaster.mfd_status.db_column,
            BatchMaster.mfd_status
        )
    )

    print('Table(s) modified: BatchMaster')

    GROUP_MASTER_DATA = [
        dict(id=src.constants.GROUP_MASTER_BATCH_MFD, name='Mfd Batch')
    ]

    CODE_MASTER_DATA = [
        dict(id=src.constants.MFD_BATCH_PENDING, group_id=src.constants.GROUP_MASTER_BATCH_MFD,
             key=src.constants.MFD_BATCH_PENDING, value="Pending"),
        dict(id=src.constants.MFD_BATCH_IN_PROGRESS, group_id=src.constants.GROUP_MASTER_BATCH_MFD,
             key=src.constants.MFD_BATCH_IN_PROGRESS, value="In Progress"),
        dict(id=src.constants.MFD_BATCH_FILLED, group_id=src.constants.GROUP_MASTER_BATCH_MFD,
             key=src.constants.MFD_BATCH_FILLED, value="Filled"),
    ]

    GroupMaster.insert_many(GROUP_MASTER_DATA).execute()

    CodeMaster.insert_many(CODE_MASTER_DATA).execute()

    print("Table modified: GroupMaster, CodeMaster")



if __name__ == "__main__":
    migrate_batch_mfd()
