from dosepack.base_model.base_model import db
from src.model.model_drug_master import DrugMaster
from sync_drug_data import update_drug_data


def populate_drug_data(old_database, new_database):
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    cursor = db.execute_sql('select * from drug_master;')
    drug_data = []

    for row in cursor.fetchall():
        drug_name = row[1]
        ndc = row[2]
        strength = row[3]
        strength_value = row[4]
        manufacturer = row[5]
        txr = row[6]
        generic_drug = row[7]
        brand_drug = row[8]
        brand_flag = row[9]
        image_name = row[10]
        shape = row[11]
        color = row[12]
        imprint = row[13]

        drug_data.append({"drug_name": drug_name, "ndc": ndc, "strength": strength,
                              "strength_value": strength_value, "manufacturer": manufacturer, "txr": txr, "generic_drug": generic_drug,
                              "brand_flag": brand_flag, "brand_drug": brand_drug, "image_name": image_name,
                              "shape": shape, "color": color, "imprint": imprint, "formatted_ndc": ndc[0:9]})

    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    # Todo check for strength length for new database
    # Bulk insertion -- 1000 records at once
    with db.atomic():
        for idx in range(0, len(drug_data), 1):
            try:
                DrugMaster.insert_many(drug_data[idx:idx+1]).execute()
                # counter += 1
                # if counter == 1000:
                #     print('.', end="", flush=True)
                #     counter = 0
            except Exception as e:
                print('-', end="", flush=True)
                pass

    update_drug_data.populate_drug_master([], True)
    update_drug_data.populate_exception_drug_master([], True)



