"""
    @file: http_service.py
    @createdBy: Manish Agarwal
    @createdDate: 7/22/2015
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 08/06/2015
    @type: file
    @desc: Contains wrappers for python functions into web services
"""


# class GetPackDetailsV2(object):
#     """
#     @class: GetPackDetailsV2
#     @type: class
#     @param: object
#     @desc: Get the pack details for the given pack id and system id.
#     """
#     exposed = True
#
#     @use_database(db, settings.logger)
#     def GET(self, pack_id=None, device_id=None, system_id=None,
#             non_fractional=None, **kwargs):
#         # check if packid is present
#         if pack_id is None or system_id is None:
#             return error(1001, "Missing Parameter(s): pack_id or system_id.")
#         if device_id:
#             device_id = int(device_id)
#         if non_fractional is None:
#             non_fractional = 0
#         non_fractional = bool(int(non_fractional))
#
#         args = {
#             "pack_id": pack_id,
#             "device_id": device_id,
#             "system_id": int(system_id),
#             "non_fractional": non_fractional
#         }
#         response = get_pack_details_v2(args)
#
#         return response



