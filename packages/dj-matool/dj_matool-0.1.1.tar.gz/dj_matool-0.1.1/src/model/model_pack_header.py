from peewee import IntegerField, ForeignKeyField, DateTimeField, \
    PrimaryKeyField, SmallIntegerField, BooleanField
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

from src.model.model_patient_master import PatientMaster
from src.model.model_file_header import FileHeader


class PackHeader(BaseModel):
    id = PrimaryKeyField()
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    total_packs = SmallIntegerField()
    start_day = SmallIntegerField()
    pharmacy_fill_id = IntegerField()
    delivery_datetime = DateTimeField(null=True, default=None)
    scheduled_delivery_date = DateTimeField(null=True, default=None)  # delivery_date from the facility schedule
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    change_rx_flag = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_header"
