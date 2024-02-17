from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings


class PackFillErrorDetails(BaseModel):
    id = PrimaryKeyField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_fill_error_details"


class SlotFillErrorDetail(BaseModel):
    id = PrimaryKeyField()
    pack_fill_error_details_id = ForeignKeyField(PackFillErrorDetails)
    slot_row = SmallIntegerField()
    slot_column = SmallIntegerField()
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error_details"


def migrate_20():
    init_db(db, 'database_migration')

    db.create_tables([SlotFillErrorDetail], safe=True)
    print("Table created: SlotFillErrorDetails")
