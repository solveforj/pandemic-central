<p align="center">
  <img width="460" src="https://i.ibb.co/s65MwMK/pandemic-central-github.png"><br>
  <b>An application of Machine Learning in predicting COVID-19 cases</b>
</p>

## Introduction
This provides you a high level overview of the package: how to understand the options, how to feed your own data, and how to read the output.

### Disclaimer
 This does not aim to give you all detailed problems, or full knowledge of Machine Learning in a highly technical manner. Thus, if you have question such as "What is Random Forest?" and "What is an estimator?" then this is not for you. Official documentations are always the best sources to learn it!

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

If you are simply concerned of COVID-19, blogger, or reporter, and you only want to predict the information, then please visit our [Twitter](https://twitter.com/PandemicCentral) or [website](https://itsonit.com) first. These should always cover the lastest information about our project, with visuals, and also related information.

If you are a developer, then please proceed. Also, even if you do not use prediction, but are needing for a great source of related data about COVID-19 in USA, then we do believe that our project is also very useful for you. We have mobility data, epidemiological data, census, number of cases, facts, sorted to the precision of U.S. county and date!

## Understand The Menu
Here is a menu, if you run it correctly without errors (well hopefully), here is what you should expect to see:
![Main_Menu](https://i.ibb.co/NsdY2Qk/Screen-Shot-2020-06-24-at-1-59-10-PM.png)

1. **Option 1:** you will use this option to create a full dataset of all necessary information, up-to-date (or at least to the lastest date that our source can provide data). If you clone and pull from Pandemic Central's repository frequently then you should have the latest processed data already, so unless you know what you are doing, you do not have to run this.

   * Output file size: around 12-30 MB after it completes (as zipped), make sure you have enough storage (at least 700 MB) for downloading some data from sources (will be erased after it is done).

   * Location: the output file will be placed inside the project folder, in `processed_data/merge/` with the name as the date when it is generated.

   * How to view: first you need to unzip the file, it is in gzip format, so you may need special tool (Windows users) to unzip it. The unzipped will be in Comma-separated-values format (csv) and you can view it in many ways, but we recommend excel.


2. **Option 2:** you will use this option to create a full datasets of information but Google and Apple mobility, these files (although not required to be generated) should give you a visual look of the input training data of Scikit-learn models.

    * Output file sizes: there will be 5 files, around 2-250 MB / ea, after it completes (as csv files), make sure you have enough storage.

    * Location: the output files will be placed **outside** the project folder.

    * How to view: first you need to unzip the file, it is in gzip format, so you may need special tool (Windows users) to unzip it. The unzipped will be in Comma-separated-values format (csv) and you can view it in many ways, but we recommend Microsoft Excel.


3. **Option 3:** this option is initially similar to *option 2* (except datasets are not exported into local csv files), before the processed dataframe is feeded into Scikit-learn (module `train.py`) for training and printing predictions.

  * Output file sizes: there will be 2 files, around 130-200 MB / ea, after it completes (as Pickle files), these will be our models for further evaluation or prediction.

  * Location: the output files will be placed **outside** the project folder.

4. **Option 4:** this option assumes that you have already preprocessed the lastest data using option 1 or by cloning and pulling from our repository frequently. The lastest zipped dataset in `processed_data/merge/` will be used for TensorFlow training.


5. **Option 5:** exit Python.


## Preprocess
If you run Pandemic Central, you may be surprised by how many time the word 'preprocess' is repeated.

![preprocess-funny-art](https://i.ibb.co/SvWtmHk/preprocess-funny-art.png)


Indeed, in this project, we consider data preprocessing is the most important stage. Without proper data, Machine Learning is either non-applicable or meaningless!

**So how do we preprocess data?**

### Collect raw data
Our project uses data from a variety of sources.

#### Google Community Mobility Reports
These are one of the first datasets that we have used in this project. For these kind of datasets, the latest file is the most important one since it should contain all of the data up to a point it is created. Here's how you can also collect this data for yourself!

First, you need to visit [Google Community Mobility Reports](https://www.google.com/covid19/mobility/).

![google_mobility_data_1](https://i.ibb.co/XCtyDsP/Screen-Shot-2020-06-24-at-5-23-08-PM.png)

Right-click on "Download global CSV" and save as csv into your local machine. Then what you need to do is to rename it into the exact iso-formatted string after "Reports created ..." For example, if the CSV is created on 2020-06-22, then rename your download file from `Global_Mobility_Report.csv` to `2020-06-22.csv`. Then you copy that file to this directory: `raw_data/google/` and it is done!

With Google Data, as you may see in the CSV there have been a lot of empty values in the dataset showing that there is no record in many points of time and locations. So, after calculating the correlation between categories, we decide to go forward and average out the columns with the number of available entries on rows instead of dropping rows with NaNs. For example, a row with values

Retail |  Grocery and Pharmacy |  Park |  Transit |  Workplace |  Residential
--|---|---|---|---|--
1  |  2 |  3 |  4 |  5 | 6

will be saved as 3.5.

Meanwhile, a row with entries

Retail |  Grocery and Pharmacy |  Park |  Transit |  Workplace |  Residential
--|---|---|---|---|--
NaN  |  Nan |  3 |  NaN |  NaN | NaN

will be noticed as 3.

#### Apple Maps Mobility Trends Reports

To collect lastest Apple Mobility data, first you need to visit [Apple Maps Mobility Trends Reports](https://www.apple.com/covid19/mobility).

![apple_mobility_1](https://i.ibb.co/gyKFf87/Screen-Shot-2020-06-24-at-5-48-15-PM.png)

Go ahead download the CSV file, then copy it into this directory: `raw_data/merged`. Leave the name as it is.

In Apple Mobility Data, we have used rows with transportation type as `driving` since driving fit Google Mobility data better.

#### Facebook Movement Range, Johns Hopkins COVID-19 and geographical data

For the rest data, they will be downloaded online automatically (since the link is permanent) for preprocessing, or data is constant and already saved in our repository (`data/`) (for example census or locally health statistics).

#### 7-day Moving Average

In stock markets, Moving Average is a very well-known method to smooth out the fluctuations (if any) and to point out the trends of data.

**But, why do we need it for COVID-19?**

As you may have noticed, COVID-19 scenario is very time-sensitive. Situations change daily, even hours, it can also be rephrased as time series data. Also, the data report is really inconsitent between dates and counties.

For example, as common sense, one may argue that since people are more available on weekends than weekdays, people normally test COVID-19 more on weekends (just an example to clarify the point, do not quote us on this!). There are many similar factors can make the pikes in data occur, so smoothing the data is never redundant.
