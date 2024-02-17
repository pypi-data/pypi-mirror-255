from peewee import CharField, BooleanField, \
    IntegerField, ForeignKeyField, DateTimeField, \
    PrimaryKeyField, InternalError, DoesNotExist, IntegrityError, \
    DecimalField, fn, DataError
import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.utilities.utils import get_current_date_time
from src.model.model_configuration_master import ConfigurationMaster
from src.model.model_canister_master import CanisterMaster
from src.model.model_location_master import LocationMaster
from src.model.model_drug_master import DrugMaster
from src.model.model_pack_details import PackDetails
from src.model.model_slot_details import SlotDetails

logger = settings.logger


class SlotTransaction(BaseModel):
    id = PrimaryKeyField()
    pack_id = ForeignKeyField(PackDetails)
    slot_id = ForeignKeyField(SlotDetails)
    # robot_id = ForeignKeyField(RobotMaster, null=True)
    drug_id = ForeignKeyField(DrugMaster, related_name="SlotTransaction_drug_id")
    canister_id = ForeignKeyField(CanisterMaster, related_name="SlotTransaction_canister_id", null=True)
    # canister_number = SmallIntegerField(null=True)
    alternate_drug_id = ForeignKeyField(DrugMaster, null=True, related_name="SlotTransaction_alt_drug_id")
    alternate_canister_id = ForeignKeyField(CanisterMaster, null=True, related_name="SlotTransaction_alt_canister_id")
    dropped_qty = DecimalField(decimal_places=2, max_digits=4, null=True)
    mft_drug = BooleanField(default=False)
    IPS_update_alt_drug = BooleanField(null=True)
    IPS_update_alt_drug_error = CharField(null=True, max_length=150)
    location_id = ForeignKeyField(LocationMaster)
    config_id = ForeignKeyField(ConfigurationMaster, null=True)
    created_by = IntegerField()
    created_date_time = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "slot_transaction"

    @classmethod
    def db_get_distinct_canister_from_slot_transaction(cls):
        """
        get unique canister from slot transaction data
        :return:
        """
        try:
            query = SlotTransaction.select(SlotTransaction.canister_id).distinct().dicts()
            return query
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e


    @classmethod
    def db_delete_slot_transaction(cls, pack_id):
        """
        Deletes slot transaction for pack id

        :param pack_id:
        :return: int
        """
        try:
            status = SlotTransaction.delete().where(SlotTransaction.pack_id == pack_id).execute()
            return status
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_last_used_data_time_by_canister_id_list(cls, canister_id_list):
        """

        :param canister_id_list:
        :return:
        """
        db_result = dict()

        for canister_id in canister_id_list:
            try:
                last_time_used_data = SlotTransaction.select(SlotTransaction.created_date_time).where(
                    (SlotTransaction.canister_id == canister_id)).order_by(SlotTransaction.created_date_time).get()

                db_result[canister_id] = last_time_used_data.created_date_time
            except DoesNotExist as e:
                db_result[canister_id] = None

        return db_result

    @classmethod
    def get_packs_processed_by_robot(cls, track_date, offset):
        """
        @param track_date: date
        @param offset: for timezone conversion
        :return:
        """
        try:
            logger.info("In get_packs_processed_by_robot")
            query = SlotTransaction.select(fn.COUNT(fn.distinct(SlotTransaction.pack_id)).alias("pack_count")).dicts() \
                .where(fn.DATE(fn.CONVERT_TZ(SlotTransaction.created_date_time, settings.TZ_UTC,
                                             offset)) == track_date)

            logger.info("In get_packs_processed query:{}".format(query))

            return query.scalar()

        except (InternalError, IntegrityError, DataError, DoesNotExist) as e:
            logger.error("error in get_packs_processed {}".format(e))
            raise e
        except Exception as e:
            logger.error("error in get_packs_processed {}".format(e))
            raise e


