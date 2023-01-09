import pandas as pd
pd.set_option('display.max_columns', 7)


def extract_data():
    """
    Extracts the data from the .csv files to include only the columns needed
    :return: dataframe with the columns including: date, wakeup time, time slept, efficiency, quality,
    deep sleep and SpO2 agerage.
    """

    df = pd.read_csv('AutoSleep Data/2022 - 2023.csv',
                     usecols=['toDate', 'waketime', 'asleep', 'efficiency', 'quality', 'deep', 'SpO2Avg'])

    return df


def remove_empty_spo2(data):
    """
    SpO2 can sometimes have no values (NaN) because the Sleep focus mode was not activated on the Apple Watch
    These entries will still be included in the data because they include data associated with sleep
    :param data: dataframe with NaN values
    :return: dataframe without NaN values
    """
    data = data[data['Oxygen Saturation Average'].notna()]

    return data


def transform_data(data):
    """
    Transforming the data so that it is useful and all rows have data
    :return: data that has been cleaned
    """

    # renaming columns
    data.columns = ['Date', 'Wakeup Time', 'Hours Slept', 'Efficiency', 'Quality Sleep Time', 'Deep Sleep Time',
                    'Oxygen Saturation Average']

    # slicing the string because it includes the date as well
    # cannot use datetime (%H:%M:%S) format as it is stored as a string
    data['Wakeup Time'] = data['Wakeup Time'].str.slice(11, 19)

    data = remove_empty_spo2(data)

    return data


extracted_data = extract_data()
transformed_data = transform_data(extracted_data)

print(transformed_data)
