from peewee import IntegerField, ForeignKeyField, DateTimeField, \
    PrimaryKeyField, SmallIntegerField
import settings
from dosepack.base_model.base_model import BaseModel, db
from src.model.model_pack_details import PackDetails
from peewee import PrimaryKeyField, CharField, ForeignKeyField, BooleanField, fn, DoesNotExist, InternalError, \
    IntegrityError, DataError
logger = settings.logger


class PackQueue(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, index=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_queue"

    @classmethod
    def insert_pack_ids(cls, pack_id_list):
        try:
            with db.transaction():
                for pack_id in pack_id_list:
                    pack_data = {"pack_id": pack_id}
                    status = PackQueue.insert(pack_data).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def remove_pack_from_pack_queue(cls, ids):
        try:
            with db.transaction():
                status = PackQueue.delete().where(PackQueue.id << ids).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def count_packs_in_queue(cls):
        try:
            count = PackQueue.select(fn.COUNT(PackQueue.id))
            return count.scalar()

        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_pack_ids_pack_queue(cls):
        try:
            pack_id_list = list()
            pack_ids = PackQueue.select(PackQueue.pack_id).dicts()
            for pack_id in pack_ids:
                pack_id_list.append(pack_id['pack_id'])
            return pack_id_list

        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def packs_in_pack_queue_or_not(cls, pack_ids):
        try:
            if pack_ids:
                count_query = PackQueue.select().dicts() \
                        .where(PackQueue.pack_id.in_(pack_ids)).count()

                if count_query == len(pack_ids):
                    return True
                else:
                    return False
            else:
                return True
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e
        except Exception as e:
            logger.error(e)
            raise e
