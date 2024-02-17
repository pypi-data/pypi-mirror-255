# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
import pandas as pd

data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/Japan/'
latest_date = '20231222'

sql = "select rq, sfjy from st_main.t_st_gg_hwjyrl where scdm='76'"
cal = HBDB().get_df(sql, "alluser", page_size=5000)
cal['rq'] = cal['rq'].astype(str)
cal = cal.sort_values('rq')
trade_cal = cal[cal['sfjy'] == '1']
trade_cal = trade_cal.sort_values('rq')

overseas_index_daily_k = HBDB().read_overseas_index_daily_k_given_indexs(['TPX Index', 'NKY Index', 'MXJP Index'])
overseas_index_daily_k = overseas_index_daily_k[['bzzsdm', 'jyrq', 'px_last', 'cur_mkt_cap', 'indx_traded_val']]
overseas_index_best = HBDB().read_overseas_index_best_given_indexs(['TPX Index', 'NKY Index', 'MXJP Index'])
overseas_index_best = overseas_index_best[['bzzsdm', 'jyrq', 'best_pe_ratio', 'best_eps']]
overseas_data = overseas_index_daily_k.merge(overseas_index_best, on=['bzzsdm', 'jyrq'], how='left')
overseas_data['jyrq'] = overseas_data['jyrq'].astype(str)
overseas_data = overseas_data[overseas_data['jyrq'] <= latest_date]
overseas_data = overseas_data[overseas_data['jyrq'].isin(trade_cal['rq'].unique().tolist())]
overseas_data['year_month'] = overseas_data['jyrq'].apply(lambda x: x[:6])
overseas_data = overseas_data.sort_values(['bzzsdm', 'jyrq']).drop_duplicates(['bzzsdm', 'year_month'], keep='last')
overseas_data = overseas_data[['bzzsdm', 'year_month', 'px_last', 'cur_mkt_cap', 'indx_traded_val', 'best_pe_ratio', 'best_eps']]
overseas_data.columns = ['指数名称', '年月', '最新价', '市值', '成交额', 'BEST_PE', 'BEST_EPS']
overseas_data_xls = pd.read_excel(data_path + '日本相关指数信息与数据.xlsx', sheet_name='彭博指数数据')
overseas_data_xls['日期'] = overseas_data_xls['日期'].apply(lambda x: x.date().strftime('%Y%m%d'))
overseas_data_xls = overseas_data_xls.sort_values('日期').fillna(method='ffill')
overseas_data_xls = overseas_data_xls[overseas_data_xls['日期'] <= latest_date]
overseas_data_xls = overseas_data_xls[overseas_data_xls['日期'].isin(trade_cal['rq'].unique().tolist())]
overseas_data_xls['年月'] = overseas_data_xls['日期'].apply(lambda x: x[:6])
overseas_data_xls = overseas_data_xls.sort_values(['指数名称', '日期']).drop_duplicates(['指数名称', '年月'], keep='last')
overseas_data_xls = overseas_data_xls[['指数名称', '年月', '最新价', '市值', '成交额', 'BEST_PE', 'BEST_EPS']]
overseas_data = pd.concat([overseas_data, overseas_data_xls])
overseas_data['市值'] = overseas_data['市值'] / 1000000.0
overseas_data['成交额'] = overseas_data['成交额'] / 1000000000.0
overseas_data['年月'] = overseas_data['年月'].apply(lambda x: datetime.strptime(x, '%Y%m'))
overseas_data.to_excel(data_path + 'overseas_data.xlsx')
overseas_data.to_hdf(data_path + 'overseas_data.hdf', key='table', mode='w')

overseas_data = pd.read_hdf(data_path + 'overseas_data.hdf', key='table')
data = overseas_data.pivot(index='年月', columns='指数名称', values='最新价')
data = data[['TPX Index', 'NKY Index', 'MXJP Index', 'FTJPNPR Index']]
data.columns = ['东京证交所股价指数', '日经225指数', 'MSCI日本指数', 'FTSE Japan RIC Capped Index']
data = data.dropna()
data = data / data.iloc[0]
data.to_excel(data_path + '最新价.xlsx')

