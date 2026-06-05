import pandas as pd
import numpy as np

def load_installation_data(df, col='KWH', groupby='Date', sum_rows=True):
    card_data = df.groupby(groupby)
    if sum_rows==False:
        cd = card_data[col].count().apply(lambda x: x if x > 0 else None).dropna()
    else:
        cd = card_data[col].apply(lambda x: np.sum(x) if np.sum(x) > 0 else None ).dropna()
    return cd
        
