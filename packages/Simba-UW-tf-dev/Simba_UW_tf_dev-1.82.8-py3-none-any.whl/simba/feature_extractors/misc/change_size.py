import pandas as pd
import glob
from simba.utils.read_write import get_fn_ext
import numpy as np
import os

# ORIGINAL DATA LOCATION
data_path = '/Users/simon/Desktop/envs/troubleshooting/sophie/project_folder/csv/targets_inserted'

# DATA DIRECTORY WHERE TO SAVE YOUR REDUCED-SAZE DATA
out_path = '/Users/simon/Desktop/envs/troubleshooting/sophie/project_folder/csv/targets_inserted/corrected'

if not os.path.isdir(out_path): os.makedirs(out_path)
files_p = glob.glob(data_path + '/*.csv')
cnt = 0
for file_cnt, file in enumerate(files_p):
    print(file_cnt)
    name = get_fn_ext(filepath=file)[1]
    df = pd.read_csv(file)
    df = df.astype(np.float32)
    cnt += len(df)
    save_path = os.path.join(out_path, name + '.csv')
    df.to_csv(save_path)

print(f'Total row count: {cnt}')