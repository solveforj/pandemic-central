# covid-vaccine-data

<p align="center">
  <img width="300" src="https://itsonit.com/static/images/Pandemic-Central-white-background.png"><br>
  <a href="itsonit.com"><b>For more details about COVID-19, check itsonit.com</b></a>
</p>

This is reformatted data from the CDC. For data repo alone, see [here.](https://github.com/caominhduy/covid-vaccine-data)

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)]()
[![License](http://img.shields.io/:license-mit-blue.svg)]()

## How to Use
Column Name  |  Meaning
--|--
state  |  name of state in two-letter format
date  |  date of **distribution allocations*** _(not cumulative)_
pfizer_first_doses  |  number of Pfizer doses allocated _(not cumulative)_
moderna_first_doses  |  number of Moderna doses allocated _(not cumulative)_
total_first_doses  |  pfizer_first_doses + moderna_first_doses _(not cumulative)_

## Notice

- 2nd doses of Pfizer are scheduled to be administered 21 days after 1st doses

- 2nd doses of Moderna are scheduled to be administered 28 days after 1st doses

    Source: https://www.cdc.gov/vaccines/covid-19/info-by-product/clinical-considerations.html

- The efficacy of Pfizer is claimed to be ~95% on 28th day after first dose

    Source: https://www.pfizer.com/news/press-release/press-release-detail/pfizer-and-biontech-conclude-phase-3-study-covid-19-vaccine

- Generally for vaccines, longer gap between first and booster doses create a better immune response. However, there has not been enough data about extending such gap with COVID-19 vaccines.

- *Date of distribution allocations are different from dates of administered, which vary by states.

- Again, values not cumulative, doses are new ones on specified dates.
