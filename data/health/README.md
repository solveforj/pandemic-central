# Health Data

- **Description**: Population health data released by [IHME](http://www.healthdata.org/) for US counties.

- **Files**:
  - **preprocess.py** loads and cleans and cleans IHME datasets to make the output dataset (_health.csv_)

  - **health.csv** is the output of _preprocess.py_ and contains the following columns:
  
  | Column                         | Description                                  |
  |--------------------------------|----------------------------------------------|
  | Location                       | County name                                  |
  | FIPS                           | FIPS of reference                            |
  | Diabetes_Prevalence_Both_Sexes | Diabetes prevalence in both sexes            |
  | Male_Obesity_%                 | Percent of males who are obese               |
  | Female_Obesity_%               | Percent of females who are obese             |
  | life_expectancy                | Average life expectancy                      |
  | mortality_risk_0-5             | Mortality risk (ages 0-5)                    |
  | mortality_risk_5-25            | Mortality risk (ages 5-25)                   |
  | mortality_risk_25-45           | Mortality risk (ages 25-45)                  |
  | mortality_risk_45-65           | Mortality risk (ages 45-65)                  |
  | mortality_risk_65-85           | Mortality risk (ages 65-85)                  |
  | tubercolosis_mortality         | Mortality from tuberculosis                  |
  | AIDS_mortality                 | Mortality from AIDS                          |
  | diarrheal_mortality            | Mortality from diarrheal disease             |
  | lower_respiratory_mortality    | Mortality from lower respiratory diseases    |
  | meningitis_mortality           | Mortality from meningitis                    |
  | hepatitis_mortality            | Mortality from hepatitis                     |
  | other_resp_mortality           | Mortality from other respiratory diseases    |
  | interstitial_lung_mortality    | Mortality from interstitial lung diseases    |
  | asthma_mortality               | Mortality from asthma                        |
  | other_pneumoconiosis_mortality | Mortality from other pneumoconiosis diseases |
  | coal_pneumoconiosis_mortality  | Mortality from coal pneumoconiosis diseases  |
  | asbestosis_mortality           | Mortality from asbestosis                    |
  | silicosis_mortality            | Mortality from silicosis                     |
  | pneumoconiosis_mortality       | Mortality from pneumoconiosis                |
  | COPD_mortality                 | Mortality from COPD                          |
  | chronic_respiratory_mortality  | Mortality from chronic respiratory diseases  |

  - **IHME_Diabetes.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S., 1999-2012. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2016.
    - _Note_: "Total" sheet from XSLX file is exported as CSV in Excel


  - **IHME_Infections_Disease_Mortality.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Infectious Disease Mortality Rates by County 1980-2014. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2018.
    - [_Link_](http://ghdx.healthdata.org/record/ihme-data/united-states-infectious-disease-mortality-rates-county-1980-2014)
    - _Note_: All columns for all sheets in the original XLSX file were merged into 1 sheet by FIPS, which was exported into a CSV file in Excel


  - **IHME_Mortality.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Life Expectancy and Age-specific Mortality Risk by County 1980-2014. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2017.
    - [_Link_](http://ghdx.healthdata.org/record/ihme-data/united-states-life-expectancy-and-age-specific-mortality-risk-county-1980-2014)
    - _Note_: All columns for all sheets in the original XLSX file were merged into 1 sheet by FIPS, which was exported into a CSV file in Excel


  - **IHME_Respiratory_Disease_Mortality.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Chronic Respiratory Disease Mortality Rates by County 1980-2014. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2017.
    - [_Link_](http://ghdx.healthdata.org/record/ihme-data/united-states-chronic-respiratory-disease-mortality-rates-county-1980-2014)
    - _Note_: All columns for all sheets in the original XLSX file were merged into 1 sheet by FIPS,which was exported into a CSV file in Excel


  - **IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012.csv**
    - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Smoking Prevalence by County 1996-2012. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2014
    - [_Link_](https://ghdx.healthdata.org/record/ihme-data/united-states-smoking-prevalence-county-1996-2012)
    - _Note_: We used the file _IHME_US_COUNTY_TOTAL_AND_DAILY_SMOKING_PREVALENCE_1996_2012.csv_


  - **IHME_USA_OBESITY_PHYSICAL_ACTIVITY_2001_2011.csv**
   - _Citation_: Institute for Health Metrics and Evaluation (IHME). United States Physical Activity and Obesity Prevalence by County 2001-2011. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2013.
   - [_Link_](https://ghdx.healthdata.org/record/ihme-data/united-states-physical-activity-and-obesity-prevalence-county-2001-2011)
