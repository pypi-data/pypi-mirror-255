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


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    # patient_id = ForeignKeyField(PatientMaster)
    # file_id = ForeignKeyField(FileHeader)
    # status = ForeignKeyField(CodeMaster)
    is_modified = SmallIntegerField()
    delivery_datetime = DateTimeField(null=True, default=None)
    fill_manual = BooleanField(default=False)  # for marking packs manual generated from template
    task_id = CharField(max_length=155, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


def migrate_77():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if TemplateMaster.table_exists():
        migrate(
            migrator.add_column(
                TemplateMaster._meta.db_table,
                TemplateMaster.task_id.db_column,
                TemplateMaster.task_id
            )
        )

    print("Table Modified: TemplateMaster")

    CodeMaster.create(**{'id': settings.PROGRESS_TEMPLATE_STATUS,
                         'key': settings.PROGRESS_TEMPLATE_STATUS,
                         'value': 'In Progress',
                         'group_id': settings.GROUP_MASTER_TEMPLATE})

    print("Table modified: CodeMaster")


if __name__ == "__main__":
    migrate_77()
