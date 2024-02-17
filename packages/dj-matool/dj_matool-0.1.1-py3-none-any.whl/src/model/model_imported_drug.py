from peewee import PrimaryKeyField, CharField, ForeignKeyField, DateTimeField, IntegerField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_file_header import FileHeader
from src.model.model_batch_drug_data import BatchDrugData


class ImportedDrug(BaseModel):
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14)
    formatted_ndc = CharField(max_length=12, null=True)
    strength = CharField(max_length=50, null=True)
    strength_value = CharField(max_length=16, null=True)
    manufacturer = CharField(null=True, max_length=100)
    txr = CharField(max_length=8, null=True)
    imprint = CharField(null=True, max_length=82)
    color = CharField(null=True, max_length=30)
    shape = CharField(null=True, max_length=30)
    image_name = CharField(null=True, max_length=255)
    brand_flag = CharField(null=True, max_length=1)
    brand_drug = CharField(null=True, max_length=50)
    drug_form = CharField(null=True, max_length=15)
    file_id = ForeignKeyField(FileHeader, null=True)
    source = CharField(max_length=500, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(null=True)
    batch_drug_data_id = ForeignKeyField(BatchDrugData, null=True, related_name="batch_drug_data_id")

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "imported_drug"