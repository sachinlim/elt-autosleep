# AutoSleep

[AutoSleep](https://apps.apple.com/us/app/autosleep-track-sleep-on-watch/id1164801111) is an app available from the Apple App Store, which allows the user to track their sleep using an Apple Watch. The documentation for the app is available on [its website](https://autosleepapp.tantsissa.com/). The specific focus for this project is the usage of the [exported data](https://autosleepapp.tantsissa.com/settings/export) from the app. 

In order for AutoSleep to generate the data, it uses the built in functions available though an Apple Watch. The Apple Watch Series 6 and onwards support [blood oxygen monitoring](https://support.apple.com/en-gb/guide/watch/apdaf17aa5ef/watchos), of which can also be monitored while sleeping, but only when the Sleep focus mode is enabled. 


# ETL 

ETL stands for **E**xtract, **T**ransform, and **L**oad. In this project, data is being extracted from a CSV file that was exported by the AutoSleep app, transformed to contain only the necessary data, and loaded onto an SQLite database. This project is using a batch processing model, as there is no continous stream of data due to how the data is originally obtained. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/216351883-f531de06-f12d-4764-bd23-0272ae0711c2.png" width=800>
</p>

Within Airflow, this is what the graph currently looks like for the tasks:

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/216355805-e36ff03b-05d7-46a9-8944-14b370e97a14.png" width=700>
</p>

## Data Extraction 

Data is available to be exported from within the app only, meaning it has to be manually done and no [Siri Shortcuts](https://support.apple.com/en-gb/HT209055) are available. 

### Manual Extraction

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/216352011-00244ed0-9309-4c30-b75c-c8c00882c9ec.png" width=600>
</p>

This process leads to a manual implementation for the first part of the project, of which a CSV file is first exported for analysis from within the app. Using Airflow, the process of uploading the CSV file to Amazon S3 is [automated](dags/upload_to_s3.py). 


### Airflow Sensors

Once the CSV file has been exported manually, it is placed in a folder before being uploaded to an Amazon S3 bucket. This process is not needed to be done with Airflow, as the data could be manually uploaded to the S3 bucket or Airflow could directly use the file once it has been exported to the local file system, but it was a good way to learn a few things about Amazon S3.

An S3 Sensor is [used](dags/etl_airflow.py) to be able to see if a file exists within the S3 bucket. Once that is fulfilled, the rest of the tasks can begin once the `data.csv` file has been downloaded to the [AutoSleep Data](/AutoSleep%20Data) directory.

## Data Transformation

The CSV file contains a lot of columns that may have empty data, as the sensors on the Apple Watch may not be able to pick them up throughout the sleep phase. This data is likely the information being used by the app to display the sleep information from the previous night/week. Regardless of what data is included or missing, the entire file is exported and only certain columns are extracted into a pandas dataframe.

With the data columns included, the main focus for this project is the following: 

- Date
- Wakeup time
- Hours slept
- Quality sleep time
- Deep sleep time
- Sleep efficiency 
- Oxygen saturation average (SpO2)

The column headers for the relevant data have other names, and the data formatting is not the best to store onto a database. The first step of the transformation phase is to remove rows (dates) where there are empty columns, convert the months to numerical values, and change the column headers prior to insertion to the database. 

### Removal of empty rows

One important bit of information to take note of is that each date will have rows filled with information. It is not possible to have a date without there being some form of sleep data being available. However, the oxygen saturation levels (SpO2) may not always be included for each recorded date because the Sleep focus mode was not enabled. This leads to some columns being empty, which does not provide the entire picture of sleep - data will not be as accurate as a proper sleep study but it gives an idea.

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/216354027-0e89467b-8c97-4e3f-adf5-03180b311e35.png" width=450>
</p>


In the screenshot above, the last 3 columns on the right contain SpO2 data from that night's sleep record. The empty columns will mean that the entire row is removed because of there being not enough data.


### Conversion of months to numerical values

Some of the columns of data have months spelt out, meaning January is stored as `Jan` rather than `01`, and separated by spaces. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/216353090-5fe877b3-b999-4836-b481-8faa2c0d5d96.png" width=250>
</p>

In order to convert these to numbers, a [dictionary](https://github.com/sachinlim/etl-autosleep/blob/2b24ceef3520f48299efc3c4f1161d80f356031a/dags/etl_airflow.py#L49) is used. Each month has the text abbreviation as its key, and the numerical month as the values. The day of the week is also removed, as it is not needed. The new format of the dates follow the `YYYY-MM-DD` format, shown in the screenshot in the next section under the `date` column.


### Changing of column headers

The headers are changed to match the names on the database. Some of the column headers do not make much sense and can be formatted in a way to make it easier to understand what the data each column contains. 

The pandas dataframe is exported with the `to_csv('transformed_data.csv')` function, and it looks like this: 

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/216352418-f043644d-b530-45a1-8a8f-68a15d3e53fe.png" width=600>
</p>


## Loading onto a database

The final step of this process is the loading of the data onto a database. The script will generate a table with the name of "autosleep" and last year's date. The [SQL query](https://github.com/sachinlim/etl-autosleep/blob/main/main.py#L105) used to create the tables follow the same format as the column headers, and the date is set as the primary key. 

Once the data has been loaded onto an SQLite database, it can be accessed for future analysis.  

![image](https://user-images.githubusercontent.com/80691974/216355281-a19369f9-e399-4c6c-8883-063a05ad5b8f.png)


The columns are formatted in the following way:

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/216355463-651cd9b4-51fa-4faf-a871-af382673a59f.png" width=400>
</p>


## Deletion of temporary files

Two temporary files are created by this process: one is downloaded from Amazon S3 named `data.csv` and the second is exported by the script named `transformed_data.csv`. After the data has been loaded to the SQLite database, the two temporary files are no longer needed, and therefore, are deleted. Both of these files reside in the [AutoSleep Data](/AutoSleep%20Data) directory throughout the process, and can also be accessed through the Docker container. 


## Data Analysis

Now that the data resides in a SQLite databse, it can be used in many ways, one of which is for data anslysis. This process can be seen in the [sql-to-graph](sql-to-graph.ipynb) file that is in a Jupyter Notebook format.
