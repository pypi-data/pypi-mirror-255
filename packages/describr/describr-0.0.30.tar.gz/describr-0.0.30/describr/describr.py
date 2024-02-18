import pandas as pd
import numpy as np
import scipy.stats as stats

# may remove this FindOutliers in future release as it is not efficient
class FindOutliers:
    def __init__(self, df, id_col, group_col):
        self.df = df
        self.id_col = id_col
        self.group_col = group_col
        self.outlier_flag_col = 'outlier_flag'
        self.outlierdf=None
    
    def flag_outliers(self):
        def flag_outliers(row):
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            numeric_cols = [col for col in numeric_cols if col not in [self.id_col, self.group_col]]
            outliers = pd.Series(False, index=row.index)
            
            for col in numeric_cols:
                if isinstance(row[col], (int, float)):
                    q1 = self.df[col].quantile(0.25)
                    q3 = self.df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower = q1 - 1.5 * iqr
                    upper = q3 + 1.5 * iqr
                    is_outlier = (row[col] < lower) or (row[col] > upper)
                    outliers[col] = is_outlier
            
            return outliers.any()
        
        self.df[self.outlier_flag_col] = self.df.apply(flag_outliers, axis=1).astype(int)
        self.outlierdf=self.df.copy()
        self.df.drop(columns=self.outlier_flag_col, inplace=True)
    
    def count_outliers(self):
        if self.outlier_flag_col not in self.outlierdf.columns:
            raise KeyError(f"Column not found: {self.outlier_flag_col}")
        
        outlier_counts = self.outlierdf.groupby(self.group_col)[self.outlier_flag_col].sum()
        print("Outlier Counts:")
        for group, count in outlier_counts.items():
            print(f"Group: {self.group_col} = {group}, Outlier Count: {count}")
    
    def remove_outliers(self):
        cleaned_df = self.outlierdf[self.outlierdf[self.outlier_flag_col] == 0].copy()
        cleaned_df.drop(columns=self.outlier_flag_col, inplace=True)
        return cleaned_df

