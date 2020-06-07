# pandemic-central
An AI that predicts the next location to be severely hit by COVID-19.

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/solveforj/pandemic-central/blob/master/LICENSE.txt)

## Project Structure
```
pandemic-central/
│
├── raw_data/
│    ├── apple
│    ├── census
│    ├── dicts
│    ├── google
│    ├── health_data
│    ├── jhu
│    ├── kaggle
│    └── unacast
│
├── jhu_rename.py
├── LICENSE.txt
├── preprocess_census.py
├── preprocess_health.py
├── preprocess.py
└── README.md
```
In which:
- `raw_data/` contains the raw datasets (in csv or txt formats) that we have collected or generated locally.


- `jhu_rename.py` automates the process of renaming Johns Hopkins datasets into isoformat date.


- `LICENSE.txt` is MIT license.


- `preprocess_census.py` preprocesses the 2010-2018 Census data (to shrink the size for our need only)


- `preprocess_health.py` preprocesses and merges datasets in `raw_data/health_data/`


- `preprocess.py` preprocesses and merges Apple, Google Mobility Reports and Unacast datasets.

- `README.md` is what you are reading.


## Database
In this project, we take advantage of these specific variables.

* From **Apple Maps Mobility Trends Reports**:
  - `geo_type`: country, region, sub-region, city, or county
  - `region` and `country`
  - `transportation`: _driving_ or _walking_
  - Date columns from `1/13/2020`


* From **Novel Corona Virus 2019 Dataset** _(Kaggle)_
  - `date`
  - `fips`: FIPS codes for county/ state _(see reference in Unacast section)_
  - `cases`
  - `deaths`


* From **Unacast**:
  - `state_fips`: FIPS codes for state. [_See a list here._](https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013696)
  - `state_name`
  - `county_fips`: FIPS codes for county. [_See a list here._](https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/home/?cid=nrcs143_013697)
  - `county_name`
  - `date`
  - `n_grade_total`, `n_grade_distance`, `n_grade_visitation`, and `n_grade_encounters`

## Authors
* [**Joseph Galasso**](https://github.com/solveforj/)
* [**Duy Cao**](https://github.com/caominhduy/)
* [**Kimberly Diwa**](https://github.com/kdiwa/)

## Credits
Here is a list of datasets we have used so far. We thank you for your great efforts and supports.

* **Apple Maps Mobility Trends Reports**

  [https://www.apple.com/covid19/mobility](https://www.apple.com/covid19/mobility)

  * Duy - get average movement for past 7 days


* **Google Community Mobility Reports**

  [https://www.google.com/covid19/mobility/](https://www.google.com/covid19/mobility/)

  * Duy - get average movement for past 7 days


* **Johns Hopkins CSSEGISandData**

  [https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)

  * Duy/Joseph - completed


* **COVID Tracking Project**

  https://www.covidtracking.com/

  * Joseph - completed


* **MIT Projections**

  https://github.com/youyanggu/covid19_projections/blob/master/projections/combined/latest_us.csv

  * Joseph - completed


* **IHME Datasets**

  http://ghdx.healthdata.org/us-data

  * Joseph - completed


* **Rt.live Reproduction Rate**

  https://rt.live/

  * Joseph - completed


* **CCVI Index**

  https://docs.google.com/spreadsheets/d/1qEPuziEpxj-VG11IAZoa5RWEr4GhNoxMn7aBdU76O5k/edit#gid=549685106

  * Joseph - completed


* **US Census Population Data**

  https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html

  https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/

  * Joseph - completed


**Websites with interesting data:**

* Facebook Data for Good

  https://dataforgood.fb.com/docs/covid19/

  https://visualization.covid19mobility.org/

* Unacast

  [https://www.unacast.com/covid19](https://www.unacast.com/covid19)


* COVID Tracking Project

  https://www.covidtracking.com/


* US FIPS Codes

  https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013696


* Kaggle COVID-19 Database

  https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset

**Full Data Google Drive Link**

https://drive.google.com/drive/folders/1gBTJ_Gq7qE0zkzLBxJpxq65ydMfODHBl?usp=sharing
