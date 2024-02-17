# -*- coding: utf-8 -*-
"""
    src.canister
    ~~~~~~~~~~~~~~~~

    This is the core canister module.It contains the set of apis to perform crud
    operations on canisters.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""


# def get_and_format_device_location_data(device_id, location, company_id):
#     response = DeviceLayoutDetails.get_device_by_device_id(device_id=device_id, company_id=company_id)
#     device_data = dict()
#     device_data['company_id'] = response['company_id']
#     device_data['zone_id'] = response['zone_id']
#     device_data['device_name'] = response['name']
#     device_data['device_id'] = response['device_id']
#     device_data['drawer_initials_pattern'] = response['drawer_initials_pattern']
#     zone_data = ZoneMaster.get_zone_data_by_zone_id(zone_id=response['zone_id'], company_id=response['company_id'])
#     device_data['zone_name'] = zone_data['name']
#     device_data['location'] = location
#
#     # total_drawers, canister_per_drawer = get_csr_data_from_couch_db(device_id=response['device_id'],
#     #                                                                 company_id=company_id)
#     total_drawers, canister_per_drawer = 4, 6
#     if total_drawers is not None and canister_per_drawer is not None:
#         device_data['drawer_location'] = device_data['location'] // canister_per_drawer
#         device_data['formatted_location'] = device_data['location'] % canister_per_drawer
#         if device_data['formatted_location'] == 0:
#             device_data['formatted_location'] = canister_per_drawer
#         else:
#             device_data['drawer_location'] += 1
#
#         # Get drawers ip address and drawer id that was registered at the time of device registration.
#         ip_address_data = None
#         try:
#             ip_address_data = CSRDrawers.get_ip_address(device_id=response['device_id'],
#                                                         drawer_number=device_data['drawer_location'])
#         except DoesNotExist:
#             device_data['ip_address'] = None
#             device_data['container_id'] = None
#         if ip_address_data is not None:
#             device_data['ip_address'] = ip_address_data['ip_address']
#             device_data['container_id'] = ip_address_data['container_id']
#     else:
#         # Due to some reason we did not get data from couch db then we will send drawer location and formatted
#         # location as None.
#         device_data['drawer_location'] = None
#         device_data['formatted_location'] = None
#     return device_data


# def add_drug_canister_info_in_odoo(data_dict):
#     # data_dict = json.dumps(data_dict)
#     token_request_data = {
#         'username': settings.INVENTORY_USERNAME,
#         'password': settings.INVENTORY_PASSWORD,
#         'db': settings.INVENTORY_DATABASE_NAME
#     }
#     ACCESS_TOKEN = call_webservice(settings.BASE_URL_INVENTORY, settings.GET_ACCESS_TOKEN, token_request_data,
#                                    request_type="POST", odoo_api=True, use_ssl=settings.ODOO_SSL)
#     if not ACCESS_TOKEN \
#             or not ACCESS_TOKEN[0] or 'error' in ACCESS_TOKEN[1]:
#         return error(4003)
#     ACCESS_TOKEN = ACCESS_TOKEN[1]['access_token']
#
#     logger.info(ACCESS_TOKEN)
#     data = call_webservice(settings.BASE_URL_INVENTORY, settings.CREATE_CANISTER_PACKAGES, data_dict,
#                            request_type="POST", use_ssl=settings.ODOO_SSL,
#                            headers={"Authorization": ACCESS_TOKEN},
#                            odoo_api=True)
#
#     logger.info("data {}".format(data))
#     if data[0]:
#         return True, data
#     else:
#         return False, data


