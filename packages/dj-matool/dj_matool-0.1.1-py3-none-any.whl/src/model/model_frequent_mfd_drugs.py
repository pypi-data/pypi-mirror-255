from peewee import IntegerField, ForeignKeyField, PrimaryKeyField, DateTimeField, DecimalField, TextField

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_code_master import CodeMaster
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger


class FrequentMfdDrugs(BaseModel):

    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    quantity = DecimalField(decimal_places=2)
    required_canister = IntegerField(default=1)
    batch_id = IntegerField(default=1)
    status = ForeignKeyField(CodeMaster)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    current_pack_queue = IntegerField(null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "frequent_mfd_drugs"

