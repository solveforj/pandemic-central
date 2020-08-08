# R<sub>t</sub> Data

- **Description**: We use 3 data sources for R<sub>t</sub>, which is an estimation of how many people each individual infected with COVID-19 will further infect at the present. The first 2, [rt.live](https://www.rt.live/) and [covid19-projections.com](https://covid19-projections.com/), both provide state-level R<sub>t</sub> values.  The last, [covidactnow.org](https://www.covidactnow.org/), provides county-level R<sub>t</sub> values for some counties in the US.

- **Files**:

  - **preprocess.py** cleans and processes the data from the following sources to generate the output data file, _rt_data.csv_:

    - [rt.live](https://d14wlfuexuxgcm.cloudfront.net/covid/rt.csv) - access through rt.live website

    - [covid19-projections.com](https://raw.githubusercontent.com/youyanggu/covid19_projections/master/projections/combined/latest_us.csv) - access through covid19-projections.com Github

    - [covidactnow.org](https://data.covidactnow.org/latest/us/counties.WEAK_INTERVENTION.timeseries.csv) - access through covidactnow.org API

  - **rt_data.csv** is the output of _preprocess.py_ and contains the following columns:

    | Column      | Description |
    | ----------- | ----------- |
    | FIPS   | The full FIPS of interest        |
    | date  | The date of interest      |
    | state  | The state FIPS of interest      |
    | region  | The state abbreviation of interest      |
    | rt_mean_rt.live   |  rt.live state-level R<sub>t</sub>       |
    | rt_mean_MIT   |  covid19-projections.com state-level R<sub>t</sub>      |
    | RtIndicator   |  covidactnow.org county-level R<sub>t</sub>     |
