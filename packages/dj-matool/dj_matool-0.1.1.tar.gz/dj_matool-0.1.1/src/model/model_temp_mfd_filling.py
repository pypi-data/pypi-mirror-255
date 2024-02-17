from peewee import (ForeignKeyField, DateTimeField, PrimaryKeyField, InternalError, IntegrityError, BooleanField)
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from src.model.model_batch_master import BatchMaster
from src.model.model_mfd_analysis import MfdAnalysis
from src.model.model_device_master import DeviceMaster
logger = settings.logger


class TempMfdFilling(BaseModel):
    id = PrimaryKeyField()
    batch_id = ForeignKeyField(BatchMaster)
    mfd_analysis_id = ForeignKeyField(MfdAnalysis, null=True, unique=True)
    mfs_device_id = ForeignKeyField(DeviceMaster, null=True)
    transfer_done = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "temp_mfd_filling"

    @classmethod
    def db_delete_current_filling(cls, mfs_id: int) -> int:
        """
        deletes current canister info of particular mfs_id
        :param mfs_id:
        :return:
        """
        try:
            status = cls.delete() \
                .where(cls.mfs_device_id == mfs_id).execute()
            logger.info("mfd_filling_done_for_canisters: " + str(status) + ' for mfs_id: ' + str(mfs_id))
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_canister_transfer_status(cls, analysis_ids: list, status: bool) -> int:
        """
        updates transfer status(transfer to trolley) for given analysis_ids
        :param analysis_ids: list
        :param status: int
        :return: int
        """
        try:
            update_status = cls.update(transfer_done=status,
                                       modified_date=get_current_date_time()) \
                .where(cls.mfd_analysis_id << analysis_ids).execute()
            logger.info("mfd_can_status_changed_to: " + str(status) + ' for analysis_id: ' + str(analysis_ids) +
                        ' with update status: ' + str(update_status))
            return update_status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
