from settings import *
import sqlalchemy
from sqlalchemy.sql import select
from tqdm import tqdm

srcDB = res_db_uri
dstDB = resmin_db_uri

srcEngine = sqlalchemy.create_engine(srcDB)
dstEngine = sqlalchemy.create_engine(dstDB)

srcConn = srcEngine.connect()
dstConn = dstEngine.connect()

srcMetaData = sqlalchemy.MetaData()
srcMetaData.reflect(bind=srcEngine)


for tableName in ['MESYS', 'SIM_INFO', 'MESECT']:
    print('Copying table: ' + tableName)

    # drop the table if it exists in the destination
    dstConn.execute(sqlalchemy.text('DROP TABLE IF EXISTS ' + tableName))
    dstConn.commit()
    dstMetaData = sqlalchemy.MetaData()
    dstMetaData.reflect(bind=dstEngine)

    # get the table from the source
    table = sqlalchemy.Table(tableName, srcMetaData, autoload_with=srcEngine)

    dstTable = sqlalchemy.Table(tableName, dstMetaData)
    for column in table.columns:
        dstTable.append_column(sqlalchemy.Column(column.name, column.type))
    dstTable.create(bind=dstEngine)

    countQuery = select(sqlalchemy.func.count()).select_from(table)
    rowsCount = srcConn.execute(countQuery).scalar()
    print('Rows in table: ' + str(rowsCount))

    chunk_size = 5000
    num_chunks = (rowsCount + chunk_size - 1) // chunk_size

    for chunk in tqdm(range(num_chunks), desc="Copying chunks"):
        offset = chunk * chunk_size
        query = table.select().offset(offset).limit(chunk_size)
        data = srcConn.execute(query).fetchall()
        dataDict = [dict(row._mapping) for row in data]
        dstConn.execute(dstTable.insert(), dataDict)



    # continue
    # data = srcConn.execute(table.select()).fetchall()

    # # copy the data from the source to the destination
    # dataDict = [dict(row._mapping) for row in data]
    
    # dstConn.execute(dstTable.insert(), dataDict)

    # commit the changes
    dstConn.commit()


srcConn.close()
dstConn.close()
