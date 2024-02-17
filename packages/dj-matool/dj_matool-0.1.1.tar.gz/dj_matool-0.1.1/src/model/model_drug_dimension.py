from peewee import PrimaryKeyField, ForeignKeyField, DecimalField, DateTimeField, IntegerField, CharField, \
    IntegrityError, InternalError, fn

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_unique_drug import UniqueDrug
from src.model.model_custom_drug_shape import CustomDrugShape

logger = settings.logger


class DrugDimension(BaseModel):
    """
    It contains the data related to drug dimensions.
    """
    id = PrimaryKeyField()
    unique_drug_id = ForeignKeyField(UniqueDrug, unique=True)
    width = DecimalField(decimal_places=3, max_digits=6)  # in mm
    length = DecimalField(decimal_places=3, max_digits=6)  # in mm
    depth = DecimalField(decimal_places=3, max_digits=6)  # in mm
    fillet = DecimalField(decimal_places=3, max_digits=6, null=True)
    approx_volume = DecimalField(decimal_places=6, max_digits=10)  # in mm^3
    # approx_volume must be calculated using length*width*depth on every insert and update
    accurate_volume = DecimalField(decimal_places=6, max_digits=10, null=True)  # in mm^3  # provided by user
    shape = ForeignKeyField(CustomDrugShape, null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    created_by = IntegerField(default=1)
    modified_by = IntegerField(default=1)
    verification_status_id = ForeignKeyField(CodeMaster, default=settings.DRUG_VERIFICATION_STATUS['pending'])
    verified_by = IntegerField(default=None, null=True)  # verification needs to be done by second pharmacy tech.
    verified_date = DateTimeField(default=None, null=True)
    rejection_note = CharField(default=None, null=True, max_length=1000)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_dimension'

    @classmethod
    def db_get_drug_dimension_data(cls):
        """
        get drug dimension data of drugs from drug dimension table
        :return:
        """
        try:
            drug_with_dimension_query = DrugDimension.select(DrugDimension.unique_drug_id, DrugDimension.verification_status_id).dicts() \
                                        .join(UniqueDrug, on=UniqueDrug.id == DrugDimension.unique_drug_id) \
                                        .join(DrugMaster, on=((DrugMaster.formatted_ndc == UniqueDrug.formatted_ndc) &
                                                              (DrugMaster.txr == UniqueDrug.txr))) \
                                        .group_by(UniqueDrug.id)
            return drug_with_dimension_query
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_drug_dimension_info(cls, unique_drug_id):
        """
        Deletes canisters data from table
        :return:
        """
        try:
            query = cls.select().dicts().where(cls.unique_drug_id == unique_drug_id)
            return query
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_insert_drug_dimension_data(cls, dimension_data) -> int:
        """
        insert drug dimension data in drug dimension table
        :return:
        """
        try:
            dimension_id = DrugDimension.insert(**dimension_data).execute()
            return dimension_id
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_get_drug_dimension_data_by_dimension_id(cls, dimension_id) -> dict:
        """
        get drug dimension data by dimension id
        :return:
        """
        try:
            query = DrugDimension.select(DrugDimension.unique_drug_id,
                                        DrugDimension.length,
                                        DrugDimension.width,
                                        DrugDimension.depth,
                                        DrugDimension.accurate_volume,
                                        DrugDimension.shape).dicts()\
                .where(DrugDimension.id == dimension_id).get()
            return query
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_update_drug_dimension_by_dimension_id(cls, dimension_id: int, update_dict: dict) -> bool:
        """
        update drug dimension by dimension id
        :return:
        """
        try:
            status = DrugDimension.update(**update_dict).where(DrugDimension.id == dimension_id).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e
