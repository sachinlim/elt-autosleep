import pandas as pd
import sqlite3
import datetime


def extract_data(file):
    """
    Extracts the data from the .csv files to include only the columns needed
    :param file: name of csv file that exists in the AutoSleep Data directory
    :return: dataframe with the columns including: date, wakeup time, time slept, efficiency, quality,
    deep sleep and SpO2 average.
    """
    df = pd.read_csv(f'AutoSleep Data/{file}.csv',
                     usecols=['toDate', 'waketime', 'asleep', 'efficiency', 'quality', 'deep', 'SpO2Avg'])

    return df


def remove_empty_spo2(data):
    """
    SpO2 can sometimes have no values (NaN) because the Sleep focus mode was not activated on the Apple Watch
    These entries will still be included in the data because they include data associated with sleep
    :param data: dataframe with NaN values
    :return: dataframe without NaN values
    """
    full_data = data[data['SpO2Avg'].notna()].copy()

    return full_data


def convert_date(data):
    """
    Converts dates to include the month with its numeric value before formatting the strings to datetime
    :param data: dataframe with month names
    :return: dataframe with month numbers
    """
    dates = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12',
    }

    # slicing the string so that it only includes the date.
    data['toDate'] = data['toDate'].replace(dates, regex=True).str.slice(-11)

    # removing the first value in the string because it is an integer, and formatting it as a date
    data['toDate'] = data['toDate'].str.replace(',', '').str.replace(' ', '', 1).str.replace(' ', '-')

    # converting the string to a datetime format
    data['toDate'] = pd.to_datetime(data['toDate'], dayfirst=True).dt.strftime("%Y/%m/%d")

    return data


def transform_data(data):
    """
    Transforming the data so that it is useful and all rows have data
    :param data: dataframe extracted with extract_data()
    :return: data that has been cleaned and formatted for SQL database
    """
    transformed = remove_empty_spo2(data)
    convert_date(transformed)

    # slicing the string because it includes the date as well
    # cannot use datetime (%H:%M:%S) format as it is stored as a string
    transformed['waketime'] = transformed['waketime'].str.slice(11, 19)

    # renaming columns to match database
    transformed.columns = ['date', 'wakeup_time', 'hours_slept', 'sleep_efficiency', 'quality_sleep_time',
                           'deep_sleep_time', 'oxygen_saturation_average']

    # rearranging column layout to include percentage values at the end
    transformed = transformed[['date', 'wakeup_time', 'hours_slept', 'quality_sleep_time',
                               'deep_sleep_time', 'sleep_efficiency', 'oxygen_saturation_average']]

    return transformed


try:
    # getting a user input for the name of the csv file
    file_name = input('Name of .csv file that is located inside the AutoSleep Data directory: ')

    # extracting and transforming the data
    extracted_data = extract_data(file_name)
    transformed_data = transform_data(extracted_data)

    # creating a connection to SQL database
    connection = sqlite3.connect('etl_autosleep.db')
    cursor = connection.cursor()

    # finding out what year it was last year to name the SQL table
    now = datetime.datetime.now()
    last_year = now.year - 1

    # executing query to create a table in the database, and to append the data from dataframe onto it

    sql_query = f'CREATE TABLE IF NOT EXISTS autosleep_{last_year}(date DATE PRIMARY KEY, ' \
                f'wakeup_time TIME,hours_slept TIME, quality_sleep_time TIME, deep_sleep_time TIME, ' \
                f'sleep_efficiency VARCHAR(5), oxygen_saturation_average VARCHAR(5))'

    cursor.execute(sql_query)
    transformed_data.to_sql('autosleep_2022', connection, if_exists='append', index=False)

    connection.close()
    print(f'Database successfully updated with AutoSleep data from {last_year}!')
except IOError:
    # file couldn't be opened, perhaps you need to create it
    print('File does not exist!')
