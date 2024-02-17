# -*- coding: utf-8 -*-

from datetime import datetime
from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
import numpy as np
import pandas as pd
import os

from WindPy import w
w.start()  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
w.isconnected()  # 判断WindPy是否已经登录成功

import warnings
warnings.filterwarnings("ignore")


def get_date(start_date, end_date):
    calendar_df = HBDB().read_cal_nodate()
    calendar_df = calendar_df.rename(columns={'jyrq': 'CALENDAR_DATE', 'sfjj': 'IS_OPEN', 'sfzm': 'IS_WEEK_END', 'sfym': 'IS_MONTH_END'})
    calendar_df['CALENDAR_DATE'] = calendar_df['CALENDAR_DATE'].astype(str)
    calendar_df = calendar_df.sort_values('CALENDAR_DATE')
    calendar_df['IS_OPEN'] = calendar_df['IS_OPEN'].astype(int).replace({0: 1, 1: 0})
    calendar_df['YEAR_MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[:6])
    calendar_df['MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:6])
    calendar_df['MONTH_DAY'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:])
    trade_df = calendar_df[calendar_df['IS_OPEN'] == 1].rename(columns={'CALENDAR_DATE': 'TRADE_DATE'})
    report_df = calendar_df.drop_duplicates('YEAR_MONTH', keep='last').rename(columns={'CALENDAR_DATE': 'REPORT_DATE'})
    report_df = report_df[report_df['MONTH_DAY'].isin(['0331', '0630', '0930', '1231'])]
    report_trade_df = calendar_df[calendar_df['IS_OPEN'] == 1].rename(columns={'CALENDAR_DATE': 'TRADE_DATE'})
    report_trade_df = report_trade_df.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
    report_trade_df = report_trade_df[report_trade_df['MONTH'].isin(['03', '06', '09', '12'])]
    calendar_trade_df = calendar_df[['CALENDAR_DATE']].merge(trade_df[['TRADE_DATE']], left_on=['CALENDAR_DATE'], right_on=['TRADE_DATE'], how='left')
    calendar_trade_df['TRADE_DATE'] = calendar_trade_df['TRADE_DATE'].fillna(method='ffill')
    calendar_df = calendar_df[(calendar_df['CALENDAR_DATE'] >= start_date) & (calendar_df['CALENDAR_DATE'] <= end_date)]
    trade_df = trade_df[(trade_df['TRADE_DATE'] >= start_date) & (trade_df['TRADE_DATE'] <= end_date)]
    report_df = report_df[(report_df['REPORT_DATE'] >= start_date) & (report_df['REPORT_DATE'] <= end_date)]
    report_trade_df = report_trade_df[(report_trade_df['TRADE_DATE'] >= start_date) & (report_trade_df['TRADE_DATE'] <= end_date)]
    calendar_trade_df = calendar_trade_df[(calendar_trade_df['TRADE_DATE'] >= start_date) & (calendar_trade_df['TRADE_DATE'] <= end_date)]
    return calendar_df, trade_df, report_df, report_trade_df, calendar_trade_df


def get_industry_info():
    industry_info = HBDB().read_industry_info()
    industry_info = industry_info.rename(columns={'flmc': 'INDUSTRY_NAME', 'zsdm': 'INDUSTRY_ID', 'hyhfbz': 'INDUSTRY_VERSION', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    industry_info = industry_info.dropna(subset=['BEGIN_DATE'])
    industry_info['END_DATE'] = industry_info['END_DATE'].replace('', np.nan).fillna('20990101')
    industry_info['BEGIN_DATE'] = industry_info['BEGIN_DATE'].apply(lambda x: datetime.strptime(x, '%Y/%m/%d').strftime('%Y%m%d') if '/' in x else x)
    industry_info['END_DATE'] = industry_info['END_DATE'].apply(lambda x: datetime.strptime(x, '%Y/%m/%d').strftime('%Y%m%d') if '/' in x else x)
    industry_info['BEGIN_DATE'] = industry_info['BEGIN_DATE'].astype(int).astype(str)
    industry_info['END_DATE'] = industry_info['END_DATE'].astype(int).astype(str)
    industry_info['INDUSTRY_VERSION'] = industry_info['INDUSTRY_VERSION'].astype(int)
    industry_info['INDUSTRY_TYPE'] = industry_info['INDUSTRY_TYPE'].astype(int)
    industry_info['IS_NEW'] = industry_info['IS_NEW'].astype(int)
    industry_info = industry_info[industry_info['INDUSTRY_VERSION'] == 3]
    return industry_info


def get_industry_symbol():
    industry_symbol = HBDB().read_industry_symbol()
    industry_symbol = industry_symbol.rename(columns={'hyhfbz': 'INDUSTRY_VERSION', 'fldm': 'INDUSTRY_ID', 'flmc': 'INDUSTRY_NAME', 'zsdm': 'INDEX_SYMBOL', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    industry_symbol = industry_symbol.dropna(subset=['BEGIN_DATE'])
    industry_symbol['END_DATE'] = industry_symbol['END_DATE'].replace('', np.nan).fillna('20990101')
    industry_symbol['BEGIN_DATE'] = industry_symbol['BEGIN_DATE'].astype(int).astype(str)
    industry_symbol['END_DATE'] = industry_symbol['END_DATE'].astype(int).astype(str)
    industry_symbol['INDUSTRY_VERSION'] = industry_symbol['INDUSTRY_VERSION'].astype(int)
    industry_symbol['INDUSTRY_TYPE'] = industry_symbol['INDUSTRY_TYPE'].astype(int)
    industry_symbol['IS_NEW'] = industry_symbol['IS_NEW'].astype(int)
    industry_symbol = industry_symbol[industry_symbol['INDUSTRY_VERSION'] == 3]
    return industry_symbol


def get_stock_industry():
    stock_industry = HBDB().read_stock_industry()
    stock_industry.to_hdf('{0}stock_industry.hdf'.format(data_path), key='table', mode='w')
    stock_industry = pd.read_hdf('{0}stock_industry.hdf'.format(data_path), key='table')
    stock_industry = stock_industry.rename(columns={'zqdm': 'TICKER_SYMBOL', 'flmc': 'INDUSTRY_NAME', 'fldm': 'INDUSTRY_ID', 'hyhfbz': 'INDUSTRY_VERSION', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    stock_industry = stock_industry.dropna(subset=['BEGIN_DATE'])
    stock_industry['END_DATE'] = stock_industry['END_DATE'].fillna('20990101')
    stock_industry['BEGIN_DATE'] = stock_industry['BEGIN_DATE'].astype(int).astype(str)
    stock_industry['END_DATE'] = stock_industry['END_DATE'].astype(int).astype(str)
    stock_industry['INDUSTRY_VERSION'] = stock_industry['INDUSTRY_VERSION'].astype(int)
    stock_industry['INDUSTRY_TYPE'] = stock_industry['INDUSTRY_TYPE'].astype(int)
    stock_industry['IS_NEW'] = stock_industry['IS_NEW'].astype(int)
    stock_industry = stock_industry[stock_industry['INDUSTRY_VERSION'] == 2]
    stock_industry = stock_industry.loc[stock_industry['TICKER_SYMBOL'].str.len() == 6]
    stock_industry = stock_industry.loc[stock_industry['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
    return stock_industry


def quantile_definition(idxs, col, daily_df):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    q = (1.0 - np.count_nonzero(part_df[col].iloc[-1] < part_df[col]) / len(part_df)) if len(part_df[col].dropna()) != 0 else np.nan
    return q


class Crowding:
    def __init__(self, start_date, end_date, report_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.data_path = data_path

        self.index_list = ['000300.SH', '000905.SH', '000852.SH', '932000.CSI', 'other', '8841431.WI',
                           '399371.SZ', '399370.SZ', 'value', 'growth',
                           '801010.SI', '801030.SI', '801040.SI', '801050.SI', '801080.SI',
                           '801110.SI', '801120.SI', '801130.SI', '801140.SI', '801150.SI',
                           '801160.SI', '801170.SI', '801180.SI', '801200.SI', '801210.SI',
                           '801230.SI', '801710.SI', '801720.SI', '801730.SI', '801740.SI',
                           '801750.SI', '801760.SI', '801770.SI', '801780.SI', '801790.SI',
                           '801880.SI', '801890.SI', '801950.SI', '801960.SI', '801970.SI',
                           '801980.SI',
                           'guangfu', 'donglidianchi', 'qiche', 'bandaoti']
        self.index_dict = {
            '000300.SH': '沪深300', '000905.SH': '中证500', '000852.SH': '中证1000', '932000.CSI': '中证2000', 'other': '其他', '8841431.WI': '微盘股',
            '399371.SZ': '国证价值', '399370.SZ': '国证成长', 'value': '行业聚合价值', 'growth': '行业聚合成长',
            'guangfu': '光伏', 'donglidianchi': '动力电池', 'qiche': '汽车', 'bandaoti': '半导体'
        }

        # 行业相关
        self.industry_info = get_industry_info()
        self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == 1]
        self.industry_info = self.industry_info[self.industry_info['IS_NEW'] == 1]
        self.industry_info = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.industry_list = self.industry_info['INDUSTRY_ID'].unique().tolist()
        self.industry_symbol = get_industry_symbol()
        self.industry_symbol = self.industry_symbol[self.industry_symbol['INDUSTRY_TYPE'] == 1]
        self.industry_symbol = self.industry_symbol[self.industry_symbol['IS_NEW'] == 1]
        self.industry_symbol = self.industry_symbol[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.stock_industry = get_stock_industry()
        self.stock_industry = self.stock_industry[self.stock_industry['INDUSTRY_TYPE'] == 1]
        self.stock_industry = self.stock_industry[self.stock_industry['IS_NEW'] == 1]
        self.stock_industry = self.stock_industry.drop('INDUSTRY_NAME', axis=1).merge(self.industry_symbol, on=['INDUSTRY_ID'], how='left')
        self.stock_industry = self.stock_industry.drop('INDUSTRY_ID', axis=1).merge(self.industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID']], on=['INDUSTRY_NAME'], how='left')
        self.stock_industry = self.stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME', 'TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE']]

        self.stock_industry['INDUSTRY_ID'] = self.stock_industry['INDUSTRY_ID'].apply(lambda x: str(x) + '.SI')
        self.industry_info['INDUSTRY_ID'] = self.industry_info['INDUSTRY_ID'].apply(lambda x: str(x) + '.SI')
        self.sw_symbol_name_dic = self.industry_info.set_index('INDUSTRY_ID')['INDUSTRY_NAME'].to_dict()
        self.sw_name_symbol_dic = self.industry_info.set_index('INDUSTRY_NAME')['INDUSTRY_ID'].to_dict()
        self.index_dict.update(self.sw_symbol_name_dic)

        # self.index_code_dict = {
        #     '000300.SH': '3145', '000905.SH': '4978', '000852.SH': '39144', '932000.CSI': '561230',
        #     '399371.SZ': '10053', '399370.SZ': '10052',
        #     '801010.SI': '5375', '801030.SI': '5377', '801040.SI': '5378', '801050.SI': '5379', '801080.SI': '5382',
        #     '801110.SI': '5385', '801120.SI': '5386', '801130.SI': '5387', '801140.SI': '5388', '801150.SI': '5389',
        #     '801160.SI': '5390', '801170.SI': '5391', '801180.SI': '5392', '801200.SI': '5394', '801210.SI': '5395',
        #     '801230.SI': '5397', '801710.SI': '32616', '801720.SI': '32617', '801730.SI': '32618', '801740.SI': '32620',
        #     '801750.SI': '32622', '801760.SI': '32623', '801770.SI': '32624', '801780.SI': '32625', '801790.SI': '32626',
        #     '801880.SI': '32621', '801890.SI': '32619', '801950.SI': '415355', '801960.SI': '415384', '801970.SI': '415401',
        #     '801980.SI': '415412'
        # }

        self.calendar_df, self.trade_df, self.report_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

    def load_index_cons(self):
        # 指数成分股（每季度更新）
        for index in self.index_list:
            if index not in ['other', 'value', 'growth', 'guangfu', 'donglidianchi', 'qiche', 'bandaoti']:
                index_cons_path = '{0}index_cons/index_cons_{1}.hdf'.format(self.data_path, index)
                if os.path.isfile(index_cons_path):
                    existed_index_cons = pd.read_hdf(index_cons_path, key='table')
                    max_date = max(existed_index_cons['date']).strftime('%Y%m%d')
                    start_date = max(str(max_date), '20091201')
                else:
                    existed_index_cons = pd.DataFrame()
                    start_date = '20091201'
                report_trade_df = self.report_trade_df[(self.report_trade_df['TRADE_DATE'] > start_date) & (self.report_trade_df['TRADE_DATE'] <= self.end_date)]
                index_cons_list = []
                for date in report_trade_df['TRADE_DATE'].unique().tolist():
                    date_hyphen = datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d')
                    index_cons_date = w.wset("sectorconstituent", "date={0};windcode={1}".format(date_hyphen, index), usedf=True)[1]
                    index_cons_list.append(index_cons_date)
                    print(date)
                index_cons = pd.concat([existed_index_cons] + index_cons_list, ignore_index=True)
                index_cons.to_hdf(index_cons_path, key='table', mode='w')
        return

    def load_stock_daily_k(self):
        # 股票行情
        stock_daily_k_path = '{0}stock_daily_k.hdf'.format(self.data_path)
        if os.path.isfile(stock_daily_k_path):
            existed_stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
            max_date = max(existed_stock_daily_k['TDATE'])
            start_date = max(str(max_date), '20061201')
        else:
            existed_stock_daily_k = pd.DataFrame()
            start_date = '20061201'
        trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.end_date)]
        stock_daily_k_list = []
        for date in trade_df['TRADE_DATE'].unique().tolist():
            stock_daily_k_date = HBDB().read_stock_daily_k_ch_mkt(date)
            stock_daily_k_list.append(stock_daily_k_date)
            print(date)
        self.stock_daily_k = pd.concat([existed_stock_daily_k] + stock_daily_k_list, ignore_index=True)
        self.stock_daily_k.to_hdf(stock_daily_k_path, key='table', mode='w')
        self.stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        self.stock_daily_k = self.stock_daily_k.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VOTURNOVER': 'TURNOVER_VOLUME', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'TOTAL_MARKET_VALUE'})
        self.stock_daily_k['TRADE_DATE'] = self.stock_daily_k['TRADE_DATE'].astype(str)
        self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
        self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]

        self.turnover_value = self.stock_daily_k.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='TURNOVER_VALUE').sort_index()
        self.turnover_value = self.turnover_value.rolling(20).mean()
        self.neg_market_value = self.stock_daily_k.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NEG_MARKET_VALUE').sort_index()
        self.neg_market_value = self.neg_market_value.rolling(20).mean()
        self.stock_tclose = self.stock_daily_k.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CLOSE_PRICE').sort_index()
        self.stock_tclose_max = self.stock_tclose.rolling(60).max()
        self.stock_tclose_mean = self.stock_tclose.rolling(20).mean()
        return

    def load_fund_holding(self):
        # 公募基金持仓数据
        fund_holding_path = '{0}fund_holding.hdf'.format(self.data_path)
        self.fund_holding = pd.read_hdf(fund_holding_path, key='table')
        self.fund_holding = self.fund_holding.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME', 'ccsz': 'HOLDING_VALUE', 'ccsl': 'HOLDING_AMOUNT', 'zjbl': 'MV_IN_NA'})
        self.fund_holding['REPORT_DATE'] = self.fund_holding['REPORT_DATE'].astype(str)
        self.fund_holding = self.fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'], ascending=[True, True, False]).groupby(['FUND_CODE', 'REPORT_DATE']).head(10)
        self.fund_holding = self.fund_holding.loc[self.fund_holding['TICKER_SYMBOL'].str.len() == 6]
        self.fund_holding = self.fund_holding.loc[self.fund_holding['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]

        self.fund_holding_volume = self.fund_holding[['REPORT_DATE', 'TICKER_SYMBOL', 'HOLDING_AMOUNT']].groupby(['REPORT_DATE', 'TICKER_SYMBOL']).sum().reset_index()
        self.fund_holding_volume = self.fund_holding_volume.pivot(index='REPORT_DATE', columns='TICKER_SYMBOL', values='HOLDING_AMOUNT').sort_index()
        self.fund_holding_volume = self.fund_holding_volume.reset_index()
        self.fund_holding_volume = self.fund_holding_volume.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
        self.fund_holding_volume = self.fund_holding_volume.set_index('TRADE_DATE').drop('REPORT_DATE', axis=1)
        self.fund_holding_value = self.fund_holding[['REPORT_DATE', 'TICKER_SYMBOL', 'HOLDING_VALUE']].groupby(['REPORT_DATE', 'TICKER_SYMBOL']).sum().reset_index()
        self.fund_holding_value = self.fund_holding_value.pivot(index='REPORT_DATE', columns='TICKER_SYMBOL', values='HOLDING_VALUE').sort_index()
        self.fund_holding_value = self.fund_holding_value.reset_index()
        self.fund_holding_value = self.fund_holding_value.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
        self.fund_holding_value = self.fund_holding_value.set_index('TRADE_DATE').drop('REPORT_DATE', axis=1)
        return

    def get_index_cons(self, index):
        # 指数成分股
        if index not in ['other', 'value', 'growth', 'guangfu', 'donglidianchi', 'qiche', 'bandaoti']:
            index_cons_path = '{0}index_cons/index_cons_{1}.hdf'.format(self.data_path, index)
            self.index_cons = pd.read_hdf(index_cons_path, key='table')
            self.index_cons = self.index_cons.rename(columns={'date': 'TRADE_DATE', 'wind_code': 'TICKER_SYMBOL', 'sec_name': 'SEC_SHORT_NAME'})
            self.index_cons['TRADE_DATE'] = self.index_cons['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
            self.index_cons['TICKER_SYMBOL'] = self.index_cons['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
            self.index_cons = self.index_cons[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']]
        elif index in ['other']:
            index_cons_000300 = pd.read_hdf('{0}index_cons/index_cons_{1}.hdf'.format(self.data_path, '000300.SH'), key='table')
            index_cons_000905 = pd.read_hdf('{0}index_cons/index_cons_{1}.hdf'.format(self.data_path, '000905.SH'), key='table')
            index_cons_000852 = pd.read_hdf('{0}index_cons/index_cons_{1}.hdf'.format(self.data_path, '000852.SH'), key='table')
            self.index_cons = pd.concat([index_cons_000300, index_cons_000905, index_cons_000852])
            self.index_cons = self.index_cons.rename(columns={'date': 'TRADE_DATE', 'wind_code': 'TICKER_SYMBOL', 'sec_name': 'SEC_SHORT_NAME'})
            self.index_cons['TRADE_DATE'] = self.index_cons['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
            self.index_cons['TICKER_SYMBOL'] = self.index_cons['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
            self.index_cons = self.index_cons[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']]
        elif index in ['value', 'growth']:
            style_cons_path = '{0}index_cons/{1}_industry.xlsx'.format(self.data_path, index)
            style_cons = pd.read_excel(style_cons_path).dropna(how='all', axis=1)
            style_cons = style_cons.rename(columns={'Unnamed: 0': 'REPORT_DATE'})
            style_cons['REPORT_DATE'] = style_cons['REPORT_DATE'].astype(str)
            style_cons = style_cons.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
            style_cons = style_cons.set_index('TRADE_DATE').drop('REPORT_DATE', axis=1)
            style_cons = style_cons.reindex(self.report_trade_df['TRADE_DATE'].unique().tolist()).fillna(method='ffill').dropna()
            style_cons = style_cons.replace(self.sw_name_symbol_dic)
            report_trade_df = self.report_trade_df[(self.report_trade_df['TRADE_DATE'] > '20091201') & (self.report_trade_df['TRADE_DATE'] <= self.end_date)]
            index_cons_list = []
            for date in report_trade_df['TRADE_DATE'].unique().tolist():
                if date not in style_cons.index:
                    index_cons_date = pd.DataFrame()
                else:
                    index_cons_i_list = []
                    for i in list(style_cons.loc[date].values):
                        index_cons_i_path = '{0}index_cons/index_cons_{1}.hdf'.format(self.data_path, i)
                        index_cons_i = pd.read_hdf(index_cons_i_path, key='table')
                        index_cons_i = index_cons_i.rename(columns={'date': 'TRADE_DATE', 'wind_code': 'TICKER_SYMBOL', 'sec_name': 'SEC_SHORT_NAME'})
                        index_cons_i['TRADE_DATE'] = index_cons_i['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
                        index_cons_i['TICKER_SYMBOL'] = index_cons_i['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
                        index_cons_i = index_cons_i[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']]
                        index_cons_i = index_cons_i[index_cons_i['TRADE_DATE'] == date]
                        index_cons_i_list.append(index_cons_i)
                    index_cons_date = pd.concat(index_cons_i_list)
                index_cons_list.append(index_cons_date)
            self.index_cons = pd.concat(index_cons_list, ignore_index=True)
            self.index_cons = self.index_cons[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']]
        elif index in ['guangfu', 'donglidianchi', 'qiche', 'bandaoti']:
            index_cons_path = '{0}index_cons/{1}_信息.xlsx'.format(self.data_path, self.index_dict[index])
            index_cons = pd.read_excel(index_cons_path, sheet_name='股票池')
            index_cons.columns = ['SUB_SECTOR', 'SEC_SHORT_NAME', 'TICKER_SYMBOL', 'HK_STOCK']
            index_cons = index_cons[index_cons['HK_STOCK'] == 0]
            index_cons['TICKER_SYMBOL'] = index_cons['TICKER_SYMBOL'].apply(lambda x: str(x).zfill(6))
            report_trade_df = self.report_trade_df[(self.report_trade_df['TRADE_DATE'] > '20091201') & (self.report_trade_df['TRADE_DATE'] <= self.end_date)]
            index_cons_list = []
            for date in report_trade_df['TRADE_DATE'].unique().tolist():
                index_cons_date = index_cons[['TICKER_SYMBOL', 'SEC_SHORT_NAME']]
                index_cons_date['TRADE_DATE'] = date
                index_cons_list.append(index_cons_date)
            self.index_cons = pd.concat(index_cons_list, ignore_index=True)
            self.index_cons = self.index_cons[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']]
        else:
            self.index_cons = pd.DataFrame()
        return

    def get_tech_crowding(self, index):
        index_cons = self.index_cons.copy(deep=True)
        index_cons['IS_CON'] = 1
        index_cons = index_cons.drop_duplicates(['TRADE_DATE', 'TICKER_SYMBOL', 'IS_CON'])
        index_cons = index_cons.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='IS_CON').sort_index()
        index_cons = index_cons.T.reindex(self.stock_daily_k['TICKER_SYMBOL'].unique().tolist()).T
        index_cons = index_cons.fillna(0)
        index_cons = self.trade_df[['TRADE_DATE']].set_index('TRADE_DATE').merge(index_cons, left_index=True, right_index=True, how='left')
        index_cons = index_cons.fillna(method='ffill')
        index_cons = index_cons.dropna(how='all', axis=0).sort_index()
        if index == 'other':
            index_cons = index_cons.replace({0: 1, 1: 0})

        # 成交额占比
        turnover_propotion = (self.turnover_value * index_cons).sum(axis=1) / self.turnover_value.sum(axis=1)
        turnover_propotion = turnover_propotion[turnover_propotion.index.isin(list(index_cons.index))]
        turnover_propotion = pd.DataFrame(turnover_propotion, columns=[self.index_dict[index]])

        # 换手率
        turnover_rate = (self.turnover_value * index_cons).sum(axis=1) / (self.neg_market_value * index_cons).sum(axis=1)
        turnover_rate = turnover_rate[turnover_rate.index.isin(list(index_cons.index))]
        turnover_rate = pd.DataFrame(turnover_rate, columns=[self.index_dict[index]])

        # 创60日新高个股数量占比
        stock_new_high = (self.stock_tclose >= self.stock_tclose_max).astype(int)
        stock_new_high = stock_new_high.rolling(20).sum()
        stock_new_high = (stock_new_high * index_cons).sum(axis=1) / (index_cons.sum(axis=1) * 20)
        stock_new_high = stock_new_high[stock_new_high.index.isin(list(index_cons.index))]
        stock_new_high = pd.DataFrame(stock_new_high, columns=[self.index_dict[index]])

        # 20日均线上个股数量占比
        stock_mean_above = (self.stock_tclose >= self.stock_tclose_mean).astype(int)
        stock_mean_above = stock_mean_above.rolling(20).sum()
        stock_mean_above = (stock_mean_above * index_cons).sum(axis=1) / (index_cons.sum(axis=1) * 20)
        stock_mean_above = stock_mean_above[stock_mean_above.index.isin(list(index_cons.index))]
        stock_mean_above = pd.DataFrame(stock_mean_above, columns=[self.index_dict[index]])

        # 量价复合拥挤度
        crowding = pd.concat([turnover_propotion, turnover_rate, stock_new_high, stock_mean_above], axis=1)
        crowding.columns = [index + '_成交额占比', index + '_换手率', index + '_创60日新高个股数量占比', index + '_20日均线上个股数量占比']
        crowding['IDX'] = range(len(crowding))
        for col in list(crowding.columns)[:-1]:
            crowding[col + '_分位水平'] = crowding['IDX'].rolling(250).apply(lambda x: quantile_definition(x, col, crowding))
        crowding = crowding[[index + '_成交额占比_分位水平', index + '_换手率_分位水平', index + '_创60日新高个股数量占比_分位水平', index + '_20日均线上个股数量占比_分位水平']].mean(axis=1)
        crowding = crowding[crowding.index.isin(list(index_cons.index))]
        crowding = pd.DataFrame(crowding, columns=[self.index_dict[index]])

        # 量价复合相对拥挤度
        crowding_up = crowding.rolling(window=250, min_periods=1, center=False).mean() + 1.0 * crowding.rolling(window=250, min_periods=1, center=False).std(ddof=1)
        crowding_down = crowding.rolling(window=250, min_periods=1, center=False).mean() - 1.0 * crowding.rolling(window=250, min_periods=1, center=False).std(ddof=1)
        crowding_relative = (crowding - crowding_down) / (crowding_up - crowding_down)
        return turnover_propotion, turnover_rate, stock_new_high, stock_mean_above, crowding, crowding_relative

    def get_fund_crowding(self, index):
        index_cons = self.index_cons.copy(deep=True)
        index_cons['IS_CON'] = 1
        index_cons = index_cons.drop_duplicates(['TRADE_DATE', 'TICKER_SYMBOL', 'IS_CON'])
        index_cons = index_cons.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='IS_CON').sort_index()
        index_cons = index_cons.T.reindex(self.stock_daily_k['TICKER_SYMBOL'].unique().tolist()).T
        index_cons = index_cons.fillna(0)
        if index == 'other':
            index_cons = index_cons.replace({0: 1, 1: 0})
        if index in self.sw_symbol_name_dic.keys():
            report_trade_df = self.report_trade_df[(self.report_trade_df['TRADE_DATE'] > '20091201') & (self.report_trade_df['TRADE_DATE'] <= self.end_date)]
            index_cons_list = []
            for date in report_trade_df['TRADE_DATE'].unique().tolist():
                index_cons_date = self.stock_industry[self.stock_industry['INDUSTRY_ID'] == index][['TICKER_SYMBOL']]
                index_cons_date['TRADE_DATE'] = date
                index_cons_list.append(index_cons_date)
            index_cons = pd.concat(index_cons_list, ignore_index=True)
            index_cons = index_cons[['TRADE_DATE', 'TICKER_SYMBOL']]
            index_cons['IS_CON'] = 1
            index_cons = index_cons.drop_duplicates(['TRADE_DATE', 'TICKER_SYMBOL', 'IS_CON'])
            index_cons = index_cons.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='IS_CON').sort_index()
            index_cons = index_cons.T.reindex(self.stock_daily_k['TICKER_SYMBOL'].unique().tolist()).T
            index_cons = index_cons.fillna(0)
        index_cons = index_cons[index_cons.index <= self.report_date]

        # 公募基金持仓数量占比
        fund_holding_volume = (self.fund_holding_volume * index_cons).sum(axis=1) / self.fund_holding_volume.sum(axis=1)
        fund_holding_volume = fund_holding_volume[fund_holding_volume.index.isin(list(index_cons.index))]
        fund_holding_volume = pd.DataFrame(fund_holding_volume, columns=[self.index_dict[index]])

        # 公募基金持仓市值占比
        fund_holding_value = (self.fund_holding_value * index_cons).sum(axis=1) / (self.fund_holding_value).sum(axis=1)
        fund_holding_value = fund_holding_value[fund_holding_value.index.isin(list(index_cons.index))]
        fund_holding_value = pd.DataFrame(fund_holding_value, columns=[self.index_dict[index]])
        return fund_holding_volume, fund_holding_value

    def get_full_df(self, df):
        df['IDX'] = range(len(df))
        for i, col in enumerate(list(df.columns)[:-1]):
            df[col + '_分位水平'] = df['IDX'].rolling(250).apply(lambda x: quantile_definition(x, col, df))
            print(i)
        df = df.drop(['IDX'], axis=1)
        col1 = [i for i in list(df.columns) if len(i.split('_')) == 1]
        col2 = [i for i in list(df.columns) if len(i.split('_')) == 2]
        df1 = df[col1]
        df2 = df[col2]
        df2.columns = col1
        df1 = df1.T.reset_index()
        df1['indic'] = '原值'
        df1 = df1.set_index(['indic', 'index']).T
        df2 = df2.T.reset_index()
        df2['indic'] = '分位水平'
        df2 = df2.set_index(['indic', 'index']).T
        df = pd.concat([df1, df2], axis=1)
        return df

    def get_crowding_quantile(self, crowding):
        crowding_quantile_list = []
        for index in ['000300.SH', '000905.SH', '000852.SH', '932000.CSI', '399371.SZ', '399370.SZ', 'value', 'growth']:
            crowding_quantile = crowding[[self.index_dict[index]]].rename(columns={self.index_dict[index]: '量价复合拥挤度'})
            crowding_quantile['均值'] = crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).mean()
            crowding_quantile['均值±1.0*标准差'] = crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).mean() + 1.0 * crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).std(ddof=1)
            crowding_quantile['均值-1.0*标准差'] = crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).mean() - 1.0 * crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).std(ddof=1)
            crowding_quantile['均值±1.5*标准差'] = crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).mean() + 1.5 * crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).std(ddof=1)
            crowding_quantile['均值-1.5*标准差'] = crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).mean() - 1.5 * crowding_quantile['量价复合拥挤度'].rolling(window=250, min_periods=250, center=False).std(ddof=1)

            if index not in ('value', 'growth'):
                close = w.wsd(index, "close", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
                close = close.set_index('index').rename(columns={'CLOSE': '收盘点位（右轴）'})
                close.index = map(lambda x: x.strftime('%Y%m%d'), close.index)
            else:
                close = pd.read_excel('{0}style.xlsx'.format(self.data_path))
                close['TRADE_DATE'] = close['TRADE_DATE'].astype(str)
                close = close[['TRADE_DATE', index.upper()]].rename(columns={index.upper(): '收盘点位（右轴）', 'TRADE_DATE': 'index'}).set_index('index')
            crowding_quantile = crowding_quantile.merge(close, left_index=True, right_index=True, how='left')
            crowding_quantile = crowding_quantile.T.reset_index()
            crowding_quantile['INDEX'] = self.index_dict[index]
            crowding_quantile = crowding_quantile.set_index(['INDEX', 'index']).T
            crowding_quantile_list.append(crowding_quantile)
        crowding_quantile = pd.concat(crowding_quantile_list, axis=1)
        return crowding_quantile

    def get_theme_df(self, df):
        industry_theme_dic = {'银行': '大金融', '非银金融': '大金融', '房地产': '大金融',
                              '食品饮料': '消费', '家用电器': '消费', '社会服务': '消费', '农林牧渔': '消费', '商贸零售': '消费', '美容护理': '消费',
                              '医药生物': '医药生物',
                              '通信': 'TMT', '计算机': 'TMT', '电子': 'TMT', '传媒': 'TMT', '国防军工': 'TMT',
                              '交通运输': '制造', '机械设备': '制造', '汽车': '制造', '纺织服饰': '制造', '轻工制造': '制造', '电力设备': '制造',
                              '钢铁': '周期', '有色金属': '周期', '建筑装饰': '周期', '建筑材料': '周期', '基础化工': '周期', '石油石化': '周期', '煤炭': '周期', '公用事业': '周期', '环保': '周期',
                              '综合': '其他'}
        df = df[industry_theme_dic.keys()].unstack().reset_index()
        df.columns = ['INDUSTRY_NAME', 'REPORT_DATE', 'VALUE']
        df['THEME_NAME'] = df['INDUSTRY_NAME'].apply(lambda x: industry_theme_dic[x])
        df = df[['THEME_NAME', 'REPORT_DATE', 'VALUE']].groupby(['THEME_NAME', 'REPORT_DATE']).sum().reset_index()
        df = df.pivot(index='REPORT_DATE', columns='THEME_NAME', values='VALUE').sort_index()
        df = df[['消费', '医药生物', '制造', 'TMT', '周期', '大金融', '其他']]
        return df

    def get_etf(self):
        # ETF数据
        etf_path = '{0}ETF基金基本资料.xlsx'.format(self.data_path)
        self.etf_info = pd.read_excel(etf_path)
        self.etf_info = self.etf_info[self.etf_info['细分类型'].isin(['沪深300', '中证500', '中证1000', '中证2000'])]
        self.etf = pd.read_excel(etf_path, sheet_name='ETF份额')
        self.etf = self.etf_info[['细分类型', '代码']].merge(self.etf, on=['代码'], how='left')
        self.etf = self.etf.drop(['类型', '代码'], axis=1)
        etf = self.etf.groupby(['细分类型']).sum()
        etf = etf.reindex(['沪深300', '中证500', '中证1000', '中证2000']).T
        etf.index = map(lambda x: x.strftime('%Y%m%d'), etf.index)
        etf = etf.reset_index().rename(columns={'index': 'REPORT_DATE'})
        etf = etf.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
        etf = etf.set_index('TRADE_DATE').drop('REPORT_DATE', axis=1)
        return etf

    def get_style(self):
        # 风格拥挤度
        style = FEDB().read_timing_data(['TRADE_DATE', 'VALUE_CROWDING', 'GROWTH_CROWDING'], 'timing_style', self.start_date, self.end_date)
        style['TRADE_DATE'] = style['TRADE_DATE'].astype(str)
        style = style[style['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style = style.set_index('TRADE_DATE').sort_index()
        style = style.rename(columns={'VALUE_CROWDING': '价值', 'GROWTH_CROWDING': '成长'})
        return style

    def get_all(self):
        self.load_index_cons()
        self.load_stock_daily_k()
        self.load_fund_holding()
        turnover_propotion_list, turnover_rate_list, stock_new_high_list, stock_mean_above_list, crowding_list, \
        crowding_relative_list, fund_holding_volume_list, fund_holding_value_list = [], [], [], [], [], [], [], []
        for index in self.index_list:
            self.get_index_cons(index)
            turnover_propotion, turnover_rate, stock_new_high, stock_mean_above, crowding, crowding_relative = self.get_tech_crowding(index)
            fund_holding_volume, fund_holding_value = self.get_fund_crowding(index)
            turnover_propotion_list.append(turnover_propotion)
            turnover_rate_list.append(turnover_rate)
            stock_new_high_list.append(stock_new_high)
            stock_mean_above_list.append(stock_mean_above)
            crowding_list.append(crowding)
            crowding_relative_list.append(crowding_relative)
            fund_holding_volume_list.append(fund_holding_volume)
            fund_holding_value_list.append(fund_holding_value)
            print(index)
        turnover_propotion = pd.concat(turnover_propotion_list, axis=1)
        turnover_rate = pd.concat(turnover_rate_list, axis=1)
        stock_new_high = pd.concat(stock_new_high_list, axis=1)
        stock_mean_above = pd.concat(stock_mean_above_list, axis=1)
        crowding = pd.concat(crowding_list, axis=1)
        crowding_relative = pd.concat(crowding_relative_list, axis=1)
        fund_holding_volume = pd.concat(fund_holding_volume_list, axis=1)
        fund_holding_value = pd.concat(fund_holding_value_list, axis=1)

        turnover_propotion.to_csv('{0}test/turnover_propotion.csv'.format(self.data_path))
        turnover_rate.to_csv('{0}test/turnover_rate.csv'.format(self.data_path))
        stock_new_high.to_csv('{0}test/stock_new_high.csv'.format(self.data_path))
        stock_mean_above.to_csv('{0}test/stock_mean_above.csv'.format(self.data_path))
        crowding.to_csv('{0}test/crowding.csv'.format(self.data_path))
        crowding_relative.to_csv('{0}test/crowding_relative.csv'.format(self.data_path))
        fund_holding_volume.to_csv('{0}test/fund_holding_volume.csv'.format(self.data_path))
        fund_holding_value.to_csv('{0}test/fund_holding_value.csv'.format(self.data_path))

        turnover_propotion = pd.read_csv('{0}test/turnover_propotion.csv'.format(self.data_path), index_col=0)
        turnover_rate = pd.read_csv('{0}test/turnover_rate.csv'.format(self.data_path), index_col=0)
        stock_new_high = pd.read_csv('{0}test/stock_new_high.csv'.format(self.data_path), index_col=0)
        stock_mean_above = pd.read_csv('{0}test/stock_mean_above.csv'.format(self.data_path), index_col=0)
        crowding = pd.read_csv('{0}test/crowding.csv'.format(self.data_path), index_col=0)
        crowding_relative = pd.read_csv('{0}test/crowding_relative.csv'.format(self.data_path), index_col=0)
        fund_holding_volume = pd.read_csv('{0}test/fund_holding_volume.csv'.format(self.data_path), index_col=0)
        fund_holding_value = pd.read_csv('{0}test/fund_holding_value.csv'.format(self.data_path), index_col=0)

        turnover_propotion.index = map(lambda x: str(x), turnover_propotion.index)
        turnover_rate.index = map(lambda x: str(x), turnover_rate.index)
        stock_new_high.index = map(lambda x: str(x), stock_new_high.index)
        stock_mean_above.index = map(lambda x: str(x), stock_mean_above.index)
        crowding.index = map(lambda x: str(x), crowding.index)
        crowding_relative.index = map(lambda x: str(x), crowding_relative.index)
        fund_holding_volume.index = map(lambda x: str(x), fund_holding_volume.index)
        fund_holding_value.index = map(lambda x: str(x), fund_holding_value.index)

        turnover_propotion = self.get_full_df(turnover_propotion)
        turnover_rate = self.get_full_df(turnover_rate)
        stock_new_high = self.get_full_df(stock_new_high)
        stock_mean_above = self.get_full_df(stock_mean_above)
        crowding_quantile = self.get_crowding_quantile(crowding)
        fund_holding_volume_theme = self.get_theme_df(fund_holding_volume)
        fund_holding_value_theme = self.get_theme_df(fund_holding_value)
        etf = self.get_etf()
        style = self.get_style()

        turnover_propotion = turnover_propotion[turnover_propotion.index > self.start_date]
        turnover_rate = turnover_rate[turnover_rate.index > self.start_date]
        stock_new_high = stock_new_high[stock_new_high.index > self.start_date]
        stock_mean_above = stock_mean_above[stock_mean_above.index > self.start_date]
        crowding = crowding[crowding.index > self.start_date]
        crowding_relative = crowding_relative[crowding_relative.index > self.start_date]
        crowding_quantile = crowding_quantile[crowding_quantile.index > self.start_date]
        fund_holding_volume = fund_holding_volume[fund_holding_volume.index > self.start_date]
        fund_holding_value = fund_holding_value[fund_holding_value.index > self.start_date]
        fund_holding_volume_theme = fund_holding_volume_theme[fund_holding_volume_theme.index > self.start_date]
        fund_holding_value_theme = fund_holding_value_theme[fund_holding_value_theme.index > self.start_date]
        etf = etf[etf.index > self.start_date]
        style = style[style.index > self.start_date]

        turnover_propotion = turnover_propotion[turnover_propotion.index.isin(self.trade_df[self.trade_df['IS_WEEK_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        turnover_rate = turnover_rate[turnover_rate.index.isin(self.trade_df[self.trade_df['IS_WEEK_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        stock_new_high = stock_new_high[stock_new_high.index.isin(self.trade_df[self.trade_df['IS_WEEK_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        stock_mean_above = stock_mean_above[stock_mean_above.index.isin(self.trade_df[self.trade_df['IS_WEEK_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        crowding = crowding[crowding.index.isin(self.trade_df[self.trade_df['IS_WEEK_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        crowding_relative = crowding_relative[crowding_relative.index.isin(self.trade_df[self.trade_df['IS_WEEK_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        crowding_quantile = crowding_quantile[crowding_quantile.index.isin(self.trade_df[self.trade_df['IS_WEEK_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        fund_holding_volume = fund_holding_volume[fund_holding_volume.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        fund_holding_value = fund_holding_value[fund_holding_value.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        fund_holding_volume_theme = fund_holding_volume_theme[fund_holding_volume_theme.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        fund_holding_value_theme = fund_holding_value_theme[fund_holding_value_theme.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        etf = etf[etf.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()
        style = style[style.index.isin(self.trade_df[self.trade_df['IS_WEEK_END'] == '1']['TRADE_DATE'].unique().tolist())].sort_index()

        crowding = crowding.sort_index()
        crowding_change_1M = crowding.pct_change(1*4)
        crowding_change_1Q = crowding.pct_change(3*4)
        crowding = crowding.T.reset_index()
        crowding['indic'] = '原值'
        crowding = crowding.set_index(['indic', 'index']).T
        crowding_change_1M = crowding_change_1M.T.reset_index()
        crowding_change_1M['indic'] = '近一月变动'
        crowding_change_1M = crowding_change_1M.set_index(['indic', 'index']).T
        crowding_change_1Q = crowding_change_1Q.T.reset_index()
        crowding_change_1Q['indic'] = '近一季变动'
        crowding_change_1Q = crowding_change_1Q.set_index(['indic', 'index']).T
        crowding = pd.concat([crowding, crowding_change_1M, crowding_change_1Q], axis=1)

        crowding_relative = crowding_relative.sort_index()
        crowding_relative_change_1M = crowding_relative - crowding_relative.shift(1*4)
        crowding_relative_change_1Q = crowding_relative - crowding_relative.shift(3*4)
        crowding_relative = crowding_relative.T.reset_index()
        crowding_relative['indic'] = '原值'
        crowding_relative = crowding_relative.set_index(['indic', 'index']).T
        crowding_relative_change_1M = crowding_relative_change_1M.T.reset_index()
        crowding_relative_change_1M['indic'] = '近一月绝对变动'
        crowding_relative_change_1M = crowding_relative_change_1M.set_index(['indic', 'index']).T
        crowding_relative_change_1Q = crowding_relative_change_1Q.T.reset_index()
        crowding_relative_change_1Q['indic'] = '近一季绝对变动'
        crowding_relative_change_1Q = crowding_relative_change_1Q.set_index(['indic', 'index']).T
        crowding_relative = pd.concat([crowding_relative, crowding_relative_change_1M, crowding_relative_change_1Q], axis=1)

        fund_holding_volume = fund_holding_volume.sort_index()
        fund_holding_volume = fund_holding_volume.replace(0.0, np.nan)
        fund_holding_volume_change_1Q = fund_holding_volume - fund_holding_volume.shift(1)
        fund_holding_volume = fund_holding_volume.T.reset_index()
        fund_holding_volume['indic'] = '原值'
        fund_holding_volume = fund_holding_volume.set_index(['indic', 'index']).T
        fund_holding_volume_change_1Q = fund_holding_volume_change_1Q.T.reset_index()
        fund_holding_volume_change_1Q['indic'] = '近一季变动'
        fund_holding_volume_change_1Q = fund_holding_volume_change_1Q.set_index(['indic', 'index']).T
        fund_holding_volume = pd.concat([fund_holding_volume, fund_holding_volume_change_1Q], axis=1)

        fund_holding_value = fund_holding_value.sort_index()
        fund_holding_value = fund_holding_value.replace(0.0, np.nan)
        fund_holding_value_change_1Q = fund_holding_value - fund_holding_value.shift(1)
        fund_holding_value = fund_holding_value.T.reset_index()
        fund_holding_value['indic'] = '原值'
        fund_holding_value = fund_holding_value.set_index(['indic', 'index']).T
        fund_holding_value_change_1Q = fund_holding_value_change_1Q.T.reset_index()
        fund_holding_value_change_1Q['indic'] = '近一季变动'
        fund_holding_value_change_1Q = fund_holding_value_change_1Q.set_index(['indic', 'index']).T
        fund_holding_value = pd.concat([fund_holding_value, fund_holding_value_change_1Q], axis=1)

        etf = etf.sort_index()
        etf = etf.replace(0.0, np.nan)
        etf_propotion = etf.apply(lambda x: x / x.sum(), axis=1)
        etf_change_1M = etf.pct_change(1)
        etf_change_1Q = etf.pct_change(3)
        etf = etf.T.reset_index()
        etf['indic'] = '原值'
        etf = etf.set_index(['indic', 'index']).T
        etf_propotion = etf_propotion.T.reset_index()
        etf_propotion['indic'] = '占比'
        etf_propotion = etf_propotion.set_index(['indic', 'index']).T
        etf_change_1M = etf_change_1M.T.reset_index()
        etf_change_1M['indic'] = '近一月变动'
        etf_change_1M = etf_change_1M.set_index(['indic', 'index']).T
        etf_change_1Q = etf_change_1Q.T.reset_index()
        etf_change_1Q['indic'] = '近一季变动'
        etf_change_1Q = etf_change_1Q.set_index(['indic', 'index']).T
        etf = pd.concat([etf, etf_propotion, etf_change_1M, etf_change_1Q], axis=1)

        style = style.sort_index()
        style_1M = style.pct_change(1*4)
        style_1Q = style.pct_change(3*4)
        style = style.T.reset_index()
        style['indic'] = '原值'
        style = style.set_index(['indic', 'index']).T
        style_1M = style_1M.T.reset_index()
        style_1M['indic'] = '近一月变动'
        style_1M = style_1M.set_index(['indic', 'index']).T
        style_1Q = style_1Q.T.reset_index()
        style_1Q['indic'] = '近一季变动'
        style_1Q = style_1Q.set_index(['indic', 'index']).T
        style = pd.concat([style, style_1M, style_1Q], axis=1)

        turnover_propotion.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), turnover_propotion.index)
        turnover_rate.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), turnover_rate.index)
        stock_new_high.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), stock_new_high.index)
        stock_mean_above.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), stock_mean_above.index)
        crowding.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), crowding.index)
        crowding_relative.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), crowding_relative.index)
        crowding_quantile.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), crowding_quantile.index)
        fund_holding_volume.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), fund_holding_volume.index)
        fund_holding_value.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), fund_holding_value.index)
        fund_holding_volume_theme.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), fund_holding_volume_theme.index)
        fund_holding_value_theme.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), fund_holding_value_theme.index)
        etf.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), etf.index)
        style.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style.index)

        import xlwings
        filename = '{0}拥挤度.xlsx'.format(self.data_path)
        if os.path.exists(filename):
            app = xlwings.App(visible=False)
            wookbook = app.books.open(filename)
        else:
            app = xlwings.App(visible=False)
            wookbook = app.books.add()
            wookbook.sheets.add('成交额占比')
            wookbook.sheets.add('换手率')
            wookbook.sheets.add('创60日新高个股数量占比')
            wookbook.sheets.add('20日均线上个股数量占比')
            wookbook.sheets.add('量价复合拥挤度')
            wookbook.sheets.add('量价复合相对拥挤度')
            wookbook.sheets.add('量价复合拥挤度_分位')
            wookbook.sheets.add('公募基金持仓数量占比')
            wookbook.sheets.add('公募基金持仓市值占比')
            wookbook.sheets.add('ETF')
            wookbook.sheets.add('风格拥挤度')
        turnover_propotion_wooksheet = wookbook.sheets['成交额占比']
        turnover_propotion_wooksheet.clear()
        turnover_propotion_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = turnover_propotion
        turnover_rate_wooksheet = wookbook.sheets['换手率']
        turnover_rate_wooksheet.clear()
        turnover_rate_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = turnover_rate
        stock_new_high_wooksheet = wookbook.sheets['创60日新高个股数量占比']
        stock_new_high_wooksheet.clear()
        stock_new_high_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = stock_new_high
        stock_mean_above_wooksheet = wookbook.sheets['20日均线上个股数量占比']
        stock_mean_above_wooksheet.clear()
        stock_mean_above_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = stock_mean_above
        crowding_wooksheet = wookbook.sheets['量价复合拥挤度']
        crowding_wooksheet.clear()
        crowding_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = crowding
        crowding_relative_wooksheet = wookbook.sheets['量价复合相对拥挤度']
        crowding_relative_wooksheet.clear()
        crowding_relative_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = crowding_relative
        crowding_quantile_wooksheet = wookbook.sheets['量价复合拥挤度分位']
        crowding_quantile_wooksheet.clear()
        crowding_quantile_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = crowding_quantile
        fund_holding_volume_wooksheet = wookbook.sheets['公募基金持仓数量占比']
        fund_holding_volume_wooksheet.clear()
        fund_holding_volume_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = fund_holding_volume
        fund_holding_value_wooksheet = wookbook.sheets['公募基金持仓市值占比']
        fund_holding_value_wooksheet.clear()
        fund_holding_value_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = fund_holding_value
        fund_holding_volume_theme_wooksheet = wookbook.sheets['公募基金持仓数量占比_主题']
        fund_holding_volume_theme_wooksheet.clear()
        fund_holding_volume_theme_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = fund_holding_volume_theme
        fund_holding_value_theme_wooksheet = wookbook.sheets['公募基金持仓市值占比_主题']
        fund_holding_value_theme_wooksheet.clear()
        fund_holding_value_theme_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = fund_holding_value_theme
        etf_wooksheet = wookbook.sheets['ETF']
        etf_wooksheet.clear()
        etf_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = etf
        style_wooksheet = wookbook.sheets['风格拥挤度']
        style_wooksheet.clear()
        style_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = style
        wookbook.save(filename)
        wookbook.close()
        app.quit()


if __name__ == '__main__':
    start_date = '20131231'
    end_date = '20240202'
    report_date = '20231231'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/crowding/'
    Crowding(start_date, end_date, report_date, data_path).get_all()