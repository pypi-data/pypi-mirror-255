from peewee import *
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_location_master import LocationMaster

logger = settings.logger


class DisabledLocationHistory(BaseModel):
    id = PrimaryKeyField()
    loc_id = ForeignKeyField(LocationMaster, related_name='dlh_location_id_id', unique=False)
    start_time = DateTimeField(default=get_current_date_time())
    end_time = DateTimeField(null=True)
    comment = CharField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "disabled_location_history"

    @classmethod
    def db_delete_location(cls, location_id):
        logger.debug("In db_delete_location")

        try:
            status = DisabledLocationHistory.delete() \
                .where(DisabledLocationHistory.loc_id << location_id) \
                .execute()
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_location_disabled(cls, loc_id):
        """
        Returns True if location is disabled for given robot id, False otherwise

        :param robot_id:
        :param location:
        :return: bool
        """
        logger.debug("In db_location_disabled")
        try:
            DisabledLocationHistory.get(
                loc_id=loc_id
            )
            return True
        except DoesNotExist:
            return False
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def update_location_status(cls,disabled_location_history_id, status):
        logger.debug("In update_location_status")
        try:
            if status == settings.LOCATION_ENABLE:
                query = cls.update(end_time=get_current_date_time()).where(cls.id == disabled_location_history_id).execute()
                return query
        except DoesNotExist as e:
            logger.error(e)
            raise

        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def add_disabled_location(cls, data_dict):
        logger.debug("In add_disabled_location")
        comment = data_dict["comment"]
        created_by = data_dict["created_by"]
        created_date = get_current_date_time()
        start_time = get_current_date_time()
        loc_id = data_dict["loc_id"]
        try:
            query = DisabledLocationHistory.insert(comment=comment, created_by=created_by, created_date=created_date,
                                                   start_time=start_time, loc_id=loc_id).execute()
            return query
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def add_multiple_disabled_location(cls, data_dict_list):
        logger.debug("In add_multiple_disabled_location")
        # comment = data_dict["comment"]
        # created_by = data_dict["created_by"]
        # created_date = get_current_date_time()
        # start_time = get_current_date_time()
        # loc_id = data_dict["loc_id"]
        try:
            query = DisabledLocationHistory.insert_many(data_dict_list).execute()
            return query
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_latest_disabled_id(cls, location_id):
        logger.info("In get_latest_disabled_id")
        try:
            query = cls.select(cls.id).dicts().where(cls.loc_id == location_id).order_by(cls.created_date.desc()).limit(1)
            for record in query:
                return record['id']
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise