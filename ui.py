import streamlit as st
import db
from sqlalchemy.sql import select, func, desc
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from sqlalchemy import create_engine, Table
from model import DAS
from resmodel import MESYS
import pandas as pd
from settings import *
import plotly.express as px
import plotly.graph_objects as go
from aimsumtables import *
from externalspeeds import getSpeeds
#import sqlite3

# some warning bug in streamlit
# see https://github.com/streamlit/streamlit/issues/1430
import warnings
warnings.filterwarnings('ignore')

RUNS_CSV = 'runs.csv'
KEYSECTIONS_CSV = 'keysections.csv'
QUESTIONS_CSV = 'questions.csv'

def showCSVStats():
    das = db.readDASCSV()

    st.write('Number of rows in DAS CSV')
    st.write(das.shape[0])

@st.cache_data
def loadTable(_session, table_name):
    metadata = MetaData()
    metadata.reflect(bind=_session.bind)
    table = Table(table_name, metadata, autoload=True)

    return table

@st.cache_data
def getTableCount(_session, table_name):
    table = loadTable(_session, table_name)

    return _session.query(table).count()

@st.cache_data
def getTableDF(_session, table_name, limit = None):
    table = loadTable(_session, table_name)

    if limit:
        return pd.read_sql_query(_session.query(table).limit(limit).statement, _session.bind)
    else:
        return pd.read_sql_query(_session.query(table).statement, _session.bind)

def readRunsCSV():
    if os.path.exists(RUNS_CSV):
        df = pd.read_csv(RUNS_CSV)
        return df
    else:
        st.warning(f'File {RUNS_CSV} not found')
        return pd.DataFrame()

def readQuestionsCSV():
    if os.path.exists(QUESTIONS_CSV):
        df = pd.read_csv(QUESTIONS_CSV)
        return df
    else:
        st.warning(f'File {QUESTIONS_CSV} not found')
        return pd.DataFrame()

def readKeySectionsCSV():
    if os.path.exists(KEYSECTIONS_CSV):
        df = pd.read_csv(KEYSECTIONS_CSV)
        return df
    else:
        st.warning(f'File {KEYSECTIONS_CSV} not found')
        return pd.DataFrame()



def showTable(session, table_name, limit = 1000):
    df = getTableDF(session, table_name)
    st.write(df)

def showRawData(res_session):
    tables = listTables(res_session.bind)

    selTable = st.selectbox('Select Table', tables, index=tables.index('SIM_INFO'))
    st.subheader(selTable)
    count = getTableCount(res_session, selTable)
    st.write(f'{count:,d} rows. Showing first 1000 rows.')

    table = loadTable(res_session, selTable)

    if 'did' in table.columns:
        dids = pd.read_sql_query(
            select(table.c.did)
            .distinct(),
            res_session.bind)['did'].to_list()

        seldid = st.selectbox('Select DID', dids, index=0)

        df = pd.read_sql_query(select(table).filter(table.c.did == seldid).limit(1000), res_session.bind)
            #res_session.query(table).limit(1000).statement, res_session.bind)
    else:
        df = getTableDF(res_session, selTable, limit=1000)
    
    st.write(df)


def mergeNameTime(res_session, df):
    info = getTableDF(res_session, 'SIM_INFO')[['did', 'didname', 'scname', 'twhen']]
    runs = readRunsCSV()
    info = pd.merge(info, runs, on='did', how='left', validate='one_to_one')

    df = pd.merge(df, info, on='did', how='left', validate='many_to_one')
    df['twhen'] = pd.to_datetime(df['twhen'])
    # create time, ent=1 is 6:15, add 15 minutes for each ent
    df['Time'] = df['twhen'] + pd.to_timedelta(6.25, unit='h') + pd.to_timedelta(df['ent'] * 15, unit='m')

    return df

