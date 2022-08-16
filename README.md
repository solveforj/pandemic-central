# Pandemic Central
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://itsonit.com)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/solveforj/pandemic-central/blob/master/LICENSE.txt)

<p align="center">
  <img width="460" src="https://i.ibb.co/NZHV7dr/Pandemic-Central-clear-background.png"><br>
  <b>An application of machine learning in forecasting U.S. COVID-19 cases</b>
</p>

## About The Model
Our model uses COVID-19 compartmental model forecasts in combination with demographic, population mobility, population health, and COVID-19 testing data to generate its own COVID-19 forecasts at the US county/county-equivalent level.

This repository contains the code we use to generate this information. For more details on our data sources and pipelines, please read the README.md files in the `data/` directory.

Our predictions were published on our [website](https://itsonit.com) and on [Twitter](https://twitter.com/PandemicCentral).

This work is published in a peer-reviewed journal article located at this doi: [10.1016/j.chaos.2021.111779](https://doi.org/10.1016/j.chaos.2021.111779).

## Disclaimer
We hope to serve as a valuable  resource for understanding trends in the ongoing pandemic and raise awareness about COVID-19 at the community level.  However, we strongly advise against **over-interpreting our predictions**. Machine learning models are only as good as the data that trains them.  We use the best quality data that is available to us, but we acknowledge that error in our predictions is unavoidable.

Some of our available data sources have updated their past data. To ensure the integrity
of data and replicate the results we report in our research journal preprint, Publication Methodology
must be used (see section *Generating Projections* below).

## Setup

* First, clone this repository:
  ```
  git clone https://github.com/solveforj/pandemic-central.git
  ```
* To install all dependencies in Python 3 (≥ 3.7):
  ```
  pip install -r requirements.txt
  ```
* For map rendering, install [Orca](https://github.com/plotly/orca) and ensure that it is added to your PATH
* Get a COVIDActNow.org API access key if you intend to generate projections (register [here](https://apidocs.covidactnow.org/#register))

## Generating Projections

There are two ways to generate projections:

1. **Standard Methodology**:  This can be used to generate the latest projections for the present date by using the latest datasets and reduces runtime by eliminating feature importance scoring. You need the *reference date* for which you want to generate projections and your *COVIDActNow.org API access key* (see above for registration instructions). Use the command below:
```
python auto.py -d 2021-05-18 -r YOUR_API_KEY
```
If your reference date is not a Sunday (i.e. week start), you may specify an optional flag to create projections for the Sunday prior to your reference date:
```
python auto.py -d 2021-05-18 -r YOUR_API_KEY --sunday
```

2. **Publication Methodology (for projections ONLY before 2021-01-15)**: Used to replicate projections using the specific methodology of our publication in progress  (i.e. including feature importance scoring and the input datasets from 2021-05-18), with a similar command to the Standard Methodology:
```
python auto.py -d 2021-05-18 -r YOUR_API_KEY --publication_method --sunday
```
Statistics and figures from the publication manuscript may be regenerated using preloaded datasets referenced specifically by the manuscript with the command below:
```
python auto.py --figures
```

Projections and related files will be in the `output/` subdirectory and publication figures will be in the `publication/output` subdirectory.

## Credits
* [Joseph Galasso](https://github.com/solveforj/)
* [Duy Cao](https://github.com/caominhduy/)

## Contact us
* [jgalasso@udallas.edu](mailto:jgalasso@udallas.edu)
* [dcao@udallas.edu](mailto:dcao@udallas.edu)

## Versioning
Our latest version is v3.0.0. For version details, see **Releases** tags.
