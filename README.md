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
Follow these instructions to get the project up and running on your local machine. For detailed information, see `USAGE.md`.

### Prerequisites

These are what you **must** install before using our project.

1. [NumPy](https://pypi.org/project/numpy/) and [Matplotlib](https://pypi.org/project/matplotlib/)

2. [Scikit-learn](https://scikit-learn.org/stable/install.html)

3. [TensorFlow](https://www.tensorflow.org/install) (release ≥ 2.0.0)

Your local machine must also have Python 3 (≥ 3.7) installed beforehand.

### Run
To run project, first clone this repository, then run this command
  ```
  python3 pandemic-central
  ```
or you can also download the zip package from Lastest Release **(we recommend cloning and pulling method since it contains the lastest data files and hot fixes.)**

For more details, please also read `USAGE.md`.

### GitHub
Make sure you always clone and pull the lastest data from Pandemic Central.
**Notice that our repository can always be found at https://github.com/solveforj/pandemic-central.**


## Project Structure
This is not complete project structure, read USAGE.md for more details.
```
pandemic-central/
  ├── __init__.py
  ├── __main__.py
  │
  ├── data/
  ├── raw_data/
  ├── processed_data/
  ├── models/
  │
  ├── generate_data.py
  ├── LICENSE.txt
  ├── predict.py
  ├── preprocess.py
  ├── README.md
  ├── tf_predict.py
  ├── train.py
  └── USAGE.md
```
In which:
- `raw_data/` contains the raw mobility datasets (in csv or txt formats) for preprocessing.

- `processed_data/` contains processed and merged mobility data that is ready for training.

- `data/` contains other necessary raw or processed datasets such as census or epidemiology.

- `models/` contains saved TensorFlow models from training and for later deployment.

- `preprocess.py` preprocesses raw Google and Apple mobility data (among other tasks) for eventual integration into training datasets.

- `generate_data.py` processes and merges all mobility, socioeconomic, and health data into the final training datasets.

- `train.py` trains a Random Forest Regression model using Scikit-Learn and appends predictions to the dataset. *This is currently the default model.*

- `tf_predict.py` trains a TensorFlow Neural Network model. *This currently an experimental model.*

- `predict.py` generates predictions for each county for the last 5 weeks, generating the latest detailed predictions, which we add to this repository daily.

- `LICENSE.txt` is MIT license.

- `README.md` is what you are reading now.

- `USAGE.md` is a detailed manual for specific use case.

## Authors
* [**Joseph Galasso**](https://github.com/solveforj/)
* [**Duy Cao**](https://github.com/caominhduy/)
* [**Kimberly Diwa**](https://github.com/kdiwa/)

## Support
Since this is still in its earliest versions, bugs and incompletions are unavoidable. Please feel free to comment or make a pull request.
Your contributions are very valuable to us and this project.

For technical support, please email our developers:
[jgalasso@itsonit.com](mailto:jgalasso@itsonit.com) (Joseph) or [dcao@udallas.edu](mailto:dcao@udallas.edu) (Duy). Thank you for your patience.

## Versioning
Our latest version is v1.0.2. For version details, see **Releases** tags.

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

We also thank the TensorFlow and Python communities for very detailed and helpful official documentations.

**Please check out these resources for yourself!**
