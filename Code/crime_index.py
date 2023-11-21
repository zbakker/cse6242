# %%
# def geoid_function(data):
#     import census_geocoder as cg
#     i=1
#     ceneus_tract=[]
#     for index, row in data.iterrows():
#         print(i)
#         location=cg.geography.from_coordinates(latitude=row['Latitude'],
#                                             longitude=row['Longitude'],
#                                             benchmark='Current',
#                                             vintage='Census2020',
#                                             layers='Census Tracts')
#         ceneus_tract.append(location.extensions['result']['geographies']['Census Tracts'][0]['GEOID'])
#         i+=1
#     data['census_tract_geoid']=ceneus_tract
#     return data

# %%

def crime_index(input_csv):
    import pandas as pd
    import numpy as np
    from geoid_function import geoid_function
    
    df = pd.read_csv(input_csv)
    df_lat_long_only = df[['Latitude', 'Longitude']]
    df_lat_long_only = df_lat_long_only.loc[(df_lat_long_only['Latitude']>0.0)].drop_duplicates()
    df_geoid_function = geoid_function(df_lat_long_only)

    
    # Merge the census tract data with the original DataFrame
    result = pd.merge(df, df_geoid_function, on=['Longitude', 'Latitude'], how='left')
    filtered_result_df = result.dropna(subset=['census_tract_geoid'])

    
    # Define weights for 'LAW_CAT_CD'
    weights = {
        'VIOLATION': 0.3,
        'FELONY': 0.5,
        'MISDEMEANOR': 0.2,
    }

    # Group the data by 'CensusTract' and 'LAW_CAT_CD' and calculate counts
    grouped_data = filtered_result_df.groupby(['census_tract_geoid', 'LAW_CAT_CD']).size().reset_index(name='Count')
    grouped_data['census_tract_geoid'] = grouped_data['census_tract_geoid'].astype(str)

    # Calculate the weighted sum based on 'LAW_CAT_CD'
    grouped_data['WeightedSum'] = grouped_data['LAW_CAT_CD'].map(weights) * grouped_data['Count']
    
    #Group weighted sum by census_tract_geoid
    grouped_data = grouped_data.groupby(['census_tract_geoid']).agg({'WeightedSum': 'sum'}).reset_index()


    # Calculate the minimum and maximum values of the 'WeightedSum' column
    min_value = grouped_data['WeightedSum'].min()
    max_value = grouped_data['WeightedSum'].max()

    # Apply min-max scaling to standardize the scores
    grouped_data['StandardizedScore'] = (grouped_data['WeightedSum'] - min_value) / (max_value - min_value)
    fin = grouped_data[['census_tract_geoid','StandardizedScore']]
    
      
    return fin
    
    
# input_csv = 'Crime_Map_.csv'
# standardized_scores = crime_index(input_csv)

    

# %%



