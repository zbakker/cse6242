def housing_index (projects_data, buildings_data, rent_data, violations_data):
    import pandas as pd
    from geoid_function import geoid_function

    #import csv

    housing_violations_df = pd.read_csv(violations_data, low_memory=False)
    projects_df = pd.read_csv(projects_data)
    buildings_df = pd.read_csv(buildings_data)
    rent_df = pd.read_csv(rent_data)
    # Merge DB
    result_rent = pd.merge(projects_df, buildings_df,
                           on='ProjectID')  # Join the first two DataFrames on a common column
    result_rent = pd.merge(result_rent, rent_df, on='BuildingID')  # Join the result with the third DataFrame

    columns_to_remove = ['BorrowerLegalEntityName', 'GeneralContractorName', 'IsDavisBacon',
                         'IsSection220NYSLaborLaw', 'ProjectID_y']

    result_rent = result_rent.drop(columns=columns_to_remove)

    result_rent=geoid_function(result_rent)

    result_rent = result_rent.dropna(subset=['census_tract_geoid'])
    result_rent = result_rent[result_rent['census_tract_geoid'] != '']


    housing_violations_df =geoid_function(housing_violations_df)
    housing_violations_df = housing_violations_df.dropna(subset=['census_tract_geoid'])
    housing_violations_df = housing_violations_df[housing_violations_df['census_tract_geoid'] != '']

    violations_agg = housing_violations_df.groupby('census_tract_geoid').size().reset_index(name='violations_count')
    rent_agg = result_rent.groupby('census_tract_geoid').size().reset_index(name='rent_count')

    housing_agg = pd.merge(violations_agg, rent_agg, on='census_tract_geoid', how='outer')

    housing_agg.fillna(0, inplace=True)

    weights = {
        'rent_count': 0.7,
        'violations_count': 0.3
    }

    min_rent = result_rent['MedianActualRent'].min()
    max_rent = result_rent['MedianActualRent'].max()
    # housing_agg['Rent_Score'] = (max_rent - housing_agg['MedianActualRent']) / (max_rent - min_rent)

    housing_agg['index'] = (housing_agg['rent_count'] * weights['rent_count'] +
                            housing_agg['violations_count'] * weights['violations_count'])

    min_value = housing_agg['index'].min()
    max_value = housing_agg['index'].max()

    housing_agg['index_score'] = (housing_agg['index'] - min_value) / (max_value - min_value)
    result = housing_agg[['census_tract_geoid', 'index_score']]

    return result

