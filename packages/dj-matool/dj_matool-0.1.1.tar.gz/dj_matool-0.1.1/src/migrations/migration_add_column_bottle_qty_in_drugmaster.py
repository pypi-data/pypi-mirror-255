import logging

from playhouse.migrate import *

import settings
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db

logger = logging.getLogger("root")


class DrugMaster(BaseModel):
    """
        @class: drug_master.py
        @type: file
        @desc: logical class for table drug_master
    """
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14, unique=True)
    formatted_ndc = CharField(max_length=12, null=True)
    strength = CharField(max_length=50)
    strength_value = CharField(max_length=16)
    manufacturer = CharField(null=True, max_length=100)
    txr = CharField(max_length=8, null=True)
    imprint = CharField(null=True, max_length=82)
    color = CharField(null=True, max_length=30)
    shape = CharField(null=True, max_length=30)
    image_name = CharField(null=True, max_length=255)
    brand_flag = CharField(null=True, max_length=1)
    brand_drug = CharField(null=True, max_length=50)
    drug_form = CharField(null=True, max_length=15)
    upc = CharField(max_length=20, unique=True, null=True)  # keeping max length 20 as allowed by IPS.
    generic_drug = CharField(null=True, max_length=120)
    bottle_quantity = FloatField(null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


def add_columns_bottle_quantity():
    init_db(db, 'database_migration')
    migrator = MySQLMigrator(db)

    try:
        migrate(
            migrator.add_column(DrugMaster._meta.db_table,
                                DrugMaster.bottle_quantity.db_column,
                                DrugMaster.bottle_quantity)
        )
        print("Added column bottle_quantity in DrugMaster")
    except Exception as e:
        logger.error("Error while adding columns in DrugMaster: ", str(e))
