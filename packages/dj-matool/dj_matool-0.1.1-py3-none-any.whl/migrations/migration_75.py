from playhouse.migrate import *
import settings
from model.model_init import init_db
from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time


class PackDetails(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_details"


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_master"


class BatchManualPacks(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    batch_id = ForeignKeyField(BatchMaster)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_manual_packs"


def migrate_75():
    init_db(db, "database_migration")

    print("creating table BatchManualPacks")
    db.create_tables([BatchManualPacks], safe=True)
    print('Table(s) Created: BatchManualPacks')


if __name__ == "__main__":
    migrate_75()
