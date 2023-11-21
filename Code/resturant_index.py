    # %%
def resturant_index(resturant_csv):
    import pandas as pd
    import numpy as np
    # !pip install census_geocoder
    from geoid_function import geoid_function
    from sklearn.preprocessing import MinMaxScaler

    df = pd.read_csv(resturant_csv)
    df_lat_long_only=df[["Latitude",'Longitude']]
    df_lat_long_only= df_lat_long_only.loc[(df_lat_long_only['Latitude']>0.0)].drop_duplicates()
    # test=df_lat_long_only.head(10)
    df_geoid_function=geoid_function(df_lat_long_only)




    df['inspection_date'] = pd.to_datetime(df['INSPECTION DATE'])
    df_sorted=df[['CAMIS','DBA','Latitude','Longitude','Census Tract','GRADE','inspection_date','VIOLATION CODE','VIOLATION DESCRIPTION','ACTION']]
    df_sorted.sort_values(by=['CAMIS','inspection_date'])
    filtered_df = df_sorted.loc[(df_sorted['Latitude']>0.0)&(df_sorted['inspection_date']!='01/01/1900')]
    not_inspected_df = df_sorted.loc[(df_sorted['Latitude']>0.0)&(df_sorted['inspection_date']=='01/01/1900')]
    not_inspected_df=not_inspected_df[['CAMIS','Latitude','Longitude']]
    filtered_df['max_inspection_date']= pd.to_datetime(filtered_df.groupby(['CAMIS'])['inspection_date'].transform(max))
    filtered_df_2=filtered_df.loc[(filtered_df['inspection_date']==filtered_df['max_inspection_date'])]
    filtered_df_2=filtered_df_2.sort_values(by=['max_inspection_date','CAMIS'])


 
    df_violation_count= filtered_df_2.groupby(['CAMIS','Latitude','Longitude']).size().reset_index(name='violation_count')




    df_resturant_grade_num=filtered_df_2
    df_resturant_grade_num['grade']=(df_resturant_grade_num['GRADE'])
    grade_num=[]
    for grade in df_resturant_grade_num['grade']:
        if grade=='A':
            grade_num.append(3)
        elif grade=='B':
            grade_num.append(2)
        elif grade=='C':
            grade_num.append(1)
        else:
            grade_num.append(None)
    df_resturant_grade_num['grade_num']=grade_num
    df_resturant_grade_num=df_resturant_grade_num[['CAMIS','grade_num']]
    df_resturant_grade_num_avg=pd.DataFrame(df_resturant_grade_num.groupby('CAMIS')['grade_num'].mean().reset_index(name='mean_grade_num'))


  
    df_closed_resturents_prep = df_sorted.loc[(df_sorted['Latitude']>0.0)& (df_sorted['ACTION']=='Establishment Closed by DOHMH. Violations were cited in the following area(s) and those requiring immediate action were addressed.')]
    df_closed_resturents_prep2=df_closed_resturents_prep.groupby(['CAMIS','inspection_date']).size().reset_index(name='closed_count_prep')
    df_closed_resturents=df_closed_resturents_prep2.groupby(['CAMIS']).size().reset_index(name='closed_count')





    join=df_violation_count.merge(df_resturant_grade_num_avg,on='CAMIS',how='left')
    join2=join.merge(df_closed_resturents,on='CAMIS',how='outer')

    not_inspected_postCensus_run= not_inspected_df.merge(df_geoid_function,on=['Latitude','Longitude'],how='inner')
    postCensus=join2.merge(df_geoid_function,on=['Latitude','Longitude'],how='inner')

    list_of_counted_camis=postCensus['CAMIS'].unique()
    not_inspected_postCensus_run_prep=not_inspected_postCensus_run[~not_inspected_postCensus_run['CAMIS'].isin(list_of_counted_camis)]
    not_inspected_postCensus_run_prep=not_inspected_postCensus_run_prep[['CAMIS','census_tract_geoid']]
    not_inspected_postCensus_count=not_inspected_postCensus_run_prep.groupby('census_tract_geoid').size().reset_index(name='resturant_count')
    postCensus_counts=postCensus.groupby('census_tract_geoid').agg(
        sum_violation_count=('violation_count',np.sum),
        resturant_count=('CAMIS',np.ma.count),
        mean_mean_grade_num=('mean_grade_num',np.mean),
        closed_count_count=('closed_count',np.sum)
                                        )

    resturant_count_join=postCensus_counts.merge(not_inspected_postCensus_count,on='census_tract_geoid',how='left')
    # .fillna(0)
    resturant_count_join_grade_prefill=resturant_count_join[['census_tract_geoid','mean_mean_grade_num']]
    resturant_count_join_prefil=resturant_count_join[['census_tract_geoid','sum_violation_count','resturant_count_x','resturant_count_y','closed_count_count']].fillna(0)
    resturant_count_join_fill=resturant_count_join_prefil.merge(resturant_count_join_grade_prefill,on='census_tract_geoid',how='inner')
    resturant_sum=[]
    violation_ratio_list=[]
    for index, row in resturant_count_join_fill.iterrows():
        additon=row['resturant_count_x']+row['resturant_count_y']
        resturant_sum.append(additon)
        violation_ratio=row['sum_violation_count']/(row['resturant_count_x']+row['resturant_count_y'])
        violation_ratio_list.append(violation_ratio)
    resturant_count_join_fill['resturant_total']=resturant_sum
    resturant_count_join_fill['violation_ratio']=violation_ratio_list
    new_census=resturant_count_join_fill[['census_tract_geoid']]
    resturant_model_unscaled=resturant_count_join_fill[['violation_ratio','mean_mean_grade_num','closed_count_count','resturant_total']]
    scaler = MinMaxScaler()
    resturant_model__scaled = scaler.fit_transform(resturant_model_unscaled.to_numpy())
    resturant_model__scaled = pd.DataFrame(resturant_model__scaled, columns=[
    'violation_ratio', 'mean_mean_grade_num', 'closed_count_count', 'resturant_total'])
    resturant_model_full_scaled=pd.concat((resturant_model__scaled,new_census),axis=1)

    mean_final_grade_num=resturant_model_full_scaled[['mean_mean_grade_num']].mean(skipna=True).to_numpy()[0]
    linear_equation=[]
    for index, row in resturant_model_full_scaled.iterrows():
        if pd.isna(row['mean_mean_grade_num']):
            equation=mean_final_grade_num-row['closed_count_count']+(3*row['resturant_total'])-(2*row['violation_ratio'])
        else:
            equation=row['mean_mean_grade_num']-row['closed_count_count']+(3*row['resturant_total'])-(2*row['violation_ratio'])
        linear_equation.append(equation)
    resturant_model_full_scaled['linear_equation']=linear_equation 
    # resturant_model_full_scaled.sort_values('linear_equation')

    new_census_final=resturant_model_full_scaled[['census_tract_geoid']]
    final_unscaled=resturant_model_full_scaled[['linear_equation']]
    final_scaled = scaler.fit_transform(final_unscaled.to_numpy())
    final_scaled = pd.DataFrame(final_scaled, columns=['linear_equation'])
    final_scaled=pd.concat((final_scaled,new_census_final),axis=1)
    final_scaled.sort_values(['linear_equation'])
    return final_scaled



