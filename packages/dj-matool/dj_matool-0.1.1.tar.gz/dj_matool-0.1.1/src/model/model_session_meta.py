from peewee import PrimaryKeyField, CharField, ForeignKeyField, \
    InternalError, IntegrityError, DataError
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_session import Session
from src.model.model_session_module_meta import SessionModuleMeta

logger = settings.logger


class SessionMeta(BaseModel):
    id = PrimaryKeyField()
    session_id = ForeignKeyField(Session)
    session_module_meta_id = ForeignKeyField(SessionModuleMeta)
    value = CharField(max_length=100)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "session_meta"

    @classmethod
    def insert_session_meta_data(cls, session_id: int = None, session_module_meta_id: int = None,
                                 value: str = None) -> dict:
        """
        This function is to insert data within session_meta table.
        @param session_id: int
        @param session_module_meta_id:int
        @param value: varchar
        @return: success
        """
        try:
            logger.debug("In insert_session_meta_data")
            query = SessionMeta.insert(session_id=session_id, session_module_meta_id=session_module_meta_id,
                                       value=value).execute()
            return query
        except (IntegrityError, InternalError, DataError) as e:
            logger.error(e, exc_info=True)
            raise