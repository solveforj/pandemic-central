# Population Mobility Data

### Description
Processes county-level population mobility data from [facebook.com](https://dataforgood.fb.com/docs/covid19/) to generate population mobility features

### Files
  * **preprocess.py** downloads and processes Facebook Movement Range Maps available from [here] (https://data.humdata.org/dataset/movement-range-maps), generating population mobility features
  * **mobility.csv.gz** is the output of `preprocess.py` and contains all population mobility features per county and date
