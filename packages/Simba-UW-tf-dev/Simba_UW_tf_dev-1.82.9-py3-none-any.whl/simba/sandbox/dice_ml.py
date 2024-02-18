import dice_ml
import pandas as pd
import numpy as np

model_path = '/Users/simon/Downloads/Attack.sav'
data_path = '/Users/simon/Downloads/attack_targets_inserted/Video29.csv'

data_df = pd.read_csv(data_path, index_col=0).iloc[:, 42:]
feature_names = list(data_df.columns)
feature_names = [x for x in feature_names if x != 'Attack']


d = dice_ml.Data(dataframe=data_df, continuous_features=feature_names, outcome_name='Attack')
m = dice_ml.Model(model_path=model_path,
                  backend='sklearn',
                  func="ohe-min-max")

exp = dice_ml.Dice(d, m, method="random")

test_df = data_df.drop(['Attack'], axis=1)

e1 = exp.generate_counterfactuals(test_df[0:30], total_CFs=1)