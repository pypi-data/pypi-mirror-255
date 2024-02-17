from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, SmallIntegerField, BooleanField, DateTimeField, \
    TextField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_unique_drug import UniqueDrug


class DrugStockHistory(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    company_id = IntegerField()
    is_in_stock = SmallIntegerField(null=True)
    is_active = BooleanField(default=True)
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    reason = TextField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_stock_history"


