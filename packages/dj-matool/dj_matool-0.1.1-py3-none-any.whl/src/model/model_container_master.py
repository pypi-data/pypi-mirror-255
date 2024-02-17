import functools
import logging
import operator
from ctypes import cast
from peewee import *
from peewee import PrimaryKeyField, ForeignKeyField, CharField, IntegerField, DateTimeField, fn, \
    IntegrityError, InternalError, DataError, DoesNotExist
from playhouse.shortcuts import cast
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_code_master import CodeMaster
from src.model.model_device_master import DeviceMaster

logger = settings.logger


class ContainerMaster(BaseModel):
    id = PrimaryKeyField()
    device_id = ForeignKeyField(DeviceMaster)
    drawer_name = CharField(max_length=20)
    ip_address = CharField(max_length=20, null=True)
    secondary_ip_address = CharField(max_length=20, null=True)
    mac_address = CharField(max_length=50, null=True)
    secondary_mac_address = CharField(max_length=50, null=True)
    drawer_level = IntegerField(null=True)
    created_by = IntegerField(null=True)
    modified_by = IntegerField(null=True)
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    drawer_type = ForeignKeyField(CodeMaster, related_name="drawer_type", null=True)
    drawer_usage = ForeignKeyField(CodeMaster, related_name="drawer_usage", null=True)
    shelf = IntegerField(null=True)
    serial_number = CharField(max_length=20, null=True, unique=True)
    lock_status = BooleanField(default=False) # True-open and False-close

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "container_master"

        indexes = (
            (('device_id', 'drawer_name', 'ip_address'), True),
        )

    @classmethod
    def concated_drawer_category(cls, sep='_'):
        """ returns concated peewee.Field for format "drawer_size, drawer_type" """
        logger.debug("In concated_drawer_category")
        return cast(fn.CONCAT(cls.drawer_type, sep, cls.drawer_usage), 'CHAR')

    @classmethod
    def insert_drawers_data(cls, drawers_data):
        logger.debug("In insert_drawers_data")
        try:
            query = BaseModel.db_create_record(drawers_data, ContainerMaster, get_or_create=False)
            return True, query.id

        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError

    @classmethod
    def insert_multiple_drawers_data(cls, drawers_data):
        logger.debug("In insert_multiple_drawers_data")
        try:
            query = ContainerMaster.insert_many(drawers_data).execute()

            return True
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DataError as e:
            raise DataError

    @classmethod
    def get_ip_address(cls, device_id, drawer_number):
        logger.debug("In get_ip_address")
        try:
            response = ContainerMaster.select(ContainerMaster.ip_address,
                                              ContainerMaster.secondary_ip_address,
                                              ContainerMaster.device_id).dicts().where(
                ContainerMaster.device_id == device_id, ContainerMaster.drawer_name == drawer_number).get()

            return response
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DoesNotExist as e:
            raise DoesNotExist

    @classmethod
    def get_max_drawer_id(cls):
        logger.debug("In get_max_drawer_id")
        try:
            drawer_id = cls.select(fn.MAX(cls.id)).scalar()
            return drawer_id

        except DoesNotExist as e:
            logger.error(e)
            raise DoesNotExist
        except IntegrityError as e:
            logger.error(e)
            raise IntegrityError
        except InternalError as e:
            logger.error(e)
            raise InternalError

    @classmethod
    def get_drawer_data_for_device(cls, device_id):
        try:
            drawer_list = []
            query = ContainerMaster.select(ContainerMaster.id.alias('trolley_drawer_id'),
                                        ContainerMaster.serial_number,
                                        ContainerMaster.drawer_name.alias('trolley_drawer_number'),
                                        ContainerMaster.shelf,
                                        ContainerMaster.drawer_level,
                                        DeviceMaster.serial_number.alias('device_serial_number')) \
                .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id)\
                .where(ContainerMaster.device_id == device_id) \
                .order_by(ContainerMaster.id)

            for record in query.dicts():
                drawer_list.append(record)
            return drawer_list

        except (InternalError, IntegrityError, DoesNotExist) as e:
            logger.error(e)
            raise

    @classmethod
    def get_drawer_number(cls, drawer_id, device_id):
        logger.debug("In get_drawer_number")
        try:
            response = ContainerMaster.select(ContainerMaster.drawer_name.alias('drawer_number')).dicts().where(
                ContainerMaster.device_id == device_id).get()

            return response

        except DoesNotExist as e:
            raise DoesNotExist
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError

    @classmethod
    def update_lock_status(cls, container_id:int, emlock_status:bool)-> int:
        logger.debug("In update_csr_emlock_status")
        try:
            response = ContainerMaster.update(lock_status=emlock_status)\
                      .where(ContainerMaster.id == container_id).execute()
            return response

        except DoesNotExist as e:
            raise DoesNotExist
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError

    @classmethod
    def get_csr_drawer_data(cls, device_id=None):
        db_result = []
        try:
            if device_id is not None:
                query = ContainerMaster.select().dicts().where(
                    ContainerMaster.device_id == device_id)
            else:
                query = ContainerMaster.select().dicts()
            for device in query:
                db_result.append(device)

            return db_result
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            raise InternalError
        except DoesNotExist as e:
            raise DoesNotExist

    @classmethod
    def db_get_drawer_data_of_device(cls, device_ids: list, shelf_list: list=None) -> list:
        """
        Fetches the container data corresponding to the given device ids
        @param device_ids:
        @param shelf_list:
        @return:
        """
        logger.debug("In db_get_csr_drawer_data")
        try:
            query = ContainerMaster.select(ContainerMaster.id,
                                           ContainerMaster.device_id,
                                           ContainerMaster.drawer_name,
                                           ContainerMaster.ip_address,
                                           ContainerMaster.secondary_ip_address,
                                           ContainerMaster.mac_address,
                                           ContainerMaster.secondary_mac_address,
                                           ContainerMaster.drawer_level,
                                           ContainerMaster.drawer_usage.alias('drawer_type'),
                                           ContainerMaster.drawer_type.alias('drawer_size'),
                                           ContainerMaster.shelf,
                                           ContainerMaster.serial_number
                                           ).dicts().where(ContainerMaster.device_id << device_ids) \
                                        .order_by(ContainerMaster.shelf, ContainerMaster.drawer_level)
            logger.debug(query)
            if shelf_list:
                query = query.where(ContainerMaster.shelf << shelf_list)
            return list(query)
        except IntegrityError as e:
            raise IntegrityError
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            raise DoesNotExist

    @classmethod
    def get_csr_drawer_data_to_hit_webservice(cls, company_id, device_id_list=None, drawer_number_list=None):
        logger.debug("In get_csr_drawer_data_to_hit_webservice")
        db_result = list()
        clauses = list()
        clauses.append((DeviceMaster.company_id == company_id))
        if device_id_list:
            clauses.append((ContainerMaster.device_id << device_id_list))

        if drawer_number_list:
            clauses.append((ContainerMaster.drawer_name << drawer_number_list))
        try:
            query = ContainerMaster.select(ContainerMaster.ip_address,
                                           ContainerMaster.secondary_ip_address,
                                           ContainerMaster.id).dicts() \
                .join(DeviceMaster, on=DeviceMaster.id == ContainerMaster.device_id) \
                .where(functools.reduce(operator.and_, clauses))

            for csr_data in query:
                db_result.append(csr_data)

            return db_result
        except IntegrityError as e:
            logger.error(e, exc_info=True)
            raise IntegrityError
        except InternalError as e:
            raise InternalError

    @classmethod
    def count_big_drawers(cls, device_id):
        """
        To return count of Big Drawers for provided device id
        @param device_id:
        @return:
        """
        logger.debug("In count_big_drawers")
        try:
            query = cls.select(fn.COUNT(cls.device_type).alias('big_drawers')).dicts() \
                .where(cls.drawer_type == settings.SIZE_OR_TYPE["BIG"], cls.device_id == device_id)
            return query
        except (IntegrityError, InternalError) as e:
            logger.error(e)
            raise

    @classmethod
    def count_small_drawers(cls, device_id):
        """
        To return count of Big Drawers for provided device id
        @param device_id:
        @return:
        """
        logger.debug("In count_small_drawers")
        try:
            query = cls.select(fn.COUNT(ContainerMaster.device_type).alias('small_drawers')).dicts() \
                .where(cls.drawer_type == settings.SIZE_OR_TYPE["SMALL"], cls.device_id == device_id)
            return query
        except (IntegrityError, InternalError) as e:
            raise

    @classmethod
    def get_unique_drawer_name(cls, device_id: int) -> list:
        """
        Fetches all the unique drawer_names for the given device id.
        @param device_id:
        @return:
        """
        logger.debug("In get_unique_drawer_name")
        try:
            query = cls.select(fn.DISTINCT(ContainerMaster.drawer_name).alias("unique_drawer_names")).dicts() \
                .where(cls.device_id == device_id).order_by(cls.id)

            response_list = []
            for record in query:
                response_list.append(record["unique_drawer_names"])
            return response_list
        except (IntegrityError, InternalError) as e:
            raise

    @classmethod
    def get_unique_shelf_values(cls, device_id: int) -> list:
        """
        Fetches all the unique shelf values for the given device id.
        @param device_id:
        @return:
        """
        logger.debug("In get_unique_shelf_values")
        try:
            query = cls.select(fn.DISTINCT(ContainerMaster.shelf).alias("unique_shelf_values")).dicts() \
                .where(cls.device_id == device_id).order_by(cls.id)
            response_list = []
            for record in query:
                response_list.append(record["unique_shelf_values"])
            return response_list
        except (IntegrityError, InternalError) as e:
            raise

    @classmethod
    def get_unique_drawer_types(cls, device_id: int) -> list:
        """
        Fetches all the unique drawer type for the given device id.
        @param device_id:
        @return:
        """
        logger.debug("In get_unique_drawer_types")
        try:
            query = cls.select(fn.DISTINCT(ContainerMaster.drawer_usage).alias("unique_drawer_types")).dicts() \
                .where(cls.device_id == device_id).order_by(cls.id)
            response_list = []
            for record in query:
                response_list.append(record["unique_drawer_types"])
            return response_list
        except (IntegrityError, InternalError) as e:
            raise

    @classmethod
    def get_unique_drawer_sizes(cls, device_id: int) -> list:
        """
        Fetches all the unique drawer size for the given device id.
        @param device_id:
        @return:
        """
        logger.debug("In get_unique_drawer_sizes")
        try:
            query = cls.select(fn.DISTINCT(ContainerMaster.drawer_type).alias("unique_drawer_sizes")).dicts() \
                .where(cls.device_id == device_id).order_by(cls.id)
            response_list = []
            for record in query:
                response_list.append(record["unique_drawer_sizes"])
            return response_list
        except (IntegrityError, InternalError) as e:
            raise

    @classmethod
    def db_verify_drawer_name_by_device(cls, drawer_name: str, device_id: int) -> bool:
        """
        validate if the given drawer belongs to the given device.
        @param drawer_name:
        @param device_id:
        @return:
        """
        logger.debug("In db_verify_drawer_name_by_device")
        try:
            device_id = int(device_id)
            drawer_name = drawer_name
            container = ContainerMaster.get(drawer_name=drawer_name)
            print(container.device_id_id)
            if device_id == container.device_id_id:
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def get_container_id_from_drawer_name_and_device_id(cls, drawer_name_list: list, device_id: int) -> list:
        """
        get the container_id for the given drawer_name and device_id
        @param drawer_name_list: list
        @param device_id: int
        @return: list
        """
        logger.debug("In get_container_id_from_drawer_name_and_device_id")
        try:
            query = cls.select(cls.id).dicts().where(cls.drawer_name << drawer_name_list,
                                                                 cls.device_id == device_id)

            container_id_list = []
            for record in query:
                container_id_list.append(record["id"])
            return container_id_list
        except (IntegrityError, InternalError, DoesNotExist) as e:
            logger.debug(e)
            raise

    @classmethod
    def db_get_container_data_based_on_container_serial_numbers(cls, container_serial_numbers: list) -> list:
        try:
            query = ContainerMaster.select().dicts().where(ContainerMaster.serial_number << container_serial_numbers)
            return list(query)
        except (IntegrityError, InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_device_by_container_id(cls, container_id: int) -> int:
        try:
            query = ContainerMaster.select(ContainerMaster.device_id).dicts().where(ContainerMaster.id == container_id)
            return query

        except (IntegrityError, InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_drawer_data(cls, drawer_id: int) -> dict:
        """
            @param drawer_id: integer
            @desc: To get drawer data using drawer_id
            @return: dictionary
        """
        logger.debug("In deb_get_drawer_data")
        try:
            query = ContainerMaster.select().where(ContainerMaster.id == drawer_id).dicts()
            for record in query:
                return record
        except (IntegrityError, InternalError, DoesNotExist) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_update_drawer_ip_by_drawer_name(cls, canister_drawer_data, ip_address, drawer_size):
        try:
            status = ContainerMaster.update(ip_address=ip_address, drawer_size=drawer_size)\
                .where(ContainerMaster.device_id == canister_drawer_data["device_id"],
                       ContainerMaster.drawer_name == canister_drawer_data["drawer_number"]).execute()
            return status
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    def db_delete_canister_drawer_by_drawer_name(cls, canister_drawer_data):
        try:
            status = ContainerMaster.delete()\
                .where(ContainerMaster.device_id == canister_drawer_data["device_id"],
                       ContainerMaster.drawer_name == canister_drawer_data["drawer_number"]).execute()
            return status
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
