import streamlit as st
import db
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from model import DAS
import pandas as pd

# some warning bug in streamlit
# see https://github.com/streamlit/streamlit/issues/1430
import warnings
warnings.filterwarnings('ignore')

def showCSVStats():
    das = db.readDASCSV()

    st.write('Number of rows in DAS CSV')
    st.write(das.shape[0])


def main():
    st.title('Hello, world!')

    #showCSVStats()

    conn = db.createEngine()
    session = Session(conn)

    st.subheader('Tables in database')
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=conn)
    for t in metadata_obj.sorted_tables:
        st.write(t.name)
        
        for c in t.columns:
            st.write(f'  {c.name} {c.type}')


    count = session.query(DAS).count()
    st.write(f'{count} rows in DAS table')

    # for user in session.query(DAS).limit(10):
    #     st.write(user)

    time_range = [6.25, 6.75]
    df = db.getDASDF(session, stop_mode='Car', removeExternalZones=True, removeInternalJourneys=True, time_range=time_range)
    st.write(f'{df.shape[0]} rows in DAS table for time range {time_range}')
    st.write(df.head(100))
    

if __name__ == "__main__":
    main()
