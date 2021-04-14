# CCVI Data

### Description
Processes CCVI scores for US counties from the Surgo Foundation.  These metrics score various socioeconomic and health factors that are relevant for vulnerability to COVID-19 outbreaks.

### Files
  * **preprocess.py** cleans and processes the data in `CCVI_raw.csv` to generate the output dataset, `CCVI.csv`
  * **CCVI.csv** is the output of `preprocess.py`
  - **CCVI_raw.csv** contains the raw CCVI scores from the [Surgo Foundation](https://precisionforcovid.org/ccvi) and are found [here](https://docs.google.com/spreadsheets/d/1qEPuziEpxj-VG11IAZoa5RWEr4GhNoxMn7aBdU76O5k/edit#gid=549685106).  The "County CCVI" sheet is downloaded as a CSV for processing by `preprocess.py`