class DescriptiveStats:
    
    def __init__(self, df, id_col, group_col, positive_class, continuous_var_summary):
        self.df = df
        self.id_col = id_col
        self.group_col = group_col
        self.positive_class = str(positive_class)
        self.continuous_var_summary = continuous_var_summary
        self.binary_stats_df = None
        self.continuous_stats_mean_df = None
        self.continuous_stats_median_df = None        

    def _identify_binary_continuous_vars(self):
        binary_vars = []
        continuous_vars = []

        self.df = self.df.set_index(self.id_col)        

        categorical_columns = self.df.select_dtypes(include=['object']).columns      
        self.df[categorical_columns] = self.df[categorical_columns].fillna('Missing')  # Fill null values with 'Missing'
        self.df[categorical_columns] = self.df[categorical_columns].replace('', 'Missing')  # Replace blank values with 'Missing'
        
        df_group_col = self.df[[self.group_col]]
        
        self.df.drop(self.group_col, axis=1, inplace=True)

        self.df = pd.get_dummies(self.df, dtype='int64')
        
        self.df[self.group_col] = df_group_col[self.group_col]

        for col in self.df.columns:
            if self.df[col].dtype in ['int64', 'int32'] and self.df[col].nunique() <= 2 and self.group_col not in col:
                binary_vars.append(col)
            elif self.df[col].dtype in ['int64', 'int32', 'float64','float32'] and self.group_col not in col:
                continuous_vars.append(col)

        return binary_vars, continuous_vars

    def _compute_binary_stats(self, binary_vars):
        treatment_values = self.df[self.group_col].unique()
        treatment_values.sort()
        
        if not binary_vars:
            return pd.DataFrame()
        
        binary_stats = self.df.groupby(self.group_col)[binary_vars].agg(['size', 'mean'])
        
        binary_p_values = {}
        for var in binary_vars:
            for val in treatment_values:
                group_val = 'group_{}'.format(val)
                _, p_value = stats.ttest_ind(
                    self.df[(self.df[self.group_col] == val) & (~self.df[var].isnull())][var],
                    self.df[(self.df[self.group_col] != val) & (~self.df[var].isnull())][var]
                )
                binary_p_values[var] = p_value

        binary_stats_df = pd.DataFrame(binary_stats).T
        binary_p_values_df = pd.DataFrame.from_dict(binary_p_values, orient='index', columns=['p-value'])

        binary_stats_df.reset_index(inplace=True)
        new_columns = {'level_0': 'variable', 'level_1': 'stats'}
        binary_stats_df = binary_stats_df.rename(columns=new_columns)
        binary_stats_df = binary_stats_df.rename(columns={col: self.group_col + '_' + str(col) + '_Proportion' for col in binary_stats_df.columns[-2:]})

        binary_stats_df_sample_mean = binary_stats_df[binary_stats_df['stats'] == 'mean']
        binary_stats_df_sample_size = binary_stats_df[binary_stats_df['stats'] == 'size']
        binary_stats_df_sample_mean = binary_stats_df_sample_mean.copy()  # Create a copy of the DataFrame

        for col in binary_stats_df_sample_size.columns[-2:]:
            globals()['mapping_dict_' + col] = dict(zip(binary_stats_df_sample_size['variable'], binary_stats_df_sample_size[col]))
            binary_stats_df_sample_mean[col.rsplit('_', 1)[0] + '_n'] = binary_stats_df_sample_mean[col] * binary_stats_df_sample_mean['variable'].map(globals()['mapping_dict_' + col])

        binary_stats_df_sample_mean.drop('stats', axis=1, inplace=True)

        binary_p_values_df.reset_index(inplace=True)
        binary_p_values_df.rename(columns={'index': 'variable'}, inplace=True)

        df_binary = binary_stats_df_sample_mean.merge(binary_p_values_df, on='variable')

        return df_binary

    def _compute_continuous_stats_with_mean(self, continuous_vars):
        treatment_values = self.df[self.group_col].unique()
        treatment_values.sort()
        
        continuous_stats = self.df.groupby(self.group_col)[continuous_vars].agg(['mean', 'std'])

        continuous_p_values = {}
        for var in continuous_vars:
            for val in treatment_values:
                group_val = 'group_{}'.format(val)
                _, p_value = stats.ttest_ind(
                    self.df[(self.df[self.group_col] == val) & (~self.df[var].isnull())][var],
                    self.df[(self.df[self.group_col] != val) & (~self.df[var].isnull())][var]
                )
                continuous_p_values[var] = p_value

        continuous_stats_mean_df = pd.DataFrame(continuous_stats).T
        continuous_p_values_df = pd.DataFrame.from_dict(continuous_p_values, orient='index', columns=['p-value'])

        continuous_stats_mean_df.reset_index(inplace=True)
        new_columns = {'level_0': 'variable', 'level_1': 'stats'}
        continuous_stats_mean_df = continuous_stats_mean_df.rename(columns=new_columns)
        continuous_stats_mean_df = continuous_stats_mean_df.rename(columns={col: self.group_col + '_' + str(col) + '_mean' for col in continuous_stats_mean_df.columns[-2:]})

        mean_df = continuous_stats_mean_df[continuous_stats_mean_df['stats'] == 'mean']
        std_df = continuous_stats_mean_df[continuous_stats_mean_df['stats'] == 'std']

        mean_df = mean_df.copy()  # Create a copy of the DataFrame
        for col in mean_df.columns[-2:]:
            globals()['mapping_dict_' + col] = dict(zip(std_df['variable'], std_df[col]))
            mean_df[col.rsplit('_', 1)[0] + '_std'] = mean_df['variable'].map(globals()['mapping_dict_' + col])

        mean_df.drop('stats', axis=1, inplace=True)

        continuous_p_values_df.reset_index(inplace=True)
        continuous_p_values_df.rename(columns={'index': 'variable'}, inplace=True)

        df_continuous = mean_df.merge(continuous_p_values_df, on='variable')
        return df_continuous

    def _compute_continuous_stats_with_median(self, continuous_vars):
        continuous_vars.append(self.group_col)
        continuous_median = self.df[continuous_vars].groupby(self.group_col).agg(['median', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)])
        treatment_values = self.df[self.group_col].unique()
        treatment_values.sort()
        continuous_median = continuous_median.T
        continuous_median.reset_index(inplace=True)
        new_columns = {'level_0': 'variable', 'level_1': 'stats'}
        continuous_median = continuous_median.rename(columns=new_columns)
        continuous_median['stats'] = continuous_median['stats'].replace({'<lambda_0>': 'Q1', '<lambda_1>': 'Q3'})
        continuous_median = continuous_median.rename(columns={col: self.group_col + '_' + str(col) + '_median' for col in continuous_median.columns[-2:]})
        
        median_df = continuous_median[continuous_median['stats'] == 'median']
        q1_df = continuous_median[continuous_median['stats'] == 'Q1']
        q3_df = continuous_median[continuous_median['stats'] == 'Q3']
        
        median_df = median_df.copy()  # Create a copy of the DataFrame
        for col in median_df.columns[-2:]:
            globals()['mapping_dict_' + col] = dict(zip(q1_df['variable'], q1_df[col]))
            median_df[col.rsplit('_', 1)[0] + '_Q1'] = median_df['variable'].map(globals()['mapping_dict_' + col])
            globals()['mapping_dict_' + col] = dict(zip(q3_df['variable'], q3_df[col]))
            median_df[col.rsplit('_', 1)[0] + '_Q3'] = median_df['variable'].map(globals()['mapping_dict_' + col])

        median_df.drop('stats', axis=1, inplace=True)

        continuous_p_values_median = {}
        continuous_vars.remove(self.group_col)
        for var in continuous_vars:
            for val in treatment_values:
                group_val = 'group_{}'.format(val)
                # Check if continuous_var_summary is 'median', and set p-value to 'null' if true
                if self.continuous_var_summary.lower() == 'median':
                    p_value = 'null'
                else:
                    _, p_value = stats.ttest_ind(
                        self.df[(self.df[self.group_col] == val) & (~self.df[var].isnull())][var],
                        self.df[(self.df[self.group_col] != val) & (~self.df[var].isnull())][var]
                    )
                continuous_p_values_median[var] = p_value

        # Initialize an empty dataframe to store the continuous stats
        continuous_stats_median_df = median_df.copy()

        continuous_p_values_median_df = pd.DataFrame.from_dict(continuous_p_values_median, orient='index', columns=['p-value'])

        continuous_p_values_median_df.reset_index(inplace=True)
        continuous_p_values_median_df.rename(columns={'index': 'variable'}, inplace=True)

        df_continuous_median = continuous_stats_median_df.merge(continuous_p_values_median_df, on='variable')
        return df_continuous_median


    def compute_descriptive_stats(self):
        binary_vars, continuous_vars = self._identify_binary_continuous_vars()

        self.binary_stats_df = self._compute_binary_stats(binary_vars)
        self.continuous_stats_mean_df = self._compute_continuous_stats_with_mean(continuous_vars)
        self.continuous_stats_median_df = self._compute_continuous_stats_with_median(continuous_vars)

    def get_binary_stats(self):
        return self.binary_stats_df

    def get_continuous_mean_stats(self):
        return self.continuous_stats_mean_df
    
    def get_continuous_median_stats(self):
        return self.continuous_stats_median_df
    
    def format_binary_column(self, row, column_name):
        sample_size = row[column_name.replace('_Proportion', '_n')]
        fraction = row[column_name]
        return '{:.0f} ({:.1%})'.format(sample_size, fraction)
    
    def format_continuous_column(self, row, column_name):        
        mean = row[column_name]
        std = row[column_name.replace('_mean', '_std')]
        return '{:.2f} ({:.2f})'.format(mean, std)
    
    def format_continuous_median_column(self, row, column_name):
        median = row[column_name]
        q1 = row[column_name.replace('_median', '_Q1')]
        q3 = row[column_name.replace('_median', '_Q3')]
        return '{:.2f} ({:.2f} - {:.2f})'.format(median, q1, q3)
    
    def format_binary_stats(self):
        columns_to_format = [col for col in self.binary_stats_df.columns if col.endswith('_Proportion')]

        # Apply formatting to the selected columns
        summary_stats_binary = self.binary_stats_df.copy()
        for column in columns_to_format:
            summary_stats_binary[column] = summary_stats_binary.apply(lambda row: self.format_binary_column(row, column), axis=1)

        # Rename columns
        summary_stats_binary.rename(columns={col: col.replace('_Proportion', '') for col in columns_to_format}, inplace=True)

        # Add the suffix to the specified column
        summary_stats_binary['variable'] = self.binary_stats_df['variable'] + ", n (%)"

        # Drop columns
        columns_to_delete = [col for col in self.binary_stats_df.columns if col.endswith('_n')]
        summary_stats_binary.drop(columns=columns_to_delete, axis=1, inplace=True)

        return summary_stats_binary

    def format_continuous_mean_stats(self):
        columns_to_format = [col for col in self.continuous_stats_mean_df.columns if col.endswith('_mean')]

        # Apply formatting to the selected columns
        summary_stats_continuous_mean = self.continuous_stats_mean_df.copy()
        for column in columns_to_format:
            summary_stats_continuous_mean[column] = summary_stats_continuous_mean.apply(lambda row: self.format_continuous_column(row, column), axis=1)

        # Rename columns
        summary_stats_continuous_mean.rename(columns={col: col.replace('_mean', '') for col in columns_to_format}, inplace=True)

        # Add the suffix to the specified column
        summary_stats_continuous_mean['variable'] = self.continuous_stats_mean_df['variable'] + ", Mean (SD)"

        # Drop columns
        columns_to_delete = [col for col in self.continuous_stats_mean_df.columns if col.endswith('_std')]
        summary_stats_continuous_mean.drop(columns=columns_to_delete, axis=1, inplace=True)

        return summary_stats_continuous_mean
        

    def format_continuous_median_stats(self):
        columns_to_format = [col for col in self.continuous_stats_median_df.columns if col.endswith('_median')]

        # Apply formatting to the selected columns
        summary_stats_continuous_median = self.continuous_stats_median_df.copy()
        for column in columns_to_format:
            summary_stats_continuous_median[column] = summary_stats_continuous_median.apply(lambda row: self.format_continuous_median_column(row, column), axis=1)

        # Rename columns
        summary_stats_continuous_median.rename(columns={col: col.replace('_median', '') for col in columns_to_format}, inplace=True)

        # Add the suffix to the specified column
        summary_stats_continuous_median['variable'] = self.continuous_stats_median_df['variable'] + ", Median (Q1-Q3)"

        # Drop columns
        columns_to_delete = [col for col in self.continuous_stats_median_df.columns if col.endswith('_Q1') or col.endswith('_Q3')]
        summary_stats_continuous_median.drop(columns=columns_to_delete, axis=1, inplace=True)

        return summary_stats_continuous_median
    

    def _order_columns_dynamically(self, df):
        # Get the list of columns in the resulting dataframe
        columns = list(df.columns)
        # Determine the index of the first and last column
        first_column_index = columns.index(columns[0])
        last_column_index = columns.index(columns[-1])
        # Exclude the first and last column
        middle_columns = columns[first_column_index + 1:last_column_index]
        # Order the remaining columns in descending order
        middle_columns = sorted(middle_columns, reverse=True)
        # Reorder columns while preserving the order of the first and last columns
        column_order = [columns[0]] + middle_columns + [columns[-1]]
        df = df[column_order]
        return df
    
    def summary_stats(self):
        summary_stats_continuous_mean = self.format_continuous_mean_stats()
        summary_stats_binary = self.format_binary_stats()
        summary_stats_continuous_median = self.format_continuous_median_stats()
        if self.continuous_var_summary.lower() == 'mean':
            stacked_df = pd.concat([summary_stats_continuous_mean, summary_stats_binary], ignore_index=True)
        else:
            stacked_df = pd.concat([summary_stats_continuous_median, summary_stats_binary], ignore_index=True)
        # Order columns dynamically
        stacked_df = self._order_columns_dynamically(stacked_df)
        return stacked_df
