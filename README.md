# Pandemic Central

<p align="center">
  <img width="460" src="https://i.ibb.co/NZHV7dr/Pandemic-Central-clear-background.png"><br>
  <b>An application of machine learning in forecasting U.S. COVID-19 cases</b>
</p>

We utilize socioeconomic, mobility, and epidemiological datasets to forecast COVID-19 cases at the US county/county-equivalent level. This repository contains the code we use to generate this information.


See our latest predictions at our [website](https://itsonit.com) and check us out on [Twitter](https://twitter.com/PandemicCentral).

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://itsonit.com)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/solveforj/pandemic-central/blob/master/LICENSE.txt)

## Disclaimer
We hope to serve as a valuable  resource for understanding trends in the ongoing pandemic and raise awareness about COVID-19 at the community level, something which is desperately needed in our attempts to lower the curve.  However, we strongly advise against **over-interpreting our predictions**. Machine learning models are only as good as the data that trains them.  We use the best quality data that is available to us, but we acknowledge that error in our predictions is unavoidable.

## Getting Started
Follow these instructions to get the project up and running on your local machine.

### Prerequisites

These are what you **must** install before using our project.

1. [NumPy](https://pypi.org/project/numpy/), [Pandas](https://pandas.pydata.org/) and [Matplotlib](https://pypi.org/project/matplotlib/)

2. [Scikit-learn](https://scikit-learn.org/stable/install.html)

Optional:

1. [TensorFlow](https://www.tensorflow.org/install) (release ≥ 2.0.0) and [TensorFlow_docs](https://github.com/tensorflow/docs)

2. [Plotly](https://plotly.com/) including: plotly, chart_studio, and [Plotly Orca](https://github.com/plotly/orca)
3. [psutil](https://pypi.org/project/psutil/)

Your local machine must also have Python 3 (≥ 3.7) installed beforehand.

### Run
To run this project, first clone this repository.
  ```
  git clone https://github.com/solveforj/pandemic-central.git
  ```
<br>

For a basic usage, use this command
  ```
  python covid.py -d
  ```
or
  ```
  python covid.py --default
  ```
This command should download the data from sources, preprocess them, train, and export predictions.
<br><br><br>
For full list of available commands, use
  ```
  python covid.py --help
  ```

### GitHub
Make sure you always clone and pull the latest version from Pandemic Central.
**Our repository can always be found at https://github.com/solveforj/pandemic-central.**

## Authors
* [**Joseph Galasso**](https://github.com/solveforj/)
* [**Duy Cao**](https://github.com/caominhduy/)

## Support
Since this is still in its earliest versions, bugs and incompletions are unavoidable. Please feel free to comment or contact our developers!
Your contributions are very valuable to us and this project.

For technical support, please email our developers:
[jgalasso@itsonit.com](mailto:jgalasso@udallas.edu) (Joseph) or [dcao@udallas.edu](mailto:dcao@udallas.edu) (Duy). Thank you for your patience.

## Versioning
Our latest version is v2.0.0. For version details, see **Releases** tags.

## Credits
 Our project can not be completed without these great sources. We do not own any data; all input data we use are open-source or permission-granted. More details about how we process this data may be found in `generate_data.py` and `preprocess.py`.

 Here is a list of datasets we have used so far:

1. [Apple Maps Mobility Trends Reports](https://www.apple.com/covid19/mobility)

2. [Google Community Mobility Reports](https://www.google.com/covid19/mobility/)

3. [Facebook Movement Range](https://data.humdata.org/dataset/movement-range-maps)

3. [Johns Hopkins CSSEGISandData](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)

4. [COVID Tracking Project](https://www.covidtracking.com/)

5. [MIT Projections](https://github.com/youyanggu/covid19_projections/blob/master/projections/combined/latest_us.csv)
6.    [IHME Datasets](http://ghdx.healthdata.org/us-data)
7.    [Rt.live Reproduction Rate](https://rt.live/)
8.    [CCVI Index](https://docs.google.com/spreadsheets/d/1qEPuziEpxj-VG11IAZoa5RWEr4GhNoxMn7aBdU76O5k/edit#gid=549685106)
9.    [US Census Population Data](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html)
10.    [USDA FIPS Code List](https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/)

We also thank Plotly, TensorFlow and Python communities for very detailed and helpful documentations.

**Please check out these resources for yourself!**
