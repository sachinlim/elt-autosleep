# AutoSleep

[AutoSleep](https://apps.apple.com/us/app/autosleep-track-sleep-on-watch/id1164801111) is an app available from the Apple App Store, which allows the user to track their sleep using an Apple Watch. The documentation for the app is available on [its website](https://autosleepapp.tantsissa.com/). The specific focus for this project is the usage of the [exported data](https://autosleepapp.tantsissa.com/settings/export) from the app. 

In order for AutoSleep to generate the data, it uses the built in functions available though an Apple Watch. The Apple Watch Series 6 and onwards support [blood oxygen monitoring](https://support.apple.com/en-gb/guide/watch/apdaf17aa5ef/watchos), of which can also be monitored while sleeping, but only when the Sleep focus mode is enabled. 


# ETL 

ETL stands for **E**xtract, **T**ransform, and **L**oad. In this project, data is being extracted from a CSV file that was exported by the AutoSleep app, transformed to contain only the necessary data, and loaded onto an SQLite database.

![image](https://user-images.githubusercontent.com/80691974/211582158-0ae4654f-916a-4e7e-922f-2a290aaf91ec.png)


## Data Extraction 

Data is available to be exported from within the app only, meaning it has to be manually done and no [Siri Shortcuts](https://support.apple.com/en-gb/HT209055) are available. This process leads to a manual implementation of batch processing, of which a CSV file is exported for analysis. This data is likely the information being used by the app to display the sleep information from the previous night/week. 

The CSV file contains a lot of columns that may have empty data, as the sensors on the Apple Watch may not be able to pick them up throughout the sleep phase. Regardless of what data is included or missing, the entire file is exported and only certain columns are extracted into a pandas dataframe.


## Data Transformation

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
  <img src="https://user-images.githubusercontent.com/80691974/211573853-c0401973-1016-4639-a856-b47e17ef8441.png">
</p>

In the screenshot above, the last 3 columns on the right contain SpO2 data from that night's sleep record. The empty columns will mean that the entire row is removed because of there being not enough data.

### Conversion of months to numerical values

Some of the columns of data have months spelt out, meaning July is stored as `Jul` rather than `07`, and separated by spaces. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/211575032-9664347b-f376-4f05-b9c7-18a296a9de4e.png">
</p>

In order to convert these to numbers, a [dictionary](https://github.com/sachinlim/etl-autosleep/blob/main/main.py#L37) is used. Each month has the text abbreviation as its key, and the numerical month as the values. The day of the week is also removed, as it is not needed.

### Changing of column headers

The headers are changed to match the names on the database. Some of the column headers do not make much sense and can be formatted in a way to make it easier to understand what the data each column contains. 


The pandas dataframe can be exported with the `to_csv('output.csv')` function, and it looks like this: 

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/211798584-56664b38-3995-4d43-83bc-a8e77811c058.png">
</p>


## Loading onto a database

The final step of this process is the loading of the data onto a database. The script will generate a table with the name of "autosleep" and last year's date. The [SQL query](https://github.com/sachinlim/etl-autosleep/blob/main/main.py#L105) used to create the tables follow the same format as the column headers, and the date is set as the primary key. 

Once the data has been loaded onto an SQLite database, it can be accessed for future needs.  

![image](https://user-images.githubusercontent.com/80691974/211798887-519cbdb4-10be-4870-bffa-ec581ca50424.png)

The columns are formatted in the following way:

<p align="center">
  <img src="https://user-images.githubusercontent.com/80691974/211578899-961c6ba5-ebd2-4637-bb4c-8f3131b4ca97.png">
</p>
