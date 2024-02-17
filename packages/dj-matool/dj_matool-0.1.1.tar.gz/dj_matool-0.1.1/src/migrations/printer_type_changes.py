from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from dosepack.utilities.utils import get_current_date, get_current_time
from model.model_init import init_db


class GroupMaster(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "group_master"


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"


class Printers(BaseModel):
    """
        @class:
        @createdBy: Jitendra Saxena
        @createdDate: 01/08/2018
        @lastModifiedBy:
        @lastModifiedDate:
        @type: file
        @desc: stores the printers associated with a given system.
    """
    id = PrimaryKeyField()
    printer_name = CharField(max_length=50)
    # printer_type_id = SmallIntegerField(null=True, default=None)  # 1 = CRM, 2 = User Station
    printer_type_id = ForeignKeyField(CodeMaster)
    unique_code = CharField(max_length=55, unique=True)
    ip_address = CharField()
    system_id = IntegerField()
    added_date = DateField(default=get_current_date)
    added_time = TimeField(default=get_current_time)
    print_count = IntegerField(default=0)


def printer_type_changes():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)
    printer_type_code_and_group_insertion()
    printer_type_column_constraint_addition(migrator)
    update_values_in_printers_table()


def printer_type_code_and_group_insertion():
    if GroupMaster.table_exists():
        GroupMaster.insert(id=35, name='PrinterType').execute()
    if CodeMaster.table_exists():
        CodeMaster.insert(id=141, group_id=35, value='CRM').execute()
        CodeMaster.insert(id=142, group_id=35, value='User Station').execute()
    print("Insertion in Group Master and Code Master completed.")


def printer_type_column_constraint_addition(migrator):
    if Printers.table_exists():
        try:
            db.execute_sql("ALTER TABLE printers CHANGE printer_type printer_type_id_id INT;")
            migrate(
                migrator.add_foreign_key_constraint(Printers._meta.db_table, Printers.printer_type_id.db_column,
                                                    CodeMaster._meta.db_table, CodeMaster.id.db_column)
            )
            print("constraint addition successful.")
        except Exception as e:
            print(e)
            print("Could not add constraint to Printers.")


def update_values_in_printers_table():
    Printers.update(printer_type_id=Printers.printer_type_id + 140).where(Printers.id.is_null(False)).execute()
    print("Values updation successful.")


if __name__ == "__main__":
    printer_type_changes()
