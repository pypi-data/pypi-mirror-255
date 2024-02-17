import model
import inspect
from dosepack.base_model.base_model import db, BaseModel
from model.model_init import init_db
from peewee import sort_models_topologically


def get_sorted_tables():
    """
    list of sorted class objects in which tables needs to be created.
    :return:
    """
    tables = [m[1] for model_module in inspect.getmembers(model, inspect.ismodule)
                   for m in inspect.getmembers(model_module[1], inspect.isclass)
                        if issubclass(m[1], BaseModel) and m[0] != 'BaseModel' and
                        not (m[1]._meta.not_in_use if hasattr(m[1]._meta, "not_in_use") else False)]

    tables = sort_models_topologically(tables)
    return tables


def migrate_initial():
    init_db(db, 'database_migration')
    tables = get_sorted_tables()
    db.create_tables(tables, safe=True)
    print('Tables Created: ', tables)

    for table in tables:
        if hasattr(table, "get_initial_data"):
            table.insert_many(table.get_initial_data()).execute()
