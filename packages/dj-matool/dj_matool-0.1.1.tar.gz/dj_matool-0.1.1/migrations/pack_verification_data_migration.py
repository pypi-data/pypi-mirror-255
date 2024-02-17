from dosepack.base_model.base_model import BaseModel
from dosepack.base_model.base_model import db
from src.model.model_note_master import NoteMaster
from src.model.model_pack_verification import PackVerification


def pack_verification_data_migration(old_database, new_database):
    db.init(old_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()

    cursor = db.execute_sql('select * from pack_verification;')
    pack_data = []

    for row in cursor.fetchall():
        pack_id = row[1]
        pack_fill_status = row[2]
        image_path = row[3]
        created_date = row[11]
        modified_date = row[12]

        pack_data.append({"pack_id": pack_id, "pack_fill_status": pack_fill_status, "image_path": image_path,
                          "created_date": created_date, "modified_date": modified_date})

    db.init(new_database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    counter = 0

    pack_list = []

    note_id = NoteMaster.create(**{"note1": None, "note2": None, "note3": None, "note4": None, "note5": None,
                                   "created_by": 1, "modified_by": 1,
                                   }).id

    for record in pack_data:
        try:
            if record["pack_fill_status"]:
                record["pack_fill_status"] = 19
            else:
                record["pack_fill_status"] = 20

            pack_verification_record = {"pack_id": record["pack_id"], "note_id": note_id,
                                        "pack_fill_status": record["pack_fill_status"],
                                        "created_date": record["created_date"], "modified_date": record["modified_date"],
                                        "created_by": 1, "modified_by": 1, "image_path": record["image_path"]}

            pack_list.append(pack_verification_record)
            counter += 1
            if counter == 1000:
                print('.', end="", flush=True)
                counter = 0
                with db.transaction():
                    BaseModel.db_create_multi_record(pack_list, PackVerification)
                pack_list = []
        except Exception as e:
            print(e)
    if pack_list:
        with db.transaction():
            BaseModel.db_create_multi_record(pack_list, PackVerification)






