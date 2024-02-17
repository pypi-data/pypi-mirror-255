from peewee import PrimaryKeyField, IntegerField, ForeignKeyField, CharField, BooleanField, DateField, TimeField, \
    DateTimeField, InternalError, IntegrityError, DoesNotExist, DataError

import settings
from dosepack.base_model.base_model import BaseModel
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import get_current_date, get_current_time, get_current_date_time
from src.model.model_code_master import CodeMaster

logger = settings.logger


class FileHeader(BaseModel):
    id = PrimaryKeyField()
    company_id = IntegerField()
    status = ForeignKeyField(CodeMaster)
    filename = CharField(max_length=150)
    filepath = CharField(null=True, max_length=200)
    manual_upload = BooleanField(null=True)  # added - Amisha
    message = CharField(null=True, max_length=500)
    task_id = CharField(max_length=155, null=True)
    created_by = IntegerField()
    modified_by = IntegerField()
    created_date = DateField(default=get_current_date)
    created_time = TimeField(default=get_current_time)
    modified_date = DateTimeField(default=get_current_date_time)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "file_header"

    @classmethod
    def db_update(cls, file_ids, status, message=None):
        """ Updates the status of the file after packs are generated from it.

            Args:
                file_ids (list): The file ids.
                status (int): The status at which the given template ids is to be updated.
                message (str): The message corresponding to the status.

            Returns:
                Boolean: Returns True if the status of the template got updated successfully else False.

            Examples:
                >>> FileHeader.db_update([1, 2], 1)
                >>> True

        """
        try:
            if not message:
                status = FileHeader.update(status=status) \
                    .where(FileHeader.id << file_ids).execute()
            else:
                status = FileHeader.update(status=status, message=message) \
                    .where(FileHeader.id << file_ids).execute()
            return create_response(status)
        except InternalError as e:
            logger.error(e, exc_info=True)
            return error(2002)
        except IntegrityError as e:
            logger.error(e, exc_info=True)
            return error(2002)

    @classmethod
    def db_get_files_by_filename(cls, filename, company_id):
        """ Returns file name and status with it"""
        try:
            data = []
            filename_search_without_extension = filename + "%"
            for record in FileHeader.select() \
                    .dicts() \
                    .where(FileHeader.filename ** filename_search_without_extension,
                           FileHeader.company_id == company_id) \
                    .order_by(FileHeader.id.desc()):
                data.append(record)
            return data
        except (InternalError, IntegrityError) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_file_info_not_ungenerated(cls, company_id, file_ids, status):
        try:
            return FileHeader.select(FileHeader.id).distinct()\
                .where(FileHeader.company_id == company_id, FileHeader.id << file_ids,
                       FileHeader.status != status).dicts()
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_verify_file_id(cls, file_id, company_id):
        """ verifies file is of given company_id
        Returns:
             Boolean: Returns True if file_id was generated for given
             company_id, False otherwise
        """
        try:
            file = FileHeader.get(id=file_id)
            if company_id == file.company_id:
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError as e:
            logger.error(e, exc_info=True)
            return False

    @classmethod
    def db_verify_filelist(cls, filelist, company_id):
        """ Returns True if file list is generated for given company id,
         False otherwise

        :param filelist:
        :param company_id:
        :return: Boolean
        """
        company_id = int(company_id)
        try:
            file_count = FileHeader.select().where(
                FileHeader.id << filelist,
                FileHeader.company_id == company_id
            ).count()
            if file_count == len(set(filelist)):
                return True
            return False
        except DoesNotExist:
            return False
        except InternalError:
            return False

    @classmethod
    def db_get_file_by_filename_status_company(cls, filename, status, company_id):
        try:
            return FileHeader.select(FileHeader.id) \
                .where(FileHeader.filename == filename,
                       FileHeader.status << status,
                       FileHeader.company_id == company_id) \
                .order_by(FileHeader.id).dicts().get()

        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_get_or_create(cls, filename, status, file_dict):
        try:
            return FileHeader.get_or_create(
                filename=filename, status=status,
                defaults=file_dict
            )
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_file_status_message_path(cls, status, message, filepath, file_id):
        try:
            return FileHeader.update(status=status, message=message, filepath=filepath)\
                .where(FileHeader.id == file_id).execute()
        except (InternalError, IntegrityError, DataError, Exception) as e:
            logger.error(e, exc_info=True)
            raise

    @classmethod
    def db_update_task_id(cls, file_id, task_id):
        try:
            status = FileHeader.update(task_id=task_id) \
                .where(FileHeader.id == file_id).execute()

            return create_response(status)
        except InternalError as e:
            logger.error(e, exc_info=True)
            return error(2002)
        except IntegrityError as e:
            logger.error(e, exc_info=True)
            return error(2002)

    @classmethod
    def db_get_file_upload_data(cls, file_id):
        try:
            return FileHeader.select(FileHeader.created_date, FileHeader.created_time, FileHeader.created_by
                                     ).where(FileHeader.id == file_id).get()
        except (InternalError, IntegrityError, Exception) as e:
            logger.error(e, exc_info=True)
            raise e
