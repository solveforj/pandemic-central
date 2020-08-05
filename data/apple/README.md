# Apple Mobility Data

- **Description**: Global mobility data released by Apple which we filter driving trends for US counties and process to show a 14-day rolling average. This is because COVID-19 is generally believed to take up to 14 days to manifest symptoms, meaning mobility  from the past 2 weeks will be relevant for a date of interest. Notice that we interpolate the missing data for May 11-12.

- **Files**:
  - **preprocess.py** cleans and processes the data to generate the output dataset (_mobility.csv.gz_) from [here](https://www.apple.com/covid19/mobility) (COVID-19 Mobility Trends Reports, Apple Inc.).

  - **mobility.csv.gz** is the output of _preprocess.py_ and contains the following columns:
    | Column      | Description |
    | ----------- | ----------- |
    | fips   | The FIPS of interest        |
    | date | The date of interest       |
    | apple_mobility   | Change in movement relative to baseline _(`100` means no change)_ |
