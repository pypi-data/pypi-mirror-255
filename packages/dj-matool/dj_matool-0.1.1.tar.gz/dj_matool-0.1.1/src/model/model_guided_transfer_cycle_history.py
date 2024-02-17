from playhouse.migrate import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster
from src.model.model_guided_tracker import GuidedTracker
from src.model.model_canister_master import CanisterMaster

logger = settings.logger


class GuidedTransferCycleHistory(BaseModel):
    id = PrimaryKeyField()
    guided_tracker_id = ForeignKeyField(GuidedTracker)
    canister_id = ForeignKeyField(CanisterMaster)
    action_id = ForeignKeyField(ActionMaster)
    current_status_id = ForeignKeyField(CodeMaster, related_name='current_status_id')
    previous_status_id = ForeignKeyField(CodeMaster, related_name='previous_state_id')
    action_taken_by = IntegerField(null=False)
    action_datetime = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_transfer_cycle_history"

    @classmethod
    def insert_guided_transfer_cycle_history_data(cls, data_dict: dict):
        """
        This function inserts multiple records to the canister_transfer_cycle_history table.
        @param data_dict:
        @return:
        """
        logger.info("Input of insert_canister_transfer_cycle_history_data {}".format(data_dict))
        try:
            record = cls.create(**data_dict)
            return record
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e)
            raise

    @classmethod
    def add_multiple_guided_transfer_cycle_history_data(cls, insert_data: list):
        """
        This function inserts multiple records to the canister_transfer_cycle_history table.
        @param insert_data:
        @return:
        """
        logger.info("Input of insert_canister_transfer_cycle_history_data {}".format(insert_data))
        try:
            cls.db_create_multi_record(insert_data, cls)
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e)
            raise
