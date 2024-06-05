import os
from pathlib import Path

MODES = ['Car']

PROJECT_PATH = os.path.dirname(__file__)

#zones_keys_fn = os.path.join(PROJECT_PATH, 'key.csv')

das_fn = os.path.join(PROJECT_PATH, 'November_Base_Case_Aggregate')
id_fn = os.path.join(PROJECT_PATH, 'Id.csv')

das_db_fn = os.path.join(PROJECT_PATH, 'das.db')
das_db_uri = 'sqlite:///' + Path(das_db_fn).absolute().as_posix()

res_db_fn = os.path.join(PROJECT_PATH, 'Base_Case_November.sqlite')
res_db_uri = 'sqlite:///' + Path(res_db_fn).absolute().as_posix()

START_TIMES_RANGE = list(range(6, 24))
# only do first 10 for now
START_TIMES_RANGE = START_TIMES_RANGE[0:4]

EXTERNAL_ZONES = [41,42,43]

SPEED_INPUT_FN = 'proprietary/ExternalSpeed.dbf'