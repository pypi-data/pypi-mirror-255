import settings
from multiprocessing import Lock
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField, DateField, InternalError, IntegrityError, DataError
from src.model.model_consumable_type_master import ConsumableTypeMaster
lock = Lock()
logger = settings.logger


class ConsumableUsed(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    consumable_id = ForeignKeyField(ConsumableTypeMaster)
    used_quantity = IntegerField()
    created_date = DateField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "consumable_used"

    @classmethod
    def db_update_or_create(cls, company_id, consumable_id, consumed_date, defaults_data_dict=None):
        try:
            with lock:
                logger.info("in_consumable_used_update_or_create: " + str(defaults_data_dict))
                record, created = ConsumableUsed.get_or_create(company_id=company_id, consumable_id=consumable_id,
                                                               created_date=consumed_date, defaults=defaults_data_dict)

                if created:
                    logger.info(
                        'consumable_used_get_or_create: Record created at {0}: '.format(get_current_date_time()) + str(
                            consumed_date) + ' ' +
                        str(consumable_id) + ' ' + str(record.used_quantity))

                if record.used_quantity == 1:
                    logger.info('consumable_used_get_or_create ' + str(consumed_date) + ' ' +
                                str(consumable_id) + ' ' + str(created))
                if not created:
                    ConsumableUsed.update(
                        **{'used_quantity': record.used_quantity + defaults_data_dict["used_quantity"]}) \
                        .where(ConsumableUsed.id == record.id).execute()

                    logger.info('consumable_used_get_or_create ' + str(consumed_date) + ' ' +
                                str(consumable_id) + ' ' + str(created) + ' ' + str(record.used_quantity))
                    logger.info(
                        'consumable_used_get_or_create: Record updated at {0}: '.format(get_current_date_time()) + str(
                            consumed_date) + ' ' +
                        str(consumable_id) + ' updated quantity: ' + str(
                            record.used_quantity + defaults_data_dict["used_quantity"]))
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise