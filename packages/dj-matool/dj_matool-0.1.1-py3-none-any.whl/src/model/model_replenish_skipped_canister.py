import settings
from dosepack.base_model.base_model import BaseModel
from peewee import PrimaryKeyField, ForeignKeyField, DateTimeField, SmallIntegerField

from dosepack.utilities.utils import get_current_date_time
from src.model.model_device_master import DeviceMaster
from src.model.model_pack_details import PackDetails
from src.model.model_canister_master import CanisterMaster


class ReplenishSkippedCanister(BaseModel):

    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    canister_id = ForeignKeyField(CanisterMaster)
    device_id = ForeignKeyField(DeviceMaster, null=True)
    location_number = SmallIntegerField(null=True)
    quadrant = SmallIntegerField(null=True)
    created_at = DateTimeField(default=get_current_date_time)

    class Meta:

        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'replenish_skipped_canister'

