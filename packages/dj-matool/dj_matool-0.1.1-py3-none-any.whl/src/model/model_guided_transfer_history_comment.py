import logging

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_guided_transfer_cycle_history import GuidedTransferCycleHistory

logger = logging.getLogger("root")


class GuidedTransferHistoryComment(BaseModel):
    id = PrimaryKeyField()
    guided_transfer_history_id = ForeignKeyField(GuidedTransferCycleHistory)
    comment = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "guided_transfer_history_comment"

    @classmethod
    def insert_guided_transfer_history_comment_data(cls, data_dict: dict):
        """
        This function inserts multiple records to the canister_transfer_history_comment table.
        @param data_dict:
        @return:
        """
        logger.debug("Inside insert_canister_transfer_history_comment_data.")

        try:
            record = cls.create(**data_dict)
            return record
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e)
            raise
