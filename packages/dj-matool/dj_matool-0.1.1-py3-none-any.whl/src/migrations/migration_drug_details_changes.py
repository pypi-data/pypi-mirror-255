from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db


class DrugMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class UniqueDrug(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "unique_drug"


class OldDrugDetails(BaseModel):
    id = PrimaryKeyField()
    drug_master_id = ForeignKeyField(DrugMaster, unique=True)
    last_seen_by = IntegerField()
    last_seen_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_details"


class NewDrugDetails(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    last_seen_by = IntegerField()
    last_seen_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_details"


def migration_alter_drug_details():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    if OldDrugDetails.table_exists():
        db.drop_tables([OldDrugDetails])
        db.create_tables([NewDrugDetails])
    print("Table modified: DrugDetails")