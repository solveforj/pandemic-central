# JHU Data

- **Description**: We download cumulative COVID-19 county-level case data from [John Hopkins University](https://coronavirus.jhu.edu/) and convert it into a 14-day moving average of daily case increases. It is important to note that cases from the boroughs of New York City are reported jointly.  Thus, we gather case data for them individually from [NYC Public Health](https://www1.nyc.gov/site/doh/covid/covid-19-data.page).

- **Files**:

  - **preprocess.py** cleans and processes the data from [JHU's Github](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv) to generate the output dataset, _jhu_data.csv_. NYC data is downloaded using the links in the graphs from [here](https://www1.nyc.gov/site/doh/covid/covid-19-data-boroughs.page) and added to the JHU data.

  - **jhu_data.csv** is the output of _preprocess.py_ and contains the following columns:

    | Column      | Description |
    | ----------- | ----------- |
    | FIPS   | The FIPS of interest        |
    | date  | The date of interest      |
    | confirmed_cases   |  A 7-day moving average of daily case increases per county       |
    | confirmed_cases_norm   |  A 7-day moving average of daily case increases per county normalized to cases per 100,000 people      |
