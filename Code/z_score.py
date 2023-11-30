import pandas as pd
import numpy as np
from scipy import stats


file_path = "final_index.csv"
df = pd.read_csv(file_path)

exclude_columns = ['census_tract_geoid', 'crime_index', 'transit_index', 'health_index', 'housing_index']  

for column in df.columns:
    if column not in exclude_columns:       
        z_scores = np.abs(stats.zscore(df[column]))
        threshold = 3
        outliers = np.where(z_scores > threshold)
        filtered_data = df[column].values[z_scores <= threshold]       
        filtered_data = np.where(filtered_data < 0, 0, filtered_data)
        filtered_data = np.where(filtered_data > 1, 1, filtered_data)
        min_value = np.min(filtered_data)
        max_value = np.max(filtered_data)
        normalized_data = (filtered_data - min_value) / (max_value - min_value)       
        df.loc[z_scores <= threshold, column] = normalized_data

output_file_path = 'output_file.csv'  
df.to_csv(output_file_path, index=False)