# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
import numpy as np
import pandas as pd
import xlwings

from WindPy import w
w.start()  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
w.isconnected()  # 判断WindPy是否已经登录成功

import warnings
warnings.filterwarnings("ignore")


def get_overseas_date(start_date, end_date):
    calendar_df = HBDB().read_cal(start_date, end_date)
    calendar_df = calendar_df.rename(columns={'jyrq': 'CALENDAR_DATE', 'sfjj': 'IS_OPEN', 'sfzm': 'IS_WEEK_END', 'sfym': 'IS_MONTH_END'})
    calendar_df['CALENDAR_DATE'] = calendar_df['CALENDAR_DATE'].astype(str)
    calendar_df = calendar_df.sort_values('CALENDAR_DATE')
    calendar_df['IS_OPEN'] = calendar_df['IS_OPEN'].astype(int).replace({0: 1, 1: 0})
    calendar_df['YEAR_MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[:6])
    calendar_df['MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:6])
    calendar_df['MONTH_DAY'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:])
    calendar_df = calendar_df[(calendar_df['CALENDAR_DATE'] >= start_date) & (calendar_df['CALENDAR_DATE'] <= end_date)]

    start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
    end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
    trade_df = w.wsd("SPX.GI", "close", start_date_hyphen, end_date_hyphen, usedf=True)[1].reset_index()
    trade_df['index'] = trade_df['index'].apply(lambda x: x.strftime('%Y%m%d'))
    trade_df = trade_df[['index']].rename(columns={'index': 'TRADE_DATE'})
    trade_df.to_hdf('{0}trade_df.hdf'.format(data_path), key='table', mode='w')
    trade_df = pd.read_hdf('{0}trade_df.hdf'.format(data_path), key='table')
    return calendar_df, trade_df


def df_add_info(df, info):
    df = df.T
    df.index.name = 'INDEX'
    df = df.reset_index()
    df['TYPE'] = info
    df = df.set_index(['TYPE', 'INDEX']).T
    return df


def cal_drawdown(ser):
    df = pd.DataFrame(ser)
    df.columns = ['NAV']
    df = df.sort_index()
    df['IDX'] = range(len(df))
    df['HIGHEST'] = df['NAV'].cummax()
    df['DRAWDOWN'] = (df['NAV'] - df['HIGHEST']) / df['HIGHEST']
    return df['DRAWDOWN']


def cal_annual_ret(idxs, col, daily_df, q):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    annual_ret = (part_df[col].iloc[-1] / part_df[col].iloc[0]) ** (float(q) / len(part_df)) - 1 if part_df[col].iloc[0] != 0 else np.nan
    return annual_ret


def cal_annual_vol(idxs, col, daily_df, q):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    annual_vol = np.std(part_df[col].pct_change().dropna(), ddof=1) * np.sqrt(q)
    return annual_vol


def cal_max_drawdown(idxs, col, daily_df, q):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    part_df['HIGHEST'] = part_df[col].cummax()
    part_df['DRAWDOWN'] = (part_df[col] - part_df['HIGHEST']) / part_df['HIGHEST']
    max_drawdown = min(part_df['DRAWDOWN'])
    return max_drawdown


def quantile_definition(idxs, col, daily_df):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    q = (1.0 - np.count_nonzero(part_df[col].iloc[-1] < part_df[col]) / len(part_df)) if len(part_df[col].dropna()) != 0 else np.nan
    return q


class OverseasOverview:
    def __init__(self, start_date, end_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_hyphen = datetime.strptime(self.start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(self.end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.data_path = data_path

        self.index_list = ['881001.WI', 'HSI.HI', 'HSTECH.HI',
                           'SPX Index', 'SPW Index', 'INDU Index', 'CCMP Index',
                           'SXXP Index', 'SX5E Index', 'UKX Index', 'CAC Index', 'DAX Index',
                           'TPX Index', 'NKY Index', 'KOSPI Index', 'VN30 Index', 'SENSEX Index',
                           'MXEF Index', 'M1WO Index',
                           'RIY Index', 'RTY Index', 'RAY Index', 'RUMCINTR Index', 'RMICRO Index', 'RLV Index', 'RLG Index',
                           'S5TELS Index', 'S5COND Index', 'S5CONS Index', 'S5ENRS Index', 'S5FINL Index',
                           'S5HLTH Index', 'S5INDU Index', 'S5MATR Index', 'S5RLST Index', 'S5INFT Index', 'S5UTIL Index']
        self.index_name_dict = {'881001.WI': '万得全A指数', 'HSI.HI': '恒生指数', 'HSTECH.HI': '恒生科技指数',
                                'SPX Index': '标普500指数', 'SPW Index': '标普500等权重指数', 'INDU Index': '道琼斯工业平均指数', 'CCMP Index': '纳斯达克综合指数',
                                'SXXP Index': '欧洲斯托克600指数', 'SX5E Index': '欧洲斯托克50指数', 'UKX Index': '英国富时100指数', 'CAC Index': '法国CAC40指数', 'DAX Index': '德国DAX30指数',
                                'TPX Index': '日本东证指数', 'NKY Index': '日经225指数', 'KOSPI Index': '韩国综合指数', 'VN30 Index': '越南VN30指数', 'SENSEX Index': '印度孟买30指数',
                                'MXEF Index': 'MSCI新兴市场指数', 'M1WO Index': 'MSCI全球指数',
                                'RIY Index': '罗素1000指数', 'RTY Index': '罗素2000指数', 'RAY Index': '罗素3000指数', 'RUMCINTR Index': '罗素中市值指数', 'RMICRO Index': '罗素微型股指数', 'RLV Index': '罗素1000价值指数', 'RLG Index': '罗素1000成长指数',
                                'S5TELS Index': '通信服务', 'S5COND Index': '可选消费', 'S5CONS Index': '日常消费', 'S5ENRS Index': '能源', 'S5FINL Index': '金融',
                                'S5HLTH Index': '医疗保健', 'S5INDU Index': '工业', 'S5MATR Index': '材料', 'S5RLST Index': '房地产', 'S5INFT Index': '信息技术', 'S5UTIL Index': '公用事业'}

        self.calendar_df, self.trade_df = get_overseas_date(self.start_date, self.end_date)
        self.date_1w = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-5]
        self.date_1m = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-20 * 1]
        self.date_3m = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-20 * 3]
        self.date_6m = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-20 * 6]
        self.date_1y = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-250]
        self.date_2023 = self.trade_df[self.trade_df['TRADE_DATE'] < '20230101']['TRADE_DATE'].iloc[-1]
        self.date_2022 = self.trade_df[self.trade_df['TRADE_DATE'] < '20220101']['TRADE_DATE'].iloc[-1]
        self.date_2021 = self.trade_df[self.trade_df['TRADE_DATE'] < '20210101']['TRADE_DATE'].iloc[-1]
        self.date_2015 = self.trade_df[self.trade_df['TRADE_DATE'] < '20150101']['TRADE_DATE'].iloc[-1]

        self.load()

    def load(self):
        self.overseas_index_daily_k = HBDB().read_overseas_index_daily_k_given_indexs(self.index_list)
        self.overseas_index_daily_k.to_hdf('{0}overseas_index_daily_k.hdf'.format(self.data_path), key='table', mode='w')
        self.overseas_index_daily_k = pd.read_hdf('{0}overseas_index_daily_k.hdf'.format(self.data_path), key='table')

        self.overseas_index_finance = HBDB().read_overseas_index_finance_given_indexs(self.index_list)
        self.overseas_index_finance.to_hdf('{0}overseas_index_finance.hdf'.format(self.data_path), key='table', mode='w')
        self.overseas_index_finance = pd.read_hdf('{0}overseas_index_finance.hdf'.format(self.data_path), key='table')

        self.overseas_index_best = HBDB().read_overseas_index_best_given_indexs(self.index_list)
        self.overseas_index_best.to_hdf('{0}overseas_index_best.hdf'.format(self.data_path), key='table', mode='w')
        self.overseas_index_best = pd.read_hdf('{0}overseas_index_best.hdf'.format(self.data_path), key='table')

    def index(self):
        index_w = w.wsd(",".join(self.index_list[:3]), "close", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        index_w['index'] = index_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        index_w = index_w.set_index('index').sort_index()
        index = self.overseas_index_daily_k[['bzzsdm', 'jyrq', 'px_last']]
        index['jyrq'] = index['jyrq'].astype(str)
        index = index.pivot(index='jyrq', columns='bzzsdm', values='px_last').sort_index()
        index = index_w.merge(index, left_index=True, right_index=True, how='right').sort_index()
        index = index[index.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        index = index[self.index_list].rename(columns=self.index_name_dict)
        index = index[(index.index >= self.start_date) & (index.index <= self.end_date)]

        close = index.copy(deep=True)
        close = df_add_info(close, '收盘点位')

        close_nav = index.dropna()
        close_nav = close_nav / close_nav.iloc[0]
        close_nav = df_add_info(close_nav, '收盘点位（最大同期归一化）')

        close_ytd = index[index.index >= '20221230']
        close_ytd = close_ytd / close_ytd.iloc[0]
        close_ytd = df_add_info(close_ytd, '收盘点位（今年以来归一化）')

        ret_1w = index.pct_change(5)
        ret_1w = df_add_info(ret_1w, '近一周')

        ret_1m = index.pct_change(20 * 1)
        ret_1m = df_add_info(ret_1m, '近一月')

        ret_3m = index.pct_change(20 * 3)
        ret_3m = df_add_info(ret_3m, '近三月')

        ret_6m = index.pct_change(20 * 6)
        ret_6m = df_add_info(ret_6m, '近六月')

        ret_1y = index.pct_change(250)
        ret_1y = df_add_info(ret_1y, '近一年')

        index_2023 = index[index.index >= self.date_2023]
        ret_2023 = index_2023 / index_2023.iloc[0] - 1
        ret_2023 = df_add_info(ret_2023, '2023年以来')

        index_2022 = index[index.index >= self.date_2022]
        ret_2022 = index_2022 / index_2022.iloc[0] - 1
        ret_2022 = df_add_info(ret_2022, '2022年以来')

        index_2021 = index[index.index >= self.date_2021]
        ret_2021 = index_2021 / index_2021.iloc[0] - 1
        ret_2021 = df_add_info(ret_2021, '2021年以来')

        index_2015 = index[index.index >= self.date_2015]
        ret_2015 = index_2015 / index_2015.iloc[0] - 1
        ret_2015 = df_add_info(ret_2015, '2015年以来')

        drawdown = index.copy(deep=True)
        drawdown = drawdown.apply(lambda x: cal_drawdown(x))
        drawdown = df_add_info(drawdown, '回撤')

        annual_ret_1y, annual_ret_3y, annual_ret_5y, annual_ret_10y, \
        annual_vol_1y, annual_vol_3y, annual_vol_5y, annual_vol_10y, \
        max_drawdown_1y, max_drawdown_3y, max_drawdown_5y, max_drawdown_10y = \
        index.copy(deep=True), index.copy(deep=True), index.copy(deep=True), index.copy(deep=True), \
        index.copy(deep=True), index.copy(deep=True), index.copy(deep=True), index.copy(deep=True), \
        index.copy(deep=True), index.copy(deep=True), index.copy(deep=True), index.copy(deep=True)
        ret_risk = index.copy(deep=True)
        ret_risk['IDX'] = range(len(ret_risk))
        for col in list(ret_risk.columns)[:-1]:
            print(col)
            annual_ret_1y[col] = ret_risk['IDX'].rolling(250 * 1).apply(lambda x: cal_annual_ret(x, col, ret_risk, 250))
            annual_ret_3y[col] = ret_risk['IDX'].rolling(250 * 3).apply(lambda x: cal_annual_ret(x, col, ret_risk, 250))
            annual_ret_5y[col] = ret_risk['IDX'].rolling(250 * 5).apply(lambda x: cal_annual_ret(x, col, ret_risk, 250))
            annual_ret_10y[col] = ret_risk['IDX'].rolling(250 * 10).apply(lambda x: cal_annual_ret(x, col, ret_risk, 250))
            annual_vol_1y[col] = ret_risk['IDX'].rolling(250 * 1).apply(lambda x: cal_annual_vol(x, col, ret_risk, 250))
            annual_vol_3y[col] = ret_risk['IDX'].rolling(250 * 3).apply(lambda x: cal_annual_vol(x, col, ret_risk, 250))
            annual_vol_5y[col] = ret_risk['IDX'].rolling(250 * 5).apply(lambda x: cal_annual_vol(x, col, ret_risk, 250))
            annual_vol_10y[col] = ret_risk['IDX'].rolling(250 * 10).apply(lambda x: cal_annual_vol(x, col, ret_risk, 250))
            max_drawdown_1y[col] = ret_risk['IDX'].rolling(250 * 1).apply(lambda x: cal_max_drawdown(x, col, ret_risk, 250))
            max_drawdown_3y[col] = ret_risk['IDX'].rolling(250 * 3).apply(lambda x: cal_max_drawdown(x, col, ret_risk, 250))
            max_drawdown_5y[col] = ret_risk['IDX'].rolling(250 * 5).apply(lambda x: cal_max_drawdown(x, col, ret_risk, 250))
            max_drawdown_10y[col] = ret_risk['IDX'].rolling(250 * 10).apply(lambda x: cal_max_drawdown(x, col, ret_risk, 250))
        sharpe_ratio_1y = (annual_ret_1y - 0.015) / annual_vol_1y
        sharpe_ratio_3y = (annual_ret_3y - 0.015) / annual_vol_3y
        sharpe_ratio_5y = (annual_ret_5y - 0.015) / annual_vol_5y
        sharpe_ratio_10y = (annual_ret_10y - 0.015) / annual_vol_10y
        annual_ret_1y = df_add_info(annual_ret_1y, '年化收益率（近一年）')
        annual_ret_3y = df_add_info(annual_ret_3y, '年化收益率（近三年）')
        annual_ret_5y = df_add_info(annual_ret_5y, '年化收益率（近五年）')
        annual_ret_10y = df_add_info(annual_ret_10y, '年化收益率（近十年）')
        annual_vol_1y = df_add_info(annual_vol_1y, '年化波动率（近一年）')
        annual_vol_3y = df_add_info(annual_vol_3y, '年化波动率（近三年）')
        annual_vol_5y = df_add_info(annual_vol_5y, '年化波动率（近五年）')
        annual_vol_10y = df_add_info(annual_vol_10y, '年化波动率（近十年）')
        sharpe_ratio_1y = df_add_info(sharpe_ratio_1y, '夏普比率（近一年）')
        sharpe_ratio_3y = df_add_info(sharpe_ratio_3y, '夏普比率（近三年）')
        sharpe_ratio_5y = df_add_info(sharpe_ratio_5y, '夏普比率（近五年）')
        sharpe_ratio_10y = df_add_info(sharpe_ratio_10y, '夏普比率（近十年）')
        max_drawdown_1y = df_add_info(max_drawdown_1y, '最大回撤（近一年）')
        max_drawdown_3y = df_add_info(max_drawdown_3y, '最大回撤（近三年）')
        max_drawdown_5y = df_add_info(max_drawdown_5y, '最大回撤（近五年）')
        max_drawdown_10y = df_add_info(max_drawdown_10y, '最大回撤（近十年）')

        index = pd.concat([close, close_nav, close_ytd, ret_1w, ret_1m, ret_3m, ret_6m, ret_1y, ret_2023, ret_2022, ret_2021, ret_2015, drawdown,
                           annual_ret_1y, annual_vol_1y, sharpe_ratio_1y, max_drawdown_1y,
                           annual_ret_3y, annual_vol_3y, sharpe_ratio_3y, max_drawdown_3y,
                           annual_ret_5y, annual_vol_5y, sharpe_ratio_5y, max_drawdown_5y,
                           annual_ret_10y, annual_vol_10y, sharpe_ratio_10y, max_drawdown_10y], axis=1)
        index.index = map(lambda x: datetime.strptime(x, '%Y%m%d').date(), index.index)
        return index

    def turnover(self):
        mv_w = w.wsd(",".join(self.index_list[:3]), "mkt_cap_ard", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        mv_w['index'] = mv_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        mv_w = mv_w.set_index('index').sort_index()
        free_mv_w = w.wsd(",".join(self.index_list[:3]), "mkt_freeshares", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        free_mv_w['index'] = free_mv_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        free_mv_w = free_mv_w.set_index('index').sort_index()
        turnover_volume_w = w.wsd(",".join(self.index_list[:3]), "volume", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        turnover_volume_w['index'] = turnover_volume_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        turnover_volume_w = turnover_volume_w.set_index('index').sort_index()
        turnover_value_w = w.wsd(",".join(self.index_list[:3]), "amt", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        turnover_value_w['index'] = turnover_value_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        turnover_value_w = turnover_value_w.set_index('index').sort_index()
        index_w = w.wsd(",".join(self.index_list[:3]), "close", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        index_w['index'] = index_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        index_w = index_w.set_index('index').sort_index()
        mv = self.overseas_index_daily_k[['bzzsdm', 'jyrq', 'cur_mkt_cap']]
        mv['jyrq'] = mv['jyrq'].astype(str)
        mv = mv.pivot(index='jyrq', columns='bzzsdm', values='cur_mkt_cap').sort_index()
        free_mv = self.overseas_index_daily_k[['bzzsdm', 'jyrq', 'free_float_market_cap']]
        free_mv['jyrq'] = free_mv['jyrq'].astype(str)
        free_mv = free_mv.pivot(index='jyrq', columns='bzzsdm', values='free_float_market_cap').sort_index()
        turnover_volume = self.overseas_index_daily_k[['bzzsdm', 'jyrq', 'px_volume']]
        turnover_volume['jyrq'] = turnover_volume['jyrq'].astype(str)
        turnover_volume = turnover_volume.pivot(index='jyrq', columns='bzzsdm', values='px_volume').sort_index()
        turnover_value = self.overseas_index_daily_k[['bzzsdm', 'jyrq', 'indx_traded_val']]
        turnover_value['jyrq'] = turnover_value['jyrq'].astype(str)
        turnover_value = turnover_value.pivot(index='jyrq', columns='bzzsdm', values='indx_traded_val').sort_index()
        index = self.overseas_index_daily_k[['bzzsdm', 'jyrq', 'px_last']]
        index['jyrq'] = index['jyrq'].astype(str)
        index = index.pivot(index='jyrq', columns='bzzsdm', values='px_last').sort_index()
        mv = (mv_w / 10000000000.0).merge((mv / 10000.0), left_index=True, right_index=True, how='right').sort_index()
        free_mv = (free_mv_w / 10000000000.0).merge((free_mv / 10000.0), left_index=True, right_index=True, how='right').sort_index()
        turnover_volume = (turnover_volume_w / 10000000000.0).merge((turnover_volume / 10000000.0), left_index=True, right_index=True, how='right').sort_index()
        turnover_value = (turnover_value_w / 10000000000.0).merge((turnover_value / 10000000.0), left_index=True, right_index=True, how='right').sort_index()
        index = index_w.merge(index, left_index=True, right_index=True, how='right').sort_index()
        mv = mv[mv.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        free_mv = free_mv[free_mv.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        turnover_volume = turnover_volume[turnover_volume.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        turnover_value = turnover_value[turnover_value.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        index = index[index.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        mv = mv[self.index_list].rename(columns=self.index_name_dict)
        free_mv = free_mv[self.index_list].rename(columns=self.index_name_dict)
        turnover_volume = turnover_volume[self.index_list].rename(columns=self.index_name_dict)
        turnover_value = turnover_value[self.index_list].rename(columns=self.index_name_dict)
        index = index[self.index_list].rename(columns=self.index_name_dict)
        mv = mv[(mv.index >= self.start_date) & (mv.index <= self.end_date)]
        free_mv = free_mv[(free_mv.index >= self.start_date) & (free_mv.index <= self.end_date)]
        turnover_volume = turnover_volume[(turnover_volume.index >= self.start_date) & (turnover_volume.index <= self.end_date)]
        turnover_value = turnover_value[(turnover_value.index >= self.start_date) & (turnover_value.index <= self.end_date)]
        index = index[(index.index >= self.start_date) & (index.index <= self.end_date)]
        turnover_rate = turnover_value / mv
        volatility = index.pct_change().rolling(20).std()

        mv = df_add_info(mv, '总市值（百亿）')
        free_mv = df_add_info(free_mv, '自由流通市值（百亿）')
        turnover_volume = df_add_info(turnover_volume, '成交量（百亿）')
        turnover_value = df_add_info(turnover_value, '成交额（百亿）')
        turnover_rate = df_add_info(turnover_rate, '换手率')
        volatility = df_add_info(volatility, '20日波动率')

        turnover = pd.concat([mv, free_mv, turnover_volume, turnover_value, turnover_rate, volatility], axis=1)
        turnover.index = map(lambda x: datetime.strptime(x, '%Y%m%d').date(), turnover.index)
        return turnover

    def valuation(self):
        pe_ttm_w = w.wsd(",".join(self.index_list[:3]), "pe_ttm", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        pe_ttm_w['index'] = pe_ttm_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        pe_ttm_w = pe_ttm_w.set_index('index').sort_index()
        pb_lf_w = w.wsd(",".join(self.index_list[:3]), "pb_lf", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        pb_lf_w['index'] = pb_lf_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        pb_lf_w = pb_lf_w.set_index('index').sort_index()
        div_yield_w = w.wsd(",".join(self.index_list[:3]), "dividendyield2", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        div_yield_w['index'] = div_yield_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        div_yield_w = div_yield_w.set_index('index').sort_index()
        pe_ttm = self.overseas_index_daily_k[['bzzsdm', 'jyrq', 'pe_ratio']]
        pe_ttm['jyrq'] = pe_ttm['jyrq'].astype(str)
        pe_ttm = pe_ttm.pivot(index='jyrq', columns='bzzsdm', values='pe_ratio').sort_index()
        pb_lf = self.overseas_index_finance[['bzzsdm', 'jyrq', 'px_to_book_ratio']]
        pb_lf['jyrq'] = pb_lf['jyrq'].astype(str)
        pb_lf = pb_lf.pivot(index='jyrq', columns='bzzsdm', values='px_to_book_ratio').sort_index()
        div_yield = self.overseas_index_daily_k[['bzzsdm', 'jyrq', 'eqy_dvd_yld_12m']]
        div_yield['jyrq'] = div_yield['jyrq'].astype(str)
        div_yield = div_yield.pivot(index='jyrq', columns='bzzsdm', values='eqy_dvd_yld_12m').sort_index()
        pe_ttm = pe_ttm_w.merge(pe_ttm, left_index=True, right_index=True, how='right').sort_index()
        pb_lf = pb_lf_w.merge(pb_lf, left_index=True, right_index=True, how='right').sort_index()
        div_yield = div_yield_w.merge(div_yield, left_index=True, right_index=True, how='right').sort_index()
        pe_ttm = pe_ttm[pe_ttm.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        pb_lf = pb_lf[pb_lf.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        div_yield = div_yield[div_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        pe_ttm = pe_ttm[self.index_list].rename(columns=self.index_name_dict)
        pb_lf = pb_lf[self.index_list].rename(columns=self.index_name_dict)
        div_yield = div_yield[self.index_list].rename(columns=self.index_name_dict)
        pe_ttm = pe_ttm[(pe_ttm.index >= self.start_date) & (pe_ttm.index <= self.end_date)]
        pb_lf = pb_lf[(pb_lf.index >= self.start_date) & (pb_lf.index <= self.end_date)]
        div_yield = div_yield[(div_yield.index >= self.start_date) & (div_yield.index <= self.end_date)]

        mv_w = w.wsd(",".join(self.index_list[:3]), "mkt_cap_ard", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        mv_w['index'] = mv_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        mv_w = mv_w.set_index('index').sort_index()
        best_np_ntm_w = w.wsd(",".join(self.index_list[:3]), "west_netprofit_FTM", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        best_np_ntm_w['index'] = best_np_ntm_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        best_np_ntm_w = best_np_ntm_w.set_index('index').sort_index()
        best_pe_ttm_w = mv_w / best_np_ntm_w
        best_pb_lf_w = pd.DataFrame(index=best_pe_ttm_w.index, columns=best_pe_ttm_w.columns)
        best_div_yield_w = pd.DataFrame(index=best_pe_ttm_w.index, columns=best_pe_ttm_w.columns)
        best_pe_ttm = self.overseas_index_best[['bzzsdm', 'jyrq', 'best_pe_ratio']]
        best_pe_ttm['jyrq'] = best_pe_ttm['jyrq'].astype(str)
        best_pe_ttm = best_pe_ttm.pivot(index='jyrq', columns='bzzsdm', values='best_pe_ratio').sort_index()
        best_pb_lf = self.overseas_index_best[['bzzsdm', 'jyrq', 'best_px_bps_ratio']]
        best_pb_lf['jyrq'] = best_pb_lf['jyrq'].astype(str)
        best_pb_lf = best_pb_lf.pivot(index='jyrq', columns='bzzsdm', values='best_px_bps_ratio').sort_index()
        best_div_yield = self.overseas_index_best[['bzzsdm', 'jyrq', 'best_div_yld']]
        best_div_yield['jyrq'] = best_div_yield['jyrq'].astype(str)
        best_div_yield = best_div_yield.pivot(index='jyrq', columns='bzzsdm', values='best_div_yld').sort_index()
        best_pe_ttm = best_pe_ttm_w.merge(best_pe_ttm, left_index=True, right_index=True, how='right').sort_index()
        best_pb_lf = best_pb_lf_w.merge(best_pb_lf, left_index=True, right_index=True, how='right').sort_index()
        best_div_yield = best_div_yield_w.merge(best_div_yield, left_index=True, right_index=True, how='right').sort_index()
        best_pe_ttm = best_pe_ttm[best_pe_ttm.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        best_pb_lf = best_pb_lf[best_pb_lf.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        best_div_yield = best_div_yield[best_div_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        best_pe_ttm = best_pe_ttm[self.index_list].rename(columns=self.index_name_dict)
        best_pb_lf = best_pb_lf[self.index_list].rename(columns=self.index_name_dict)
        best_div_yield = best_div_yield[self.index_list].rename(columns=self.index_name_dict)
        best_pe_ttm = best_pe_ttm[(best_pe_ttm.index >= self.start_date) & (best_pe_ttm.index <= self.end_date)]
        best_pb_lf = best_pb_lf[(best_pb_lf.index >= self.start_date) & (best_pb_lf.index <= self.end_date)]
        best_div_yield = best_div_yield[(best_div_yield.index >= self.start_date) & (best_div_yield.index <= self.end_date)]

        pe_ttm_1y, pe_ttm_3y, pe_ttm_5y, pe_ttm_10y, \
        pb_lf_1y, pb_lf_3y, pb_lf_5y, pb_lf_10y, \
        div_yield_1y, div_yield_3y, div_yield_5y, div_yield_10y, \
        best_pe_ttm_1y, best_pe_ttm_3y, best_pe_ttm_5y, best_pe_ttm_10y, \
        best_pb_lf_1y, best_pb_lf_3y, best_pb_lf_5y, best_pb_lf_10y, \
        best_div_yield_1y, best_div_yield_3y, best_div_yield_5y, best_div_yield_10y = \
        pe_ttm.copy(deep=True), pe_ttm.copy(deep=True), pe_ttm.copy(deep=True), pe_ttm.copy(deep=True), \
        pb_lf.copy(deep=True), pb_lf.copy(deep=True), pb_lf.copy(deep=True), pb_lf.copy(deep=True), \
        div_yield.copy(deep=True), div_yield.copy(deep=True), div_yield.copy(deep=True), div_yield.copy(deep=True), \
        best_pe_ttm.copy(deep=True), best_pe_ttm.copy(deep=True), best_pe_ttm.copy(deep=True), best_pe_ttm.copy(deep=True), \
        best_pb_lf.copy(deep=True), best_pb_lf.copy(deep=True), best_pb_lf.copy(deep=True), best_pb_lf.copy(deep=True), \
        best_div_yield.copy(deep=True), best_div_yield.copy(deep=True), best_div_yield.copy(deep=True), best_div_yield.copy(deep=True)
        pe_ttm['IDX'] = range(len(pe_ttm))
        pb_lf['IDX'] = range(len(pb_lf))
        div_yield['IDX'] = range(len(div_yield))
        best_pe_ttm['IDX'] = range(len(best_pe_ttm))
        best_pb_lf['IDX'] = range(len(best_pb_lf))
        best_div_yield['IDX'] = range(len(best_div_yield))
        for col in list(pe_ttm.columns)[:-1]:
            print(col)
            pe_ttm_1y[col] = pe_ttm['IDX'].rolling(250 * 1).apply(lambda x: quantile_definition(x, col, pe_ttm))
            pe_ttm_3y[col] = pe_ttm['IDX'].rolling(250 * 3).apply(lambda x: quantile_definition(x, col, pe_ttm))
            pe_ttm_5y[col] = pe_ttm['IDX'].rolling(250 * 5).apply(lambda x: quantile_definition(x, col, pe_ttm))
            pe_ttm_10y[col] = pe_ttm['IDX'].rolling(250 * 10).apply(lambda x: quantile_definition(x, col, pe_ttm))
            pb_lf_1y[col] = pb_lf['IDX'].rolling(250 * 1).apply(lambda x: quantile_definition(x, col, pb_lf))
            pb_lf_3y[col] = pb_lf['IDX'].rolling(250 * 3).apply(lambda x: quantile_definition(x, col, pb_lf))
            pb_lf_5y[col] = pb_lf['IDX'].rolling(250 * 5).apply(lambda x: quantile_definition(x, col, pb_lf))
            pb_lf_10y[col] = pb_lf['IDX'].rolling(250 * 10).apply(lambda x: quantile_definition(x, col, pb_lf))
            div_yield_1y[col] = div_yield['IDX'].rolling(250 * 1).apply(lambda x: quantile_definition(x, col, div_yield))
            div_yield_3y[col] = div_yield['IDX'].rolling(250 * 3).apply(lambda x: quantile_definition(x, col, div_yield))
            div_yield_5y[col] = div_yield['IDX'].rolling(250 * 5).apply(lambda x: quantile_definition(x, col, div_yield))
            div_yield_10y[col] = div_yield['IDX'].rolling(250 * 10).apply(lambda x: quantile_definition(x, col, div_yield))
            best_pe_ttm_1y[col] = best_pe_ttm['IDX'].rolling(250 * 1).apply(lambda x: quantile_definition(x, col, best_pe_ttm))
            best_pe_ttm_3y[col] = best_pe_ttm['IDX'].rolling(250 * 3).apply(lambda x: quantile_definition(x, col, best_pe_ttm))
            best_pe_ttm_5y[col] = best_pe_ttm['IDX'].rolling(250 * 5).apply(lambda x: quantile_definition(x, col, best_pe_ttm))
            best_pe_ttm_10y[col] = best_pe_ttm['IDX'].rolling(250 * 10).apply(lambda x: quantile_definition(x, col, best_pe_ttm))
            best_pb_lf_1y[col] = best_pb_lf['IDX'].rolling(250 * 1).apply(lambda x: quantile_definition(x, col, best_pb_lf))
            best_pb_lf_3y[col] = best_pb_lf['IDX'].rolling(250 * 3).apply(lambda x: quantile_definition(x, col, best_pb_lf))
            best_pb_lf_5y[col] = best_pb_lf['IDX'].rolling(250 * 5).apply(lambda x: quantile_definition(x, col, best_pb_lf))
            best_pb_lf_10y[col] = best_pb_lf['IDX'].rolling(250 * 10).apply(lambda x: quantile_definition(x, col, best_pb_lf))
            best_div_yield_1y[col] = best_div_yield['IDX'].rolling(250 * 1).apply(lambda x: quantile_definition(x, col, best_div_yield))
            best_div_yield_3y[col] = best_div_yield['IDX'].rolling(250 * 3).apply(lambda x: quantile_definition(x, col, best_div_yield))
            best_div_yield_5y[col] = best_div_yield['IDX'].rolling(250 * 5).apply(lambda x: quantile_definition(x, col, best_div_yield))
            best_div_yield_10y[col] = best_div_yield['IDX'].rolling(250 * 10).apply(lambda x: quantile_definition(x, col, best_div_yield))
        pe_ttm = pe_ttm.drop('IDX', axis=1)
        pb_lf = pb_lf.drop('IDX', axis=1)
        div_yield = div_yield.drop('IDX', axis=1)
        best_pe_ttm = best_pe_ttm.drop('IDX', axis=1)
        best_pb_lf = best_pb_lf.drop('IDX', axis=1)
        best_div_yield = best_div_yield.drop('IDX', axis=1)
        pe_ttm = df_add_info(pe_ttm, 'PE_TTM')
        pb_lf = df_add_info(pb_lf, 'PB_LF')
        div_yield = df_add_info(div_yield, 'DIV_YIELD')
        best_pe_ttm = df_add_info(best_pe_ttm, 'BEST_PE_TTM')
        best_pb_lf = df_add_info(best_pb_lf, 'BEST_PB_LF')
        best_div_yield = df_add_info(best_div_yield, 'BEST_DIV_YIELD')
        pe_ttm_1y = df_add_info(pe_ttm_1y, 'PE_TTM（近一年分位水平）')
        pe_ttm_3y = df_add_info(pe_ttm_3y, 'PE_TTM（近三年分位水平）')
        pe_ttm_5y = df_add_info(pe_ttm_5y, 'PE_TTM（近五年分位水平）')
        pe_ttm_10y = df_add_info(pe_ttm_10y, 'PE_TTM（近十年分位水平）')
        pb_lf_1y = df_add_info(pb_lf_1y, 'PB_LF（近一年分位水平）')
        pb_lf_3y = df_add_info(pb_lf_3y, 'PB_LF（近三年分位水平）')
        pb_lf_5y = df_add_info(pb_lf_5y, 'PB_LF（近五年分位水平）')
        pb_lf_10y = df_add_info(pb_lf_10y, 'PB_LF（近十年分位水平）')
        div_yield_1y = df_add_info(div_yield_1y, 'DIV_YIELD_TTM（近一年分位水平）')
        div_yield_3y = df_add_info(div_yield_3y, 'DIV_YIELD_TTM（近三年分位水平）')
        div_yield_5y = df_add_info(div_yield_5y, 'DIV_YIELD_TTM（近五年分位水平）')
        div_yield_10y = df_add_info(div_yield_10y, 'DIV_YIELD_TTM（近十年分位水平）')
        best_pe_ttm_1y = df_add_info(best_pe_ttm_1y, 'BEST_PE_TTM（近一年分位水平）')
        best_pe_ttm_3y = df_add_info(best_pe_ttm_3y, 'BEST_PE_TTM（近三年分位水平）')
        best_pe_ttm_5y = df_add_info(best_pe_ttm_5y, 'BEST_PE_TTM（近五年分位水平）')
        best_pe_ttm_10y = df_add_info(best_pe_ttm_10y, 'BEST_PE_TTM（近十年分位水平）')
        best_pb_lf_1y = df_add_info(best_pb_lf_1y, 'BEST_PB_LF（近一年分位水平）')
        best_pb_lf_3y = df_add_info(best_pb_lf_3y, 'BEST_PB_LF（近三年分位水平）')
        best_pb_lf_5y = df_add_info(best_pb_lf_5y, 'BEST_PB_LF（近五年分位水平）')
        best_pb_lf_10y = df_add_info(best_pb_lf_10y, 'BEST_PB_LF（近十年分位水平）')
        best_div_yield_1y = df_add_info(best_div_yield_1y, 'BEST_DIV_YIELD_TTM（近一年分位水平）')
        best_div_yield_3y = df_add_info(best_div_yield_3y, 'BEST_DIV_YIELD_TTM（近三年分位水平）')
        best_div_yield_5y = df_add_info(best_div_yield_5y, 'BEST_DIV_YIELD_TTM（近五年分位水平）')
        best_div_yield_10y = df_add_info(best_div_yield_10y, 'BEST_DIV_YIELD_TTM（近十年分位水平）')

        valuation = pd.concat([pe_ttm, pe_ttm_1y, pe_ttm_3y, pe_ttm_5y, pe_ttm_10y,
                               pb_lf, pb_lf_1y, pb_lf_3y, pb_lf_5y, pb_lf_10y,
                               div_yield, div_yield_1y, div_yield_3y, div_yield_5y, div_yield_10y,
                               best_pe_ttm, best_pe_ttm_1y, best_pe_ttm_3y, best_pe_ttm_5y, best_pe_ttm_10y,
                               best_pb_lf, best_pb_lf_1y, best_pb_lf_3y, best_pb_lf_5y, best_pb_lf_10y,
                               best_div_yield, best_div_yield_1y, best_div_yield_3y, best_div_yield_5y, best_div_yield_10y], axis=1)
        valuation.index = map(lambda x: datetime.strptime(x, '%Y%m%d').date(), valuation.index)
        return valuation

    def finance(self):
        eps_ttm_w = w.wsd(",".join(self.index_list[:3]), "eps_ttm", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        eps_ttm_w['index'] = eps_ttm_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        eps_ttm_w = eps_ttm_w.set_index('index').sort_index()
        eps_ttm = self.overseas_index_finance[['bzzsdm', 'jyrq', 'trail_12m_eps_bef_xo_item']]
        eps_ttm['jyrq'] = eps_ttm['jyrq'].astype(str)
        eps_ttm = eps_ttm.pivot(index='jyrq', columns='bzzsdm', values='trail_12m_eps_bef_xo_item').sort_index()
        eps_ttm = eps_ttm_w.merge(eps_ttm, left_index=True, right_index=True, how='right').sort_index()
        eps_ttm = eps_ttm[eps_ttm.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        eps_ttm = eps_ttm[self.index_list].rename(columns=self.index_name_dict)
        eps_ttm = eps_ttm[(eps_ttm.index >= self.start_date) & (eps_ttm.index <= self.end_date)]

        best_eps_ttm_w = w.wsd(",".join(self.index_list[:3]), "west_eps_FTM", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        best_eps_ttm_w['index'] = best_eps_ttm_w['index'].apply(lambda x: x.strftime('%Y%m%d'))
        best_eps_ttm_w = best_eps_ttm_w.set_index('index').sort_index()
        best_eps_ttm = self.overseas_index_best[['bzzsdm', 'jyrq', 'best_eps']]
        best_eps_ttm['jyrq'] = best_eps_ttm['jyrq'].astype(str)
        best_eps_ttm = best_eps_ttm.pivot(index='jyrq', columns='bzzsdm', values='best_eps').sort_index()
        best_eps_ttm = best_eps_ttm_w.merge(best_eps_ttm, left_index=True, right_index=True, how='right').sort_index()
        best_eps_ttm = best_eps_ttm[best_eps_ttm.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())].sort_index().fillna(method='ffill')
        best_eps_ttm = best_eps_ttm[self.index_list].rename(columns=self.index_name_dict)
        best_eps_ttm = best_eps_ttm[(best_eps_ttm.index >= self.start_date) & (best_eps_ttm.index <= self.end_date)]

        eps_ttm_mom_1m = eps_ttm.pct_change(20)
        eps_ttm_mom_1q = eps_ttm.pct_change(60)
        eps_ttm_yoy = eps_ttm.pct_change(250)

        best_eps_ttm_mom_1m = best_eps_ttm.pct_change(20)
        best_eps_ttm_mom_1q = best_eps_ttm.pct_change(60)
        best_eps_ttm_yoy = best_eps_ttm.pct_change(250)

        eps_ttm = df_add_info(eps_ttm, 'EPS_TTM')
        eps_ttm_mom_1m = df_add_info(eps_ttm_mom_1m, 'EPS_TTM（月度环比）')
        eps_ttm_mom_1q = df_add_info(eps_ttm_mom_1q, 'EPS_TTM（季度环比）')
        eps_ttm_yoy = df_add_info(eps_ttm_yoy, 'EPS_TTM（同比）')
        best_eps_ttm = df_add_info(best_eps_ttm, 'BEST_EPS_TTM')
        best_eps_ttm_mom_1m = df_add_info(best_eps_ttm_mom_1m, 'BEST_EPS_TTM（月度环比）')
        best_eps_ttm_mom_1q = df_add_info(best_eps_ttm_mom_1q, 'BEST_EPS_TTM（季度环比）')
        best_eps_ttm_yoy = df_add_info(best_eps_ttm_yoy, 'BEST_EPS_TTM（同比）')

        finance = pd.concat([eps_ttm, eps_ttm_mom_1m, eps_ttm_mom_1q, eps_ttm_yoy,
                             best_eps_ttm, best_eps_ttm_mom_1m, best_eps_ttm_mom_1q, best_eps_ttm_yoy], axis=1)
        finance.index = map(lambda x: datetime.strptime(x, '%Y%m%d').date(), finance.index)
        return finance

    def get_all(self):
        index = self.index()
        turnover = self.turnover()
        valuation = self.valuation()
        finance = self.finance()

        filename = '{0}overseas_overview.xlsx'.format(self.data_path)
        app = xlwings.App(visible=False)
        wookbook = app.books.open(filename)
        sheet_names = [wookbook.sheets[i].name for i in range(len(wookbook.sheets))]
        index_wooksheet = wookbook.sheets['指数']
        index_wooksheet.clear()
        index_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = index
        turnover_wooksheet = wookbook.sheets['成交']
        turnover_wooksheet.clear()
        turnover_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = turnover
        valuation_wooksheet = wookbook.sheets['估值']
        valuation_wooksheet.clear()
        valuation_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = valuation
        finance_wooksheet = wookbook.sheets['财务']
        finance_wooksheet.clear()
        finance_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = finance
        wookbook.save(filename)
        wookbook.close()
        app.quit()
        return


if __name__ == '__main__':
    start_date = '20070101'
    end_date = '20240126'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/overseas_overview/'
    OverseasOverview(start_date, end_date, data_path).get_all()