from typing import Dict, List, Any

from peewee import PrimaryKeyField, CharField, fn, DoesNotExist, IntegrityError, InternalError, DataError, \
    JOIN_LEFT_OUTER, IntegerField, FloatField, DecimalField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.error_handling.error_handler import error

logger = settings.logger


class DrugMaster(BaseModel):
    """
        @class: drug_master.py
        @type: file
        @desc: logical class for table drug_master
    """
    id = PrimaryKeyField()
    drug_name = CharField(max_length=255)
    ndc = CharField(max_length=14, null=True)
    formatted_ndc = CharField(max_length=12, null=True)
    pharmacy_drug_id = CharField(null=True, unique=True)
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
    drug_schedule = IntegerField(null=True, default=None)
    dispense_qty = DecimalField(decimal_places=4, max_digits=7, null=True, default=None)
    package_size = DecimalField(decimal_places=2, max_digits=7, null=True, default=None)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "drug_master"

    @classmethod
    def concated_drug_name_field(cls, include_ndc=False):
        """ Returns CONCAT on drug_name, strength_value, strength """
        if include_ndc:
            return fn.CONCAT(
                cls.drug_name, ' ', cls.strength_value, ' ', cls.strength, ' (', cls.ndc, ')'
            )
        return fn.CONCAT(
            cls.drug_name, ' ', cls.strength_value, ' ', cls.strength
        )

    @classmethod
    def concated_fndc_txr_field(cls, sep='#'):
        """ Returns CONCAT on formatted_ndc, `sep`, txr """
        return fn.CONCAT(
            cls.formatted_ndc, sep, fn.IFNULL(cls.txr, '')
        )

    @classmethod
    def db_get_by_ids(cls, drug_ids):
        try:
            for record in DrugMaster.select() \
                    .where(DrugMaster.id << drug_ids).dicts():
                yield record
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError

    @classmethod
    def db_get_drug_txr_fndc_id(cls, drug_id):
        try:
            drug_master_data = DrugMaster.select(DrugMaster.txr, DrugMaster.formatted_ndc, DrugMaster.id).dicts()\
                .where(DrugMaster.id == drug_id).get()
            return drug_master_data
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_or_create(cls, data, add_fields=None, remove_fields=None,
                            default_data_dict=None, ndc=None, upc=None):
        """

        :param data:
        :param ndc:
        :param upc:
        :param add_fields:
        :param remove_fields:
        :param default_data_dict:
        :return: record, created
        """
        if default_data_dict:
            data.update(default_data_dict)

        # List of fields to be removed from data dictionary
        if remove_fields:
            for item in remove_fields:
                data.pop(item, 0)

        # List of additional fields to be added to data dictionary
        if add_fields:
            data.update(add_fields)

        try:
            if ndc:
                record, created = DrugMaster.get_or_create(ndc=ndc, defaults=data)
                if not created:
                    DrugMaster.update(**data).where(DrugMaster.ndc == ndc).execute()
            else:
                record, created = DrugMaster.get_or_create(upc=upc, defaults=data)
                if not created:
                    DrugMaster.update(**data).where(DrugMaster.upc == upc).execute()

        except DataError as e:
            raise DataError(e)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)
        except Exception as e:
            logger.error("Error in db_update_or_create drug data {}".format(e))
            raise error(1000)
        return record, created

    @classmethod
    def get_drug_image_and_id_from_ndc(cls, ndc):
        """
        This function will be used to check if image name exist for given ndc or not
        :param ndc: NDC for which we need to check if image exist or not
        :return: True/False
        """

        drug_image = False
        drug_id = 0
        print("NDC: ", ndc)
        try:
            for data in DrugMaster.select(DrugMaster.id, DrugMaster.image_name).dicts().where((DrugMaster.ndc == ndc)):
                drug_image = data["image_name"]
                drug_id = data["id"]

        except Exception as e:
            print("Exception is: ", e)
            logger.error(e, exc_info=True)
            return False, drug_id

        if drug_image:
            return True, drug_id
        else:
            return False, drug_id

    @classmethod
    def get_drug_and_bottle_information_by_drug_id(cls, drug_id):
        """
        This function will be used to get information about the drug and its bottle image
        :param drug_id: Drug id for which we need data
        :return: List of drug data
        """
        try:
            query = DrugMaster.select(DrugMaster).dicts().where(DrugMaster.id == drug_id)
            data = query.get()
        except DataError as e:
            raise DataError(e)
        except IntegrityError as e:
            raise InternalError(e)
        except InternalError as e:
            raise InternalError(e)

        return data

    @classmethod
    def get_drugs_by_formatted_ndc_txr(cls, formatted_ndc, txr, dicts=False):
        try:
            query = DrugMaster.select(DrugMaster).where(
                DrugMaster.formatted_ndc == formatted_ndc,
                DrugMaster.txr == txr
            )
            if dicts:
                query = query.dicts()
            for record in query:
                yield record
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_ndc_list_from_fndc_list(cls, formatted_ndc_list):
        try:
            if not formatted_ndc_list:
                return []
            query = DrugMaster.select(DrugMaster.ndc,
                                      DrugMaster.upc).dicts().where(DrugMaster.formatted_ndc << formatted_ndc_list)
            return [(record['ndc'], record['upc']) for record in query]
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_drugs_details_by_ndclist(cls, ndc_list):
        drug_details: list = list()
        try:
            if ndc_list:
                query = DrugMaster.select(DrugMaster.ndc,
                                          DrugMaster.drug_name,
                                          DrugMaster.strength_value,
                                          DrugMaster.strength,
                                          DrugMaster.formatted_ndc,
                                          DrugMaster.txr,
                                          DrugMaster.id.alias("drug_id"),
                                          DrugMaster.pharmacy_drug_id) \
                    .where(DrugMaster.ndc << ndc_list).dicts()
                for record in query:
                    drug_details.append(record)
            return drug_details
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            return None

    @classmethod
    def get_drugs_details_by_upclist(cls, upc_list):
        drug_details: list = list()
        try:
            if upc_list:
                query = DrugMaster.select(DrugMaster.ndc,
                                          DrugMaster.drug_name,
                                          DrugMaster.strength_value,
                                          DrugMaster.strength,
                                          DrugMaster.formatted_ndc,
                                          DrugMaster.txr,
                                          DrugMaster.upc,
                                          DrugMaster.id.alias("drug_id")) \
                    .where(DrugMaster.upc << upc_list).dicts()
                for record in query:
                    drug_details.append(record)
            return drug_details
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            return None

    @classmethod
    def db_update_and_get(cls, data, add_fields=None, remove_fields=None,
                          default_data_dict=None, ndc=None, upc=None):
        """

        :param data:
        :param ndc:
        :param upc:
        :param add_fields:
        :param remove_fields:
        :param default_data_dict:
        :return: record, created
        """
        if default_data_dict:
            data.update(default_data_dict)

        # List of fields to be removed from data dictionary
        if remove_fields:
            for item in remove_fields:
                data.pop(item, 0)

        # List of additional fields to be added to data dictionary
        if add_fields:
            data.update(add_fields)

        try:
            if ndc:
                record = DrugMaster.select().where(DrugMaster.ndc == ndc).get()
                DrugMaster.update(**data).where(DrugMaster.ndc == ndc).execute()
                return True, record
            else:
                record = DrugMaster.select().where(DrugMaster.upc == upc).get()
                DrugMaster.update(**data).where(DrugMaster.upc == upc).execute()
                return True, record

        except DataError as e:
            logger.error("Error in db_update_and_get drug data {}".format(e))
            raise DataError(e)
        except IntegrityError as e:
            logger.error("Error in db_update_and_get drug data {}".format(e))
            raise InternalError(e)
        except InternalError as e:
            logger.error("Error in db_update_and_get drug data {}".format(e))
            raise InternalError(e)
        except DoesNotExist as e:
            logger.error("Error in db_update_and_get drug data {}".format(e))
            return False, None
        except Exception as e:
            logger.error("Error in db_update_and_get drug data {}".format(e))
            raise error(1000)

    @classmethod
    def db_get_drug_data_based_on_ndc(cls, ndc_list: List[str]) -> Dict[str, Any]:
        """
        Class method to get drug data based on ndc
        @param ndc_list:
        @return:
        """
        logger.debug("In db_get_drug_data_based_on_ndc")
        result_dict: Dict[str, Any] = dict()
        try:
            query = cls.select().dicts().where(cls.ndc.in_(ndc_list))
            for record in query:
                result_dict[record["ndc"]] = record
            print("===================", result_dict)
            return result_dict
        except (DataError, IntegrityError, InternalError) as e:
            print(e)
            raise e

    @classmethod
    def db_get_drug_data_by_ndc_parser(cls, ndc_list):
        try:
            return DrugMaster.select().dicts().where(DrugMaster.ndc << ndc_list)
        except (DataError, IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def update_txr_by_ndc(cls, txr: str, ndc: str) -> bool:
        """
        Class method to update the txr by ndc.
        @param txr:
        @param ndc:
        @return:
        """
        try:
            cls.update(txr=txr).where(cls.ndc == ndc).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def udpate_bottle_qty(cls, qty: str, ndc: str) -> bool:
        try:
            cls.update(bottle_quantity=qty).where(cls.ndc == ndc).execute()
            return True
        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def fetch_drug_bottle_qty(cls, ndc: list):
        try:
            bottle_qty_dict = {}
            query = cls.select(cls.ndc, cls.bottle_quantity).dicts().where(cls.ndc << ndc)
            for record in query:
                if str(record['ndc']).zfill(11) not in bottle_qty_dict.keys():
                    if record['bottle_quantity']:
                        bottle_qty_dict[str(record['ndc']).zfill(11)] = record['bottle_quantity']

            return bottle_qty_dict

        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_image_name_in_drug_master(cls, image_url, drug_list):
        try:
            cls.update(image_name=image_url) \
                .where(cls.id << drug_list)
        except (IntegrityError, InternalError) as e:
            logger.error("Error in update_drug_name_in_drug_master".format(e))
            raise e
        except Exception as e:
            logger.error(f"Error in update_drug_name_in_drug_master:{e}")

    @classmethod
    def db_get_txr_and_drug_id_by_ndc(cls, ndc):
        try:
            logger.info("Inside db_get_txr_and_drug_id_by_ndc with ndc: {}".format(ndc))
            query = DrugMaster.select(DrugMaster.txr, DrugMaster.id).where(DrugMaster.ndc == ndc).dicts().get()
            return query["txr"], query["id"]
        except Exception as e:
            logger.error("Error in db_get_txr_by_ndc".format(e))
            raise e

    @classmethod
    def db_get_drug_id_dict_by_ndc_list(cls, ndc: list):
        try:
            ndc_drug = {}
            logger.info("Inside db_get_txr_and_drug_id_by_ndc with ndc: {}".format(ndc))
            query = DrugMaster.select(DrugMaster.ndc, DrugMaster.id).where(DrugMaster.ndc << ndc).dicts()

            for drug in query:
                ndc_drug[drug["ndc"]] = drug["id"]
            return ndc_drug
        except Exception as e:
            logger.error("Error in db_get_txr_by_ndc".format(e))
            raise e

    @classmethod
    def db_get_txr_by_drug_id(cls, drug_id):
        try:
            logger.info("Inside db_get_txr_by_drug_id with drug_id {}".format(drug_id))
            query = DrugMaster.select(DrugMaster.txr).where(DrugMaster.id == drug_id).dicts().get()
            return query["txr"]
        except Exception as e:
            logger.error("Error in db_get_txr_by_drug_id".format(e))
            raise e

    @classmethod
    def db_get_multiple_txr_by_drug_id(cls, drug_ids):
        try:
            logger.info("Inside db_get_multiple_txr_by_drug_id with drug_ids {}".format(drug_ids))
            query = DrugMaster.select(DrugMaster.txr).where(DrugMaster.id << drug_ids).dicts()
            txr_list = list()
            for record in query:
                if record["txr"] not in txr_list:
                    txr_list.append(record["txr"])

            return txr_list
        except Exception as e:
            logger.error("Error in db_get_multiple_txr_by_drug_id".format(e))
            raise e

    @classmethod
    def db_get_brand_flag_and_fndc_by_drug_id(cls, drug_id):
        try:
            logger.info("In db_get_brand_flag_by_drug_id with drug_ids: {}".format(drug_id))
            query = DrugMaster.select(DrugMaster.formatted_ndc,
                                      DrugMaster.brand_flag).where(DrugMaster.id == drug_id).dicts().get()
            return query["brand_flag"], query["formatted_ndc"]
        except Exception as e:
            logger.error("Error in db_get_brand_flag_by_drug_id: {}".format(e))
            raise e

    @classmethod
    def db_get_drug_master_data_by_drug_id(cls, drug_id):
        try:
            logger.info("In db_get_drug_master_data_by_drug_id with drug_id: {}".format(drug_id))
            query = (DrugMaster.select(DrugMaster,
                                       DrugMaster.concated_drug_name_field(include_ndc=True).alias("drug_image_name")
                                       )
                     .where(DrugMaster.id == drug_id).dicts())

            return query
        except Exception as e:
            logger.error("Error in db_get_drug_master_data_by_drug_id: {}".format(e))
            raise e

