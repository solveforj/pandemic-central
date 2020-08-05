# Google Mobility Data

- **Source**: https://www.google.com/covid19/mobility/ (COVID-19 Community Mobility Reports, Google LLC)

- **Description**: Global mobility data released by Google which we filter driving trends for US counties and process to show a 14-day rolling average. This is because COVID-19 is generally believed to take up to 14 days to manifest symptoms, meaning mobility  from the past 2 weeks will be relevant for a date of interest.

- **Processed Data Columns**:


| Column      | Description |
| ----------- | ----------- |
| fips   | The FIPS of interest        |
| date | The date of interest       |
| google_mobility   | Positive or negative change in movement relative to baseline (mean of all categories)|