def showWholeStats(res_session, dids):
    df = getTableDF(res_session, 'MESYS')
    dfcam = getTableDF(res_session, 'MESYSCAM')

    df = pd.merge(df, dfcam, on=['did', 'oid', 'eid', 'sid', 'ent'], how='left', validate='one_to_one')

    # filter by dids
    df = df[df['did'].isin(dids)]

    # filter for aggregated data only by ent=0
    df = df[df['ent'] != 0]

    # filter for total traffic sid=0
    df = df[df['sid'] == 0]

    # sort data by order of dids in the dids list
    df['did'] = pd.Categorical(df['did'], dids)
    df = df.sort_values(['did', 'ent'])

    df = mergeNameTime(res_session, df)

    # did,oid,eid,sid,ent,density,density_D,flow,flow_D,input_flow,input_flow_D,
    # input_count,input_count_D,gridlock_vehs,gridlock_vehs_D,ttime,ttime_D,dtime,dtime_D,
    # wtimeVQ,wtimeVQ_D,speed,speed_D,spdh,spdh_D,travel,travel_D,traveltime,traveltime_D,
    # vWait,vWait_D,vIn,vIn_D,vOut,vOut_D,totalDistanceTraveledInside,totalDistanceTraveledInside_D
    # totalTravelTimeInside,totalTravelTimeInside_D,totalWaitingTime,totalWaitingTime_D,vLostIn,vLostIn_D,
    # vLostOut,vLostOut_D,qmean,qmean_D,qvmean,qvmean_D,missedTurnings,missedTurnings_D,lane_changes,
    # lane_changes_D,total_lane_changes,total_lane_changes_D,didname,scname,twhen,Time
    
    target = st.selectbox('Variable', sorted(MESYS_STATS.keys()), index=1, format_func=lambda x: f"{x} ({MESYS_STATS[x]['label']})")
    logScale = st.checkbox('Log Scale', False)
    #st.write(df[['didname']+list(target_stats.keys())])

    label = MESYS_STATS[target]['label']
    units = MESYS_STATS[target]['units']

    data = df[['didlabel', 'Time', target]]

    # plotly bar chart
    fig = px.line(data, x='Time', color='didlabel', y=target)
    fig.update_layout(title=f'{label}', xaxis_title='Time', yaxis_title=units)
    fig.update_xaxes(
        tickformat="%H:%M", # the date format you want 
    )
    if logScale:
        fig.update_yaxes(type="log")
    st.plotly_chart(fig, 
            config = {'toImageButtonOptions': {
                'scale': 2,
                'filename': f'{target} - dids {" ".join(map(str,dids))} Overall'
            }},
            use_container_width=True)
        

