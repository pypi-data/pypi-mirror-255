from typing import List, Dict, Any
from peewee import (IntegerField, ForeignKeyField, DateTimeField, PrimaryKeyField, BooleanField, CharField,
                    IntegrityError, InternalError, DataError, DoesNotExist)
import settings
from dosepack.base_model.base_model import (BaseModel)
from dosepack.utilities.utils import (get_current_date_time)
from src.model.model_batch_drug_data import BatchDrugData

logger = settings.logger


class BatchDrugOrderData(BaseModel):
    id = PrimaryKeyField()
    batch_drug_data_id = ForeignKeyField(BatchDrugData, unique=True)
    ndc = CharField(max_length=14)
    original_qty = IntegerField(default=0)
    daw = IntegerField()
    pack_size = IntegerField(default=0)
    pack_unit = IntegerField(default=0)
    cfi = CharField(null=True)
    is_ndc_active = BooleanField(default=True)
    is_sub = BooleanField(default=False, null=True)
    sub_reason = CharField(default=None, null=True)
    pre_ordered_ndc = CharField(max_length=14, null=True)
    pre_ordered_qty = IntegerField(default=0, null=True)
    pre_ordered_pack_size = IntegerField(default=0, null=True)
    pre_ordered_pack_unit = IntegerField(default=0, null=True)
    is_processed = BooleanField(default=True)
    message = CharField(default=None, null=True)
    created_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField(null=True)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "batch_drug_order_data"

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the BatchDrugOrderData.
        """
        logger.debug("Inside BatchDrugOrderData.insert_data")
        try:
            return cls.insert_many(data_list).execute()
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_data_by_id(cls, data: Dict[str, Any], batch_drug_data_id: int) -> bool:
        """
        Updates the record for the given drug_id and the facility_dist_id.
        """
        try:
            query = cls.update(**data).where(cls.batch_drug_data_id == batch_drug_data_id).execute()
            if query >= 0:
                return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
