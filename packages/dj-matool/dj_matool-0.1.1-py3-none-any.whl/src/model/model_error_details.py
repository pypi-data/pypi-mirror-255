from peewee import BooleanField, ForeignKeyField, DateTimeField, \
    PrimaryKeyField, InternalError, IntegrityError, DecimalField, DataError
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_pack_details import PackDetails
from src.model.model_pack_grid import PackGrid
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger


class ErrorDetails(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    unique_drug_id = ForeignKeyField(UniqueDrug)
    pack_grid_id = ForeignKeyField(PackGrid)
    error_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    pvs_error_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    missing = DecimalField(decimal_places=2, max_digits=4, null=True)
    extra = DecimalField(decimal_places=2, max_digits=4, null=True)
    mpse = DecimalField(decimal_places=2, max_digits=4, null=True)
    broken = BooleanField(default=False)
    out_of_class_reported = BooleanField(default=False)
    created_date = DateTimeField(default=get_current_date_time)

    class Meta:
        indexes = (
            (('pack_id', 'unique_drug_id', 'pack_grid_id'), True),
        )
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "error_details"

    @classmethod
    def db_add_update_errors(cls, error_data_list):
        error_id_list = list()
        try:
            for error_data in error_data_list:
                create_dict = {
                    'pack_id': error_data['pack_id'],
                    'unique_drug_id': error_data['unique_drug_id'],
                    'pack_grid_id': error_data['pack_grid_id'],
                }
                update_dict = {
                    'error_qty': error_data['error_qty'],
                    'pvs_error_qty': error_data['pvs_error_qty'],
                    'missing': error_data['missing'],
                    'extra': error_data['extra'],
                    'mpse': error_data['mpse'],
                    'broken': error_data['broken'],
                    'out_of_class_reported': error_data['out_of_class_reported']
                }
                record = cls.db_update_or_create(create_dict, update_dict)
                error_id_list.append(record)
            return error_id_list
        except (IntegrityError, DataError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_delete_error_details_by_id(cls, delete_error_details_list) -> bool:
        """
        delete error details data by id
        @param delete_error_details_list:
        """
        try:
            status = ErrorDetails.delete().where(ErrorDetails.id << delete_error_details_list).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e
