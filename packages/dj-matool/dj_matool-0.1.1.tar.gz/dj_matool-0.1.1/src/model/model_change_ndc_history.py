from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_master import CanisterMaster
from src.model.model_drug_master import DrugMaster

logger = settings.logger


class ChangeNdcHistory(BaseModel):
    id = PrimaryKeyField()
    old_drug_id = ForeignKeyField(DrugMaster, related_name="old_drug_id")
    old_canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="old_canister_id")
    new_drug_id = ForeignKeyField(DrugMaster, related_name="new_drug_id")
    new_canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="new_caniter_id")
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "change_ndc_history"

