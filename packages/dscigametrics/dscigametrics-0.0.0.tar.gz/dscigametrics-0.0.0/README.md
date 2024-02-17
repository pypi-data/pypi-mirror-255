[![Documentation Status](https://readthedocs.org/projects/group-9-ga-metrics/badge/?version=latest)](https://group-9-ga-metrics.readthedocs.io/en/latest/?badge=latest)

# dscigametrics

`dscigametrics`, or *Data Science Google Analytics Metrics*, is a python package that provides a set of ready-made functions that can help users with minimual coding skills easily digest and analyse advertising data obtained from Google Analytics. While Google Analytics allows users to easily download data as a csv file, the resulting spreadsheet is an intimidating and unituitive block of dense information. Instead of trying to analyse this in excel, users can instead load it into a python script as a pandas dataframe and let this package do the analysis work for them! 

## Fuctions in the package

1. `compute_metrics` summarises general performance of campaign based on four metrics.
2. `stat_summary` summarises variance of campaign performance based on four metrics.
3. `daily_plot` visualises performance changes of campaign based on four metrics.
4. `find_campaigns` identifies the best and worst performing campaigns based on a selected metric.

## Where this package fits in

The popularity and influence of Google Analytics means that there is already a decent number of related python packages, such as googleanalytics, which can be found [here](https://pypi.org/project/googleanalytics/) on PyPI. However the majority of these packages provide functionality that allows developers to interact with the Google Analytics API, which presupposes a fairly high level of technical skill. Our package is intended to help users with a novice familiarity with python by operating directly on downloaded GA data sets instead.

## Installation
Since the package has not uploaded to PyPI, this is not feasible for now. Please see the **developer installation instructions** to install it.
```bash
$ pip install dscigametrics
```

### Developer Installation Instruction
#### Step 1: Clone the Repository
```bash
git clone git@github.com:UBC-MDS/Group_9_GA_Metrics.git
cd Group_9_GA_Metrics  # Navigate to the cloned repository directory
```

#### Step 2: Create and Activate the Conda Environment
```bash
$ conda env create -f environment.yml  # Create Conda environment
$ conda activate ga_package  # Activate the Conda environment
```

#### Step 3: Install the Package Using Poetry
Ensure the Conda environment is activated. You should see **Group_9_GA_Metrics** in the terminal prompt.
```bash
$ poetry install  # Install the package using Poetry
```

## Quick Start 

Here is a basic  example of how to use this package:
```python
import dscigametrics
import pandas as pd

data = pd.read_csv('where/is/your/data/saved.csv')

campaign_id = 123851219
start_date = 20220801
end_date = 20220831

metrics_dictionary = compute_metrics(data, campaign_id, start_date, end_date)
summary = stat_summary(data, campaign_id, start_date, end_date)
plot = daily_plot(data, campaign_id, start_date, end_date, width=300, height=800)

campaign_ids = [219011657, 140569061, 215934049, 123851219]
metric = 'conversion_rate'
best_worst_campaigns = find_campaigns(
    data=data,
    start_date=start_date,
    end_date=end_date,
    campaign_ids=campaign_ids,
    metric=metric
)
```

## Online Documentation

Documentation for all functions in the package, as well as a demonstration notebook, can be found [here](https://group-9-ga-metrics.readthedocs.io/en/latest/) on Read the Docs.

## Main Contributors

Beth Ou-Yang, Ian MacCarthy, Yili Tang, Weilin Han

## Contributing

Contributions are welcome and greatly appreciated! If you're interested in contributing to this project, take a look at the [contributor guide](contributing.md).

## License

`dscigametrics` was created by DSCI524 Cohort8 Group9. It is licensed under the terms of the MIT license.

## Credits

`dscigametrics` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).