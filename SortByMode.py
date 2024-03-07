import pandas as pd
import numpy as np

EXTERNAL_ZONES = [41,42,43]

def sort(das,mode,t,transformation_list, time_range):
    # remove external zone, which are modeled in fixed matrices
    das=das[das['prev_stop_zone'].isin(EXTERNAL_ZONES)==False]
    das=das[das['stop_zone'].isin(EXTERNAL_ZONES)==False]
    
    
    # add region Ex key from zone numbers
    das=das.merge(transformation_list,left_on='prev_stop_zone' ,right_on='Ex',how='left')
    das['prev_stop_zone_new']= das['Aimsun']
    das=das.merge(transformation_list,left_on='stop_zone' ,right_on='Ex',how='left')
    das['stop_zone_new']= das['Aimsun_y']
    
    # filter DAS according to time
    das["prev_stop_departure_time"] = pd.to_numeric(das["prev_stop_departure_time"])
    arry=np.array(time_range)
    das_filter=das[das['prev_stop_departure_time']==arry[t]]
    
    # Keep only selected mode
    das_filter=das_filter[das_filter['stop_mode']==mode]
    
    # Remove journeys from one zone to itself
    das_filter=das_filter[das_filter['prev_stop_zone_new']!=das_filter['stop_zone_new']]
    
    # Create matrix
    matrix=das_filter.groupby(['prev_stop_zone_new','stop_zone_new']).count()
    matrix=matrix['model']
    matrix = matrix.unstack(level=0)
    matrix=matrix.fillna(0)
    matrix=matrix.T

    # Reorder matrix cols according to Aimsum zone order
    matrix_empty=pd.DataFrame(columns=transformation_list['Aimsun'],index=transformation_list['Aimsun'])
    matrix_empty=matrix_empty.fillna(0)
    matrix  = matrix.combine_first(matrix_empty)

    

    return matrix
    
