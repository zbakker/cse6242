import pandas as pd
import numpy as np
from scipy.stats import boxcox

file_path = 'output_file.csv'  
df = pd.read_csv(file_path)

exclude_columns = ['census_tract_geoid', 'restaurant_index']  

for column in df.columns:
    if column not in exclude_columns:
        transformed_data, _ = boxcox(df[column] + 1)  
        transformed_data = np.where(transformed_data < 0, 0, transformed_data)
        transformed_data = np.where(transformed_data > 1, 1, transformed_data)
        min_value = np.min(transformed_data)
        max_value = np.max(transformed_data)
        normalized_data = (transformed_data - min_value) / (max_value - min_value)
        df[column] = normalized_data


output_file_path = 'Final/final_index.csv' 
df.to_csv(output_file_path, index=False)
