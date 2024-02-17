from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from model.model_init import init_db
from playhouse.migrate import *
import settings
from peewee import fn


class CanisterTracker(BaseModel):
    id = PrimaryKeyField()
    refill_type = SmallIntegerField(null=True)
    quantity_adjusted = SmallIntegerField()
    original_quantity = SmallIntegerField()
    lot_number = CharField(max_length=30, null=True)
    expiration_date = CharField(max_length=8, null=True)
    note = CharField(null=True, max_length=100)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    created_time = TimeField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_tracker"


def migrate_23():
    init_db(db, 'database_migration')

    CanisterTracker.update(lot_number=None).where(CanisterTracker.lot_number == "").execute()
    CanisterTracker.update(expiration_date=None).where(CanisterTracker.expiration_date == "").execute()

    print("CanisterTracker data being updated")
    counter = 0
    query = CanisterTracker.select(CanisterTracker).dicts()\
        .where(fn.substr(fn.trim(CanisterTracker.expiration_date), 5, 1) == "-")
    for record in query:
        expiration_date = record["expiration_date"]
        year, month = expiration_date.split('-')
        update_date = "{}-{}".format(month, year)
        CanisterTracker.update(expiration_date=update_date).where(CanisterTracker.id == record["id"]).execute()
        counter += 1
        print(counter)
    print("CanisterTracker data updated")
