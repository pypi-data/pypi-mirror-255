from statsmodels.imputation import mice
import pandas as pd
import numpy as np



df = pd.DataFrame([[1, 2, 3], [1, np.nan, 3]], columns=['A', 'B', 'C'])


imputer = mice.MICEData(df[['B']])
imputer.set_imputer('B', method='hotdeck', selection_method='srswr')



