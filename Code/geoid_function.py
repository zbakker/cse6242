def geoid_function(data):
    import census_geocoder as cg
    import pandas as pd
    import numpy as np
    import time
    start_time = time.time()
    time_change=5*60*60
    i=1
    census_tract=[]
    lat_log=data[['Latitude','Longitude']].drop_duplicates()
    data_lenght=len(lat_log)
    for index, row in lat_log.iterrows():
        # print(row['Latitude'], row['Longitude'])
        print(i)
        try:
            location=cg.geography.from_coordinates(latitude=str(row['Latitude']),
                                                longitude=str(row['Longitude']),
                                                benchmark='Current',
                                                vintage='Census2020',
                                                layers='Census Tracts')

            census_tract.append(location.extensions['result']['geographies']['Census Tracts'][0]['GEOID'])
        except Exception as e:
            census_tract.append(None)
        if i %10==0:
            # print("--- %s seconds ---" % (time.time() - start_time))
            duration=time.time()-start_time
            time_per_number=duration/i
            amount_left=data_lenght-i
            time_left_sec=time_per_number*amount_left
            print(time.strftime("%H:%M:%S", time.gmtime(time_left_sec))+" left to run complete")
            print("ETA: "+(time.strftime("%H:%M:%S", time.gmtime(time.time()+time_left_sec-time_change))+" EST"))

        i+=1
    lat_log['census_tract_geoid']=census_tract
    data=data.merge(lat_log,on=['Latitude','Longitude'],how='left')
    return data
#out of 23114