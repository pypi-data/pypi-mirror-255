from peewee import PrimaryKeyField, DecimalField, CharField, DateTimeField, IntegerField, InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

logger = settings.logger


class BigCanisterStick(BaseModel):
    """
    It contains the data related to big canister sticks.
    """
    id = PrimaryKeyField()
    width = DecimalField(decimal_places=3, max_digits=6)
    depth = DecimalField(decimal_places=3, max_digits=6)
    serial_number = CharField(unique=True, max_length=10)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'big_canister_stick'

    @classmethod
    def get_big_canister_stick_dimension_id(cls) -> list:
        """
        Function to get details about big canister stick dimension based on range of value for width and depth
        along with serial_number = optional argument.
        :return:
        """
        big_canister_stick_data = list()

        try:
            query = BigCanisterStick.select(
                BigCanisterStick.id,
                BigCanisterStick.width,
                BigCanisterStick.depth,).dicts()

            for record in query:
                big_canister_stick_data.append(record)
            return big_canister_stick_data
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_big_canister_stick_by_bs_serial_number(cls, bs_serial_number: str) -> int:
        """
        Function to get big canister stick id for given bs_serial_number.
        @param bs_serial_number: big stick serial number
        :return big_canister_stick_id:
        """
        logger.info("In get_big_canister_stick_by_bs_serial_number")
        big_canister_stick_id: int = 0

        try:
            query = BigCanisterStick.select(BigCanisterStick.id.alias('big_canister_stick_id')).dicts() \
                .where(BigCanisterStick.serial_number == bs_serial_number)
            for record in query:
                big_canister_stick_id = record['big_canister_stick_id']
            return big_canister_stick_id
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