def showSectionsStats(res_session, dids):
    table = loadTable(res_session, 'MESECT')
    keysections = readKeySectionsCSV().rename(columns={'oid': 'oid', 'name': 'oidName'})

    selSectionSelector = st.selectbox('Section Selector', ['Key Sections', 'By Volume'], index=0)

    if selSectionSelector == 'Key Sections':
        selected_oids = st.multiselect('Select Key Sections', keysections['oid'].to_list(), keysections['oid'].to_list(), format_func=lambda x: f"{keysections[keysections['oid'] == x]['oidName'].values[0]} ({x})")
        #st.write(f'Selected OIDs: {selected_oids}')
    else:
        grpoid = pd.read_sql_query(
            select(
                table.c.did, table.c.oid,
                func.count('*').label('rows'),
                func.sum(table.c.input_count).label('input_count_sum'),
                func.avg(table.c.input_count).label('flow_capacity_avg')
                )
            .filter(table.c.did.in_(dids))
            .filter(table.c.sid == 0) # total traffic only
            .group_by(table.c.did, table.c.oid)
            .order_by(desc("input_count_sum")),
            res_session.bind)

        # add select col
        grpoid.insert(0, 'select', False)

        res = st.data_editor(grpoid)

        selected_oids = set(res[res['select'] == True]['oid'].to_list())
        st.write(f'Selected OIDs: {selected_oids}')

    secdf = pd.read_sql_query(
        select('*')
        .filter(table.c.did.in_(dids))
        .filter(table.c.sid == 0) # total traffic only
        .filter(table.c.ent != 0) # ignore aggregated data
        .filter(table.c.oid.in_(selected_oids)) ,
        res_session.bind)

    secdf = mergeNameTime(res_session, secdf)
    secdf['did'] = pd.Categorical(secdf['did'], dids)
    #secdf = df.sort_values(['did', 'ent'])

    secdf = pd.merge(secdf, keysections, on='oid', how='left', validate='many_to_one')
    secdf['oidName'] = secdf['oidName'].fillna(secdf['oid'])
    
    variables = sorted(MESECT_STATS.keys())
    target = st.selectbox('Variable', variables, index=variables.index('speed'), format_func=lambda x: f"{x} ({MESECT_STATS[x]['label']})")
    
    logScale = st.checkbox('Log Scale', False, key='logScaleSections')
    selSingle = st.checkbox('Single Chart', False)
    selSlidingWindow = st.selectbox('Sliding Window Gaussian Smoothing', [0, 2, 3, 4, 6, 8], index=3)

    if target == 'speed':
        selExternalSpeed = st.checkbox('External Speeds', True)
        selInterpolate = st.checkbox('Interpolate External Speeds', True)
    else:
        selExternalSpeed = False
        selInterpolate = False

    if selExternalSpeed:
        gids = keysections['gid']
        speeds = getSpeeds(gids)
        speeds = speeds.melt(id_vars='ID', var_name='Time', value_name='speed')
        speeds['Time'] = speeds['Time'].str.replace('SPD_', '').astype(int)
        speeds = speeds.rename(columns={'ID': 'gid'})
        speeds = speeds.sort_values(['gid', 'Time'])
        #st.write(speeds)

    label = MESECT_STATS[target]['label']
    units = MESECT_STATS[target]['units']

    if selSingle:
        data = secdf[['did', 'didlabel', 'Time', 'oidName', target]]
        data['label'] = data['oidName'].astype(str) + ', ' + data['didlabel']

        data = data.sort_values(['did', 'oidName', 'Time'])

        # plotly bar chart
        fig = px.line(data, x='Time', color='didlabel', symbol='oidName', y=target)
        fig.update_layout(title=f'Section {label}', xaxis_title='Time', yaxis_title=units)
        fig.update_xaxes(
            tickformat="%H:%M", # the date format you want 
        )

        if logScale:
            fig.update_yaxes(type="log")

        st.plotly_chart(fig, config = {'toImageButtonOptions': {
            'scale': 2,
            'filename': f'{target} - dids {" ".join(map(str,dids))} - oids {" ".join(map(str,selected_oids))}'
        }})

    else:
        cmpTable = []
        for i,oid in enumerate(selected_oids):
            data = secdf[secdf['oid'] == oid][['didlabel', 'Time', target]]
            
            if data.empty:
                continue

            data = data.sort_values(['didlabel', 'Time'])

            if selSlidingWindow > 0:
                data[target] = data.groupby('didlabel')[target].transform(lambda x: x.rolling(
                    window=selSlidingWindow,
                    win_type='exponential',
                    min_periods=1,
                    center=True).mean())
            
            # get the date component from first row
            date = data['Time'].iloc[0].date()
            
            # plotly bar chart
            fig = px.line(data, x='Time', color='didlabel', y=target)
            oidNames = keysections[keysections['oid'] == oid]['oidName'].values
            oidName = oidNames[0] if len(oidNames) > 0 else oid

            if selExternalSpeed:
                gid = keysections[keysections['oid'] == oid]['gid'].values[0]
                speedData = speeds[speeds['gid'] == gid]

                # convert time to datetime using date 
                speedData['Time'] = pd.to_datetime(date) + pd.to_timedelta(speedData['Time'], unit='h')
                
                if selInterpolate:
                    # find times missing in speedData
                    missingTimes = data[~data['Time'].isin(speedData['Time'])]['Time'].unique()
                    # concat the times missing in speedData with NaN speed
                    speedDataInterpolated = pd.concat([speedData, pd.DataFrame({'Time': missingTimes, 'speed': [None]*len(missingTimes)})]).sort_values('Time')

                    # set index to Time
                    speedDataInterpolated = speedDataInterpolated.set_index('Time')

                    # interpolate speed data using times
                    speedDataInterpolated['speed'] = speedDataInterpolated['speed'].interpolate(method='time')

                    # reset Time as column
                    speedDataInterpolated['Time'] = speedDataInterpolated.index
                    speedDataInterpolated.reset_index(drop=True, inplace=True)

                    speedData = speedDataInterpolated


                
                fig.add_trace(go.Scatter(
                    x=speedData['Time'],
                    y=speedData['speed'],
                    mode='lines+markers',
                    line=dict(color='orange', dash='dot'),
                    #marker=dict(size=2),
                    name=f'External Speed {"interpolated" if selInterpolate else ""}'))

                

                for didlabel in data['didlabel'].unique():
                    #st.write(didlabel)
                    didData = data[data['didlabel'] == didlabel]

                    speedDidData = speedData[speedData['Time'].isin(didData['Time'])]
                    didData = didData[didData['Time'].isin(speedData['Time'])]

                    vspeed= speedDidData['speed'].reset_index(drop=True)
                    vdata = didData[target].reset_index(drop=True)

                    #st.dataframe(pd.DataFrame({'external': vspeed, 'data': vdata}))
                    if len(vspeed) > 0:
                        corr = vspeed.corr(vdata, method='pearson')
                        
                        rmse = ((vspeed - vdata) ** 2).mean() ** .5
                        
                        # add corr and rmse to cmpTable
                        cmpTable.append({'didlabel': didlabel, 'oidName': oidName, 'corr': corr, 'rmse': rmse})

            fig.update_layout(title=f"Section {oidName} ({oid}) {label}", xaxis_title='Time', yaxis_title=units)
            fig.update_xaxes(
                tickformat="%H:%M", # the date format you want 
            )

            if logScale:
                fig.update_yaxes(type="log")

            st.plotly_chart(fig)

        if cmpTable:
            cmpdf = pd.DataFrame(cmpTable)
            #st.write(cmpdf)

            # filter the df by time
            

            # convert to pivot table of didlabel vs oidName
            for value in ['corr', 'rmse']:
                valueDesc = 'Correlation' if value == 'corr' else 'RMSE'
                cmpdfpivot = cmpdf.pivot(index='didlabel', columns='oidName', values=value)
                # add average colomn
                mean = cmpdfpivot.mean(axis=1)
                median = cmpdfpivot.median(axis=1)
                cmpdfpivot['Mean'] = mean
                cmpdfpivot['Median'] = median
                fig = px.imshow(
                    cmpdfpivot, 
                    color_continuous_scale='RdYlGn' if value == 'corr' else 'Reds',
                    title=f'{valueDesc} with External Speeds {"interpolated" if selInterpolate else ""}'
                )
                st.plotly_chart(fig)
            #cmpdf = cmpdf.pivot(index='didlabel', columns='oidName', values='corr')

        

    #st.write(secdf)

    

