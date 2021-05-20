# Model Training and Forecasting

### Description
All the files in this directory sequentially update datasets, merge them into a training dataset, train Random Forest models, and generate projections and visualizations of those projections for [itsonit.com](https://www.itsonit.com) and the [COVID-19 Forecast Hub](https://covid19forecasthub.org/).  Output is found in the `output/` directory.

### Files
- **merge.py** updates time-series datasets in the `data/` directory and merges all datasets in this directory into training datasets
- **train.py** trains mobility and non-mobility Random Forest models for forecasting COVID-19 cases and then generates projections and feature importance scores for the models
- **predict.py** reformats and condenses projections
- **web.py** reformats projections for the website
- **map.py** generates visualizations of the projections
- **reichlab.py** reformats projections for the COVID-19 Forecasting Hub
