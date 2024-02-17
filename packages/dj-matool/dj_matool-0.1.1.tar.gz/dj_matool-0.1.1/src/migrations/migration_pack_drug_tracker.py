from dosepack.base_model.base_model import db, BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_drug_master import DrugMaster
from model.model_init import init_db
from playhouse.migrate import *
import settings
from src.model.model_slot_details import SlotDetails


class PackDrugTracker(BaseModel):
    id = PrimaryKeyField()
    slot_details_id = ForeignKeyField(SlotDetails, related_name="slot_details_id")
    previous_drug_id = ForeignKeyField(DrugMaster, related_name="previous_drug_id")
    updated_drug_id = ForeignKeyField(DrugMaster, related_name="updated_drug_id")
    module = IntegerField()
    reason = TextField(null=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_drug_tracker"


def migration_pack_drug_tracker():
    init_db(db, 'database_migration')

    try:
        if PackDrugTracker.table_exists():
            db.drop_tables([PackDrugTracker])
        db.create_tables([PackDrugTracker], safe=True)
        print('Table(s) created: PackDrugTracker')
    except Exception as e:
        print("Error in creating table")
        raise
