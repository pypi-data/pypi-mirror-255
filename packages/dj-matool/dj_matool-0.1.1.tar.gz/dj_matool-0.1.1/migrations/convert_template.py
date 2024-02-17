

from dosepack.base_model.base_model import db
import time

from src.model.model_template_details import TemplateDetails


def convert_template(database):
    """
    to converts template from old to new format acc. to IER #15552
    updates column numbers for template,
    ex- For a template : old_columns = [1,2,5,9,13] --> new_columns = [1,2,3,4,5]
    :param database:
    :return:
    """
    db.init(database, user="root", password="root".encode('utf-8'))
    start_time = time.time()
    count = 0
    with db.transaction():
        for patient in TemplateDetails.select(TemplateDetails.patient_id, TemplateDetails.system_id).distinct().dicts():
            column_numbers = [0]  # initializing column_numbers
            template_data = []
            system_id = patient["system_id"]
            count += 1
            for record in TemplateDetails.select().dicts()\
                    .where(TemplateDetails.patient_id == patient["patient_id"],
                           TemplateDetails.system_id == system_id)\
                    .order_by(TemplateDetails.column_number):

                if record["column_number"] not in column_numbers:
                    column_numbers.append(record["column_number"])
                temp = column_numbers.index(record["column_number"])
                # print(temp, record["column_number"])
                record["column_number"] = temp
                record.pop("id", None)
                template_data.append(record)

            TemplateDetails.db_delete(patient["patient_id"], system_id)
            status = TemplateDetails.insert_many(template_data).execute()
            print('.', end="", flush=True) # don't use if used as script

    stop_time = time.time()
    print(stop_time-start_time)