def getSimulations(res_session):
    df = getTableDF(res_session, 'SIM_INFO')
    df['exec_date'] = pd.to_datetime(df['exec_date'])
    df['exec_date_end'] = pd.to_datetime(df['exec_date_end'])
    df['exec_duration'] = df['exec_date_end'] - df['exec_date']
    return df

def showSimulations(res_session, didlist):
    df = getSimulations(res_session)

    runs = readRunsCSV()

    df = pd.merge(df, runs, left_on='did', right_on='did', how='left', validate='one_to_one')

    # add select boolean column as first col
    #df.insert(0, 'show order', 0)

    if didlist:
        #selected_dids = st.session_state['selected_dids']
        df['show order'] = None
        df.loc[df['did'].isin(didlist), 'show order'] = df[df['did'].isin(didlist)].apply(lambda row: didlist.index(row['did'])+1, axis=1)
    

    
    res = st.data_editor(df[['show order', 'did', 'didlabel', 'comments', 'didname', 'scname', 'exec_date', 'exec_duration']],
                         key='diddata',
                         use_container_width=True,
                         column_config={
                             'show order': st.column_config.SelectboxColumn(
                                 options=list(range(11)),
                             )
                         }
                        )

    selected_dids = res[res['show order'] > 0].sort_values('show order')['did'].to_list()

    #st.write(f'Selected DIDs: {selected_dids}')
    with st.expander('Save Question'):
        question_name = st.text_input('Question Name')
        
        if st.button('Save'):
            questions = readQuestionsCSV()
            new_question = pd.DataFrame([{'question': question_name, 'didlist': '/'.join(map(str, selected_dids))}])
            questions = pd.concat([questions, new_question], ignore_index=True)
            questions.to_csv(QUESTIONS_CSV, index=False)
            st.success('Question saved')

        


    tab1, tab2 = st.tabs(['Whole Stats', 'Sections Stats'])
    with tab1:
        showWholeStats(res_session, selected_dids)
    with tab2:
        showSectionsStats(res_session, selected_dids)


def listTables(conn):
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=conn)
    return [t.name for t in metadata_obj.sorted_tables]

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
    df = db.getDASDF(input_session, stop_mode='Car', removeExternalZones=True, removeInternalJourneys=True, time_range=time_range)
    st.write(f'{df.shape[0]} rows in DAS table for time range {time_range}')
    st.write(df.head(100))
    

@st._cache_resource
def createInputEngineCachced():
    return db.createInputEngine()

@st._cache_resource
def createResEngineCached():
    return db.createResEngine()

def showQuestions():
    questions = readQuestionsCSV()

    sel_question = st.selectbox('Select Question', [None] + questions['question'].to_list())
    if sel_question:
        sel_didlist = questions[questions['question'] == sel_question]['didlist'].values[0]
        sel_didlist = sel_didlist.split('/')
        sel_didlist = list(map(int, sel_didlist))

        return sel_didlist

    return []

def main():
    st.set_page_config(layout="wide")
    st.title('AIMSUM MURSA UI')
    st.markdown("Welcome to the AIMSUM's *Multifaceted Unified Residual System Analysis* UI")
    st.link_button('AIMSUM Output definition', 'https://docs.aimsun.com/next/22.0.1/UsersManual/OutputDatabaseDefinition.html#mesys-table')
    #showCSVStats()

    input_conn = createInputEngineCachced()
    res_conn = createResEngineCached()

    input_session = Session(input_conn)
    res_session = Session(res_conn)

    with st.expander('Raw Results'):
        showRawData(res_session)
    
    didlist = showQuestions()
    showSimulations(res_session, didlist)



    

if __name__ == "__main__":
    main()
