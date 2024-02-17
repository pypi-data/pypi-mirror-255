from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, fn, InternalError, IntegrityError, DataError, \
    DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_unique_drug import UniqueDrug


class RtsSlotAssignInfo(BaseModel):
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug)
    user_id = IntegerField()
    current_queue = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "rts_slot_assign_info"

    @classmethod
    def get_user_wise_drug_assigned_count(cls, user_id):
        try:
            query = cls.select(fn.COUNT(cls.id).alias('count')).where(cls.user_id==user_id)
            for record in query.dicts():
                return record['count']
            return 0
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e

    @classmethod
    def remove_user_from_current_queue(cls, user_id):
        try:
            status = cls.update(current_queue=0).where(cls.user_id == user_id, cls.current_queue == 1).execute()
            return status
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e

    @classmethod
    def insert_into_rts_slot_assign_info(cls, drugs_in_queue, user_id):
        try:
            record = None
            for drug in drugs_in_queue:
                create_dict = {
                    'unique_drug_id': drug
                }
                update_dict = {
                    'user_id': user_id,
                    'current_queue': 1
                }
                record = RtsSlotAssignInfo.db_update_or_create(create_dict, update_dict)
            return True if record else False
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e

    @classmethod
    def check_rts_slot_assigning_in_progress(cls, user_id):
        try:
            query = cls.select(fn.COUNT(cls.id).alias('count')).dicts().where(
                cls.user_id == user_id,
                cls.current_queue == 1).get()
            return query['count']
        except DoesNotExist as e:
            settings.logger.error(e, exc_info=True)
            return None
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e

    @classmethod
    def check_rts_user(cls, user_id):
        try:
            query = cls.select(cls.id).dicts().where(cls.user_id==user_id).get()
            return query['id']
        except DoesNotExist as e:
            settings.logger.error(e, exc_info=True)
            return None
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            settings.logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_change_drug_queue_status_in_rts_slot_assign_info(cls, unique_drug_id):
        try:
            status = cls.update(current_queue=2).where(cls.unique_drug_id==unique_drug_id).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            settings.logger.error(e, exc_info=True)
            raise e