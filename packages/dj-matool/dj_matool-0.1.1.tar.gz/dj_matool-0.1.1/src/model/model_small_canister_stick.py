from peewee import PrimaryKeyField, DecimalField, DateTimeField, IntegerField, DoesNotExist, IntegrityError, \
    InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
logger = settings.logger


class SmallCanisterStick(BaseModel):
    """
    It contain the data related to small canister sticks.
    """
    id = PrimaryKeyField()
    length = DecimalField(decimal_places=3, max_digits=6)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'small_canister_stick'

    @classmethod
    def db_get_data_by_length(cls, req_length) -> dict or None:
        """
        Function to get data for small canister stick by length
        :param req_length: Length for which we need to find the data
        :return:
        """
        try:
            data = SmallCanisterStick.select().dicts().where(SmallCanisterStick.length == req_length).get()
            return data
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return None
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_small_canister_stick_by_ss_serial_number(cls, ss_serial_number: str) -> int:
        """
        Function to get small canister stick id for given ss_serial_number.
        :param ss_serial_number: small stick serial number
        :return small_canister_stick_id:
         """
        logger.info("In get_small_canister_stick_by_ss_serial_number")
        small_canister_stick_id: int = 0

        try:
            query = SmallCanisterStick.select(SmallCanisterStick.id.alias('small_canister_stick_id')).dicts() \
                .where(SmallCanisterStick.length == ss_serial_number)
            for record in query:
                small_canister_stick_id = record['small_canister_stick_id']
            return small_canister_stick_id
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e
