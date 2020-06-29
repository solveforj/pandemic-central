# Pandemic Central

<p align="center">
  <img width="460" src="https://i.ibb.co/s65MwMK/pandemic-central-github.png"><br>
  <b>An application of Machine Learning in predicting U.S. COVID-19 cases (by county)</b>
</p>

Follow us on [Twitter](https://twitter.com/PandemicCentral)!

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/solveforj/pandemic-central/blob/master/LICENSE.txt)

## Getting Started
Follow these instructions to get the project up and running on your local machine.

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

For more details, please also read USAGE.md.

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
  ├── preprocess.py
  ├── README.md
  ├── tf_predict.py
  ├── train.py
  └── USAGE.md
```
In which:
- `raw_data/` contains the raw datasets (in csv or txt formats) for preprocessing.

- `processed_data/` contains processed and merged data and ready for training.

- `data/` contains other necessary datasets such as census or epidemiology.

- `models/` contains saved model from training and for later deployment.

- `generate_data.py` and `preprocess.py` process raw data.

- `train.py` uses processed data and trains in deep neural network using Scikit-learn.

- `tf_predict.py` does similar thing as train_scikit module but using TensorFlow. *This module is experimental at this moment.*

- `LICENSE.txt` is MIT license.

- `README.md` is what you are reading.

- `USAGE.md` is a detailed manual for specific use case.

## Authors
* [**Joseph Galasso**](https://github.com/solveforj/)
* [**Duy Cao**](https://github.com/caominhduy/)
* [**Kimberly Diwa**](https://github.com/kdiwa/)

## Support
Since this is still in its first versions, bugs and incompletions are unavoidable. Please feel free to comment or do pull request.
Your contributions are very valuable to us and this project.

For techical support, please email our developers:
jgalasso@udallas.edu (Joseph) or dcao@udallas.edu (Duy). Thank you for your patience.

## Credits
 Our project can not be completed without these great sources. We do not own any data, all input data we use are open-source or permission-granted.

 **Here is a list of datasets we have used so far:**

1. [Apple Maps Mobility Trends Reports](https://www.apple.com/covid19/mobility)

2. [Google Community Mobility Reports](https://www.google.com/covid19/mobility/)

3. [Facebook Movement Range](https://data.humdata.org/dataset/movement-range-maps)

3. [Johns Hopkins CSSEGISandData](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)

4. [COVID Tracking Project](https://www.covidtracking.com/)

5. [MIT Projections](https://github.com/youyanggu/covid19_projections/blob/master/projections/combined/latest_us.csv)

6. [IHME Datasets](http://ghdx.healthdata.org/us-data)

7. [Rt.live Reproduction Rate](https://rt.live/)

8. [CCVI Index](https://docs.google.com/spreadsheets/d/1qEPuziEpxj-VG11IAZoa5RWEr4GhNoxMn7aBdU76O5k/edit#gid=549685106)

9. [US Census Population Data](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html)

10. [USDA FIPS Code List](https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/)

We also thank you TensorFlow and community for very detailed and helpful official documentations.

**Don't forget to visit our friend websites with interesting data:**

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
