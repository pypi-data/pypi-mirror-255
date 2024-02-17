from peewee import Expression


def mod(lhs, rhs):
    return Expression(lhs, '%', rhs)

# def get_pack_count_for_batch_by_status(args):
#     """
#
#     @param args: status, batch_id
#     @return: dict of pack_count as key and count of packs with given batch id and status as value
#     """
#     status = json.loads(args['status'])
#     batch_id = args['batch_id']
#     batch_status_pack_count = {}
#     try:
#         query = PackDetails.select(fn.COUNT(PackDetails.id).alias("id"),CodeMaster.value).where(PackDetails.pack_status << status, PackDetails.batch_id == batch_id) \
#                 .join(CodeMaster, on=CodeMaster.id == PackDetails.pack_status) \
#                 .group_by(PackDetails.pack_status)
#         for record in query.dicts():
#             batch_status_pack_count[record['value']] = record['id']
#         return create_response(batch_status_pack_count)
#     except Exception as e:
#         logger.info(e)
#         return e


# def get_packs_count_by_robot_id(args):
#     """
#     @param args: robot id
#     @return: pack count which are in progress by given robot id
#     """
#     robot_wise_pack_count = {}
#
#     if args['robot_id'] is not None:
#         data = "progress_pack_count"
#         query_append = (PackDetails.pack_status == settings.PROGRESS_PACK_STATUS) & (
#                     PackAnalysisDetails.device_id == args['robot_id'])
#         group_by_clause = PackAnalysis.pack_id
#     elif args['batch_id'] is not None:
#         data = "pending_pack_count"
#         query_append = (PackDetails.pack_status == settings.PENDING_PACK_STATUS) & (
#                     PackDetails.batch_id == args['batch_id'])
#         group_by_clause = PackAnalysisDetails.device_id
#     else:
#         return error(1001, "Missing Parameters. ")
#     try:
#         query = PackDetails.select(fn.count(PackDetails.id).alias('count'), PackAnalysisDetails.device_id.alias('robot_id')).distinct() \
#             .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
#             .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
#             .join(DeviceMaster, on=PackAnalysisDetails.device_id == DeviceMaster.id) \
#             .where(query_append) \
#             .group_by(group_by_clause)
#
#         for record in query.dicts():
#             if record['robot_id'] not in robot_wise_pack_count.keys():
#                 robot_wise_pack_count[record['robot_id']] = 0
#             robot_wise_pack_count[record['robot_id']] += 1
#
#         return create_response(robot_wise_pack_count)
#
#     except (InternalError, IntegrityError) as e:
#         logger.error(e, exc_info=True)
#         return error(2001)


# def get_robot_pending_packs_count(args):
#     """
#
#     @param args: batch id
#     @return: robot_id and packs_left as key and robot id and count of packs left by that robot as value
#     """
#     try:
#         robot_pending_pack = []
#         batch_id = args['batch_id']
#         print(batch_id)
#         query = PackDetails.select(fn.count(PackDetails.id).alias('count'), PackAnalysisDetails.robot_id)\
#                 .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
#                 .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id)\
#                 .where((PackDetails.pack_status == settings.PENDING_PACK_STATUS) & query_append)
#                 .group_by(PackAnalysisDetails.robot_id)
#         for record in query.dicts():
#             robot_pending_pack.append({"robot_id":record['robot_id'] , "pending_pack_count": record['count'] })
#         return create_response(robot_pending_pack)
#     except (InternalError, IntegrityError) as e:
#         logger.error(e, exc_info=True)
#         return error(2001)

# def get_robot_wise_pack_list():
#     robot_pack_list = {}
#     try:
#         query = PackDetails.select(PackDetails.id, PackAnalysisDetails.robot_id) \
#             .join(PackAnalysis, on=PackAnalysis.pack_id == PackDetails.id) \
#             .join(PackAnalysisDetails, on=PackAnalysisDetails.analysis_id == PackAnalysis.id) \
#             .where(PackDetails.pack_status == settings.PENDING_PACK_STATUS, PackAnalysisDetails.robot_id.is_null(False))\
#             .group_by(PackDetails.id)
#
#         for record in query.dicts():
#             if record['robot_id'] not in robot_pack_list:
#                 robot_pack_list[record['robot_id']] = []
#             robot_pack_list[record['robot_id']].append(record['id'])
#
#         return create_response(robot_pack_list)
#
#     except (InternalError, IntegrityError) as e:
#         logger.error(e, exc_info=True)
#         return error(2001)


# def check_mfd_required_notification(user_id: int, batch_id: int):
#     """
#     Function to check if there is need of next mfd trolley in 15 minutes
#     If true then sends  screen and google home notifications
#     @param batch_id: int
#     @param user_id: int
#     @return:
#     """
#     pack_to_notify = get_mfd_required_pending_packs(batch_id)
#
#     if pack_to_notify:
#         pack_info_dict, device_trolley_dict = get_trolley_and_device_for_given_pack \
#             (pack_id_list=[pack_to_notify], batch_id=batch_id)
#
#         device_message = dict()
#         for device, trolley_list in device_trolley_dict.items():
#             device_message[device] = "Trolley {} is required for MFD transfer in 15 mins".format(trolley_list)
#
#         Notifications(user_id=None, call_from_client=True) \
#             .send_transfer_notification(user_id=None, device_message=device_message,
#                                         batch_id=batch_id, flow='mfd')

