import settings

logger = settings.logger


# @validate(required_fields=["pack_display_id", "technician_fill_status", "technician_user_name",
#                            "technician_status_datetime"])
# def ext_update_pack_fill_status(pack_info):
#     """
#     Creates pack details info from IPS or External software if not already exists
#     :param pack_info: dict
#     :return: str
#     """
#     try:
#         record = ExtPackDetails.db_update_or_create(
#             pack_info["pack_display_id"],
#             pack_info["pack_id"],
#             pack_info["technician_fill_status"],
#             pack_info["technician_user_name"],
#             pack_info["technician_status_datetime"]
#         )
#         return create_response(record.id)
#     except (IntegrityError, InternalError) as e:
#         logger.error(e, exc_info=True)
#         return error(2001)
#
# @validate(required_fields=["pack_display_id", "delivery_status", "delivery_change_user_name",
#                            "delivery_status_datetime"])
# def ext_update_delivery_status(pack_info):
#     """
#     Creates pack details info from IPS or External software if not already exists
#     :param pack_info: dict
#     :return: str
#     """
#     try:
#         record = ExtPackDetails.db_update_or_create(
#             pack_info["pack_display_id"],
#             pack_info["pack_id"],
#             pack_info["delivery_status"],
#             pack_info["delivery_change_user_name"],
#             pack_info["delivery_status_datetime"]
#         )
#         return create_response(record.id)
#     except (IntegrityError, InternalError) as e:
#         logger.error(e, exc_info=True)
#         return error(2001)


# @validate(required_fields=["pack_display_ids", "technician_fill_status", "technician_fill_comment",
#                            "technician_user_name", "company_id"])
# @log_args_and_response
# def update_ext_pack_status(request_args):
#     """
#     Performs template rollback for given pack_display_ids
#     :param request_args: dict
#     :return: str
#     """
#     pack_display_ids = list(set(request_args['pack_display_ids']))
#     ips_username = request_args['technician_user_name']
#     company_id = request_args["company_id"]
#     technician_fill_status = int(request_args["technician_fill_status"])
#     reason = request_args.get('technician_fill_comment')
#     template_dict = {"company_id": request_args["company_id"], "reason": reason}
#     invalid_pack_display_ids = set()
#     valid_pack_display_ids = set()
#     template_list = list()
#     template_dict["template_ids"] = list()
#     rolled_back_or_processed_templates = list()
#     ext_pack_list = list()
#     file_ids = list()
#     patient_ids = list()
#     available_pack_display_ids = list()
#     pack_dict = dict()
#     file_patient_dict = dict()
#     pack_display_ids_having_packs = list()
#
#     try:
#         if not technician_fill_status == constants.EXT_PACK_STATUS_CODE_DELETED:
#             if not reason:
#                 reason = 'Deleted from Pharmacy Software'
#
#             if not pack_display_ids:
#                 logger.error("empty pack_display_ids")
#                 return error(1035, 'pack_display_ids.')
#
#             logger.info("validating template data for given pack_display_ids {} in company {}".format(
#                 str(pack_display_ids), str(company_id)))
#             # fetch and validate template ids based on pack display id,
#             # fetch template id based on pharmacy_fill_id which is same as given pack_display_id
#             temp_slot_data = TempSlotInfo.db_get_temp_data_based_on_pharmacy_fill_ids(
#                 pharmacy_fill_ids=pack_display_ids)
#
#             for record in temp_slot_data:
#                 file_ids.append(record["file_id"])
#                 patient_ids.append(record["patient_id"])
#                 available_pack_display_ids.append(record["pharmacy_fill_id"])
#                 pack_dict[record["pharmacy_fill_id"]] = record["file_id"], record["patient_id"]
#
#             logger.info("available_pack_display_ids: " + str(available_pack_display_ids))
#             invalid_pack_display_ids = set(pack_display_ids).difference(available_pack_display_ids)
#             logger.info("received valid pack ids: " + str(set(pack_display_ids).difference(invalid_pack_display_ids)))
#
#             if file_ids and patient_ids:
#                 template_list = TemplateMaster.db_get_templates_for_file_patient_ids(file_ids=file_ids,
#                                                                                      patient_ids=patient_ids,
#                                                                                      status=[
#                                                                                          settings.PENDING_TEMPLATE_STATUS,
#                                                                                          settings.PROGRESS_TEMPLATE_STATUS])
#
#             for template in template_list:
#                 template_dict["template_ids"].append(template["id"])
#                 file_patient_dict[(template["file_id"], template["patient_id"])] = template
#             logger.info("valid template ids {} for given pack ids: {} ".format(str(template_dict["template_ids"]),
#                                                                                str(pack_display_ids)))
#             # fetch userid based on ips_username
#             user_info = get_userid_by_ext_username(ips_username, company_id)
#             if user_info and "id" in user_info:
#                 user_id = template_dict["user_id"] = user_info["id"]
#             else:
#                 logger.error("Error while fetching user_info for technician_user_name {}".format(ips_username))
#                 return error(8005)
#             logger.info("userinfo: {} for ips_username: {}".format(user_info, ips_username))
#
#             # save data in ext_pack_details
#             for display_id in available_pack_display_ids:
#                 if file_patient_dict and pack_dict[display_id] in file_patient_dict.keys():
#                     ext_dict = {"pack_id": None,
#                                 "template_id": file_patient_dict[pack_dict[display_id]].get("id"),
#                                 "status_id": file_patient_dict[pack_dict[display_id]].get("status"),
#                                 "ext_pack_display_id": display_id,
#                                 "ext_status_id": constants.EXT_PACK_STATUS_CODE_DELETED,
#                                 "ext_comment": reason,
#                                 "ext_company_id": company_id,
#                                 "ext_user_id": user_id,
#                                 "ext_created_date": get_current_date_time()}
#                     ext_pack_list.append(ext_dict)
#                 else:
#                     pack_display_ids_having_packs.append(display_id)
#
#             ext_data_update_flag = save_ext_pack_data(data_list=ext_pack_list)
#
#             if file_patient_dict:
#                 # rollback given template ids
#                 logger.info("ungenerating templates: " + str(template_dict["template_ids"]))
#                 response = json.loads(rollback_templates(template_dict))
#                 logger.info("response of rollback_templates: " + str(response))
#
#                 if response["status"] == settings.FAILURE_STATUS and response["code"] == 5005:
#                     logger.error(
#                         "Templates {} already rolled back or processed".format(str(template_dict["template_ids"])))
#                     return error(5003)
#                 elif response["status"] == settings.FAILURE_STATUS and response["code"] == 2001:
#                     logger.error("Internal SQL Error while ungenerating templates")
#                     return response
#
#                 if "data" in response and response["data"]:
#                     logger.info("updating couch-db for rolled back templates from ips")
#                     real_time_db_timestamp_trigger(settings.CONST_TEMPLATE_MASTER_DOC_ID, company_id=company_id)
#                     logger.info("couch-db updated for rolled back templates from ips")
#
#                 logger.info("ungenerated templates: " + str(template_dict["template_ids"]))
#
#             else:
#                 # todo- handle pack level scenario here
#                 pass
#         else:
#             return error(1035, 'technician_fill_status.')
#
#         if invalid_pack_display_ids:
#             logger.error(str(invalid_pack_display_ids) + " are not valid pack_display_id(s) from IPS.")
#             return error(5007, str(invalid_pack_display_ids))
#
#         return ips_response(200, 'ok')
#     except (IntegrityError, InternalError) as e:
#         logger.error(e, exc_info=True)
#         return error(2001)


