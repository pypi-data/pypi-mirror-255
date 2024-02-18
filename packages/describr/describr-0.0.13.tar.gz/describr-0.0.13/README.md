## README.md

describr is a Python library that provides functionality for descriptive statistics and outlier detection in pandas DataFrames.

**Installation**

You can install describr using pip:

```python
pip install describr
```

#### Example usage
```python
import pandas as pd
import numpy as np
from describr import FindOutliers, DescriptiveStats
```
#### Create a sample dataframe
```python
np.random.seed(0)
n = 500

data = {
    'MCID': ['MCID_' + str(i) for i in range(1, n + 1)],
    'Age': np.random.randint(18, 90, size=n),
    'Race': np.random.choice(['White', 'Black', 'Asian', 'Hispanic',''], size=n),
    'Educational_Status': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD',''], size=n),
    'Gender': np.random.choice(['Male', 'Female', ''], size=n),
    'ER_COST': np.random.uniform(500, 5000, size=n),
    'ER_VISITS': np.random.randint(0, 10, size=n),
    'IP_COST': np.random.uniform(5000, 20000, size=n),
    'IP_ADMITS': np.random.randint(0, 5, size=n),
    'CHF': np.random.choice([0, 1], size=n),
    'COPD': np.random.choice([0, 1], size=n),
    'DM': np.random.choice([0, 1], size=n),
    'ASTHMA': np.random.choice([0, 1], size=n),
    'HYPERTENSION': np.random.choice([0, 1], size=n),
    'SCHIZOPHRENIA': np.random.choice([0, 1], size=n),
    'MOOD_DEPRESSED': np.random.choice([0, 1], size=n),
    'MOOD_BIPOLAR': np.random.choice([0, 1], size=n),
    'TREATMENT': np.random.choice(['Yes', 'No'], size=n)
}

df = pd.DataFrame(data)
```
#### Parameters
**df**: name of dataframe

**id_col**: Primary key of the dataframe; accepts string or integer or float.

**group_col**: A Column to group by, It must be a binary column. Strings or integers are acceptable. 

**positive_class**: This is the response value for the primary outcome of interest. For instance, positive value for a Treatment cohort is 'Yes' or 1 otherwise 'No' or 0, respectively. Strings or integers are acceptable.

**continuous_var_summary**: Users specifies measures of central tendency, only mean and median are acceptable. This parameter is case insensitive.


#### Example usage of FindOutliers Class

This returns a dataframe (outliers_flag_df) with outlier_flag column (outlier_flag =1: record contains one or more ouliers). Tukey's IQR method is used to detect outliers in the data

```python
outliers_flag=FindOutliers(df=df, id_col='MCID', group_col='TREATMENT')
outliers_flag_df=outliers_flag.flag_outliers()
```
#### This example counts number of rows with outliers stratified by a defined grouping variable
```python
outliers_flag.count_outliers()
```
#### This example removes all outliers
```python
df2=outliers_flag.remove_outliers()
df2.shape
```

#### Example usage of DescriptiveStats Class
```python 
descriptive_stats = DescriptiveStats(df=df, id_col='MCID', group_col='TREATMENT', positive_class='Yes', continuous_var_summary='median')
```
#### Gets statistics for binary and categorical variables and returns a dataframe.
```python
binary_stats_df = descriptive_stats.get_binary_stats()
```

#### Gets mean and standard deviation for continuous variables and returns a dataframe.

```python
continuous_stats_mean_df = descriptive_stats.get_continuous_mean_stats()
```

#### Gets median and interquartile range for continuous variables and returns a dataframe.
```python
continuous_stats_median_df = descriptive_stats.get_continuous_median_stats()
```

#### Computes summary statistics for binary and continuous variables based on defined measure of central tendency. Method returns a dataframe.
````python
descriptive_stats.compute_descriptive_stats()
summary_stats = descriptive_stats.summary_stats()
````
