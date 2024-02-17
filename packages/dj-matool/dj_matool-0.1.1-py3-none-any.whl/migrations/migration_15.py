from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()
    system_id = IntegerField()
    # patient_id = ForeignKeyField(PatientMaster)
    # file_id = ForeignKeyField(FileHeader)
    # status = ForeignKeyField(CodeMaster)
    is_modified = BooleanField()
    delivery_datetime = DateTimeField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


class PackHeader(BaseModel):
    id = PrimaryKeyField()
    # patient_id = ForeignKeyField(PatientMaster)
    # file_id = ForeignKeyField(FileHeader)
    total_packs = SmallIntegerField()
    start_day = SmallIntegerField()
    pharmacy_fill_id = IntegerField()
    delivery_datetime = DateTimeField(null=True, default=None)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_header"


def migrate_15():
    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)

    if TemplateMaster.table_exists():
        migrate(migrator.add_column(TemplateMaster._meta.db_table,
                                    TemplateMaster.delivery_datetime.db_column,
                                    TemplateMaster.delivery_datetime)
                )
        print("Table Modified: TemplateMaster")
    if PackHeader.table_exists():
        migrate(migrator.add_column(PackHeader._meta.db_table,
                                    PackHeader.delivery_datetime.db_column,
                                    PackHeader.delivery_datetime)
                )
        print("Table Modified: PackHeader")
