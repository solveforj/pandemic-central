# Model

- **Description**: This folder contains files to merge all relevant data and feed it into a random forest regression model to predict COVID-19 cases at the county level. These predictions are formatted for our [website](https://www.itsonit.com) or for our collaboration with the [COVID-19 Forecast Hub](https://covid19forecasthub.org/).

- **Files**:

  - **merge.py** updates all data, merges it, and saves it to 2 files in the same directory this repository is in:

    - `../training_mobility.csv.gz`, contains daily data for all counties with mobility data from Facebook.

    - `../training_no_mobility.csv.gz`, contains daily data for all counties without mobility data from Facebook.

  - **train.py** reads the output files of *merge.py* and trains and generates predictions from a random forest regression model. Separate models are trained for the mobility and non-mobility datasets, creating 3 output files:

    - `predictions/model_stats/model_stats_yyyy-mm-dd.csv` contains calculations of mean absolute error (MAE) and R<sup>2</sup> values for the each model

    - `../mobility_full_predictions.csv.gz` contains all data from the mobility training dataset with added predictions from the mobility random forest model

    - `../no_mobility_full_predictions.csv.gz`contains all data from the non-mobility training dataset with added predictions from the non-mobility random forest model.

  - **predict.py** reads the mobility and non-mobility predictions produced by *train.py* and filters them to only show the validated projections for the past 3 weeks and the unvalidated projections for the next 2 weeks.  The 2 filtered datasets are merged into one file of predictions for US counties, `predictions/projections/predictions_yyyy-mm-dd.csv`.  Then, the resultant merged file is reformatted for our website and stored as `predictions/website/web_yyyy-mm-dd.csv`.

  - **reichlab.py** reads the output file of *predict.py* and reformats it for the COVID-19 Forecast Hub, creating `predictions/covid19-forecast-hub/yyyy-mm-dd-PandemicCentral-USCounty.csv`
  - **map.py** draws choropleth map from `predictions/projections/predictions_latest.csv`. The output will be:
    - **latest_map.html**: an interactive map with hover data
    - Four **YYYY-MM-DD-w.png**: maps in PNG format. In which:
      - YYYY-MM-DD: the date today in ISO format
      - w (labeled 1-4): the w week ahead
    - These files can be found in `predictions/graphics/` directory
  - **visualize.py** shows plot quantile and point projections as national total incident cases and export data for web development
