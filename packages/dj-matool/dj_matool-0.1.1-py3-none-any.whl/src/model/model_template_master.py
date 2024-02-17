from typing import Optional, Dict, Any, List

from kombu.exceptions import OperationalError
from peewee import PrimaryKeyField, IntegerField, ForeignKeyField, SmallIntegerField, DateTimeField, BooleanField, \
    CharField, IntegrityError, InternalError, DoesNotExist, fn, DateField

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import get_current_date_time
from src import constants
from src.model.model_code_master import CodeMaster
from src.model.model_file_header import FileHeader
from src.model.model_patient_master import PatientMaster


logger = settings.logger


class TemplateMaster(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    system_id = IntegerField(null=True)
    patient_id = ForeignKeyField(PatientMaster)
    file_id = ForeignKeyField(FileHeader)
    status = ForeignKeyField(CodeMaster)
    is_modified = SmallIntegerField()
    delivery_datetime = DateTimeField(null=True, default=None)
    fill_manual = BooleanField(default=False)  # for marking packs manual generated from template
    task_id = CharField(max_length=155, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateTimeField(default=get_current_date_time)
    modified_date = DateTimeField(default=get_current_date_time)
    reason = CharField(max_length=255, null=True)
    with_autoprocess = BooleanField(default=False)
    fill_start_date = DateField()
    fill_end_date = DateField()
    pharmacy_fill_id = IntegerField()
    pack_type = ForeignKeyField(CodeMaster, related_name='pack_fill_type', null=True, default=constants.MULTI_DOSE_PER_PACK)
    customized = BooleanField(default=False)
    true_unit = BooleanField(default=False)
    seperate_pack_per_dose = BooleanField(default=False)
    is_bubble = BooleanField(default=False)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "template_master"

    IS_MODIFIED_MAP = {
        'RED': 1,
        'YELLOW': 2,
        'GREEN': 0
    }

    @classmethod
    def db_update_status_with_id(cls, template_id, update_dict):
        """ Updates the status of given template_id

            Args:
                template_id (int): The template id for which the template status is to be updated.
                update_dict (dict): update dict

            Returns:
                Boolean: Returns True if the status of the template got updated successfully else False.

            Examples:
                >>> TemplateMaster.db_update_status_with_id(1, 1)
                >>> True

        """
        try:
            logger.info('Update_template_master_status: update_dict: {}, template_id {} '.format(update_dict, template_id))
            status = cls.update(**update_dict).where(cls.id == template_id).execute()
            logger.info('Updated_template_master_status: status: {}, template_id {} '.format(status, template_id))
            return status
        except (InternalError, IntegrityError, OperationalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_is_pending(cls, file_id, patient_id):
        """
        Returns True if template is present and is in pending state, False otherwise
        """
        try:
            template = cls.select(
                cls.status
            ).where(
                cls.file_id == file_id,
                cls.patient_id == patient_id
            ).dicts().get()
            logger.info("checking pending file: " + str(file_id) + "and patient_id: " + str(patient_id))
            return template['status'] in settings.PENDING_PROGRESS_TEMPLATE_LIST
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return False

    @classmethod
    def db_update_modification_status(cls, patient_id, file_id, is_modified_status,
                                      template_status: Optional[int] = settings.PENDING_TEMPLATE_STATUS):
        """ Updates the is_modified status of the template based on the input patient_id

                Args:
                    patient_id (int): The id of the patient whose status is to be updated.
                    file_id (int): The id of file
                    is_modified_status (int): Template Modification status
                    template_status (int): Template Status for Change Rx

                Returns:
                    Boolean: Returns True if the status of the template got updated successfully else False.

                Examples:
                    >>> TemplateMaster.db_update_modification_status()
                    >>> True

        """
        try:
            update_template_dict: Dict[str, Any] = {"is_modified": is_modified_status}

            logger.info('changing_is_modified_for patient_id: ' + str(patient_id) + 'file_id: ' + str(file_id) +
                        'with value:  ' + str(is_modified_status))

            if template_status in [settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_TEMPLATE,
                                   settings.PENDING_CHANGE_RX_TEMPLATE_STATUS_PACK]:
                logger.info('Updating Template Status as {}...'.format(template_status))
                update_template_dict.update({"status": template_status})

            status = TemplateMaster.update(**update_template_dict) \
                .where(TemplateMaster.patient_id == patient_id,
                       TemplateMaster.file_id == file_id).execute()
            logger.info('patient_id: ' + str(patient_id) + 'file_id: ' + str(file_id) + 'is_modified ' + str(status))
            return create_response(status)
        except InternalError as e:
            logger.error(e, exc_info=True)
            return error(2002)
        except IntegrityError as e:
            logger.error(e, exc_info=True)
            return error(2002)

    @classmethod
    def db_update_pending_progress_templates_by_status(cls, status, reason, user_id, template_ids, company_id):
        try:
            query = TemplateMaster.update(
                status=status,
                reason=reason,
                modified_by=user_id,
                modified_date=get_current_date_time()
            ).where(TemplateMaster.id << template_ids,
                    TemplateMaster.company_id == company_id,
                    TemplateMaster.status << settings.PENDING_PROGRESS_TEMPLATE_LIST)
            status = query.execute()
            return status
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_status(cls, file_id, patient_id):
        """ Returns the status of the template if it has been modified or not.

                Args:
                    file_id (int): The file id associated with the current patient id
                    patient_id (int): The id of the patient whose status is to be updated.

                Returns:
                    Boolean: Returns True if template is modified otherwise False

                Examples:
                    >>> TemplateMaster.db_get_status(1, 1)
                    >>> True

        """
        try:
            status = cls.get(patient_id=patient_id, file_id=file_id).is_modified
            return status
        except (InternalError, IntegrityError, DoesNotExist, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_templates_for_file_patient_ids(cls, file_ids, patient_ids):
        template_dict: List[Dict[str, Any]] = []
        try:
            query = TemplateMaster.select(TemplateMaster).dicts()\
                .where(TemplateMaster.file_id << file_ids, TemplateMaster.patient_id << patient_ids)

            for template in query:
                template_dict.append(template)

            return template_dict
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_template_count_by_status(cls, file_id, status):
        try:
            template_query = cls.select(fn.count(cls.id).alias('number_of_template')).dicts() \
                .where(cls.file_id == file_id,
                       cls.status << status).get()
            count = template_query['number_of_template']
            return count
        except DoesNotExist as e:
            logger.info("No processed templates for file_id: {}".format(file_id))
            count = 0
            return count
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_file_ids(cls, file_ids, status):
        try:
            template_query = cls.select(cls.file_id).dicts() \
                .where(cls.file_id << file_ids,
                       cls.status << status)
            file_ids = set()
            for template in template_query:
                file_ids.add(template['file_id'])
            return file_ids
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_file_id_from_template_ids(cls, template_ids, status):
        try:
            template_query = cls.select(cls.file_id).dicts() \
                .where(cls.id << template_ids,
                       cls.status == status)
            file_ids = set()
            for template in template_query:
                file_ids.add(template['file_id'])
            return file_ids
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_verify_templatelist(cls, templatelist, company_id, status):
        """ Returns True if template list is generated for given company_id and having particular status,
            False otherwise

        :param templatelist:
        :param company_id:
        :param status:
        :return: Boolean
        """
        company_id = int(company_id)
        try:
            template_count = cls.select().where(
                cls.id << templatelist,
                cls.company_id == company_id,
                cls.status << status

            ).count()
            if template_count == len(set(templatelist)):
                return True
            return False
        except (InternalError, IntegrityError, DoesNotExist, Exception) as e:
            logger.error(e, exc_info=True)
            return False

    @classmethod
    def db_get_template_master_by_patient_and_file(cls, patient_id, file_id):
        try:
            return TemplateMaster.select().dicts()\
                .where(TemplateMaster.file_id == file_id, TemplateMaster.patient_id == patient_id).get()
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return {}
        except (InternalError, IntegrityError, DoesNotExist, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def is_other_template_pending(cls, file_id, patient_id):
        """"""
        try:
            pending_templates = cls.select().dicts() \
                .where(cls.status << settings.PENDING_PROGRESS_TEMPLATE_LIST,
                       cls.patient_id == patient_id,
                       cls.file_id != file_id,
                       cls.is_modified != 0).count()
            return pending_templates
        except DoesNotExist as e:
            return 0
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            return error(2001)

    @classmethod
    def db_get_file_id(cls, patient_id, status):
        try:
            template_query = cls.select(cls.file_id, cls.status).dicts() \
                .where(cls.patient_id == patient_id,
                       cls.status << status).order_by(cls.created_date).get()
            logger.info("in db_get_file_id : cls.status {} ".format(template_query["status"]))
            return template_query['file_id']
        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return None
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_template_admin_duration(cls, patient_id, file_id):
        temp_slot_data_list: List[Dict[str, Any]] = []
        try:
            temp_data = TemplateMaster.select(TemplateMaster.fill_start_date, TemplateMaster.fill_end_date).dicts() \
                .where(TemplateMaster.patient_id == patient_id, TemplateMaster.file_id == file_id) \
                .group_by(TemplateMaster.patient_id, TemplateMaster.file_id)

            for record in temp_data:
                temp_slot_data_list.append(record)
            return temp_slot_data_list

        except DoesNotExist as e:
            logger.error(e, exc_info=True)
            return []
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_template_id(cls, file_id, patient_id):
        """
        Returns template data if template is present, {} otherwise
        """
        logger.info("checking template data: " + str(file_id) + "and patient_id: " + str(patient_id))
        try:
            template = cls.select(cls.id, cls.status)\
                .where(cls.file_id == file_id, cls.patient_id == patient_id)\
                .dicts().get()
            return {'id': template['id'],
                    'status': template['status']}
        except DoesNotExist as e:
            return {}
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_template_master_info_by_template_id(cls, template_id):
        template_dict: Dict[str, Any] = {}
        try:
            template_query = TemplateMaster.select(TemplateMaster).dicts()\
                .where(TemplateMaster.id == template_id)

            for record in template_query:
                template_dict = record

            return template_dict
        except (IntegrityError, InternalError, Exception) as e:
            logger.error(e, exc_info=True)
            raise
