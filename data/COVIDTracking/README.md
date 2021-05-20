# COVID-19 Testing Data

### Description
Processes all COVID-19 testing-related datasets to generate testing features for the model, sourced from the COVID Tracking Project API (prior to 03/07/2021) and Johns Hopkins University (after 03/07/2021).

### Files
  * **preprocess.py** downloads and processes all testing data to generate features; datasets are from these specific locations:
    * [COVID Tracking Project API](https://covidtracking.com/api/v1/states/daily.csv), with documentation [here](https://covidtracking.com/data/api)
    * [Johns Hopkins Centers for Civic Impact for the Coronavirus Resource Center](https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/testing_data/time_series_covid19_US.csv), with documentation [here](https://github.com/govex/COVID-19)
    * See `/census` and `/geodata` directories for information on any census and geographical datasets used here, respectively
  * **testing_data.csv.gz** is the output of `preprocess.py`
  * **covidtracking_2021_03_07.csv** contains the [COVID Tracking Project API](https://covidtracking.com/api/v1/states/daily.csv) dataset at its last update on 2021-03-07
  * **testing_data_test.csv.gz** contains the output of `preprocess.py` as of 2021-05-18
