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

  - **align_Rt.py** utilizes _rt_data.csv_, testing data, and case data to align the R<sub>t</sub> to the case curve.  Data from all of these files is output into _aligned_rt.csv_.

  - **with_county_rt.p** a Pickle-serialized dictionary containing alignment ranges for counties with covidactnow.org R<sub>t</sub> values

  - **with_county_rt.p** a Pickle-serialized dictionary containing alignment ranges for counties without covidactnow.org R<sub>t</sub> values

  - **aligned_rt.csv** is the output of _align_Rt.py_ and contains the following columns:

    | Column      | Description |
    | ----------- | ----------- |
    | FIPS   | The full FIPS of interest        |
    | date  | The date of interest      |
    | state  | The state FIPS of interest      |
    | region  | The state abbreviation of interest      |
    | normalized_cases_norm   |  confirmed_cases_norm from `data/JHU/jhu_data.csv` further normalized by state-wide tests conducted and aligned such that it represents the cases expected 14 days into the future from the date of interest      |
    | estimated_county_rt   |  Aligned R<sub>t</sub> value that is relevant for the desired prediction date (14 days in the future)    |
    | prediction   |  Predicted value of normalized_case_norm 14 days into the future by estimated_county_rt     |
