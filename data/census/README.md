# Census Data

### Description
Processes all census data for census related features and model output for the [COVID-19 Forecast Hub](https://covid19forecasthub.org/)

### Files
  * **Reichlab_Population.csv** contains state populations for use in generating COVID-19 Forecast Hub output, is sourced from [here](https://github.com/reichlab/covid19-forecast-hub/blob/master/data-locations/locations.csv)
  * **cc-est2018-alldata.csv.gz** is the gunzipped U.S. Census Annual County Resident Population Estimates by Age, Sex, Race, and Hispanic Origin: April 1, 2010 to July 1, 2018 (CC-EST2018-ALLDATA) file; column definitions and the file may be found [here](www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html)
  * **nst-est2019-alldata.csv** is the U.S. Census Population, Population Change, and Estimated Components of Population Change: April 1, 2010 to July 1, 2019 (NST-EST2019-alldata) file; column definitions and the file may be found [here](https://www.census.gov/data/tables/time-series/demo/popest/2010s-national-total.html#par_textimage)
  * **preprocess.py** uses U.S. census data (from this directory) and geographical data (see `/geodata` directory for relevant documentation) to generate demographic features for U.S. counties
  * **census.csv** is the output file of `preprocess.py`
