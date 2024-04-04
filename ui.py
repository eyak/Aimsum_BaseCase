import streamlit as st
import db
from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from sqlalchemy import create_engine, Table
from model import DAS
from resmodel import MESYS
import pandas as pd
from settings import *
#import sqlite3

# some warning bug in streamlit
# see https://github.com/streamlit/streamlit/iss    ues/1430
import warnings
warnings.filterwarnings('ignore')

def showCSVStats():
    das = db.readDASCSV()

    st.write('Number of rows in DAS CSV')
    st.write(das.shape[0])


def showTable(session, table_name):
    metadata = MetaData()
    metadata.reflect(bind=session.bind)
    table = Table(table_name, metadata, autoload=True)

    df = pd.read_sql_query(session.query(table).limit(1000).statement, session.bind)
    st.write(df)

def showResults(res_session):
    listTables(res_session.bind)

    for table_name in ['SIM_INFO', 'MESYS', 'MESECT']:
        st.subheader(table_name)
        showTable(res_session, table_name)



def listTables(conn):
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=conn)
    for t in metadata_obj.sorted_tables:
        st.write(t.name)
        
        #top5 = conn.query(t).limit(5).all()
        #st.write(top5)
        #for c in t.columns:
        colsStr = ", ".join([f'{c.name} ({c.type})' for c in t.columns])
        st.write(colsStr)



def showInputData(input_session):
    count = input_session.query(DAS).count()
    st.write(f'{count} rows in DAS table')

    # for user in session.query(DAS).limit(10):
    #     st.write(user)

    time_range = [6.25, 6.75]
    df = db.getDASDF(session, stop_mode='Car', removeExternalZones=True, removeInternalJourneys=True, time_range=time_range)
    st.write(f'{df.shape[0]} rows in DAS table for time range {time_range}')
    st.write(df.head(100))
    


def main():
    st.title('Hello, world!')


    #showCSVStats()

    input_conn = db.createInputEngine()
    res_conn = db.createResEngine()

    input_session = Session(input_conn)
    res_session = Session(res_conn)

    showResults(res_session)



    

if __name__ == "__main__":
    main()
