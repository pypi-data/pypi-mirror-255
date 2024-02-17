from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, DateTimeField, IntegerField, CharField, \
    IntegrityError, InternalError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_custom_drug_shape import CustomDrugShape
from src.model.model_drug_dimension import DrugDimension
from src.model.model_unique_drug import UniqueDrug

logger = settings.logger

class DrugDimensionHistory(BaseModel):
    """
    It contains the data related to drug dimensions.
    """
    id = PrimaryKeyField()
    drug_dimension_id = ForeignKeyField(DrugDimension)
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6)  # in mm
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    approx_volume = DecimalField(decimal_places=6, max_digits=10)  # in mm^3
    accurate_volume = DecimalField(decimal_places=6, max_digits=10, null=True)  # in mm^3  # provided by user
    shape = ForeignKeyField(CustomDrugShape, null=True)
    created_by = IntegerField(default=1)
    is_manual = IntegerField(default=1)
    created_date = DateTimeField(default=get_current_date_time)
    image_name = CharField(null=True, max_length=255)
    verification_status_id = ForeignKeyField(CodeMaster, default=settings.DRUG_VERIFICATION_STATUS['pending'], related_name="verification_status_id")


    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension_history'

    @classmethod
    def db_insert_drug_dimension_history_data(cls, dimension_history_data) -> int:
        """
        insert drug dimension data in drug dimension table
        :return:
        """
        try:
            dimension_id = DrugDimensionHistory.insert(**dimension_history_data).execute()
            return dimension_id
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e