import sqlalchemy
import settings
import pandas as pd
from model import DAS

def readDASCSV():
    #das.columns = ['person_id', 'tour_no', 'tour_type', 'stop_no', 'stop_type', 'stop_location', 'stop_zone','stop_mode', 'primary_stop', 'arrival_time', 'departure_time', 'prev_stop_location', 'prev_stop_zone', 'prev_stop_departure_time', 'drivetrain', 'make', 'model']
    df = pd.read_csv(settings.das_fn,header='infer')
    
    # rename first col
    df.rename(columns={df.columns[0]: "row_id"}, inplace = True)

    return df

def readCentIDsCSV():
    return pd.read_csv(settings.id_fn,header='infer')

def populateDB(conn):
    das = readDASCSV()
    centroid_ids = readCentIDsCSV()

    das = mergeAimsunZone(das, centroid_ids)

    # Create a table with the appropriate columns
    DAS.__table__.create(engine, checkfirst=True)
    # Insert the data into the table
    das.to_sql('DAS', conn, if_exists='replace', index=False)
    #centIDs.to_sql('centIDs', conn, if_exists='replace', index=False)

    # Commit the changes
    conn.commit()

def getDASDF(session, limit = None, stop_mode = None, removeExternalZones = False, removeInternalJourneys = False, time_range = None):
    query = session.query(DAS)

    if stop_mode:
        query = query.filter(DAS.stop_mode == stop_mode)
    
    if removeExternalZones:
        query = query.filter(DAS.prev_stop_zone.in_(settings.EXTERNAL_ZONES) == False)
        query = query.filter(DAS.stop_zone.in_(settings.EXTERNAL_ZONES) == False)
    
    if removeInternalJourneys:
        query = query.filter(DAS.prev_stop_zone != DAS.stop_zone)
    
    if time_range:
        query = query.filter(DAS.prev_stop_departure_time.in_(time_range))

    if limit:
        query = query.limit(limit)
    
    
    return pd.read_sql_query(query.statement, session.bind, index_col='row_id')

def createEngine():
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = sqlalchemy.create_engine(settings.das_db_uri)
    return engine

def mergeAimsunZone(das, centroid_ids):
    das=das.merge(centroid_ids,left_on='prev_stop_zone' ,right_on='Ex',how='left')
    das.rename(columns={'Aimsun': 'prev_stop_zone_aimsum'}, inplace=True)
    das.drop(columns=['Ex'], inplace=True)
    
    das=das.merge(centroid_ids,left_on='stop_zone' ,right_on='Ex',how='left')
    das.rename(columns={'Aimsun': 'stop_zone_aimsum'}, inplace=True)
    das.drop(columns=['Ex'], inplace=True)
    
    return das

if __name__ == "__main__":
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.

    print('Creating DB...')
    engine = createEngine()

    # Create a connection to the engine called conn
    conn = engine.connect()


    print('Populating DB...')
    populateDB(conn)

    # Close the connection
    conn.close()
    print('Done.')
    
    
    