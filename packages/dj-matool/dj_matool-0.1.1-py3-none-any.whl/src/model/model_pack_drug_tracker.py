import settings
from peewee import ForeignKeyField, PrimaryKeyField, IntegerField, TextField, DateTimeField, IntegrityError, \
    InternalError, DataError
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_drug_master import DrugMaster
from src.model.model_slot_details import SlotDetails

logger = settings.logger


class PackDrugTracker(BaseModel):
    id = PrimaryKeyField()
    slot_details_id = ForeignKeyField(SlotDetails)
    previous_drug_id = ForeignKeyField(DrugMaster)
    updated_drug_id = ForeignKeyField(DrugMaster, related_name="updated_drug_id_id")
    module = IntegerField()
    reason = TextField(null=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_drug_tracker"

    @classmethod
    def db_insert_pack_drug_tracker_data(cls, pack_drug_tracker_details):
        """
        insert pack_drug_tracker data to table
        :return:
        """
        try:
            status = cls.insert_many(pack_drug_tracker_details).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
            raise

