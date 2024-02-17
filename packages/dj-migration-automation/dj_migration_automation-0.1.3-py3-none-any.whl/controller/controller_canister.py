"""
    @file: http_service.py
    @createdBy: Manish Agarwal
    @createdDate: 7/22/2015
    @lastModifiedBy: Manish Agarwal
    @lastModifiedDate: 08/06/2015
    @type: file
    @desc: Contains wrappers for python functions into web services
"""

# class GetCanisterTransfers(object):
#     """
#                @class: GetCanisterTransfers
#                @type: class
#                @param: object
#                @desc: to fetch canister transfers data to and fro from robot and trolley
#     """
#     exposed = True
#
#     # @authenticate(settings.logger)
#     @use_database(db, settings.logger)
#     def GET(self, company_id=None, system_id=None, device_id=None, trolley_id=None, trolley_drawer_id=None,
#             batch_id=None,
#             transfer_to=None, user_id=None, sort_fields=None, **kwargs):
#         if not device_id:
#             return error(1001, "Missing Parameter(s): device_id.")
#         if not trolley_id:
#             return error(1001, "Missing Parameter(s): trolley_id.")
#         if not batch_id:
#             return error(1001, "Missing Parameter(s): batch_id.")
#         if not transfer_to:
#             return error(1001, "Missing Parameter(s): transfer_to.")
#         if not trolley_drawer_id:
#             return error(1001, "Missing Parameter(s): trolley_drawer_id.")
#
#         args = {
#             "company_id": company_id,
#             "system_id": system_id,
#             "transfer_to": transfer_to,
#             "device_id": device_id,
#             "trolley_id": trolley_id,
#             "trolley_drawer_id": trolley_drawer_id,
#             "batch_id": batch_id,
#             "user_id": user_id,
#         }
#
#         if sort_fields:
#             args["sort_fields"] = json.loads(sort_fields)
#
#         response = get_canister_transfers(args)
#         return response


