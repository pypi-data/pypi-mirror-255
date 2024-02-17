from peewee import PrimaryKeyField, ForeignKeyField, CharField, InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel
logger = settings.logger
from src.model.model_custom_drug_shape import CustomDrugShape


class DrugShapeFields(BaseModel):
    id = PrimaryKeyField()
    custom_shape_id = ForeignKeyField(CustomDrugShape)
    field_name = CharField()
    label_name = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == '_':
            db_table = 'drug_shape_fields'

    @classmethod
    def db_get_drug_shape_fields_by_shape_id(cls, shape_id) -> list:
        """
        This function will be used to find fields for the shape id provided
        :param shape_id: Shape id for which we need to find the data
        :return: List of dictionaries
        """
        db_result = []
        try:
            query = DrugShapeFields.select().where(DrugShapeFields.custom_shape_id == shape_id)

            for data in query.dicts():
                db_result.append(data)

            return db_result
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise
