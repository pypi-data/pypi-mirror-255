
# Migration Automation 

Python script to run SQL migration scripts sequentially from the specified folder, updating latest schema version in the database itself after each migration.

This is done for the purpose of sake of simplicity and ease of process in running migrations


## DB Requirements
it will be requiring a db schema containing table *migration_details*

        id      |migration_file_name    |status         |modified_date
        1       |migration_testing_1.py |1              |2023-11-27 14:09:51
        2       |migration_testing_2.py |0              |2023-11-27 14:09:51


#### migration files will be run as file directly

- file will include one main function containing all migration functions
- all the migration runs has to be in atomic transaction

## Database Independency:
All databases would have an individual **migration_details** table, which can consist of which migration to run and which not to run.

## NOTE
every developer creating new migration has to avoid writing this in migration file

        if __name__ == "__main__":
        testing_migration()

you directly have to call the function at the end of file as the file is going to be run from another file

        testing_migration()

Developers have to keep habit of raising the error in individual migration files on failure of migration script

## Example
    migration_path = os.getcwd() + "/src/migrations" 
    # here "/src/migrations" is the path of yout migration files folder from maim.py or app.py
    migration_manager = MigrationManager()
    migration_manager.create_migration_table()
    migration_manager.insert_migration_files(migration_path)
    migration_manager.fetch_and_run_migrations()

Please integrate this into the init of your Python project.
