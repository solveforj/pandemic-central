# COVID-19 Cases Data

### Description
COVID-19 county-level case data from [John Hopkins University](https://coronavirus.jhu.edu/) is used to generate case features and validate the model's performance

### Files
- **preprocess.py** cleans and processes the data from these sources:
  - [JHU CSSE Github](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv)
  - See `/census` and `/geodata` directories for information on any census and geographical datasets used here, respectively
- **jhu_data.csv** is the output of `preprocess.py` and contains all case features
