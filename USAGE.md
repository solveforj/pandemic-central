<p align="center">
  <img alt="pandemic-central-logo" width="460" src="https://i.ibb.co/xYSCLt7/Pandemic-Central-clear-background.png"><br>
  <b>An application of Machine Learning in predicting COVID-19 cases</b>
</p>

## Introduction
This provides you a high level overview of the package: understanding the menu, how preprocessing works, etc.

<p align="center">
  <img alt="pandemic-central-pipeline" width="460" src="https://i.ibb.co/S6LwC3M/Pandemic-Central-Pipeline.png"><br>
  <i>Figure 1: Graphic pipeline from input to processing and output</i>
</p>

### Disclaimer
 This does not aim to give you everything in details. Thus, if you have question such as "What is Random Forest?" and "What is an estimator?" then this is not for you. Official documentations and googling are always best friends!

### Decide your use case
Before you proceed to read any further, please first do the following steps:

1. **Identify your purpose:**
   * What is your purpose in discovery of this project?
   * Who are you: a newspaper reporter, a concerned citizen, a reseacher, a developer, etc?


2. **How are you going to take advantage of this repository:**
   * For your knowledge
   * For your required work / project
   * For your desire to contribute to the community
   * For commercial use


3. **How comfortable do you feel with programming, especially Python, and Machine Learning platforms**

