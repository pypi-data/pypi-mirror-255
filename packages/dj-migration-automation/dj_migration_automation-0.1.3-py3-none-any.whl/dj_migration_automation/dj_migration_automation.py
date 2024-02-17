import importlib.util
import os
import time

from dosepack.base_model.base_model import db
from model.model_init import init_db
from src import constants


class MigrationManager:
    # this is actual dj_migration_automation
    def __init__(self):
        init_db(db, 'database_migration')
        self.table_name = 'migration_details'

    def table_exists(self, table_name):
        sql_query = f"SELECT * FROM {table_name};"
        result = db.execute_sql(sql_query)
        return result is not None

    def create_migration_table(self):

        if not self.table_exists(self.table_name):
            sql = f'''
                    CREATE TABLE {self.table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        status BOOLEAN DEFAULT FALSE,
                        modified_date DATETIME NULL DEFAULT CURRENT_TIMESTAMP
                    );
                '''
            db.execute_sql(sql)

    def get_existing_migration_files(self):
        sql_query = f"SELECT name FROM {self.table_name};"
        results = db.execute_sql(sql_query)
        return set(result[0] for result in results)

    def insert_migration_files(self, folder_path):
        # Get a list of migration files from the specified folder
        migration_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]

        # Get existing migration files from the database
        existing_migration_files = self.get_existing_migration_files()

        # Insert only the migration files that are not already present
        for name in migration_files:
            if name not in existing_migration_files:
                sql_query = f"INSERT INTO {self.table_name} (name) VALUES ('{name}');"
                db.execute_sql(sql_query)

    def run_file(file_name):
        try:
            module_path = os.path.abspath(file_name[:-3] + ".py")
            spec = importlib.util.spec_from_file_location(file_name[:-3], module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'run_migration') and callable(getattr(module, 'run_migration')):
                module.run_migration()

            return True

        except FileNotFoundError as e:
            print(f"Error: {file_name} not found.")
            raise e
        except Exception as e:
            if e.args[0] == 1062:
                print("\n")
                print(
                    "*******************************************************************************************************")
                file_name = file_name.split("/")[2]
                print(f"\033[1m{file_name}\033[0m was already executed --> \033[91m{e.args[1]}\033[0m")
                print(
                    "*******************************************************************************************************")
                return constants.DUPLICATE_MIGRATION
            print(f"Error executing {file_name}: {e}")
            raise e

    def fetch_and_run_migrations(self):
        init_db(db, 'database_migration')
        try:
            with db.transaction():
                sql_query = f"SELECT name, id FROM {self.table_name} WHERE status = 0;"
                results = db.execute_sql(sql_query)
                for record in results:
                    print(record)
                    start_time = time.time()
                    migration_name = record[0]
                    status = MigrationManager.run_file(f"src/migrations/{migration_name}")
                    if status != constants.DUPLICATE_MIGRATION:
                        print(
                            "-----------------------------------------------------------------------------------------------")
                        print(f"{migration_name} is executed. time taken is --> {time.time() - start_time}")
                        print(
                            "-----------------------------------------------------------------------------------------------")
                    if status:
                        sql_query = f"UPDATE {self.table_name} SET status = 1, modified_date = CURRENT_TIMESTAMP WHERE id = {record[1]}"
                print("all migrations have been executed, no missing migrations to execute")
        except Exception as e:
            print(
                "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
            print(e)
