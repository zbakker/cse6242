# %%

def health_index(water_inspection_data,Rodent_Inspection_data,Influenza_Pneumonia_data,EMS_Incident_data):
    import pandas as pd
    from geoid_function import geoid_function
    import decimal
    from sklearn.preprocessing import MinMaxScaler
    #water_inspection_data = "Water_Inspection_data.csv"
    #columns_to_extract2 = ["LATITUDE","LONGITUDE","SI_RESULT_BIOLOGICAL_GROWTH"]
    df1=pd.read_csv(water_inspection_data)
    df1 = df1.rename(columns={'HOUSE_NUM':'HOUSE_NUMBER','ZIP':'ZIP_CODE'})

    #Load Rodent inpsection file

    #Rodent_Inspection_data = "Rodent_Inspection_data.csv"
    df2=pd.read_csv(Rodent_Inspection_data)
    #Load Influenza Pneumonia data
    #Influenza_Pneumonia_data = "Influenza_Pneumonia_data.csv"
    df3=pd.read_csv(Influenza_Pneumonia_data)
    #Load EMS Incident data
    #EMS_Incident_data = "EMS_Incident_data.csv"
    df4=pd.read_csv(EMS_Incident_data)

    #Merge all 4 data
    result1 = pd.merge(df2,df1,on=['BLOCK','LOT','HOUSE_NUMBER','STREET_NAME','ZIP_CODE'],how='left')
    result1 = pd.merge(result1,df3,on=['ZIP_CODE'],how='left')
    df4['ZIP_CODE'] = df4['ZIP_CODE'].str.replace(',', '').astype(float)
    result1 = pd.merge(result1,df4,on=['ZIP_CODE'],how='left')
    pd.set_option('display.max_columns', None)
    result1 = result1.dropna()
    result1 = result1.rename(columns={'LATITUDE_x':'Latitude','LONGITUDE_x':'Longitude'})
    result1 = result1[result1['Latitude'] !=0]
    result1 = result1[result1['Longitude'] !=0]
    # Define a dictionary to map string values to int values for water inspection results
    result_mapping1 = {
        "N": 5,
        "A": 2,
        }
    result_mapping2 = {
        "A": 5,
        "P": 0,
        }
    # Replace values in the "Water inspection results" column using the dictionary
    result1['GI_RESULT_OVERFLOW_PIPES'] = result1['GI_RESULT_OVERFLOW_PIPES'].replace(result_mapping1)
    result1['GI_RESULT_AIR_VENTS'] = result1['GI_RESULT_AIR_VENTS'].replace(result_mapping1)
    result1['SI_RESULT_BIOLOGICAL_GROWTH'] = result1['SI_RESULT_BIOLOGICAL_GROWTH'].replace(result_mapping1)
    result1['SI_RESULT_DEBRIS_INSECTS'] = result1['SI_RESULT_DEBRIS_INSECTS'].replace(result_mapping1)
    result1['COLIFORM'] = result1['COLIFORM'].replace(result_mapping2)
    result1['ECOLI'] = result1['ECOLI'].replace(result_mapping2)

    # Define a dictionary to map string values to int values for rodent inspection results
    result_mapping3 = {
        "Bait applied": 1,
        "Cleanup done": 2,
        "Failed for Other R": 0,
        "Monitoring visit": 0,
        "Passed": 5,
        "Rat Activity": 0,
        "Stoppage done": 3
    }
    # Replace values in the "rodent RESULT" column using the dictionary
    result1['RESULT'] = result1['RESULT'].replace(result_mapping3)
    #result1

    #print(result1.columns.tolist())
    result1 = result1.groupby(['Latitude', 'Longitude']).agg({
        'RESULT': 'sum',
        'GI_RESULT_OVERFLOW_PIPES': 'sum',
        'GI_RESULT_AIR_VENTS': 'sum',
        'SI_RESULT_BIOLOGICAL_GROWTH': 'sum',
        'SI_RESULT_DEBRIS_INSECTS': 'sum',
        'COLIFORM': 'sum',
        'ECOLI': 'sum',
        'total_ed_visits': 'sum',
        'ili_pne_visits': 'sum',
        'ili_pne_admissions': 'sum',
        'INCIDENT_COUNT': 'sum'
    }).reset_index()
    #result1

    result1 = geoid_function(result1)
    #Combine individual water inspection results into one value WATER_INSP_RESULT"
    result1['WATER_INSP_RESULT'] = result1['GI_RESULT_OVERFLOW_PIPES'] + result1['GI_RESULT_AIR_VENTS'] + result1['SI_RESULT_BIOLOGICAL_GROWTH'] + result1['SI_RESULT_DEBRIS_INSECTS'] + result1['COLIFORM'] + result1['ECOLI']
    #Combine total emergency department visits, illness (influenza & pneumonia) visits & illness admissions into one value INF_PNEU_Admissions"
    result1['INF_PNEU_Admissions'] = result1['total_ed_visits'] + result1['ili_pne_visits'] + result1['ili_pne_admissions']
    result1 = result1.rename(columns={'RESULT':'RODENT_INSP_RESULT','INCIDENT_COUNT':'EMS_INCIDENT_COUNT'})
    selected_columns = ['Latitude', 'Longitude', 'WATER_INSP_RESULT', 'INF_PNEU_Admissions', 'RODENT_INSP_RESULT', 'EMS_INCIDENT_COUNT', 'census_tract_geoid']

    result2 = result1[selected_columns].copy()

    result2=result2.groupby('census_tract_geoid').agg({
        'WATER_INSP_RESULT':'sum',
        'INF_PNEU_Admissions':'sum',
        'RODENT_INSP_RESULT': 'sum',
        'EMS_INCIDENT_COUNT':'sum'
        }).reset_index() 

    weights = {'WATER_INSP_RESULT': 0.1, 'INF_PNEU_Admissions': 0.4, 'RODENT_INSP_RESULT': 0.2, 'EMS_INCIDENT_COUNT': 0.3}

    # Calculate the health index based on the weighted sum
    result2['Health_Index'] = (result2['WATER_INSP_RESULT'] * weights['WATER_INSP_RESULT'] +
                               result2['INF_PNEU_Admissions'] * weights['INF_PNEU_Admissions'] +
                               result2['RODENT_INSP_RESULT'] * weights['RODENT_INSP_RESULT'] +
                               result2['EMS_INCIDENT_COUNT'] * weights['EMS_INCIDENT_COUNT'])

    # You can also drop the individual columns used for the index calculation if needed
    result3 = result2.drop(columns=['WATER_INSP_RESULT', 'INF_PNEU_Admissions', 'RODENT_INSP_RESULT', 'EMS_INCIDENT_COUNT'])
    # Initialize the MinMaxScaler
    scaler = MinMaxScaler()
    # Scale the values in the "RESULT" column to the range of 0 to 1
    result3['Health_Index'] = scaler.fit_transform(result3['Health_Index'].values.reshape(-1, 1))
    result3 = result3.sort_values(by='Health_Index', ascending=False)
    return result3
#result3.to_csv('C:/Users/p_eth/Downloads/health_index.csv', index=False)

# %%



