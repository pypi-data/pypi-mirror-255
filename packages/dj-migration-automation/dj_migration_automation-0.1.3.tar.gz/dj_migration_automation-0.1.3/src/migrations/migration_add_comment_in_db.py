import csv

import settings
from dosepack.base_model.base_model import db
from model.model_init import init_db

logger = settings.logger
init_db(db, "database_migration")


def add_comments_in_db(main_dict: dict):
    """
    main_dict = {"table_name_1":{"column_name_1": comments,
                                 "column_name_2": comments,
                                 "column_name_3": comments
                                },
                 "table_name_2":{"column_name_1": comments,
                                 "column_name_2": comments,
                                 "column_name_3": comments
                                }
                    }
    :param main_dict:
    :return:
    """
    try:
        init_db(db, "database_migration")
        table_set = set()

        total_tables_for_current_db = []
        fetch_total_tables = db.execute_sql("show tables")
        for data in fetch_total_tables:
            total_tables_for_current_db.append(data[0])

        for table, table_data in main_dict.items():

            table_name = table

            if table_name in total_tables_for_current_db:

                details = "show COLUMNS" + " from " + table_name
                table_columns_details = db.execute_sql(details)

                x = "ALTER TABLE " + table_name + " " + "CHANGE COLUMN "

                column_comment_dict = {}

                # print(list(table_columns_details))

                for row in table_columns_details.fetchall():

                    not_null = "NOT NULL "
                    null = "NULL "
                    default_null = "DEFAULT NULL "
                    default = "DEFAULT "
                    comment = "COMMENT "

                    column_name = row[0]

                    sql_query = x + "`"+ row[0] + "`" + " " + "`" + row[0] +"`"+ " " + row[1] + " "

                    # 2 : nullable or not
                    if row[2] == "NO":
                        sql_query += not_null

                    if row[2] == "YES":
                        sql_query = sql_query + null + default_null

                    # 4 : default value
                    if row[4]:
                        sql_query = sql_query + default + row[4] + " "

                    # 5 : extra
                    if row[5] != "":
                        sql_query = sql_query + row[5] + " "

                    sql_query = sql_query + comment

                    column_comment_dict[column_name] = sql_query

                for key, value in column_comment_dict.items():
                    if key in table_data.keys():
                        query = value + '"' + table_data[key] + '"'
                        print(query)
                        db.execute_sql(query)
                        table_set.add(table_name)
        print(f"table_set: {table_set}")

    except Exception as e:
        print(e)


def read_file():
    try:
        main_dict = {}
        path_to_csv = "/home/meditab/Downloads/DPWS_SCHEMA - Sheet1.csv"
        table_data = list(csv.DictReader(open(path_to_csv, "r")))
        for data in table_data:
            #data: OrderedDict([('TABLE_NAME', 'action_master'), ('COLUMN_NAME', 'id'), ('COLUMN_COMMENT', '')])
            row_data = data.values()
            row_data = list(row_data)
            if row_data[2]:
                if row_data[0] not in main_dict:
                    main_dict.setdefault(row_data[0], {})
                main_dict[row_data[0]][row_data[1]] = row_data[2]

        return main_dict

    except Exception as e:
        print(e)


def read_file_and_add_comment_in_db():
    main_dict = read_file()
    print(main_dict)
    add_comments_in_db(main_dict)