If you are simply concerned of COVID-19, blogger, politician, or reporter, etc, or you only want to keep yourself updated with predicted information, then please visit our [website](https://itsonit.com) first. It should always cover the latest information about our project, visualized, and also related information.

If you are a developer, then please proceed. Also, even if you do not use prediction, but are simply looking for a useful source of related data about COVID-19 in USA, then we do believe that our project is also very useful for you. We have mobility data, epidemiological data, census, number of cases, facts, etc. All are merged and sorted by U.S. county and timestamp!

## Understand The Menu
Here is the menu, what you should expect to see:
![Main_Menu](https://i.ibb.co/phWFd0Z/Screen-Shot-2020-07-04-at-3-24-18-AM.png)

1. **Option 1:** this will preprocess raw data and export into a CSV compressed, with up-to-date data (to the lastest date that all sources can provide data).
Tip: If you clone and pull from Pandemic Central's repository frequently then you should have the latest processed data already, as we will try to push new data everyday.

   * Output file size: make sure you have enough storage (at least 700 MB) for downloading some data from sources (most heavy files will be erased after its job is done).

   * Location: the output file will be placed inside the project folder, in `processed_data/merge/` with the name as the date when it is generated.

   * How to view: first you need to unzip the file, it is in gzip format, so you may need special tool (for Windows users) to unzip it. The unzipped will be in Comma-separated-values format (csv) and you can view it in many ways, like Excel.


2. **Option 2:** This will run the `generate_data.py` file, generating two training datasets, one with Facebook mobility data and the other without.

    * Output files (size < 50 Mb):

      1. training_mobility.csv.gz

      2. training_no_mobility.csv.gz

    * Output files are placed in the **same directory** that the project folder is located in.


3. **Option 3:** This will run the entire SciKit-Learn data processing, training, and predictions pipeline.

  * *Option 2* will be run first, generating the aforementioned datasets

  * `train.py` will be run on these datasets, creating a Random Forest Regression model that will generate predictions on these datasets.

    * Output files (size < 50 Mb):

        1. mobility_full_predictions.csv.gz

        2. no_mobility_full_predictions.csv.gz

        3. mobility_latest.csv.gz

        4. no_mobility_latest.csv.gz

    * Output files are placed in the **same directory** that the project folder is located in.

  * `predict.py` will be run on the latter two of the datasets produced by `train.py` to produce a merged .csv file of counties with and without mobility, in addition to data for our website.

    * Output files (size < 50 Mb):

        1. full_predictions_yyyy-mm-dd.csv

        2. yyyy-mm-dd_webdata.csv

    * The first output file is placed in the `pandemic-central/predictions` folder and the second is placed in the **same directory** that the project folder is located in.

4. **Option 4:** this option assumes that you have already had the lastest data using option 1 or by pulling the lastest data from our repository frequently. The lastest zipped dataset in `processed_data/merge/` will be used for TensorFlow training. At this point, TensorFlow models are still in development as the mean absolute error is still about 70 cases (as comparison to apprx. 10 cases with Scikit-learn)

5. **Option 5:** exit Python.


## Preprocess
If you run Pandemic Central, you may be surprised by how many time the word 'preprocess' is repeated.

![preprocess-funny-art](https://i.ibb.co/SvWtmHk/preprocess-funny-art.png)


Indeed, in this project, we consider data preprocessing is the most important stage. Without proper data, Machine Learning is either non-applicable or meaningless!

**So how do we preprocess data?**

### Collect raw data
Our project uses data from a variety of sources.

#### Google Community Mobility Reports
These are one of the first datasets that we have used in this project. For these kind of datasets, the latest file is the most important one since it should contain all of the data up to a point it is created.

You can visit Google Community Mobility Reports [here](https://www.google.com/covid19/mobility/).

![google_mobility_data_1](https://i.ibb.co/XCtyDsP/Screen-Shot-2020-06-24-at-5-23-08-PM.png)

When running, the global mobility data will be downloaded and store at: `raw_data/google/`.

With Google Data, as you may see in the CSV there have been a lot of empty values in the dataset showing that there is no record in many points of time and locations. So, after calculating the correlation between categories, we decide to go forward and average out the columns with the number of available entries on rows instead of dropping rows with NaNs. For example, a row with values

Retail |  Grocery and Pharmacy |  Park |  Transit |  Workplace |  Residential
--|---|---|---|---|--
1  |  2 |  3 |  4 |  5 | 6

will be noticed as 3.5.

Meanwhile, a row with entries

Retail |  Grocery and Pharmacy |  Park |  Transit |  Workplace |  Residential
--|---|---|---|---|--
NaN  |  Nan |  3 |  NaN |  NaN | NaN

will have value of 3.

#### Apple Maps Mobility Trends Reports

You can visit it [here](https://www.apple.com/covid19/mobility).

![apple_mobility_1](https://i.ibb.co/gyKFf87/Screen-Shot-2020-06-24-at-5-48-15-PM.png)

The CSV file will be downloaded and compressed in this directory: `raw_data/merged`.

In Apple Mobility Data, we have sorted to only use rows with transportation type as `driving` since *driving* suggests larger movement range as well as carpooling.

#### Facebook Movement Range

You can visit our Facebook Movement Range source [here](https://data.humdata.org/dataset/movement-range-maps)

![Facebook Movement Range Maps](https://i.ibb.co/mzV2kdH/facebook-movement-range.png)

Since the zip file has more than just data file, so when running, our program downloads, unzips, reads the data txt file, sorts out US data and compresses it in this directory `raw_data/facebook`.

Then, the data is preprocessed by keeping the necessary columns, changing column names and exporting into `data/facebook_data.csv`.

#### Other related health data

For this part, we use data from variety of sources.

1. **Racial Disparities** from *Surgo*.


2. **Diabetes Data** from Institute for Health Metrics and Evaluation (IHME). Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S.


3. **Obesity Data** from IHME [(source)](http://ghdx.healthdata.org/record/ihme-data/united-states-physical-activity-and-obesity-prevalence-county-2001-2011). We use the Obesity Prevalence 2011 data and separate male and female obesity data.

4. **Motality Data** from IHME [(source)](http://ghdx.healthdata.org/record/ihme-data/united-states-life-expectancy-and-age-specific-mortality-risk-county-1980-2014)

5. **Infectious Disease Mobility** from IHME [(source)](http://ghdx.healthdata.org/record/ihme-data/united-states-infectious-disease-mortality-rates-county-1980-2014)

6. **Respiratory Disease Mortality** from IHME [(source)](http://ghdx.healthdata.org/record/ihme-data/united-states-chronic-respiratory-disease-mortality-rates-county-1980-2014)

7. **Smoking Prevalence** from IHME [(source)](ghdx.healthdata.org/record/ihme-data/united-states-smoking-prevalence-county-1996-2012)

8. And COVID-19 Data. For this part, our source code should explain better (see in `generate_data.py` from line 321).

#### 14-day Moving Average

In stock markets, Moving Average is a very well-known method to smooth out the fluctuations (if any) and to point out the trends of data.

**But, why do we need it for COVID-19?**

As you may have noticed, COVID-19 scenario is also time-sensitive. Situations change daily, even hours, thus it is considered as time series data. Normally, symptoms may appear after up to 14 days after exposure with COVID-19. Also, the data report techniques and testing procedures maybe inconsitent between dates, counties, and human behaviors.

There are many factors causing the pikes in data to occur, so smoothing the data is very helpful in this case.

## Training

### Scikit-learn

First we split the data into 2 datasets (90% as training dataset and 10% as testing dataset).

For training in Scikit-learn, we use an built-in estimator called [*Random Forest Regressor*](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html).

The accuracy metric is then scored using coefficient of determination of the predicted data on testing dataset (R^2), where 1.00 is the best.

### TensorFlow

The input pipeline is similar to the one we use with Sklearn. However, for TensorFlow training, we use Google and Apple Mobility data along with Facebook Mobility data.

For training, TensorFlow builds model with 3 layers, with ReLU activation and RMSprop gradient optimization.

At this moment, the Mean Abosulte Error we have for TensorFlow model is about 1.09 - 1.5 cases for testing dataset (after about 700 epochs).

<p align="center">
  <img width="500" alt="tensorflow-report" src="https://i.ibb.co/mhHfLfC/overfit.png"><br>
  <i>Figure 2: TensorFlow MAE</i>
  <br><br>
</p>

<p align="center">
<a href="https://ibb.co/j6sPRjT"><img src="https://i.ibb.co/FxCLVdK/tf-projection-demo.png" alt="tf-projection-demo" border="0" /></a>
</p>

<p align="center">
<i>Figure 3: Side-by-side projections by predicted data and real data</i></p>


*TensorFlow module is still in development and we are doing our best to improve the result*
