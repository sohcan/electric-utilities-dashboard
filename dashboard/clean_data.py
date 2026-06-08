import streamlit as st
import pandas as pd
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.forecasting.stl import STLForecast
from scipy import stats

@st.cache_data
def clean_data(df, count = 23, fxct_count = 6, prd_thresh = 6, ol_thresh = 1.5):
    dfNZ = df[df['KWH'] > 0]; dfC = dfNZ.groupby(by='Meter').count();
    out = []
    for meter in dfC[dfC['Date'] > count].index:
        tmp = dfNZ[dfNZ['Meter']==meter]; tmp.set_index(['Date'], inplace=True, drop=True);
        stlf = STLForecast(tmp['KWH'].asfreq('MS').interpolate(method='time'), ARIMA, model_kwargs={'order': (1,1,0), 'trend': "t"}, period=12, robust=True);
        resf = stlf.fit();
        tmp_dict = {
            'Observed': resf.result.observed,
            'Residual': resf.result.resid,
            'Seasonal':resf.result.seasonal,
            'Trend': resf.result.trend,
            'Weights': resf.result.weights,
            }
        tmp_r = resf.result.resid
        tmp_fx= resf.get_prediction(0, resf.result.observed.count() + prd_thresh)
        tmp_dict.update(
            {
                'Forecast': resf.forecast(fxct_count),
                'Outer': abs( tmp_r-tmp_r.mean() ) > tmp_r.std()*ol_thresh
                }
        )
        tmp = tmp.reindex(index=tmp.index.union(tmp_dict['Forecast'].index.union(tmp_dict['Observed'].index)))
        tmp['Meter'] = meter
        for x in tmp_dict:
            tmp[x] = tmp_dict[x]
        tmp = tmp.join(tmp_fx.summary_frame())
        tmp['Diff'] = (tmp['Observed'].fillna(0) + tmp['Forecast'].fillna(0)) - tmp['mean'].fillna(0)
        tmp = tmp.join(
            pd.DataFrame(
                {
                    'Z':stats.zscore(resf.result.resid),
                    'CDF':stats.norm.cdf(stats.zscore(resf.result.resid))
                },
                index=resf.result.observed.index
            )
        )
        if count < 23:
            tmp['Flag'] = True
        else:
            tmp['Flag'] = False
        tmp['Selectable'] = True
        tmp.reset_index(inplace=True)
        tmp.rename(columns={'index':'Date'}, inplace=True)
        out.append(tmp) 
    df_clean = dfNZ.merge(pd.concat(out),how="outer",on=['Date','Meter'], suffixes=[None,'2']).drop(columns=['KWH2','USD2'])
    return df_clean
