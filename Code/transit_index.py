def transit_index(subway_data, bus_data, bike_data):
    import pandas as pd
    from geoid_function import geoid_function
    #import csvs 
    subways = pd.read_csv(subway_data)  
    bus_stops = pd.read_csv(bus_data)
    bike_parking = pd.read_csv(bike_data)

    #remove nulls and zeros
    subways['Latitude'] = subways['Entrance Latitude']
    subways['Longitude'] = subways['Entrance Longitude']
    subways=geoid_function(subways)

    subways = subways.dropna(subset=['census_tract_geoid'])
    subways = subways[subways['census_tract_geoid'] !='']


    
    bus_stops = geoid_function(bus_stops)
    bus_stops = bus_stops.dropna(subset='census_tract_geoid')
    bus_stops = bus_stops[bus_stops['census_tract_geoid'] !='']



    bike_parking['Latitude'] = bike_parking['Y']
    bike_parking['Longitude'] = bike_parking['X']
    bike_parking=geoid_function(bike_parking)
    bike_parking = bike_parking.dropna(subset='census_tract_geoid')
    bike_parking = bike_parking[bike_parking['census_tract_geoid'] !='']
    

    #group by census tract and count rows
    subway_agg = subways.groupby('census_tract_geoid').size().reset_index(name='subway_count')
    bus_agg = bus_stops.groupby('census_tract_geoid').size().reset_index(name='bus_count')
    bike_agg = bike_parking.groupby('census_tract_geoid').size().reset_index(name='bike_count')

    #combine transit modes
    subway_bus = pd.merge(subway_agg, bus_agg, on = 'census_tract_geoid', how='outer')
    transit_agg = pd.merge(subway_bus, bike_agg, on='census_tract_geoid', how='outer')

    #add zeros where needed to fill NaNs
    transit_agg.fillna(0, inplace = True)

    #create index and scale 
    weights = {
    'subway_count': 0.65,
    'bus_count': 0.3,
    'bike_count': 0.05
        }

    # Calculate the weighted index
    transit_agg['index'] = (transit_agg['subway_count'] * weights['subway_count'] +
                        transit_agg['bus_count'] * weights['bus_count'] +
                        transit_agg['bike_count'] * weights['bike_count'])

    # Min-Max scaling to the range [0, 1]
    min_value = transit_agg['index'].min()
    max_value = transit_agg['index'].max()

    transit_agg['index_score'] = (transit_agg['index'] - min_value) / (max_value - min_value)
    output = transit_agg[['census_tract_geoid', 'index_score']]

    return output