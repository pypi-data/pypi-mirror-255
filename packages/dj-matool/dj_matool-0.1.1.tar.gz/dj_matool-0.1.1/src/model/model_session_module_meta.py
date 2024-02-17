from peewee import PrimaryKeyField, IntegerField, CharField, ForeignKeyField
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_session_module_master import SessionModuleMaster
from peewee import InternalError, IntegrityError, DataError

logger = settings.logger


class SessionModuleMeta(BaseModel):
    id = PrimaryKeyField()
    session_module_id = ForeignKeyField(SessionModuleMaster)
    task_name = CharField(max_length=100)
    time_per_unit = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "session_module_meta"

    @classmethod
    def get_session_module_meta_id(cls, session_module_id: int=None)-> int:
        """
        Returns session_meta_id for corresponding session_module_master_id
        @param session_module_id: int
        @return: int
        """
        try:
            logger.debug("In get_session_module_meta_id")
            query = cls.select().dicts().where(cls.session_module_id == session_module_id)
            for record in query:
                return record["id"]

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise
