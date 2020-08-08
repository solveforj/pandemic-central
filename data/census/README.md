# Census Data

- **Description**: Contains multiple files for 2018 census and demographic data for US counties. Relevant columns are selected from these datasets and normalized for county population if possible.

- **Files**:

  - **preprocess.py** cleans and processes the data to generate the output dataset (_census.csv_)

  - **census.csv** is the output of _preprocess.py_ and contains the following columns:

    | Column      | Description |
    | ----------- | ----------- |
    | FIPS   | The FIPS of interest        |
    | POP_DENSITY   | Population density per sq. mile      |
    | TOT_POP   | Total population of county        |
    | BA_MALE   | % of county population that is black male        |
    | BA_FEMALE   | % of county population that is black female        |
    | IA_MALE   | % of county population that is native american male         |
    | IA_FEMALE   | % of county population that is native american female         |
    | NA_MALE   | % of county population with unknown race male         |
    | NA_MALE   | % of county population with unknown race female         |
    | TOM_MALE   | % of county population that is two or more races male         |
    | TOM_FEMALE   | % of county population that is two or more races female         |
    | H_MALE   | % of county population that is hispanic male         |
    | H_FEMALE   | % of county population that is hispanic female         |
    | ELDERLY_POP   | % of county population that is over the age of 60         |
    | Land Area   | County area in sq. miles        |


  - **cc-est2018-alldata.csv.gz** is found on [this webpage](www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html). The file is *Annual County Resident Population Estimates by Age, Sex, Race, and Hispanic Origin: April 1, 2010 to July 1, 2018 (CC-EST2018-ALLDATA)* and contains population demographics. To reduce file size, the original file has been gunzipped.

  - **nst-est2019-alldata.csv** is found on [this webpage](www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/). The file is *nst-est2019-alldata.csv* and contains population demographics at the US state level.
