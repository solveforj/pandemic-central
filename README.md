# Pandemic Central
Use Machine Learning to predict the number of COVID-19 cases in the next 7 days. We are also on [Twitter](https://twitter.com/PandemicCentral)!

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/solveforj/pandemic-central/blob/master/LICENSE.txt)

## Getting Started
Follow these instructions to get the project up and running on your local machine.

### Prerequisites
These are what you **must** install before using our project.
1. [Scikit-learn](https://scikit-learn.org/stable/install.html)

2. [TensorFlow](https://www.tensorflow.org/install) (release 2.0.0 or later)

### GitHub
Make sure you clone and pull the lastest data from Pandemic Central.
Notice that our repository can always be found at https://github.com/solveforj/pandemic-central.
This is still in its early stages, so feel free to comment or pull request.
Your contributions are very valuable to us and this project.

### Run
  ```
  python3 pandemic-central
  ```
or you can also run individual modules for your own purposes.

## Project Structure
This is not complete project structure, read USAGE.md for more details.
```
pandemic-central/
  ├── __init__.py
  ├── __main__.py
  │
  ├── raw_data/
  ├── processed_data/
  ├── models/
  │
  ├── generate_data.py
  ├── LICENSE.txt
  ├── preprocess.py
  ├── README.md
  ├── tf_predict.py
  ├── train_scikit.py
  └── USAGE.md
```
In which:
- `raw_data/` contains the raw datasets (in csv or txt formats) for preprocessing.

- `processed_data/` contains processed and merged data and ready for training.

- `models/` contains saved model from training and ready for deployment.

- `generate_data.py` and `preprocess.py` process raw data.

- `train_scikit.py` uses processed data and trains in deep neural network using Scikit-learn.

- `tf_predict.py` does similar thing as train_scikit module but using TensorFlow. *This module is experimental at this moment.*

- `LICENSE.txt` is MIT license.

- `README.md` is what you are reading.

- `USAGE.md` is a detailed manual for specific use case.

## Authors
* [**Joseph Galasso**](https://github.com/solveforj/)
* [**Duy Cao**](https://github.com/caominhduy/)
* [**Kimberly Diwa**](https://github.com/kdiwa/)

## Credits
Here is a list of datasets we have used so far. Our project can not be completed without these great and open sources.

1. [Apple Maps Mobility Trends Reports](https://www.apple.com/covid19/mobility)

2. [Google Community Mobility Reports](https://www.google.com/covid19/mobility/)

3. [Johns Hopkins CSSEGISandData](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)

4. [COVID Tracking Project](https://www.covidtracking.com/)

5. [MIT Projections](https://github.com/youyanggu/covid19_projections/blob/master/projections/combined/latest_us.csv)

6. [IHME Datasets](http://ghdx.healthdata.org/us-data)

7. [Rt.live Reproduction Rate](https://rt.live/)

8. [CCVI Index](https://docs.google.com/spreadsheets/d/1qEPuziEpxj-VG11IAZoa5RWEr4GhNoxMn7aBdU76O5k/edit#gid=549685106)

9. [US Census Population Data](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html)

10. [USDA FIPS Code List](https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/)

We also thank you TensorFlow and community for very detailed and helpful official documentations.

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
