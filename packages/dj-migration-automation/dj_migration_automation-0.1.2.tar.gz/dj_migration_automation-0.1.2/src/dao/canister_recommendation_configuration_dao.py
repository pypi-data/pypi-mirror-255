from peewee import fn
import settings
from dosepack.utilities.utils import log_args_and_response
from src import constants
from src.model.model_edge_slot_mapping import EdgeSlotMapping
from src.model.model_pack_grid import PackGrid
logger = settings.logger


def get_configuration_for_recommendation(**kwarg):
    try:

        if "edge_slot_group_wise_conf_mapping" in kwarg.keys():

            edge_slot_group_wise_conf_mapping = {}

            query = EdgeSlotMapping.select().dicts()
            for data in query:
                edge_slot_group_wise_conf_mapping[data["group_no"]] = eval(data["configuration_mapping"])

            return edge_slot_group_wise_conf_mapping

        elif "group_slot_dict" in kwarg.keys():

            group_slot_dict = {}

            query = EdgeSlotMapping.select().dicts()
            for data in query:
                group_slot_dict[data["group_no"]] = eval(data["slots"])
            return group_slot_dict

        elif "valid_slot_quadrant" in kwarg.keys():

            valid_slot_quadrant = {}

            query = EdgeSlotMapping.select().dicts()

            for data in query:
                for slot in eval(data["slots"]):
                    valid_slot_quadrant[slot] = eval(data["quadrant"])

            max_slot = PackGrid.select(fn.MAX(PackGrid.slot_number)).scalar()

            for slot in range(1, max_slot + 1):
                if slot not in valid_slot_quadrant:
                    valid_slot_quadrant[slot] = {1, 2, 3, 4}

            return valid_slot_quadrant

        elif "pack_slot_id" in kwarg.keys():

            column = PackGrid.select(fn.COUNT(fn.DISTINCT(PackGrid.slot_column))).where(PackGrid.slot_row.in_(constants.PACK_GRID_ROW_MAP[constants.PACK_GRID_ROW_7x4])).scalar()
            row = PackGrid.select(fn.COUNT(fn.DISTINCT(PackGrid.slot_row))).where(PackGrid.slot_row.in_(constants.PACK_GRID_ROW_MAP[constants.PACK_GRID_ROW_7x4])).scalar()
            pack_slot_id = []

            # below commented code as per old pack grid like 1 to 7, 8 t 14, ....
            # count = 0
            # for i in range(0, column):
            #     t = []
            #     for j in range(0, row):
            #         count = count + 1
            #         t.append(count)
            #     pack_slot_id.insert(0, t)

            for i in range(0, column):
                x = [m for m in range((row * column) - i, 0, -4)]
                pack_slot_id.insert(0, x)

            return pack_slot_id

        elif "total_slots" in kwarg.keys():

            max_slot = PackGrid.select(fn.MAX(PackGrid.slot_number)).where(PackGrid.slot_row.in_(constants.PACK_GRID_ROW_MAP[constants.PACK_GRID_ROW_7x4])).scalar()
            total_slots = [i for i in range(1, max_slot + 1)]

            return total_slots

        elif "edge_slot" in kwarg.keys():

            query = EdgeSlotMapping.select().dicts()

            edge_slot = set()

            for data in query:
                edge_slot.update(eval(data["slots"]))

            return edge_slot

    except Exception as e:
        logger.error(f"Error in get_configuration_for_recommendation: {e}")
        raise e


def get_total_column_and_row_from_pack_grid(**kwargs):
    try:
        column, row = 4, 8  # default value for SCMP

        if "column" in kwargs.keys():
            column = PackGrid.select(fn.COUNT(fn.DISTINCT(PackGrid.slot_column))).where(PackGrid.slot_row.in_(constants.PACK_GRID_ROW_MAP[constants.PACK_GRID_ROW_7x4])).scalar()

        if "row" in kwargs.keys():
            row = PackGrid.select(fn.COUNT(fn.DISTINCT(PackGrid.slot_row))).where(PackGrid.slot_row.in_(constants.PACK_GRID_ROW_MAP[constants.PACK_GRID_ROW_7x4])).scalar()

        return column, row

    except Exception as e:
        logger.error(f"Error in get_total_column_and_row_from_pack_grid: {e}")
        raise e
