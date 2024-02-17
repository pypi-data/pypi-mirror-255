from peewee import BooleanField, \
    IntegerField, ForeignKeyField, DateTimeField,\
    PrimaryKeyField, InternalError, DoesNotExist, IntegrityError,\
    DecimalField, DataError
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_fill_error_v2 import PackFillErrorV2
from src.model.model_pack_grid import PackGrid

logger = settings.logger


class SlotFillErrorV2(BaseModel):
    id = PrimaryKeyField()
    # pack_id = ForeignKeyField(PackDetails)
    # unique_drug_id = ForeignKeyField(UniqueDrug)  # TODO: remove
    pack_fill_error_id = ForeignKeyField(PackFillErrorV2)
    pack_grid_id = ForeignKeyField(PackGrid)
    error_qty = DecimalField(decimal_places=2,
                             max_digits=4, null=True)  # kept to support previously reported error and stable flow
    actual_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    counted_error_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    broken = BooleanField(null=True)
    out_of_class_reported = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    rph_error = BooleanField(default=False)
    rph_error_resolved = BooleanField(default=False)
    modified_by = IntegerField(null=True)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_fill_error_id', 'pack_grid_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_fill_error_v2"

    @classmethod
    def db_delete_slot_fill_error_data(cls, fill_error, pack_grid_id) -> bool:
        """
        @param fill_error:
        @param pack_grid_id:
        :return:
        """
        try:
            status = SlotFillErrorV2.delete().where(SlotFillErrorV2.pack_fill_error_id == fill_error,
                                           SlotFillErrorV2.pack_grid_id == pack_grid_id).execute()
            return status
        except (DoesNotExist, InternalError, IntegrityError) as e:
            raise e


    @classmethod
    def db_update_dict_slot_fill_error(cls, update_dict, slot_fill_error_id) -> bool:
        """
        update slot fill error for given slot fill error id
        @param slot_fill_error_id:
        @param update_dict:
        """
        try:
            status = SlotFillErrorV2.update(**update_dict).where(SlotFillErrorV2.id == slot_fill_error_id).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_delete_slot_fill_error_data_by_ids(cls, delete_slot_fill_error_list) -> bool:
        """
        delete slot fill error data by slot fill error id
        @param delete_slot_fill_error_list:
        """
        try:
            status = SlotFillErrorV2.delete().where(SlotFillErrorV2.id << delete_slot_fill_error_list).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e
