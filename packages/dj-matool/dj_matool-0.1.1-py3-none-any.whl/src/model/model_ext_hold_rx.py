import logging

from peewee import PrimaryKeyField, IntegrityError, DataError, InternalError, DoesNotExist, \
    ForeignKeyField, FixedCharField, CharField

import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_file_header import FileHeader

logger = logging.getLogger("root")


class ExtHoldRx(BaseModel):
    # rx that are on hold in IPS due to some reasons will be stored here
    id = PrimaryKeyField()
    file_id = ForeignKeyField(FileHeader, related_name="hold_rx_file_id")
    ext_pharmacy_rx_no = FixedCharField(max_length=20)
    ext_note = CharField(null=True, max_length=100)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "ext_hold_rx"

    @classmethod
    def insert_multiple_ext_hold_rx_data(cls, data_list: list):
        """
        Method to insert data into ext_hold_Rx table
        """
        try:
            logger.debug("In insert_ext_change_rx_data")
            status = ExtHoldRx.insert_many(data_list).execute()
            return status
        except (IntegrityError, DataError, InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise
