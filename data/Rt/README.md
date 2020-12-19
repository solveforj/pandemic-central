# R<sub>t</sub> Data

- **Description**: We use 2 data sources for R<sub>t</sub>, which is an estimation of how many people each individual infected with COVID-19 will further infect at the present. The first, [rt.live](https://www.rt.live/) (RL), provides state-level R<sub>t</sub> data.  The second, [covidactnow.org](https://www.covidactnow.org/) (CAN), provides county-level R<sub>t</sub> values for most US counties.

- **Files**:

  - **preprocess.py** cleans and processes the data from the following sources to generate the output data files, _aligned_rt_data.csv_, _aligned_rt_7.csv_, _aligned_rt_14.csv_, _aligned_rt_21.csv_, and _aligned_rt_28.csv_:

    - [rt.live](https://d14wlfuexuxgcm.cloudfront.net/covid/rt.csv) - access through [rt.live website](https://www.rt.live/)

    - [covidactnow.org](https://data.covidactnow.org/latest/us/counties.WEAK_INTERVENTION.timeseries.csv) - access through covidactnow.org API

  - **rt_data.csv** is one output of _preprocess.py_ and contains the following columns:

    | Column      | Description |
    | ----------- | ----------- |
    | FIPS   | The full FIPS of interest        |
    | date  | The date of interest      |
    | state  | The state FIPS of interest      |
    | region  | The state abbreviation of interest      |
    | rt_mean_rt.live   |  rt.live state-level R<sub>t</sub>       |
    | RtIndicator   |  covidactnow.org county-level R<sub>t</sub>     |

  - **aligned_rt_7.csv**, **aligned_rt_14.csv**, **aligned_rt_21.csv**, **aligned_rt_28.csv** are all output of _preprocess.py_ and are restructured versions of _rt_data.csv_ for each of the 4 classifiers that will be trained. They contain the following columns:
  | Column      | Description |
  | ----------- | ----------- |
  | FIPS   | The full FIPS of interest        |
  | date  | The date of interest      |
  | region  | The state abbreviation of interest      |
  | normalized_cases_norm   |   _confirmed_cases_norm_ column from `jhu_data.csv` in the JHU module further normalized by the _totalTestResultsIncrease_norm_ column from `testing_data.csv` in the COVIDTracking module        |
  | prediction_aligned_int_(7, 14, 21, 28)   |  Cases for the classifier of interest      |
  | rt_aligned_int_(7, 14, 21, 28)  | Rt values for the classifier of interest |
