import datetime
import pandas as pd

# Changing date from %m-%d-%y format to %Y-%m-%d %H:%M:%S
def convert_date_to_sql_date(from_date, to_date):
    """
        @function: convert_date_to_sql_date
        @createdBy: Manish Agarwal
        @createdDate: 4/13/2016
        @lastModifiedBy: Manish Agarwal
        @lastModifiedDate: 04/13/2016
        @type: function
        @param: none
        @purpose - convert the received data to sql date
    """
    try:

        from_date = datetime.datetime.strptime(from_date, '%m-%d-%y')
        from_date = from_date.strftime('%Y-%m-%d')

        to_date = datetime.datetime.strptime(to_date, '%m-%d-%y')
        to_date = to_date.strftime('%Y-%m-%d')

        return from_date, to_date

    except ValueError:
        raise ValueError("Input Dates not in proper format")


def converting_data_frame_to_dict_form(df):
    """
    This method will convert data frame into dictionary form.
    :return: dict_df
    """
    df_dict = {}
    for i in range(len(df)):
        df_dict[i] = []
        df_dict[i].append(df.iloc[i].to_dict())
    return df_dict


def read_data(is_excel_or_csv, file_name):
    """
    This method will read file. It will read excel if flag is 1, or it will read csv
    :param is_excel_or_csv:
    :return: df
    """
    if is_excel_or_csv:
        df = pd.read_excel(str(file_name))
    else:
        df = pd.read_csv(str(file_name))
    return df
