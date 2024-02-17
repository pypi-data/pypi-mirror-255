from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class BatchMaster(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        db_table = 'batch_master'


class BatchHash(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    batch_hash = CharField()  # hash of sorted pack ids separated by ,
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_hash"


def migrate_12():
    init_db(db, 'database_migration')
    db.create_tables([BatchHash], safe=True)
    print('Table(s) created: BatchHash')

