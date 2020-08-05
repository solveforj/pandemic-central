# Facebook Mobility Data

- **Source**: https://data.humdata.org/dataset/movement-range-maps

- **Description**: Global mobility data from Facebook which we filter for US counties and process to show a 14-day rolling average for all columns in `preprocess.py`.  This is because COVID-19 is generally believed to take up to 14 days to manifest symptoms, meaning mobility  from the past 2 weeks will be relevant for a date of interest.

- **Processed Data Columns**:
| Column      | Description |
| ----------- | ----------- |
| date | The date of interest       |
| FIPS   | The FIPS of interest        |
| fb_movement_change   | Positive or negative change in movement relative to baseline       |
| fb_stationary   | Positive proportion of users staying put within a single location        |
