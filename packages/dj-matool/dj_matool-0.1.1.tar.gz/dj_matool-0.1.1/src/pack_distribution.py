# from datetime import timedelta, datetime

from peewee import (
    InternalError, IntegrityError, DataError
)

import settings
from dosepack.error_handling.error_handler import create_response, error
from dosepack.utilities.utils import log_args_and_response
from dosepack.validation.validate import validate

from src.dao.pack_analysis_dao import update_pack_analysis_canisters_data

logger = settings.logger

########################################################################################################################
# ==================================================================================================================== #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Distribution Implementation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# =================================== should override above implemenation ============================================ #
########################################################################################################################

# def save_alternate_drug(company_id, pack_list, user_id, zone_old_new_drug_dict, zone):
#     """
#     This function save the alternate drug from available options.
#     :param company_id:
#     :param pack_list:
#     :param user_id:
#     :return:
#     """
#
#     olddruglist = list(zone_old_new_drug_dict[zone].keys())
#     newdruglist = list(zone_old_new_drug_dict[zone].values())
#     list(map(int, olddruglist))
#
#     dict_alternate_drug_info = {"olddruglist": olddruglist, "newdruglist": newdruglist,
#                                 "company_id": company_id, "user_id": user_id,
#                                 "pack_list": pack_list}
#     response = alternate_drug_update_facility(dict_alternate_drug_info)
#     return response


# def on_file_change():
#
#     with open('output.json') as outfile:
#         feeds = json.load(outfile)
#     feeds[get_current_date_time()] = json_data
#     with open('output.json', 'w') as outfile:
#         json.dump(feeds, outfile, cls=SetEncoder, indent=2)
#     return "data added"
