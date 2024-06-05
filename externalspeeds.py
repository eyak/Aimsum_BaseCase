import dbfread
import pandas as pd
from settings import SPEED_INPUT_FN

SPEED_FILE_HOURS = range(6, 22)

def getSpeeds(ids):
    dbf = dbfread.DBF(SPEED_INPUT_FN)
    df = pd.DataFrame(iter(dbf))

    df = df[df['ID'].isin(ids)]

    for hour in SPEED_FILE_HOURS:
        df.loc[df['DIR']==1, f'SPD_{hour}'] = df[f'SPD_{hour}_AB']
        df.loc[df['DIR']==-1, f'SPD_{hour}'] = df[f'SPD_{hour}_BA']

    cols = ['ID'] + [f'SPD_{hour}' for hour in SPEED_FILE_HOURS]
    df = df[cols]
    
    return df

if __name__ == '__main__':
    ids = [415449]
    df = getSpeeds(ids)
    print(df)
