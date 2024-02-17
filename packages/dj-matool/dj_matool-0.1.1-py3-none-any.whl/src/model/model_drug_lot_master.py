from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from peewee import *
import settings
import functools
import operator

from src.model.model_drug_master import DrugMaster

logger = settings.logger


class DrugLotMaster(BaseModel):
    """
    Database table to manager the data about each lot of drugs
    """
    id = PrimaryKeyField()
    lot_number = CharField(null=True)
    drug_id = ForeignKeyField(DrugMaster, related_name="drug_lot_master_drug_id")
    expiry_date = CharField(null=True)
    total_packages = IntegerField()
    total_quantity = DecimalField(decimal_places=2, max_digits=7)
    available_quantity = DecimalField(decimal_places=2, max_digits=7)
    company_id = IntegerField()
    created_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_by = IntegerField()
    modified_date = DateTimeField(default=get_current_date_time)
    case_id = CharField(null=True, default=None, unique=True)
    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_lot_master"

    @classmethod
    def insert_drug_lot_master_data(cls, drug_lot_data):
        """
        This method will be used to insert information for a lot that is being added into inventory
        :param drug_lot_data: Data dict we need to add for the lot
        :return: Row ID or error
        """
        try:
            query = BaseModel.db_create_record(drug_lot_data, DrugLotMaster, get_or_create=False)
            # Returning data
            return query.id

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_drug_lot_information(cls, drug_lot_update_dict, drug_lot_id):
        """
        This method will be used to update the information about a given lot based on lot id
        :param drug_lot_update_dict: Data we need to update
        :param drug_lot_id: Drug Lot id for which we need to update the data
        :return: True/Error
        """
        try:
            status = DrugLotMaster.update(**drug_lot_update_dict).where(DrugLotMaster.id == drug_lot_id).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def check_if_lot_number_exists(cls, lot_number, drug_id_list=-1):
        """
        This function will be used to check if given lot number exist or not, if it exists then we need to return
        the id of the lot of lot master table else -1
        :param lot_number: Lot numbers for which we need to search else -1
        :param drug_id_list: Drug id for which we need to check
        :return: True+ Lot id/ False + -1
        """
        try:
            clauses: list = list()
            clauses.append((DrugLotMaster.lot_number == lot_number))

            if drug_id_list != -1:
                clauses.append((DrugLotMaster.drug_id.in_(drug_id_list)))

            drug_lot_id = DrugLotMaster.get(functools.reduce(operator.and_, clauses)).id
            return True, drug_lot_id

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False, -1

    @classmethod
    def check_if_lot_number_is_recalled(cls, lot_number):
        """
        This function will return if given lot number is recalled or not
        :param lot_number: Lot numbers for which we need to check
        :return: True/False
        """
        try:
            existence = DrugLotMaster.select(DrugLotMaster.id).where(
                (DrugLotMaster.lot_number == lot_number) & (DrugLotMaster.is_recall == True)).exists()

            return existence
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_drug_bottle_quantity_for_lot(cls, lot_id, quantity_to_update, action_performed=1):
        """
        This function will be used to update the quantity of bottle in the lot based on the given
        data.
        @param lot_id: ID for which we need to update information
        @param quantity_to_update: Bottle quantity we need to updated
        @param action_performed: Action which needs to be performed
        0: delete
        1: Add
        :return: True/False
        """
        try:
            if action_performed == 1:
                result = DrugLotMaster.update(total_packages=DrugLotMaster.total_packages + quantity_to_update).where(
                    DrugLotMaster.id == lot_id).execute()
            else:
                result = DrugLotMaster.update(total_packages=DrugLotMaster.total_packages - quantity_to_update).where(
                    DrugLotMaster.id == lot_id).execute()
            return result
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_lot_id_list_from_drug_id(cls, drug_id):
        """
        This function will be used to get list of lot id for given drug id
        :param drug_id: Drug id for which we need to get the data
        :return: List of lot id's for given drug id
        """
        lot_id_list: list = list()

        try:
            for data in DrugLotMaster.select(DrugLotMaster.id).dicts().where((DrugLotMaster.drug_id == drug_id) &
                                                                             (DrugLotMaster.is_recall == False)):
                lot_id_list.append(data["id"])
            return lot_id_list

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return lot_id_list

    @classmethod
    def get_drug_lot_information_from_lot_number(cls, lot_number):
        """
            @param lot_number:
            :return:
        """
        try:
            lot_drug_dict = DrugLotMaster.get(DrugLotMaster.lot_number == lot_number)
            return lot_drug_dict

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return {}

    @classmethod
    def get_lot_information_from_lot_id(cls, lot_id):
        """
        This function will return information about lot using the lot id
        @param lot_id: Lot id for which we need information
        @return: Data about the
        """
        try:
            for data in DrugLotMaster.select().dicts().where(DrugLotMaster.id == lot_id):
                return data

        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_recall_status_for_lot(cls, lot_id, recall_status=True):
        """
        This function will be used to set the recall status of the lot to recall statys
        @param lot_id: Lot id which we need to update
        @param recall_status: Recall status we need to set
        @return: True/False
        """
        try:
            status = DrugLotMaster.update(is_recall=recall_status).where(DrugLotMaster.id == lot_id).execute()
            return status
        except (InternalError, IntegrityError, DataError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def get_drug_lot_master_data(cls, lot_number, drug_id, expiry_date):

        try:
            lot_drug_dict = DrugLotMaster.get((DrugLotMaster.lot_number == lot_number) &
                                              (DrugLotMaster.drug_id == drug_id) &
                                              (DrugLotMaster.expiry_date == expiry_date)
                                              )
            return lot_drug_dict
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
