# Pandemic Central
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://itsonit.com)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/solveforj/pandemic-central/blob/master/LICENSE.txt)

<p align="center">
  <img width="460" src="https://i.ibb.co/NZHV7dr/Pandemic-Central-clear-background.png"><br>
  <b>An application of machine learning in forecasting U.S. COVID-19 cases</b>
</p>

## About this model
Our model uses COVID-19 compartmental model forecasts in combination with demographic, population mobility, population health, and COVID-19 testing data to generate its own COVID-19 forecasts at the US county/county-equivalent level.

This repository contains the code we use to generate this information. For more details on our data sources and pipelines, please read the README.md files in the `data/` directory.

See our latest predictions at our [website](https://itsonit.com) and check us out on [Twitter](https://twitter.com/PandemicCentral).

## Disclaimer
We hope to serve as a valuable  resource for understanding trends in the ongoing pandemic and raise awareness about COVID-19 at the community level.  However, we strongly advise against **over-interpreting our predictions**. Machine learning models are only as good as the data that trains them.  We use the best quality data that is available to us, but we acknowledge that error in our predictions is unavoidable.

## Generating projections

* First, clone this repository:
  ```
  git clone https://github.com/solveforj/pandemic-central.git
  ```
* To install all dependencies in Python 3 (≥ 3.7):
  ```
  pip install requirements.txt
  ```
* From the project directory, run the entire module with the command below, specifying the date for which you want to generate projections and your COVIDActNow.org API Access key (register [here](https://apidocs.covidactnow.org/#register)) as follows:
  ```
  python auto.py -d 2021-04-11 -r API_KEY
  ```
* The output data files will be in the `/output` directory:
  * The `/model_stats` directory contains model performance statistics (mean absolute error and R<sup>2</sup> on forecasts vs. actual cases in the training dataset) for each date projections were generated for
  * The `/raw_predictions` directory contains model projections for the date projections were generated for and the preceding 9 weeks; all training dataset features are included for each of these weeks, as well
  * The `/ReichLabFormat` directory contains predictions formatted as necessary for submission to the COVID-19 Forecast Hub
  * The `/website` directory contains various files, many of which are published in some form on our [website](https://www.itsonit.com)

## Credits
* [Joseph Galasso](https://github.com/solveforj/)
* [Duy Cao](https://github.com/caominhduy/)

## Contact us
* [jgalasso@udallas.edu](mailto:jgalasso@udallas.edu)
* [dcao@udallas.edu](mailto:dcao@udallas.edu)

## Versioning
Our latest version is v3.0.0. For version details, see **Releases** tags.
