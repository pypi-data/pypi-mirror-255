from typing import List, Dict, Any, Optional
from peewee import (PrimaryKeyField, CharField, DecimalField, IntegrityError, InternalError, DataError, DoesNotExist,
                    fn)
import settings
from dosepack.base_model.base_model import BaseModel

logger = settings.logger


class LocalDIData(BaseModel):
    id = PrimaryKeyField()
    ndc = CharField(max_length=14, unique=True)
    formatted_ndc = CharField(max_length=12)
    txr = CharField(max_length=8, null=True)
    brand_flag = CharField(max_length=1, null=True, default=None)
    quantity = DecimalField(decimal_places=2, default=0)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "local_di_data"

    @classmethod
    def concatenated_fndc_txr_field(cls, delimiter='##'):
        """
        Returns the concatenated fndc_txr with the given separator.
        e.g.: "fndc##txr"
        """
        return fn.CONCAT(cls.formatted_ndc, delimiter, fn.IFNULL(cls.txr, ''))

    @classmethod
    def insert_data(cls, data_list: List[Dict[str, Any]]) -> bool:
        """
        Inserts multiple records in the LocalDIData.
        """
        logger.debug("Inside LocalDIData.insert_data")
        try:
            cls.insert_many(data_list).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_data(cls, fndc_txr_list: Optional[List[str]] = None, ndc_list: Optional[List[str]] = None,
                 txr_list: Optional[List[str]] = None, qty_greater_than_zero: Optional[bool] = False) -> List[Any]:
        """
        Fetches the data from the LocalDIData
        """
        logger.debug("Inside LocalDIData.get_data")
        clauses: List[Any] = list()
        if qty_greater_than_zero:
            clauses.append(cls.quantity > 0)
        if fndc_txr_list:
            clauses.append(cls.concatenated_fndc_txr_field().in_(fndc_txr_list))
        if ndc_list:
            clauses.append(cls.ndc.in_(ndc_list))
        if txr_list:
            clauses.append(cls.txr.in_(txr_list))

        try:
            if clauses:
                return cls.select(cls.id.alias("drug_inventory_id"), cls.ndc, cls.formatted_ndc, cls.txr, cls.quantity,
                                  cls.brand_flag, cls.concatenated_fndc_txr_field().alias("fndc_txr")).dicts() \
                    .where(*clauses)
            else:
                return cls.select(cls.id.alias("drug_inventory_id"), cls.ndc, cls.formatted_ndc, cls.txr, cls.quantity,
                                  cls.brand_flag, cls.concatenated_fndc_txr_field().alias("fndc_txr")).dicts()

        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_by_ndc(cls, update_dict: Dict[str, Any], ndc: str) -> bool:
        """
        Updates the data in the LocalDIData by ndc.
        """
        try:
            cls.update(**update_dict).where(cls.ndc == ndc).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
