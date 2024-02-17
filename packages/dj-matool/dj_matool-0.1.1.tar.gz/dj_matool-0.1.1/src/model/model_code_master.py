from peewee import PrimaryKeyField, ForeignKeyField, CharField
import settings
from dosepack.base_model.base_model import BaseModel
from src.model.model_group_master import GroupMaster

logger = settings.logger


class CodeMaster(BaseModel):
    id = PrimaryKeyField()
    group_id = ForeignKeyField(GroupMaster)
    # key = SmallIntegerField(unique=True)
    value = CharField(max_length=50)

    class Meta:
        if settings.TABLE_NAMING_CONVENTION == "_":
            db_table = "code_master"

    # @staticmethod
    # def get_initial_data():
    #     return [
    #         dict(id=1, group_id=1, key=1, value="ALL"),
    #         dict(id=2, group_id=1, key=2, value="Pending"),
    #         dict(id=3, group_id=1, key=3, value="Progress"),
    #         dict(id=4, group_id=1, key=4, value="Processed"),
    #         dict(id=5, group_id=1, key=5, value="Done"),
    #         dict(id=6, group_id=1, key=6, value="Verified"),
    #         dict(id=7, group_id=1, key=7, value="Deleted"),
    #         dict(id=8, group_id=1, key=8, value="Manual"),
    #         dict(id=9, group_id=1, key=9, value="Rolled Back"),
    #         dict(id=10, group_id=2, key=10, value="ALL"),
    #         dict(id=11, group_id=2, key=11, value="Pending"),
    #         dict(id=12, group_id=2, key=12, value="Processed"),
    #         dict(id=13, group_id=2, key=13, value="Error"),
    #         dict(id=14, group_id=2, key=14, value="Rolled Back"),
    #         dict(id=15, group_id=3, key=15, value="ALL"),
    #         dict(id=16, group_id=3, key=16, value="Pending"),
    #         dict(id=17, group_id=3, key=17, value="Done"),
    #         dict(id=18, group_id=3, key=18, value="Rolled Back"),
    #         dict(id=19, group_id=1, key=19, value="Verified With Success"),
    #         dict(id=20, group_id=1, key=20, value="Verified With Failure"),
    #         dict(id=21, group_id=1, key=21, value="Cancelled"),
    #         dict(id=22, group_id=1, key=22, value="InQueue"),
    #         dict(id=23, group_id=1, key=23, value="DispensePending"),
    #         dict(id=24, group_id=1, key=24, value="Dropped"),
    #         dict(id=25, group_id=4, key=25, value="Confirmation Pending"),
    #         dict(id=26, group_id=4, key=26, value="Confirmed"),
    #         dict(id=27, group_id=4, key=27, value="Processing"),
    #         dict(id=28, group_id=4, key=28, value="In Transit"),
    #         dict(id=29, group_id=4, key=29, value="Delivered"),
    #         dict(id=30, group_id=4, key=30, value="Cancelled"),
    #         dict(id=31, group_id=5, key=31, value="proforma_invoice"),
    #         dict(id=32, group_id=5, key=32, value="commercial_invoice"),
    #         dict(id=33, group_id=1, key=33, value="Discarded"),
    #         dict(id=34, group_id=7, key=34, value="Pending"),
    #         dict(id=35, group_id=7, key=35, value="Canister Transfer Recommended"),
    #         dict(id=36, group_id=7, key=36, value="Canister Transfer Done"),
    #         dict(id=37, group_id=7, key=37, value="Imported"),
    #         dict(id=38, group_id=7, key=38, value="Processing Complete"),
    #         dict(id=39, group_id=8, key=39, value="Rejected"),
    #         dict(id=40, group_id=8, key=40, value="Success"),
    #         dict(id=41, group_id=8, key=41, value="Not Confident"),
    #         dict(id=42, group_id=8, key=42, value="Deleted"),
    #         dict(id=43, group_id=8, key=43, value="Missing Pills"),
    #         dict(id=44, group_id=8, key=44, value="Missing and deleted"),
    #         dict(id=45, group_id=1, key=45, value="Processed Manually"),
    #         dict(id=46, group_id=10, key=46, value="Weekly"),
    #         dict(id=47, group_id=10, key=47, value="Bi-weekly"),
    #         dict(id=48, group_id=10, key=48, value="Monthly"),
    #         dict(id=49, group_id=10, key=49, value="Other"),
    #         dict(id=50, group_id=1, key=50, value="Fill Manually"),
    #         dict(id=51, group_id=1, key=51, value="Filled Partially"),
    #         dict(id=52, group_id=12, key=52, value="Pending"),
    #         dict(id=53, group_id=12, key=53, value="Verified"),
    #         dict(id=54, group_id=12, key=54, value="Rejected"),
    #         dict(id=55, group_id=10, key=55, value="In Progress"),
    #         dict(id=56, group_id=10, key=56, value="Pending"),
    #         dict(id=57, group_id=10, key=57, value="Batch Distribution Done"),
    #         dict(id=58, group_id=10, key=58, value="Alternate Saved"),
    #         dict(id=59, group_id=10, key=59, value="Batch Deleted"),
    #         dict(id=60, group_id=10, key=60, value="checked"),
    #         dict(id=61, group_id=10, key=61, value="error"),
    #         dict(id=62, group_id=10, key=62, value="fixed error"),
    #         dict(id=63, group_id=10, key=63, value="filled"),
    #         dict(id=64, group_id=10, key=64, value="deleted"),
    #         dict(id=65, group_id=10, key=65, value="to be delivered"),
    #         dict(id=66, group_id=10, key=66, value="delivered"),
    #         dict(id=67, group_id=10, key=67, value="delivery cancelled"),
    #         dict(id=68, group_id=10, key=68, value="RPH checked and success"),
    #         dict(id=69, group_id=10, key=69, value="RPH reported error"),
    #         dict(id=70, group_id=10, key=70, value="fixed errors"),
    #         dict(id=71, group_id=10, key=71, value="reuse pack"),
    #         dict(id=72, group_id=10, key=72, value="to be delivered"),
    #         dict(id=73, group_id=10, key=73, value="delivered"),
    #         dict(id=74, group_id=10, key=74, value="FacilityDistributionID"),
    #         dict(id=75, group_id=10, key=75, value="BatchID"),
    #     ]