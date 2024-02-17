from peewee import ForeignKeyField, PrimaryKeyField, BooleanField, InternalError, IntegrityError, DoesNotExist, fn
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_drug_master import DrugMaster
from src.model.model_pack_details import PackDetails
from src.model.model_patient_rx import PatientRx

logger = settings.logger


class PackRxLink(BaseModel):
    id = PrimaryKeyField()
    patient_rx_id = ForeignKeyField(PatientRx)
    pack_id = ForeignKeyField(PackDetails)

    # If original_drug_id is null while alternatendcupdate function
    # then store current drug id as original drug id in pack rx link
    # this is required so we can send the flag of ndc change while printing label
    original_drug_id = ForeignKeyField(DrugMaster, null=True)
    bs_drug_id = ForeignKeyField(DrugMaster, null=True,
                                 related_name='bs_drug_id')  # drug_id selected from batch scheduling logic.
    fill_manually = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "pack_rx_link"

    @classmethod
    def db_get(cls, pack_id):
        """
        Returns pack_rx_link records ids for given pack id
        :param pack_id:
        :return: generator
        """
        try:
            for record in PackRxLink.select().dicts() \
                    .where(PackRxLink.pack_id == pack_id):
                yield record
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def get_no_of_drugs(cls, pack_id):
        no_of_drugs = None
        try:
            for record in PackRxLink.select(fn.Count(PackRxLink.patient_rx_id).alias("totaldrugs")) \
                    .where(PackRxLink.pack_id == pack_id).dicts():
                no_of_drugs = record["totaldrugs"]
            return no_of_drugs
        except DoesNotExist as ex:
            logger.error(ex, exc_info=True)
            raise DoesNotExist
        except InternalError as e:
            logger.error(e, exc_info=True)
            raise InternalError


    @classmethod
    def db_update_pack_rx_link(cls, update_dict: dict, pack_rx_link_id: list) -> bool:
        """
        update patient rx link data by bs drug id
        :return:
        """
        try:
            status = PackRxLink.update(**update_dict).where(PackRxLink.id.in_(pack_rx_link_id)).execute()
            return status
        except (IntegrityError, InternalError) as e:
            logger.error(e, exc_info=True)
            raise e

