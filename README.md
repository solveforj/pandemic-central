# pandemic-central
An AI that predicts the next location to be severely hit by COVID-19.

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/solveforj/pandemic-central/blob/master/LICENSE.txt)

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

* **Unacast**

  [https://www.unacast.com/covid19](https://www.unacast.com/covid19)

* **Johns Hopkins CSSEGISandData**
  [https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)

Here is a list of websites with good data

https://dataforgood.fb.com/docs/covid19/

http://ghdx.healthdata.org/

https://www.census.gov/

https://rt.live/

https://github.com/CSSEGISandData/COVID-19

https://www.covidtracking.com/

https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013696

https://www.kaggle.com/sudalairajkumar/novel-corona-virus-2019-dataset


## Data folder

[Click here for Microsoft OneDrive Folder](https://universityofdallas-my.sharepoint.com/:f:/g/personal/jgalasso_universityofdallas_onmicrosoft_com/EjuRZaRDJWxAkSpmBCPnJ88Bu0UhsF-4M7M397EAGRN2hQ?e=awJtRN)
