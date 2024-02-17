from peewee import (IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, IntegrityError, InternalError, fn)

import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from src.model.model_action_master import ActionMaster
from src.model.model_code_master import CodeMaster
from src.model.model_mfd_analysis import (MfdAnalysis)
logger = settings.logger


class MfdCycleHistory(BaseModel):
    id = PrimaryKeyField()
    analysis_id = ForeignKeyField(MfdAnalysis)
    action_id = ForeignKeyField(ActionMaster)
    current_status_id = ForeignKeyField(CodeMaster, related_name='current_mfd_status')
    previous_status_id = ForeignKeyField(CodeMaster, related_name='previous_mfd_status')
    action_taken_by = IntegerField()
    action_date_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "mfd_cycle_history"

    @classmethod
    def db_get_max_history_id(cls, analysis_ids: list) -> dict:
        """
        to obtain the last history id for given analysis_ids
        :param analysis_ids: list
        :return:
        """
        try:
            query = cls.select(fn.MAX(cls.id).alias('max_history_id'),
                               cls.analysis_id) \
                .where(cls.analysis_id << analysis_ids).group_by(cls.analysis_id)

            return query.dicts()

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_add_history_data(cls, history_list: list) -> int:
        """
        adds history data in mfd_cycle_history
        :param history_list: list
        :return: int
        """
        try:
            update_status = cls.insert_many(history_list).execute()
            logger.debug('history_data_added_with_status: {}'.format(update_status))
            return update_status

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
