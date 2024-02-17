# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
import numpy as np
import pandas as pd
import xlwings


def get_date(start_date, end_date):
    calendar_df = HBDB().read_cal(start_date, end_date)
    calendar_df = calendar_df.rename(columns={'jyrq': 'CALENDAR_DATE', 'sfjj': 'IS_OPEN', 'sfzm': 'IS_WEEK_END', 'sfym': 'IS_MONTH_END'})
    calendar_df['CALENDAR_DATE'] = calendar_df['CALENDAR_DATE'].astype(str)
    calendar_df = calendar_df.sort_values('CALENDAR_DATE')
    calendar_df['IS_OPEN'] = calendar_df['IS_OPEN'].astype(int).replace({0: 1, 1: 0})
    calendar_df['YEAR_MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[:6])
    calendar_df['MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:6])
    calendar_df['MONTH_DAY'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:])
    calendar_df = calendar_df[(calendar_df['CALENDAR_DATE'] >= start_date) & (calendar_df['CALENDAR_DATE'] <= end_date)]
    trade_df = calendar_df[calendar_df['IS_OPEN'] == 1].rename(columns={'CALENDAR_DATE': 'TRADE_DATE'})
    trade_df = trade_df[(trade_df['TRADE_DATE'] >= start_date) & (trade_df['TRADE_DATE'] <= end_date)]
    report_df = calendar_df.drop_duplicates('YEAR_MONTH', keep='last').rename(columns={'CALENDAR_DATE': 'REPORT_DATE'})
    report_df = report_df[report_df['MONTH_DAY'].isin(['0331', '0630', '0930', '1231'])]
    report_df = report_df[(report_df['REPORT_DATE'] >= start_date) & (report_df['REPORT_DATE'] <= end_date)]
    report_trade_df = calendar_df[calendar_df['IS_OPEN'] == 1].rename(columns={'CALENDAR_DATE': 'TRADE_DATE'})
    report_trade_df = report_trade_df.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
    report_trade_df = report_trade_df[report_trade_df['MONTH'].isin(['03', '06', '09', '12'])]
    report_trade_df = report_trade_df[(report_trade_df['TRADE_DATE'] >= start_date) & (report_trade_df['TRADE_DATE'] <= end_date)]
    calendar_trade_df = calendar_df[['CALENDAR_DATE']].merge(trade_df[['TRADE_DATE']], left_on=['CALENDAR_DATE'], right_on=['TRADE_DATE'], how='left')
    calendar_trade_df['TRADE_DATE'] = calendar_trade_df['TRADE_DATE'].fillna(method='ffill')
    calendar_trade_df = calendar_trade_df[(calendar_trade_df['TRADE_DATE'] >= start_date) & (calendar_trade_df['TRADE_DATE'] <= end_date)]
    return calendar_df, report_df, trade_df, report_trade_df, calendar_trade_df


def quantile_definition(idxs, col, daily_df):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    if len(part_df.dropna(subset=[col])) < len(part_df):
        return np.nan
    else:
        q = (1.0 - np.count_nonzero(part_df[col].iloc[-1] <= part_df[col]) / len(part_df))
        return q


class IndexTracking:
    def __init__(self, start_date, end_date, report_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date
        self.data_path = data_path
        # 日历
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)
        self.dates()

    def dates(self):
        self.trade_df = self.trade_df.sort_values('TRADE_DATE')
        self.date_1w = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-5]
        self.date_1m = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-20 * 1]
        self.date_3m = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-20 * 3]
        self.date_6m = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-20 * 6]
        self.date_1y = self.trade_df[self.trade_df['TRADE_DATE'] < self.end_date]['TRADE_DATE'].iloc[-250]
        self.date_2023 = self.trade_df[self.trade_df['TRADE_DATE'] < '20230101']['TRADE_DATE'].iloc[-1]
        self.date_2022 = self.trade_df[self.trade_df['TRADE_DATE'] < '20220101']['TRADE_DATE'].iloc[-1]
        self.date_2021 = self.trade_df[self.trade_df['TRADE_DATE'] < '20210101']['TRADE_DATE'].iloc[-1]
        self.date_2015 = self.trade_df[self.trade_df['TRADE_DATE'] < '20150101']['TRADE_DATE'].iloc[-1]
        return

    def index(self):
        index_list = ['000300', '000905', '000852', '399303', '881001']
        index_name_dict = {'000300': '沪深300', '000905': '中证500', '000852': '中证1000', '399303': '国证2000', '881001': '万得全A'}
        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, index_list)
        index = index[['zqdm', 'jyrq', 'spjg']]
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index['TRADE_DATE'] = index['TRADE_DATE'].astype(str)
        index = index[index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        index = index[(index['TRADE_DATE'] >= self.start_date) & (index['TRADE_DATE'] <= self.end_date)]
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index = index.replace(0.0, np.nan)
        index = index[index_list].rename(columns=index_name_dict)

        close = index.copy(deep=True)
        close = close.T.reset_index()
        close['TYPE'] = '收盘价'
        close = close.set_index(['TYPE', 'INDEX_SYMBOL']).T

        close_2015 = index[index.index > self.date_2015]
        close_2015 = close_2015 / close_2015.iloc[0]
        close_2015 = close_2015.T.reset_index()
        close_2015['TYPE'] = '收盘价（归一化）'
        close_2015 = close_2015.set_index(['TYPE', 'INDEX_SYMBOL']).T

        close_relative = index.copy(deep=True)
        close_relative['沪深300/中证1000'] = close_relative['沪深300'] / close_relative['中证1000']
        close_relative = close_relative[['沪深300/中证1000']]
        close_relative = close_relative.T.reset_index()
        close_relative['TYPE'] = '比值'
        close_relative = close_relative.set_index(['TYPE', 'INDEX_SYMBOL']).T

        ret_1w = index.pct_change(5)
        ret_1w = ret_1w.T.reset_index()
        ret_1w['TYPE'] = '近一周'
        ret_1w = ret_1w.set_index(['TYPE', 'INDEX_SYMBOL']).T

        ret_1m = index.pct_change(20 * 1)
        ret_1m = ret_1m.T.reset_index()
        ret_1m['TYPE'] = '近一月'
        ret_1m = ret_1m.set_index(['TYPE', 'INDEX_SYMBOL']).T

        ret_3m = index.pct_change(20 * 3)
        ret_3m = ret_3m.T.reset_index()
        ret_3m['TYPE'] = '近三月'
        ret_3m = ret_3m.set_index(['TYPE', 'INDEX_SYMBOL']).T

        ret_6m = index.pct_change(20 * 6)
        ret_6m = ret_6m.T.reset_index()
        ret_6m['TYPE'] = '近六月'
        ret_6m = ret_6m.set_index(['TYPE', 'INDEX_SYMBOL']).T

        ret_1y = index.pct_change(250)
        ret_1y = ret_1y.T.reset_index()
        ret_1y['TYPE'] = '近一年'
        ret_1y = ret_1y.set_index(['TYPE', 'INDEX_SYMBOL']).T

        index_2023 = index[index.index >= self.date_2023]
        ret_2023 = index_2023 / index_2023.iloc[0] - 1
        ret_2023 = ret_2023.T.reset_index()
        ret_2023['TYPE'] = '2023年以来'
        ret_2023 = ret_2023.set_index(['TYPE', 'INDEX_SYMBOL']).T

        index_2022 = index[index.index >= self.date_2022]
        ret_2022 = index_2022 / index_2022.iloc[0] - 1
        ret_2022 = ret_2022.T.reset_index()
        ret_2022['TYPE'] = '2022年以来'
        ret_2022 = ret_2022.set_index(['TYPE', 'INDEX_SYMBOL']).T

        index_2021 = index[index.index >= self.date_2021]
        ret_2021 = index_2021 / index_2021.iloc[0] - 1
        ret_2021 = ret_2021.T.reset_index()
        ret_2021['TYPE'] = '2021年以来'
        ret_2021 = ret_2021.set_index(['TYPE', 'INDEX_SYMBOL']).T

        index_2015 = index[index.index >= self.date_2015]
        ret_2015 = index_2015 / index_2015.iloc[0] - 1
        ret_2015 = ret_2015.T.reset_index()
        ret_2015['TYPE'] = '2015年以来'
        ret_2015 = ret_2015.set_index(['TYPE', 'INDEX_SYMBOL']).T

        index = pd.concat([close, close_2015, close_relative, ret_1w, ret_1m, ret_3m, ret_6m, ret_1y, ret_2023, ret_2022, ret_2021, ret_2015], axis=1)
        index.index = map(lambda x: datetime.strptime(x, '%Y%m%d').date(), close.index)
        return index

    def valuation(self):
        index_list = ['000300', '000905', '000852', '399303', '881001']
        index_name_dict = {'000300': '沪深300', '000905': '中证500', '000852': '中证1000', '399303': '国证2000', '881001': '万得全A'}
        valuation = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, index_list)
        valuation = valuation[['zqdm', 'jyrq', 'pe']]
        valuation = valuation.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'pe': 'PE（TTM）'})
        valuation['TRADE_DATE'] = valuation['TRADE_DATE'].astype(str)
        valuation = valuation[valuation['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        valuation = valuation[(valuation['TRADE_DATE'] >= self.start_date) & (valuation['TRADE_DATE'] <= self.end_date)]
        valuation = valuation.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='PE（TTM）').sort_index()
        valuation = valuation.replace(0.0, np.nan)
        valuation = valuation[index_list].rename(columns=index_name_dict)
        valuation['IDX'] = range(len(valuation))

        pettm = valuation.copy(deep=True).drop('IDX', axis=1)
        pettm = pettm.T.reset_index()
        pettm['TYPE'] = 'PE（TTM）'
        pettm = pettm.set_index(['TYPE', 'INDEX_SYMBOL']).T

        pettm_relative = valuation.copy(deep=True)
        pettm_relative['沪深300PE（TTM）/中证1000PE（TTM）'] = pettm_relative['沪深300'] / pettm_relative['中证1000']
        pettm_relative = pettm_relative[['沪深300PE（TTM）/中证1000PE（TTM）']]
        pettm_relative = pettm_relative.T.reset_index()
        pettm_relative['TYPE'] = '比值'
        pettm_relative = pettm_relative.set_index(['TYPE', 'INDEX_SYMBOL']).T

        pettm_q1y = valuation.copy(deep=True).drop('IDX', axis=1)
        for col in list(pettm_q1y.columns):
            pettm_q1y[col] = valuation['IDX'].rolling(250 * 1).apply(lambda x: quantile_definition(x, col, valuation))
        pettm_q1y = pettm_q1y.T.reset_index()
        pettm_q1y['TYPE'] = '近一年分位水平'
        pettm_q1y = pettm_q1y.set_index(['TYPE', 'INDEX_SYMBOL']).T

        pettm_q3y = valuation.copy(deep=True).drop('IDX', axis=1)
        for col in list(pettm_q3y.columns):
            pettm_q3y[col] = valuation['IDX'].rolling(250 * 3).apply(lambda x: quantile_definition(x, col, valuation))
        pettm_q3y = pettm_q3y.T.reset_index()
        pettm_q3y['TYPE'] = '近三年分位水平'
        pettm_q3y = pettm_q3y.set_index(['TYPE', 'INDEX_SYMBOL']).T

        pettm_q5y = valuation.copy(deep=True).drop('IDX', axis=1)
        for col in list(pettm_q5y.columns):
            pettm_q5y[col] = valuation['IDX'].rolling(250 * 5).apply(lambda x: quantile_definition(x, col, valuation))
        pettm_q5y = pettm_q5y.T.reset_index()
        pettm_q5y['TYPE'] = '近五年分位水平'
        pettm_q5y = pettm_q5y.set_index(['TYPE', 'INDEX_SYMBOL']).T

        valuation = pd.concat([pettm, pettm_relative, pettm_q1y, pettm_q3y, pettm_q5y], axis=1)
        valuation.index = map(lambda x: datetime.strptime(x, '%Y%m%d').date(), valuation.index)
        return valuation

    def get_all(self):
        index = self.index()
        valuation = self.valuation()

        filename = '{0}index_tracking.xlsx'.format(self.data_path)
        app = xlwings.App(visible=False)
        wookbook = app.books.open(filename)
        sheet_names = [wookbook.sheets[i].name for i in range(len(wookbook.sheets))]
        index_wooksheet = wookbook.sheets['指数']
        index_wooksheet.clear()
        index_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = index
        valuation_wooksheet = wookbook.sheets['估值']
        valuation_wooksheet.clear()
        valuation_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = valuation
        wookbook.save(filename)
        wookbook.close()
        app.quit()
        return


if __name__ == '__main__':
    start_date = '20070101'
    end_date = '20230922'
    report_date = '20230630'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/index_tracking/'
    IndexTracking(start_date, end_date, report_date, data_path).get_all()