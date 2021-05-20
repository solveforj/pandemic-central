# COVID-19 R<sub>t</sub> Data

### Description
COVID-19 effective reproduction number (R<sub>t</sub>) time-series is obtained from the [COVIDActNow.org](https://www.covidactnow.org) API for R<sub>t</sub> features

### Files
- **preprocess.py** cleans and processes the data from these sources:
  - COVIDActNow.org API [state time-series data](https://api.covidactnow.org/v2/states.timeseries.csv) - note that API key is needed for access
  - COVIDActNow.org API [county time-series data](https://api.covidactnow.org/v2/counties.timeseries.csv) - note that API key is needed for access
  - See `/JHU`, `/census`, `/COVIDTracking` and `/geodata` directories for information on any cases, census, testing, and geographical datasets used here, respectively
- **rt_data.csv** is one output of `preprocess.py` and contains merged state and county R<sub>t</sub> time-series
- **aligned_rt_7.csv** is one output of `preprocess.py` and contains 7-week forecast R<sub>t</sub> features
- **aligned_rt_14.csv** is one output of `preprocess.py` and  contains 14-week forecast R<sub>t</sub> features
- **aligned_rt_21.csv** is one output of `preprocess.py` and contains 21-week forecast R<sub>t</sub> features
- **aligned_rt_28.csv** is one output of `preprocess.py` and contains 28-week forecast R<sub>t</sub> features
- **higher_corrs.csv** is one output of `preprocess.py` and describes, for each county that projections were made for, which of the two R<sub>t</sub> time-series (county or state) had the highest max correlation with the case time-series when aligned
