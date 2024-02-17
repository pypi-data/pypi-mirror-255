from dosepack.base_model.base_model import db
from src.model.model_unique_drug import UniqueDrug
from model.model_init import init_db
from src import constants
from src.model.model_prs_drug_details import PRSDrugDetails


def migration_prs_data():
    init_db(db, 'database_migration')
    # get the already existing unique_drug_ids in the PRSDrugDetails table
    existing_unique_ids = []
    final_list = []
    prs_unique_drug_query = PRSDrugDetails.select(PRSDrugDetails.unique_drug_id).dicts()
    if prs_unique_drug_query.count()>0:
        for record in prs_unique_drug_query:
            existing_unique_ids.append(record["unique_drug_id"])
    if existing_unique_ids:
        unique_drug_id_query = UniqueDrug.select(UniqueDrug.id).dicts().where(UniqueDrug.id.not_in(existing_unique_ids))
    else:
        unique_drug_id_query = UniqueDrug.select(UniqueDrug.id).dicts()
    for record in unique_drug_id_query:
        data = {"unique_drug_id": record["id"], "status": constants.PRS_DRUG_STATUS_PENDING}
        final_list.append(data)
    status = PRSDrugDetails.insert_many(final_list).execute()
    print(status)
