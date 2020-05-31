# pandemic-central
An AI that predicts the next location to be severely hit by COVID-19.

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

## Database
In this project, we take advantage of these specific variables.

* From **Apple Mobility Trends Reports**:
  - `geo_type`: country, region, sub-region, city, or county
  - `region` and `country`
  - `transportation`: _driving_ or _walking_
  - Date columns from `1/13/2020`


* From **Unacast**:
  - `state_fips`: FIPS codes for state. [_See a list here._](https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013696)
  - `state_name`
  - `county_fips`: FIPS codes for county. [_See a list here._](https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/home/?cid=nrcs143_013697)
  - `county_name`
  - `date`
  - `n_grade_total`, `n_grade_distance`, `n_grade_visitation`, and `n_grade_encounters`

## Authors
* **Joseph Galasso** - [solveforj](https://github.com/solveforj/)
* **Duy Cao** - [caominhduy](https://github.com/caominhduy/)
* **Kimberly Diwa**

## Credits
*Here is a list of websites with good data*

https://dataforgood.fb.com/docs/covid19/

http://ghdx.healthdata.org/

https://unacast.com/

https://www.census.gov/

https://rt.live/

https://github.com/CSSEGISandData/COVID-19

https://www.covidtracking.com/

https://www.apple.com/covid19/mobility

https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013696

## Data folder

[_Go here_] (https://universityofdallas-my.sharepoint.com/:f:/g/personal/jgalasso_universityofdallas_onmicrosoft_com/EjuRZaRDJWxAkSpmBCPnJ88ByQXvr_YX0iQqn0vySH9HzA?e=BBGsbx)
