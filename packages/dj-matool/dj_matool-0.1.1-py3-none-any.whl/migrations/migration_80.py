from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class CodeMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class FileHeader(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    status = ForeignKeyField(CodeMaster)
    filename = CharField(max_length=150)
    filepath = CharField(null=True, max_length=200)
    manual_upload = BooleanField(null=True) # added - Amisha
    message = CharField(null=True, max_length=500)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField()
    created_time = TimeField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"


class PatientMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "patient_master"


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    status = ForeignKeyField(CodeMaster)
    is_modified = SmallIntegerField()
    delivery_datetime = DateTimeField(null=True, default=None)
    fill_manual = BooleanField(default=False)  # for marking packs manual generated from template
    task_id = CharField(max_length=155, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    reason = CharField(max_length=255, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"


class TemplateDetails(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader, null=True)
    # patient_rx_id = ForeignKeyField(PatientRx)
    column_number = SmallIntegerField()
    hoa_time = TimeField()
    quantity = DecimalField(decimal_places=2, max_digits=4)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_details"


def migrate_80():

    init_db(db, 'database_migration')

    migrator = MySQLMigrator(db)
    migrate(migrator.add_column(
        TemplateDetails._meta.db_table,
        TemplateDetails.file_id.db_column,
        TemplateDetails.file_id
    ))
    print('Table Modified: TemplateDetails')
    with db.transaction():
        update_query = """UPDATE template_details td JOIN (SELECT tm.patient_id_id AS patient_id, MAX(tm.file_id_id) 
                          AS max_file_id FROM template_master tm GROUP BY tm.patient_id_id) AS k ON k.patient_id = 
                          td.patient_id_id SET td.file_id_id = k.max_file_id"""
        result = db.execute_sql(update_query)
        print('Rows updated with file_id ', result)

        deleted_td = TemplateDetails.delete().where(TemplateDetails.file_id.is_null(True)).execute()

        print('TemplateDetails data deleted', deleted_td)

    migrate(
        migrator.add_not_null(TemplateDetails._meta.db_table, TemplateDetails.file_id.db_column)
    )
    print('Table Modified: TemplateDetails')


if __name__ == '__main__':
    migrate_80()