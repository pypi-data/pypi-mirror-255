from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings


class LocationMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "location_master"

        indexes = (
            (('device_id', 'location_number'), True),
        )


class DrugMaster(BaseModel):
   id = PrimaryKeyField()

   class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class CanisterMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_master"


class CanisterHistory(BaseModel):
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    current_location_id = ForeignKeyField(LocationMaster, null=True, related_name='current_location_id')
    previous_location_id = ForeignKeyField(LocationMaster, null=True, related_name='previous_location_id')
    action = CharField(max_length=50)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField(null=True)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_history"


def migrate_canister_history():
    init_db(db, 'database_migration')
    add_columns()
    update_modified_by()
    drop_null_in_modified_by()


def add_columns():
    migrator = MySQLMigrator(db)
    try:
        with db.transaction():
            if CanisterHistory.table_exists():
                migrate(
                    migrator.add_column(CanisterHistory._meta.db_table,
                                        CanisterHistory.modified_by.db_column,
                                        CanisterHistory.modified_by),
                    migrator.add_column(CanisterHistory._meta.db_table,
                                        CanisterHistory.modified_date.db_column,
                                        CanisterHistory.modified_date)
                )
    except Exception as e:
        raise Exception("Exception generates while adding column in canister_history: ", e)


def update_modified_by():
    try:
        if CanisterHistory.table_exists():
            sql = 'UPDATE `canister_history` SET `modified_by`=`created_by`;'
            db.execute_sql(sql)
    except Exception as e:
        raise Exception("Exception generates while updating values in modified_by in canister_history: ", e)


def drop_null_in_modified_by():
    try:
        if CanisterHistory.table_exists():
            sql = 'ALTER TABLE canister_history MODIFY modified_by INT(11) NOT NULL;'
            db.execute_sql(sql)
    except Exception as e:
        raise Exception("Exception generates while altering column modified_by as not null in canister_history: ", e)


if __name__ == '__main__':
    migrate_canister_history()
    print("column modified_by and modified_date added successfully in canister_history")