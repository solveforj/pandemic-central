# CCVI Data

- **Description**: Contains multiple files for 2018 census and demographic data for US counties. Relevant columns are selected from these datasets and normalized for county population if possible.

- **Files**:

  - **preprocess.py** cleans and processes the data in _CCVI_raw.csv_ to generate the output dataset, _CCVI.csv_

  - **CCVI.csv** is the output of _preprocess.py_ and contains the following columns:

    | Column      | Description |
    | ----------- | ----------- |
    | FIPS   | The FIPS of interest        |
    | Socioeconomic Status   | Measure of individuals with low income, educational attainment, and no occupation      |
    | Household Composition & Disability   | Measure of households with elderly (over 65), young (under 17), or disabled members, or single-parent homes       |
    | Minority Status & Language   | Measure of racially marginalized groups or those with limited English proficiency        |
    | Housing Type & Transportation   | Dwellings with multiple units, mobile, group, or crowded living arrangements, and households without access to transport       |
    | Epidemiological Factors   | Measure of high-risk COVID-19 populations with underlying conditions (cardiovascular, respiratory, immunocompromised, obesity, diabetes), high flu and pneumonia mortality, or high population density         |
    | Healthcare System Factors   | Measure of poor health system capacity, strength and preparedness         |

  - **CCVI_raw.csv** contains the raw CCVI scores from the [Surgo Foundation](https://precisionforcovid.org/ccvi) and are found [here](https://docs.google.com/spreadsheets/d/1qEPuziEpxj-VG11IAZoa5RWEr4GhNoxMn7aBdU76O5k/edit#gid=549685106).  The "County CCVI" sheet is downloaded as a CSV for processing by _preprocess.py_
