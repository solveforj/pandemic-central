# Facebook Mobility Data

- **Description**: Global mobility data from Facebook which we filter for US counties and compute a 14-day rolling average relevant columns.  This is because COVID-19 is generally believed to take up to 14 days to manifest symptoms, meaning mobility  from the past 2 weeks will be relevant for a date of interest.

- **Files**:
  - **preprocess.py** cleans and processes data from [here](https://data.humdata.org/dataset/movement-range-maps) to generate the output dataset

  - **mobility.csv.gz** is the output of _preprocess.py_ and contains the following columns:
  | Column      | Description |
  | ----------- | ----------- |
  | date | The date of interest       |
  | FIPS   | The FIPS of interest        |
  | fb_movement_change   | Positive or negative change in movement relative to baseline       |
  | fb_stationary   | Positive proportion of users staying put within a single location        |
