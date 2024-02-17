from typing import List, Dict, Any

from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, CharField, IntegerField, DateTimeField, \
    InternalError, IntegrityError, DataError, DoesNotExist

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time

from src.model.model_drug_master import DrugMaster
from src.model.model_pack_details import PackDetails
logger = settings.logger


class PackError(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails, unique=False)
    comments = CharField(null=True)
    created_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time())

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_error"

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the BatchDrugData.
        """
        logger.debug("Inside PackError.insert_data insert data :{}".format(data_list))
        try:
            record = cls.insert_many(data_list).execute()
            return record
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
