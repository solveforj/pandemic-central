# Population Health Data

### Description
Population health data released by [IHME](http://www.healthdata.org/) for US counties used for only for training dataset features

### Files
  - **preprocess.py** loads and cleans all IHME datasets to make the output dataset `IHME.csv`
  - **IHME.csv** is the only output file of _preprocess.py_ containing processed population health features
  - **IHME_Diabetes.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S., 1999-2012. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2016.
    - _Note_: "Total" sheet from .xlsx file (found online [here](http://ghdx.healthdata.org/record/ihme-data/united-states-diabetes-prevalence-county-1999-2012)) is exported as .csv in Excel
  - **IHME_Infections_Disease_Mortality.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Infectious Disease Mortality Rates by County 1980-2014. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2018.
    - _Note_: All columns for all sheets in the original .xlsx file (from [here](http://ghdx.healthdata.org/record/ihme-data/united-states-infectious-disease-mortality-rates-county-1980-2014)) were merged into 1 sheet by FIPS, which was exported into a .csv file in Excel
  - **IHME_Mortality.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Life Expectancy and Age-specific Mortality Risk by County 1980-2014. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2017.
    - _Note_: All columns for all sheets in the original .xlsx file (from [here](http://ghdx.healthdata.org/record/ihme-data/united-states-life-expectancy-and-age-specific-mortality-risk-county-1980-2014)) were merged into 1 sheet by FIPS, which was exported into a .csv file in Excel
  - **IHME_Respiratory_Disease_Mortality.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Chronic Respiratory Disease Mortality Rates by County 1980-2014. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2017.
    - _Note_: All columns for all sheets in the original .xlsx file (from [here](http://ghdx.healthdata.org/record/ihme-data/united-states-chronic-respiratory-disease-mortality-rates-county-1980-2014)) were merged into 1 sheet by FIPS, which was exported into a .csv file in Excel
  - **IHME_USA_OBESITY_PHYSICAL_ACTIVITY_2001_2011.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Physical Activity and Obesity Prevalence by County 2001-2011. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2013.
    - The file available online [here](https://ghdx.healthdata.org/record/ihme-data/united-states-physical-activity-and-obesity-prevalence-county-2001-2011) was already in .csv format and needed no modifications
