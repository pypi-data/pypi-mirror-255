from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_product_details import ProductDetails


def migration_create_table_product_details():
    init_db(db, 'database_migration')
    if not ProductDetails.table_exists():
        db.create_tables([ProductDetails], safe=True)
        print('Table(s) created: ProductDetails')


if __name__ == "__main__":
    migration_create_table_product_details()
