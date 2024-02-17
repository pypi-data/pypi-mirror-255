import logging

from peewee import PrimaryKeyField, ForeignKeyField, CharField, BooleanField, DateTimeField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_details import PackDetails
from src.model.model_device_master import DeviceMaster
from src.model.model_slot_header import SlotHeader

logger = logging.getLogger("root")


# This table has one row per slot per robot
class VisionDrugPrediction(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    device_id = ForeignKeyField(DeviceMaster)
    slot_header_id = ForeignKeyField(SlotHeader)
    image_filename = CharField(null=True)  # Image name generated with UUID # image generated for a slot
    image_uploaded = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "vision_drug_prediction"
