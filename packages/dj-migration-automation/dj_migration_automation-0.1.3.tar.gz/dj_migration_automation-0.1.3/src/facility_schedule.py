import logging

logger = logging.getLogger('root')


# @validate(required_fields=["facility_id", "pack_id_list", "schedule_info", "company_id"])


#
# def week_of_month(dt, weeknumber):
#     """
#     Returns the week of the month for the specified date.
#     :param dt: date
#     :param weeknumber: number of week
#     :return:
#     """
#
#     first_day = dt.replace(day=1)
#
#     dom = dt.day
#     adjusted_dom = dom + first_day.weekday()
#
#     week_no = int(ceil(adjusted_dom/7.0))
#     if week_no == weeknumber:
#         return True
#     return False


