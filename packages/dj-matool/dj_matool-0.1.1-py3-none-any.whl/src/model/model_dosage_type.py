from peewee import PrimaryKeyField, FixedCharField, CharField, InternalError, IntegrityError

import settings
from dosepack.base_model.base_model import BaseModel


logger = settings.logger


class DosageType(BaseModel):
    id = PrimaryKeyField()
    code = FixedCharField(unique=True, max_length=10)
    name = CharField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "dosage_type"

    @classmethod
    def db_get(cls):
        """ Returns list of all dosage type """
        try:
            results = list()
            query = cls.select()
            for record in query.dicts():
                results.append(record)
            return results
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise