from playhouse.migrate import *
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from dosepack.utilities.utils import get_current_date_time
import settings
import logging

logger = logging.getLogger("root")


class DrugMaster(BaseModel):
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
    upc = CharField(max_length=20, unique=True, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"


class DrugStatus(BaseModel):
    id = PrimaryKeyField()
    drug_id = ForeignKeyField(DrugMaster, unique=True)
    ext_status = BooleanField(default=False)
    ext_status_updated_date = DateTimeField(default=None, null=True)
    last_billed_date = DateField(default=None, null=True)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_status"


def migrate_85():
    init_db(db, "database_migration")
    migrator = MySQLMigrator(db)

    migrate(
        migrator.add_column(
            DrugMaster._meta.db_table,
            DrugMaster.upc.db_column,
            DrugMaster.upc
        )
    )

    db.create_tables([DrugStatus], safe=True)

    with db.transaction():
        drug_list = list()
        drug_data = DrugMaster.select(DrugMaster.id).dicts()
        for record in drug_data:
            drug_status_data = {
                'ext_status': 0,
                'drug_id': record['id']
            }
            drug_list.append(drug_status_data)

        print(drug_list)
        for idx in range(0, len(drug_list), 1000):
            try:
                status = DrugStatus.insert_many(drug_list[idx:idx + 1000]).execute()
                print(status)
            except Exception as e:
                print(e)
                logger.info(e)


if __name__ == '__main__':
    migrate_85()
