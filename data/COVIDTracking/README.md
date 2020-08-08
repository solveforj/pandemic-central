# COVID Tracking Project Testing Data

- **Description**: The [COVID Tracking Project](https://www.covidtracking.com/) is one of the most accurate and widely used sources of testing data at the US state level.  We use it to gauge current test capacity and test positivity. Since test reporting tends to fluctuate throughout the week, we smooth it with a 14-day rolling average.  We include normalizations of this data by state population as well.

- **Files**:

  - **preprocess.py** cleans and processes the data from the COVID Tracking Project [api](https://covidtracking.com/api/v1/states/daily.csv) to generate the output data file, _testing_data.csv_

  - **testing_data.csv** is the output of _preprocess.py_ and contains the following columns:

    | Column      | Description |
    | ----------- | ----------- |
    | FIPS   | The full FIPS of interest        |
    | date  | The date of interest      |
    | positiveIncrease  | 14-day rolling average of daily positive test results increase state the county of interest is in       |
    | totalTestResultsIncrease  | 14-day rolling average of daily total test results increase state the county of interest is in      |
    | positiveIncrease_norm   |  positiveIncrease normalized by state population       |
    | totalTestResultsIncrease_norm   |  totalTestResultsIncrease normalized by state population      |
    | test_positivity   |  Positive test rate (positiveIncrease / totalTestResultsIncrease)   |