overseas_data = pd.read_hdf(data_path + 'overseas_data.hdf', key='table')
data = overseas_data.pivot(index='年月', columns='指数名称', values='市值')
data = data[['TPX Index', 'NKY Index', 'MXJP Index', 'FTJPNPR Index']]
data.columns = ['东京证交所股价指数', '日经225指数', 'MSCI日本指数', 'FTSE Japan RIC Capped Index']
data = data.dropna()
data.to_excel(data_path + '市值.xlsx')

overseas_data = pd.read_hdf(data_path + 'overseas_data.hdf', key='table')
data = overseas_data.pivot(index='年月', columns='指数名称', values='成交额')
data = data[['TPX Index', 'NKY Index', 'MXJP Index', 'FTJPNPR Index']]
data.columns = ['东京证交所股价指数', '日经225指数', 'MSCI日本指数', 'FTSE Japan RIC Capped Index']
data = data.fillna(method='ffill').dropna()
data.to_excel(data_path + '成交额.xlsx')

overseas_data = pd.read_hdf(data_path + 'overseas_data.hdf', key='table')
data = overseas_data.pivot(index='年月', columns='指数名称', values='BEST_PE')
data = data[['TPX Index', 'NKY Index', 'MXJP Index', 'FTJPNPR Index']]
data.columns = ['东京证交所股价指数', '日经225指数', 'MSCI日本指数', 'FTSE Japan RIC Capped Index']
data = data.dropna()
data.to_excel(data_path + 'BEST_PE.xlsx')

overseas_data = pd.read_hdf(data_path + 'overseas_data.hdf', key='table')
data = overseas_data.pivot(index='年月', columns='指数名称', values='BEST_EPS')
data = data[['TPX Index', 'NKY Index', 'MXJP Index', 'FTJPNPR Index']]
data.columns = ['东京证交所股价指数', '日经225指数', 'MSCI日本指数', 'FTSE Japan RIC Capped Index']
data = data.dropna()
data.to_excel(data_path + 'BEST_EPS.xlsx')

overseas_data = pd.read_hdf(data_path + 'overseas_data.hdf', key='table')
data = overseas_data.pivot(index='年月', columns='指数名称', values='最新价')
data = data[['TPX Index', 'NKY Index', 'MXJP Index', 'FTJPNPR Index']]
data.columns = ['东京证交所股价指数', '日经225指数', 'MSCI日本指数', 'FTSE Japan RIC Capped Index']
data = data.dropna()
data_year = data.copy()
data_year = data_year.reset_index()
data_year['年份'] = data_year['年月'].apply(lambda x: x.date().strftime('%Y%m')[:4])
data_year = data_year.sort_values('年月').drop_duplicates('年份', keep='last')
data_year = data_year.drop('年月', axis=1).set_index('年份').sort_index()
data_year = data_year.pct_change()
data_year = data_year.dropna()
data_year.to_excel(data_path + '收益率（每年）.xlsx')
cumret = pd.DataFrame(data.iloc[-1] / data.iloc[0] - 1, columns=['累计收益率'])
annualret = pd.DataFrame((data.iloc[-1] / data.iloc[0]) ** (12.0 / (len(data) - 1)) - 1, columns=['年化收益率'])
ret_1y = pd.DataFrame(data.iloc[-1] / data.iloc[-12 * 1 - 1] - 1, columns=['近一年收益率'])
ret_3y = pd.DataFrame(data.iloc[-1] / data.iloc[-12 * 3 - 1] - 1, columns=['近三年收益率'])
ret_5y = pd.DataFrame(data.iloc[-1] / data.iloc[-12 * 5 - 1] - 1, columns=['近五年收益率'])
ret_10y = pd.DataFrame(data.iloc[-1] / data.iloc[-12 * 10 - 1] - 1, columns=['近十年收益率'])
ret = pd.concat([cumret, annualret, ret_1y, ret_3y, ret_5y, ret_10y], axis=1).T
ret = ret[['东京证交所股价指数', '日经225指数', 'MSCI日本指数', 'FTSE Japan RIC Capped Index']]
ret.to_excel(data_path + '收益率.xlsx')