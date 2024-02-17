from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateTimeField, IntegrityError, InternalError, \
    DataError, DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_canister_master import CanisterMaster
from src.model.model_location_master import LocationMaster


class CanisterHistory(BaseModel):
    """
        @class: canister_history.py
        @createdBy: Manish Agarwal
        @createdDate: 04/19/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/19/2016
        @type: file
        @desc: logical class for table canister_history
                stores the canister history
    """
    id = PrimaryKeyField()
    canister_id = ForeignKeyField(CanisterMaster)
    current_location_id = ForeignKeyField(LocationMaster, null=True, related_name='current_location_id')
    previous_location_id = ForeignKeyField(LocationMaster, null=True, related_name='previous_location_id')
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "canister_history"

    @classmethod
    def update_canister_history(cls, dict_canister_info, canister_id):
        try:
            status = CanisterHistory.update(**dict_canister_info).where(CanisterHistory.canister_id == canister_id)
            status = status.execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            raise e

    @classmethod
    def db_get_latest_record_by_canister_id(cls, canister_id):
        try:
            record = CanisterHistory.select().where(CanisterHistory.canister_id == canister_id).order_by(
                cls.id.desc()).get()
            return record
        except (IntegrityError, InternalError, DataError) as e:
            raise e
        except DoesNotExist as e:
            return None

    @classmethod
    def update_canister_history_by_id(cls, dict_canister_info, canister_history_id):
        try:
            status = CanisterHistory.update(**dict_canister_info).where(
                CanisterHistory.id == canister_history_id).execute()
            return status
        except (IntegrityError, InternalError, DataError) as e:
            raise e

    @classmethod
    def db_canister_history_create_multi_record(cls, canister_history_list):
        try:
            cls.db_create_multi_record(canister_history_list, CanisterHistory)
        except (IntegrityError, InternalError, DataError, Exception) as e:
            raise InternalError(e)
