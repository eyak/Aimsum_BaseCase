import pandas as pd
import numpy as np
import settings
from db import getDASDF
from sqlalchemy.orm import Session

def getODMatrix(session, mode, time, centroid_ids):
    das = getDASDF(session, stop_mode=mode, removeExternalZones=True, removeInternalJourneys=True, time_range=[time])

    # Create matrix
    matrix=das.groupby(['prev_stop_zone_aimsum','stop_zone_aimsum']).count()
    matrix=matrix['model']
    matrix = matrix.unstack(level=0)
    matrix=matrix.fillna(0)
    matrix=matrix.T

    # Reorder matrix cols according to Aimsum zone order
    matrix_empty=pd.DataFrame(columns=centroid_ids['Aimsun'],index=centroid_ids['Aimsun'])
    matrix_empty=matrix_empty.fillna(0)
    matrix  = matrix.combine_first(matrix_empty)

    return matrix

def getODMatrixCSV(das,mode,t,centroid_ids, time_range):
    # original 'sort' function using das from csv

    # remove external zone, which are modeled in fixed matrices
    das=das[das['prev_stop_zone'].isin(settings.EXTERNAL_ZONES)==False]
    das=das[das['stop_zone'].isin(settings.EXTERNAL_ZONES)==False]
    
    
    # add region Ex key from zone numbers
    das=das.merge(centroid_ids,left_on='prev_stop_zone' ,right_on='Ex',how='left')
    das['prev_stop_zone_new']= das['Aimsun']
    das=das.merge(centroid_ids,left_on='stop_zone' ,right_on='Ex',how='left')
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
    matrix_empty=pd.DataFrame(columns=centroid_ids['Aimsun'],index=centroid_ids['Aimsun'])
    matrix_empty=matrix_empty.fillna(0)
    matrix  = matrix.combine_first(matrix_empty)

    

    return matrix
    

def testSortDB():
    # Test the sortdb function, make sure the resulting matrix is the
    # same as the one from the original sort function

    from db import createEngine, readCentIDsCSV, readDASCSV

    dascsv = readDASCSV()
    centroid_ids = readCentIDsCSV()

    engine = createEngine()
    conn = engine.connect()
    session = Session(conn)


    time_range = [6.25, 6.75, 7.25, 7.75]


    for i in range(len(time_range)):
        print(f'Comparing time {time_range[i]}')

        matdb = getODMatrix(session, 'Car', time_range[i], centroid_ids)
        matdbsum = matdb.sum().sum()
        matdbnonemptycount = matdb.astype(bool).sum().sum()
        print(f'DB data: SUM={matdbsum}, NONEMPTY={matdbnonemptycount}')

        matcsv = getODMatrixCSV(dascsv, 'Car', i, centroid_ids, time_range)
        matcsvsum = matcsv.sum().sum()
        matcsvnonemptycount = matcsv.astype(bool).sum().sum()
        print(f'CSV data: SUM={matcsvsum}, NONEMPTY={matcsvnonemptycount}')

        print('\n\n\n')




if __name__ == "__main__":
    testSortDB()
