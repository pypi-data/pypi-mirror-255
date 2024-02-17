
import settings


logger = settings.logger

#
# def add_used_label(info_dict):
#     """
#
#     :param info_dict:
#     :return:
#     """
#     print_date = info_dict['print_date']
#     company_id = info_dict['company_id']
#
#     try:
#         used_label_count = get_print_count(print_date)
#         consumable_type = ConsumableTypeMaster.type_data['Label']
#         record, created = ConsumableUsed.get_or_create(company_id=company_id,
#                                                        consumable_id=consumable_type,
#                                                        created_date=print_date,
#                                                        defaults={'used_quantity': used_label_count})
#         if not created:
#             status = ConsumableUsed.update(used_quantity=used_label_count)\
#                 .where(ConsumableUsed.id == record.id).execute()
#         return True
#     except (InternalError, IntegrityError) as e:
#         raise e
