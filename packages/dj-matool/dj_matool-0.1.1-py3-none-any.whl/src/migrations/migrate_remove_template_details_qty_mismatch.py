from typing import List

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src.model.model_template_details import TemplateDetails

patient_list: List[int] = [79, 161, 707, 1018, 2031, 2584]


def migrate_remove_template_details_qty_mismatch():
    init_db(db, "database_migration")

    query = TemplateDetails.delete().where(TemplateDetails.patient_id << patient_list)
    status = query.execute()

    print("Template Details deleted successfully..")


if __name__ == "__main__":
    migrate_remove_template_details_qty_mismatch()
