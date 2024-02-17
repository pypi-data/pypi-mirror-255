import settings
from dosepack.base_model.base_model import BaseModel
from peewee import PrimaryKeyField, ForeignKeyField, IntegerField
from src.model.model_consumable_type_master import ConsumableTypeMaster
from src.model.model_orders import Orders
logger = settings.logger


class OrderDetails(BaseModel):
    id = PrimaryKeyField()
    order_id = ForeignKeyField(Orders)
    consumable_id = ForeignKeyField(ConsumableTypeMaster)
    quantity = IntegerField()

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "order_details"
