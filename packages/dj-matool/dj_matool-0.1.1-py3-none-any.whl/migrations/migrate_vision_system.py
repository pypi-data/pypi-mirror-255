from dosepack.base_model.base_model import db
from model.model_vision_system import VisionDrugMapping
from src.model.model_vision_drug_count import VisionCountPrediction
from src.model.model_vision_drug_prediction import VisionDrugPrediction


def create_tables(database):
    db.init(database, user="root".encode('utf-8'), password="root".encode('utf-8'))
    db.connect()
    # fails silently if table already exists
    db.create_tables([VisionDrugMapping, VisionDrugPrediction, VisionCountPrediction], True)


