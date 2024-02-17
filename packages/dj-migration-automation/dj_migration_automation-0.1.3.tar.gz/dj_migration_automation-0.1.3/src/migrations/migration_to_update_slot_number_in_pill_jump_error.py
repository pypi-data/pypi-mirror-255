from src.model.model_pill_fill_error import PillJumpError
from src.model.model_pack_grid import PackGrid

from model.model_init import init_db
from dosepack.base_model.base_model import db


def update_slot_number_in_pill_jump_error():
    try:
        init_db(db, 'database_migration')

        new_pack_grid = {}

        old_pack_grid = {(0, 0): 28, (0, 1): 21, (0, 2): 14, (0, 3): 7,
                         (1, 0): 27, (1, 1): 20, (1, 2): 13, (1, 3): 6,
                         (2, 0): 26, (2, 1): 19, (2, 2): 12, (2, 3): 5,
                         (3, 0): 25, (3, 1): 18, (3, 2): 11, (3, 3): 4,
                         (4, 0): 24, (4, 1): 17, (4, 2): 10, (4, 3): 3,
                         (5, 0): 23, (5, 1): 16, (5, 2): 9, (5, 3): 2,
                         (6, 0): 22, (6, 1): 15, (6, 2): 8, (6, 3): 1}

        query = PackGrid.select(PillJumpError).dicts()

        for data in query:
            new_pack_grid[(data["slot_row"], data["slot_column"])] = data["slot_number"]

        pill_jump_query = PillJumpError.select(PillJumpError).dicts()
        pill_jump = {}
        for data in pill_jump_query:
            if not pill_jump.get(data["slot_number"]):
                pill_jump[data["slot_number"]] = []
            pill_jump[data["slot_number"]].append(data["id"])

        for r_c, slot_no in old_pack_grid.items():
            if pill_jump[slot_no]:
                status = PillJumpError.update(slot_number=new_pack_grid[r_c]).where(PillJumpError.id.in_(pill_jump[slot_no])).execute()
                print(f"{r_c, slot_no}: {status}")

    except Exception as e:
        print(f'error in update_slot_number_in_pill_jump_error, e: {e}')


if __name__ == "__main__":
    update_slot_number_in_pill_jump_error()
