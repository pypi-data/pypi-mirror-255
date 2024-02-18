# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
import os
import numpy as np
import pandas as pd

from WindPy import w
w.start()  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
w.isconnected()  # 判断WindPy是否已经登录成功


def filter_extreme_mad(ser, n=3):
    median = ser.quantile(0.5)
    new_median = ((ser - median).abs()).quantile(0.5)
    max_range = median + n * new_median
    min_range = median - n * new_median
    ser = np.clip(ser, min_range, max_range)
    return ser


def get_date(start_date, end_date):
    calendar_df = HBDB().read_cal(start_date, end_date)
    calendar_df = calendar_df.rename(
        columns={'jyrq': 'CALENDAR_DATE', 'sfjj': 'IS_OPEN', 'sfzm': 'IS_WEEK_END', 'sfym': 'IS_MONTH_END'})
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
    report_trade_df = report_trade_df[
        (report_trade_df['TRADE_DATE'] >= start_date) & (report_trade_df['TRADE_DATE'] <= end_date)]
    calendar_trade_df = calendar_df[['CALENDAR_DATE']].merge(trade_df[['TRADE_DATE']], left_on=['CALENDAR_DATE'],
                                                             right_on=['TRADE_DATE'], how='left')
    calendar_trade_df['TRADE_DATE'] = calendar_trade_df['TRADE_DATE'].fillna(method='ffill')
    calendar_trade_df = calendar_trade_df[
        (calendar_trade_df['TRADE_DATE'] >= start_date) & (calendar_trade_df['TRADE_DATE'] <= end_date)]
    return calendar_df, report_df, trade_df, report_trade_df, calendar_trade_df


def fund_info(date):
    # 正常运行中的普通股票型、偏股混合型、灵活配置型公募基金
    fund = HBDB().read_stock_fund_info()
    fund = fund.rename(
        columns={'jjdm': 'FUND_CODE', 'jjmc': 'FUND_FULL_NAME', 'jjjc': 'FUND_SHORT_NAME', 'clrq': 'BEGIN_DATE',
                 'zzrq': 'END_DATE', 'ejfl': 'FUND_TYPE', 'kffb': 'OPEN_CLOSE'})
    fund = fund.dropna(subset=['BEGIN_DATE'])
    fund['END_DATE'] = fund['END_DATE'].fillna(20990101)
    fund['BEGIN_DATE'] = fund['BEGIN_DATE'].astype(str)
    fund['END_DATE'] = fund['END_DATE'].astype(str)
    # 成立距计算日期满2年
    date_before = (datetime.strptime(date, '%Y%m%d') - timedelta(730)).strftime('%Y%m%d')
    fund = fund[fund['END_DATE'] >= date]
    # fund = fund[(fund['BEGIN_DATE'] <= date_before) & (fund['END_DATE'] >= date)]
    # fund = fund.sort_values(['FUND_FULL_NAME', 'FUND_CODE']).drop_duplicates('FUND_FULL_NAME')
    # 成立以来股票占基金净资产的比例均值不低于60%
    fund_gptzzjb = HBDB().read_fund_gptzzjb_given_codes(fund['FUND_CODE'].unique().tolist())
    fund_gptzzjb = fund_gptzzjb.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'gptzzjb': 'EQUITY_IN_NA'})
    fund_gptzzjb['REPORT_DATE'] = fund_gptzzjb['REPORT_DATE'].astype(str)
    fund_gptzzjb_mean = fund_gptzzjb[['FUND_CODE', 'EQUITY_IN_NA']].groupby('FUND_CODE').mean().reset_index()
    fund_gptzzjb_mean = fund_gptzzjb_mean[fund_gptzzjb_mean['EQUITY_IN_NA'] >= 60]
    fund = fund[fund['FUND_CODE'].isin(fund_gptzzjb_mean['FUND_CODE'].unique().tolist())]
    # 近2年以来股票占基金净资产的比例均不低于50%
    fund_gptzzjb = fund_gptzzjb[(fund_gptzzjb['REPORT_DATE'] >= date_before) & (fund_gptzzjb['REPORT_DATE'] <= date)]
    fund_gptzzjb_min = fund_gptzzjb[['FUND_CODE', 'EQUITY_IN_NA']].groupby('FUND_CODE').min().reset_index()
    fund_gptzzjb_min = fund_gptzzjb_min[fund_gptzzjb_min['EQUITY_IN_NA'] >= 50]
    fund = fund[fund['FUND_CODE'].isin(fund_gptzzjb_min['FUND_CODE'].unique().tolist())]
    return fund


class FundPerformanceFinance:
    def __init__(self, start_date, end_date, report_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date
        self.data_path = data_path
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date(
            '19000101', self.end_date)
        self.report_date_list = sorted(self.report_df['REPORT_DATE'].unique().tolist())
        self.fund = pd.read_excel('{0}fund.xlsx'.format(self.data_path))
        self.mutual_fund = self.fund[self.fund['基金池'] == '公募30池']
        self.private_fund = self.fund[self.fund['基金池'] == '私募主观池']
        self.stock_fund = fund_info(self.report_date)
        self.stock_fund.to_hdf('{0}stock_fund.hdf'.format(self.data_path), key='table', mode='w')
        self.stock_fund = pd.read_hdf('{0}stock_fund.hdf'.format(self.data_path), key='table')
        self.mutual_fund_holding, self.private_fund_holding, self.stock_fund_holding = self.get_holding()
        self.stock_info_ch = HBDB().read_stock_info_ch()
        self.stock_info_ch.to_hdf('{0}stock_info_ch.hdf'.format(self.data_path), key='table', mode='w')
        self.stock_info_ch = pd.read_hdf('{0}stock_info_ch.hdf'.format(self.data_path), key='table')
        self.stock_info_ch = self.stock_info_ch.rename(
            columns={'scdm': 'MARKET_CODE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME', 'zqlb': 'TICKER_TYPE',
                     'gsdm': 'COMPANY_CODE'})
        self.hk_stock = pd.read_excel('{0}hk_stock.xlsx'.format(self.data_path))
        self.finance = self.get_finance()
        self.indic_dic = {
            'PE_TTM': '估值指标', 'PB_LF': '估值指标', '股息率_TTM(%)': '估值指标',
            '每股收益_TTM(元／股)': '每股指标', '每股净资产(元／股)': '每股指标', '每股营业收入_TTM(元／股)': '每股指标', '每股现金流量净额_TTM(元／股)': '每股指标',
            '总资产收益率_TTM(%)': '盈利能力', '净资产收益率_TTM(%)': '盈利能力', '投入资本回报率_TTM(%)': '盈利能力', '销售毛利率_TTM(%)': '盈利能力', '销售净利率_TTM(%)': '盈利能力',
            '流动比率': '偿债能力', '速动比率': '偿债能力', '利息保障倍数(倍)': '偿债能力', '资产负债率(%)': '偿债能力',
            '营业收入同比增长(%)': '成长能力',  '归属母公司股东的净利润同比增长(%)': '成长能力', '经营活动产生的现金流量净额同比增长(%)': '成长能力', '净资产同比增长(%)': '成长能力', '固定资产投资扩张率(%)': '成长能力',
            '存货周转率(次)': '营运能力', '应收账款周转率(次)': '营运能力', '总资产周转率(次)': '营运能力', '营运资本周转率(次)': '营运能力',
            '经营活动产生的现金流量净额／营业收入_TTM(%)': '现金状况', '资本支出／折旧和摊销': '现金状况', '总资产现金回收率(%)': '现金状况',
            'CAPEX_TTM／营业收入_TTM(%)': 'CAPEX相关', 'CAPEX同比增长(%)': 'CAPEX相关',
            '股利支付率(%)': '分红能力', '留存盈余比率(%)': '分红能力'}
        return

    def get_holding(self):
        mutual_fund_holding = HBDB().read_fund_holding_given_codes(self.mutual_fund['基金代码'].unique().tolist())
        mutual_fund_holding = mutual_fund_holding.rename(
            columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME',
                     'ccsz': 'HOLDING_MARKET_VALUE', 'ccsl': 'HOLDING_AMOUNT', 'zjbl': 'MV_IN_NA'})
        mutual_fund_holding['REPORT_DATE'] = mutual_fund_holding['REPORT_DATE'].astype(str)
        mutual_fund_holding['TICKER_SYMBOL'] = mutual_fund_holding['TICKER_SYMBOL'].astype(str)
        mutual_fund_holding['MV_IN_NA'] = mutual_fund_holding['MV_IN_NA'] / 100.0
        mutual_fund_holding_nhk = mutual_fund_holding[mutual_fund_holding['TICKER_SYMBOL'].str.len() == 6]
        mutual_fund_holding_hk = mutual_fund_holding[mutual_fund_holding['TICKER_SYMBOL'].str.len() < 6]
        mutual_fund_holding_hk['TICKER_SYMBOL'] = mutual_fund_holding_hk['TICKER_SYMBOL'].apply(lambda x: x[1:] + '.HK')
        mutual_fund_holding = pd.concat([mutual_fund_holding_hk, mutual_fund_holding_nhk])
        mutual_fund_holding = mutual_fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'],
                                                              ascending=[True, True, False])
        mutual_fund_holding = mutual_fund_holding[['FUND_CODE', 'REPORT_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME',
                                                   'MV_IN_NA']]

        private_fund_holding = FEDB().read_private_holding_given_codes(
            self.private_fund['基金代码'].unique().tolist() + self.private_fund['拼接代码'].dropna().unique().tolist())
        private_fund_holding = private_fund_holding.rename(
            columns={'jjdm': 'FUND_CODE', 'trade_date': 'REPORT_DATE', 'ticker': 'TICKER_SYMBOL',
                     'sec_name': 'SEC_SHORT_NAME', 'weight': 'MV_IN_NA'})
        private_fund_holding['REPORT_DATE'] = private_fund_holding['REPORT_DATE'].astype(str)
        private_fund_holding['TICKER_SYMBOL'] = private_fund_holding['TICKER_SYMBOL'].astype(str)
        private_fund_holding = private_fund_holding.dropna()
        private_fund_holding = private_fund_holding[~private_fund_holding['TICKER_SYMBOL']
            .isin(['b00001', 'c00001', 'f00001', 'l00001', 'r00001', 'zc0001', 'zc0002', ''])]
        private_fund_holding = private_fund_holding[private_fund_holding['TICKER_SYMBOL'].str.len() <= 6]
        private_fund_onecode = self.private_fund.loc[self.private_fund['拼接代码'].isnull()]
        private_fund_twocode = self.private_fund.loc[~self.private_fund['拼接代码'].isnull()]
        private_fund_holding_onecode = private_fund_holding[
            private_fund_holding['FUND_CODE'].isin(private_fund_onecode['基金代码'].unique().tolist())]
        holding_ticker_list = []
        for idx, row in private_fund_twocode.iterrows():
            holding_ticker_st = private_fund_holding[private_fund_holding['FUND_CODE'] == row['基金代码']]
            holding_ticker_nd = private_fund_holding[private_fund_holding['FUND_CODE'] == row['拼接代码']]
            min_date = holding_ticker_st['REPORT_DATE'].min()
            holding_ticker_nd = holding_ticker_nd[holding_ticker_nd['REPORT_DATE'] < min_date]
            holding_ticker_nd['FUND_CODE'] = row['基金代码']
            holding_ticker = pd.concat([holding_ticker_st, holding_ticker_nd])
            holding_ticker_list.append(holding_ticker)
        private_fund_holding_twocode = pd.concat(holding_ticker_list)
        private_fund_holding = pd.concat([private_fund_holding_onecode, private_fund_holding_twocode])
        private_fund_holding_nhk = private_fund_holding[(private_fund_holding['TICKER_SYMBOL'].str.slice(0, 1) != 'H')
                                                    & (private_fund_holding['TICKER_SYMBOL'].str.slice(-2, -1) != 'H')]
        private_fund_holding_hk1 = private_fund_holding[private_fund_holding['TICKER_SYMBOL'].str.slice(0, 1) == 'H']
        private_fund_holding_hk1['TICKER_SYMBOL'] = private_fund_holding_hk1['TICKER_SYMBOL'].apply(lambda x: x[2:] + '.HK')
        private_fund_holding_hk2 = private_fund_holding[private_fund_holding['TICKER_SYMBOL'].str.slice(-2, -1) == 'H']
        private_fund_holding_hk2['TICKER_SYMBOL'] = private_fund_holding_hk2['TICKER_SYMBOL'].apply(lambda x: x[:-2] + '.HK')
        private_fund_holding = pd.concat([private_fund_holding_nhk, private_fund_holding_hk1, private_fund_holding_hk2])
        private_fund_holding = private_fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'],
                                                                ascending=[True, True, False])
        private_fund_holding = private_fund_holding[['FUND_CODE', 'REPORT_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME',
                                                     'MV_IN_NA']]

        stock_fund_holding = pd.read_hdf('{0}stock_fund_holding.hdf'.format(self.data_path), key='table')
        stock_fund_holding = stock_fund_holding[stock_fund_holding['jsrq'] < int(self.report_date)]
        stock_fund_holding_new = HBDB().read_fund_holding_given_date(self.report_date)
        stock_fund_holding = pd.concat([stock_fund_holding, stock_fund_holding_new])
        stock_fund_holding = stock_fund_holding[
            stock_fund_holding['jjdm'].isin(self.stock_fund['FUND_CODE'].unique().tolist())]
        stock_fund_holding.to_hdf('{0}stock_fund_holding.hdf'.format(self.data_path), key='table', mode='w')
        stock_fund_holding = pd.read_hdf('{0}stock_fund_holding.hdf'.format(self.data_path), key='table')
        stock_fund_holding = stock_fund_holding.rename(
            columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME',
                     'ccsz': 'HOLDING_MARKET_VALUE', 'ccsl': 'HOLDING_AMOUNT', 'zjbl': 'MV_IN_NA'})
        stock_fund_holding['REPORT_DATE'] = stock_fund_holding['REPORT_DATE'].astype(str)
        stock_fund_holding['TICKER_SYMBOL'] = stock_fund_holding['TICKER_SYMBOL'].astype(str)
        stock_fund_holding['MV_IN_NA'] = stock_fund_holding['MV_IN_NA'] / 100.0
        stock_fund_holding_nhk = stock_fund_holding[stock_fund_holding['TICKER_SYMBOL'].str.len() == 6]
        stock_fund_holding_hk = stock_fund_holding[stock_fund_holding['TICKER_SYMBOL'].str.len() < 6]
        stock_fund_holding_hk['TICKER_SYMBOL'] = stock_fund_holding_hk['TICKER_SYMBOL'].apply(lambda x: x[1:] + '.HK')
        stock_fund_holding = pd.concat([stock_fund_holding_hk, stock_fund_holding_nhk])
        stock_fund_holding = stock_fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'],
                                                              ascending=[True, True, False])
        stock_fund_holding = stock_fund_holding[['FUND_CODE', 'REPORT_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME',
                                                 'MV_IN_NA', 'HOLDING_MARKET_VALUE', 'HOLDING_AMOUNT']]
        return mutual_fund_holding, private_fund_holding, stock_fund_holding

    def get_finance(self):
        stock_finance_path = '{0}stock_finance.hdf'.format(self.data_path)
        if os.path.isfile(stock_finance_path):
            existed_stock_finance = pd.read_hdf(stock_finance_path, key='table')
            existed_stock_finance = existed_stock_finance[existed_stock_finance['END_DATE'] < self.report_date]
            max_date = max(existed_stock_finance['END_DATE'])
            start_date = max(str(max_date), '20061231')
        else:
            existed_stock_finance = pd.DataFrame()
            start_date = '20061231'
        report_df = self.report_df[
            (self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.report_date)]
        stock_finance_list = []
        for date in report_df['REPORT_DATE'].unique().tolist():
            stock_finance_date = HBDB().read_stock_finance_jy3(date)
            star_stock_finance_date = HBDB().read_star_stock_finance_jy3(date)
            stock_finance_date = pd.concat([stock_finance_date, star_stock_finance_date])
            stock_finance_list.append(stock_finance_date)
            print(date)
        stock_finance = pd.concat([existed_stock_finance] + stock_finance_list, ignore_index=True)
        stock_finance.to_hdf(stock_finance_path, key='table', mode='w')
        stock_finance = pd.read_hdf(stock_finance_path, key='table')
        stock_finance = stock_finance.rename(
            columns={'EPSTTM'.upper(): '每股收益_TTM(元／股)', 'NetAssetPS'.upper(): '每股净资产(元／股)', 'OperatingRevenuePSTTM'.upper(): '每股营业收入_TTM(元／股)', 'CashFlowPSTTM'.upper(): '每股现金流量净额_TTM(元／股)',
                     'ROATTM'.upper(): '总资产收益率_TTM(%)', 'ROETTM'.upper(): '净资产收益率_TTM(%)', 'ROICTTM'.upper(): '投入资本回报率_TTM(%)', 'GrossIncomeRatioTTM'.upper(): '销售毛利率_TTM(%)', 'NetProfitRatioTTM'.upper(): '销售净利率_TTM(%)',
                     'CurrentRatio'.upper(): '流动比率', 'QuickRatio'.upper(): '速动比率', 'InterestCover'.upper(): '利息保障倍数(倍)', 'DebtAssetsRatio'.upper(): '资产负债率(%)',
                     'OperatingRevenueGrowRate'.upper(): '营业收入同比增长(%)',  'NPParentCompanyYOY'.upper(): '归属母公司股东的净利润同比增长(%)', 'NetOperateCashFlowYOY'.upper(): '经营活动产生的现金流量净额同比增长(%)', 'NetAssetGrowRate'.upper(): '净资产同比增长(%)', 'FAExpansionRate'.upper(): '固定资产投资扩张率(%)',
                     'InventoryTRate'.upper(): '存货周转率(次)', 'ARTRate'.upper(): '应收账款周转率(次)', 'TotalAssetTRate'.upper(): '总资产周转率(次)', 'WorkingCaitalTRate'.upper(): '营运资本周转率(次)',
                     'CashRateOfSalesTTM'.upper(): '经营活动产生的现金流量净额／营业收入_TTM(%)', 'CapitalExpenditureToDM'.upper(): '资本支出／折旧和摊销', 'OperCashInToAsset'.upper(): '总资产现金回收率(%)',
                     'DividendPaidRatio'.upper(): '股利支付率(%)', 'RetainedEarningRatio'.upper(): '留存盈余比率(%)'})
        stock_finance['END_DATE'] = stock_finance['END_DATE'].astype(str)
        stock_finance['PUBLISH_DATE'] = stock_finance['PUBLISH_DATE'].astype(str)
        stock_finance = stock_finance.sort_values(
            ['TICKER_SYMBOL', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')

        stock_cf_ch_path = '{0}stock_cf_ch.hdf'.format(self.data_path)
        if os.path.isfile(stock_cf_ch_path):
            existed_stock_cf_ch = pd.read_hdf(stock_cf_ch_path, key='table')
            existed_stock_cf_ch = existed_stock_cf_ch[existed_stock_cf_ch['END_DATE'] < self.report_date]
            max_date = max(existed_stock_cf_ch['END_DATE'])
            start_date = max(str(max_date), '20061231')
        else:
            existed_stock_cf_ch = pd.DataFrame()
            start_date = '20061231'
        report_df = self.report_df[
            (self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.report_date)]
        stock_cf_ch_list = []
        for date in report_df['REPORT_DATE'].unique().tolist():
            stock_cf_ch_date = HBDB().read_stock_cf_ch_given_date(date)
            stock_cf_ch_list.append(stock_cf_ch_date)
            print(date)
        stock_cf_ch = pd.concat([existed_stock_cf_ch] + stock_cf_ch_list, ignore_index=True)
        stock_cf_ch.to_hdf(stock_cf_ch_path, key='table', mode='w')
        stock_cf_ch = pd.read_hdf(stock_cf_ch_path, key='table')
        stock_cf_ch = stock_cf_ch.merge(self.stock_info_ch[['COMPANY_CODE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']],
                                        on=['COMPANY_CODE'], how='left')
        stock_cf_ch['END_DATE'] = stock_cf_ch['END_DATE'].astype(str)
        stock_cf_ch['PUBLISH_DATE'] = stock_cf_ch['PUBLISH_DATE'].astype(str)
        stock_cf_ch = stock_cf_ch.sort_values(
            ['TICKER_SYMBOL', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')
        capex = stock_cf_ch.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='CAPEX')
        capex = capex.fillna(0.0)
        capex_Q1 = capex.loc[capex.index.str.slice(4, 6) == '03']
        capex = capex.sort_index().diff()
        capex = capex.loc[capex.index.str.slice(4, 6) != '03']
        capex = pd.concat([capex_Q1, capex])
        capex_ttm = capex.sort_index().rolling(4).sum()
        capex_ttm_yoy = capex_ttm.sort_index().replace(0.0, np.nan).pct_change(4)
        capex_ttm_yoy = capex_ttm_yoy.unstack().reset_index()
        capex_ttm_yoy.columns = ['TICKER_SYMBOL', 'END_DATE', 'CAPEX_TTM_YOY']
        capex_ttm = capex_ttm.unstack().reset_index()
        capex_ttm.columns = ['TICKER_SYMBOL', 'END_DATE', 'CAPEX_TTM']

        stock_ci_ch_path = '{0}stock_ci_ch.hdf'.format(self.data_path)
        if os.path.isfile(stock_ci_ch_path):
            existed_stock_ci_ch = pd.read_hdf(stock_ci_ch_path, key='table')
            existed_stock_ci_ch = existed_stock_ci_ch[existed_stock_ci_ch['END_DATE'] < self.report_date]
            max_date = max(existed_stock_ci_ch['END_DATE'])
            start_date = max(str(max_date), '20061231')
        else:
            existed_stock_ci_ch = pd.DataFrame()
            start_date = '20061231'
        report_df = self.report_df[
            (self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.report_date)]
        stock_ci_ch_list = []
        for date in report_df['REPORT_DATE'].unique().tolist():
            stock_ci_ch_date = HBDB().read_stock_ci_ch_given_date(date)
            stock_ci_ch_list.append(stock_ci_ch_date)
            print(date)
        stock_ci_ch = pd.concat([existed_stock_ci_ch] + stock_ci_ch_list, ignore_index=True)
        stock_ci_ch.to_hdf(stock_ci_ch_path, key='table', mode='w')
        stock_ci_ch = pd.read_hdf(stock_ci_ch_path, key='table')
        stock_ci_ch = stock_ci_ch.merge(self.stock_info_ch[['COMPANY_CODE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']],
                                        on=['COMPANY_CODE'], how='left')
        stock_ci_ch['END_DATE'] = stock_ci_ch['END_DATE'].astype(str)
        stock_ci_ch['PUBLISH_DATE'] = stock_ci_ch['PUBLISH_DATE'].astype(str)
        stock_ci_ch = stock_ci_ch.sort_values(
            ['TICKER_SYMBOL', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')
        revenue = stock_ci_ch.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='REVENUE')
        revenue = revenue.fillna(0.0)
        revenue_Q1 = revenue.loc[revenue.index.str.slice(4, 6) == '03']
        revenue = revenue.sort_index().diff()
        revenue = revenue.loc[revenue.index.str.slice(4, 6) != '03']
        revenue = pd.concat([revenue_Q1, revenue])
        revenue_ttm = revenue.sort_index().rolling(4).sum().replace(0.0, np.nan)
        revenue_ttm = revenue_ttm.unstack().reset_index()
        revenue_ttm.columns = ['TICKER_SYMBOL', 'END_DATE', 'REVENUE_TTM']

        stock_daily_k_path = '{0}stock_daily_k.hdf'.format(self.data_path)
        if os.path.isfile(stock_daily_k_path):
            existed_stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
            max_date = max(existed_stock_daily_k['TDATE'])
            start_date = max(str(max_date), '20061231')
        else:
            existed_stock_daily_k = pd.DataFrame()
            start_date = '20061231'
        report_trade_df = self.report_trade_df[
            (self.report_trade_df['TRADE_DATE'] > start_date) & (self.report_trade_df['TRADE_DATE'] <= self.report_date)]
        stock_daily_k_list = []
        for date in report_trade_df['TRADE_DATE'].unique().tolist():
            stock_daily_k_date = HBDB().read_stock_daily_k_ch(date)
            stock_daily_k_list.append(stock_daily_k_date)
            print(date)
        stock_daily_k = pd.concat([existed_stock_daily_k] + stock_daily_k_list, ignore_index=True)
        stock_daily_k.to_hdf(stock_daily_k_path, key='table', mode='w')
        stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        stock_daily_k = stock_daily_k.rename(
            columns={'SYMBOL': 'TICKER_SYMBOL', 'TDATE': 'TRADE_DATE', 'TCLOSE': 'CLOSE_PRICE', 'TCAP': 'MARKET_VALUE',
                     'MCAP': 'NEG_MARKET_VALUE'})
        stock_daily_k['TRADE_DATE'] = stock_daily_k['TRADE_DATE'].astype(str)
        stock_daily_k['END_DATE'] = stock_daily_k['TRADE_DATE'].apply(
            lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30')

        stock_valuation_path = '{0}stock_valuation.hdf'.format(self.data_path)
        if os.path.isfile(stock_valuation_path):
            existed_stock_valuation = pd.read_hdf(stock_valuation_path, key='table')
            max_date = max(existed_stock_valuation['TRADE_DATE'])
            start_date = max(str(max_date), '20061231')
        else:
            existed_stock_valuation = pd.DataFrame()
            start_date = '20061231'
        report_trade_df = self.report_trade_df[
            (self.report_trade_df['TRADE_DATE'] > start_date) & (self.report_trade_df['TRADE_DATE'] <= self.report_date)]
        stock_valuation_list = []
        for date in report_trade_df['TRADE_DATE'].unique().tolist():
            stock_valuation_date = HBDB().read_stock_valuation_given_date(date)
            star_stock_valuation_date = HBDB().read_star_stock_valuation_given_date(date)
            stock_valuation_date = pd.concat([stock_valuation_date, star_stock_valuation_date])
            stock_valuation_list.append(stock_valuation_date)
            print(date)
        stock_valuation = pd.concat([existed_stock_valuation] + stock_valuation_list, ignore_index=True)
        stock_valuation.to_hdf(stock_valuation_path, key='table', mode='w')
        stock_valuation = pd.read_hdf(stock_valuation_path, key='table')
        stock_valuation['TRADE_DATE'] = stock_valuation['TRADE_DATE'].astype(str)
        stock_valuation['END_DATE'] = stock_valuation['TRADE_DATE'].apply(
            lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30')

        stock_finance = stock_daily_k[['TICKER_SYMBOL', 'END_DATE', 'MARKET_VALUE', 'NEG_MARKET_VALUE']].rename(columns={'MARKET_VALUE': '总市值', 'NEG_MARKET_VALUE': '流通市值'}) \
            .merge(stock_valuation[['TICKER_SYMBOL', 'END_DATE', 'PE_TTM', 'PB_LF', 'DIVIDEND_RATIO_TTM']].rename(columns={'DIVIDEND_RATIO_TTM': '股息率_TTM(%)'}),
                   on=['TICKER_SYMBOL', 'END_DATE'], how='left') \
            .merge(stock_finance.drop(['PUBLISH_DATE', 'SEC_SHORT_NAME'], axis=1),
                   on=['TICKER_SYMBOL', 'END_DATE'], how='left') \
            .merge(capex_ttm.rename(columns={'CAPEX_TTM': 'CAPEX_TTM'}),
                   on=['TICKER_SYMBOL', 'END_DATE'], how='left') \
            .merge(revenue_ttm.rename(columns={'REVENUE_TTM': '营业收入_TTM'}),
                   on=['TICKER_SYMBOL', 'END_DATE'], how='left') \
            .merge(capex_ttm_yoy.rename(columns={'CAPEX_TTM_YOY': 'CAPEX同比增长(%)'}),
                   on=['TICKER_SYMBOL', 'END_DATE'], how='left')
        stock_finance['CAPEX_TTM／营业收入_TTM(%)'] = stock_finance['CAPEX_TTM'] / stock_finance['营业收入_TTM'] * 100
        stock_finance['CAPEX同比增长(%)'] = stock_finance['CAPEX同比增长(%)'] * 100
        stock_finance = stock_finance.drop(['CAPEX_TTM', '营业收入_TTM'], axis=1)
        stock_finance = stock_finance[['TICKER_SYMBOL', 'END_DATE', '总市值', '流通市值', 'PE_TTM', 'PB_LF', '股息率_TTM(%)',
                                       '每股收益_TTM(元／股)', '每股净资产(元／股)', '每股营业收入_TTM(元／股)', '每股现金流量净额_TTM(元／股)',
                                       '总资产收益率_TTM(%)', '净资产收益率_TTM(%)', '投入资本回报率_TTM(%)', '销售毛利率_TTM(%)', '销售净利率_TTM(%)',
                                       '流动比率', '速动比率', '利息保障倍数(倍)', '资产负债率(%)',
                                       '营业收入同比增长(%)', '归属母公司股东的净利润同比增长(%)', '经营活动产生的现金流量净额同比增长(%)', '净资产同比增长(%)', '固定资产投资扩张率(%)',
                                       '存货周转率(次)', '应收账款周转率(次)', '总资产周转率(次)', '营运资本周转率(次)',
                                       '经营活动产生的现金流量净额／营业收入_TTM(%)', '资本支出／折旧和摊销', '总资产现金回收率(%)',
                                       'CAPEX_TTM／营业收入_TTM(%)', 'CAPEX同比增长(%)',
                                       '股利支付率(%)', '留存盈余比率(%)']]

        hk_fund_holding = pd.concat([self.mutual_fund_holding, self.private_fund_holding])
        hk_fund_holding = hk_fund_holding[hk_fund_holding['REPORT_DATE'].isin(self.report_date_list[-12:])]
        hk_fund_holding['HK_STOCK'] = hk_fund_holding['TICKER_SYMBOL'].apply(lambda x: 1 if len(x.split('.')) == 2 else 0)
        hk_fund_holding = hk_fund_holding[hk_fund_holding['HK_STOCK'] == 1]
        hk_stock_finance_list = []
        for ticker in hk_fund_holding['TICKER_SYMBOL'].unique().tolist():
            hk_stock_finance_ticker = w.wsd("{0}".format(ticker),
                "mkt_cap_ard,mkt_cap_float,pe_ttm,pb_lyr,dividendyield2,eps_ttm,bps,orps_ttm,cfps_ttm,roa_ttm2,roe_ttm3,roic_ttm3,grossprofitmargin_ttm3,netprofitmargin_ttm3,wgsd_current,wgsd_quick,wgsd_ebittointerest,wgsd_debttoassets,wgsd_yoy_or,wgsd_yoynetprofit,wgsd_yoyocf,yoy_equity,yoy_fixedassets,wgsd_invturn,wgsd_arturn,wgsd_assetsturn,operatecaptialturn,ocftosales_ttm2,wgsd_capitalizedtoda,ocftoassets",
                "{0}".format(datetime.strptime(self.report_date_list[-12:][0], "%Y%m%d").strftime("%Y-%m-%d")), "{0}".format(datetime.strptime(self.report_date, "%Y%m%d").strftime("%Y-%m-%d")), "unit=1;currencyType=;Period=Q", usedf=True)[1].reset_index()
            hk_stock_finance_ticker = hk_stock_finance_ticker.rename(columns={'index': 'END_DATE'})
            hk_stock_finance_ticker['END_DATE'] = hk_stock_finance_ticker['END_DATE'].apply(lambda x: x.strftime("%Y%m%d"))
            hk_stock_finance_ticker['END_DATE'] = hk_stock_finance_ticker['END_DATE'].replace('20221230', '20231231')
            hk_stock_finance_ticker['TICKER_SYMBOL'] = ticker
            hk_stock_finance_list.append(hk_stock_finance_ticker)
        hk_stock_finance = pd.concat(hk_stock_finance_list)
        hk_stock_finance.to_hdf('{0}hk_stock_finance.hdf'.format(self.data_path), key='table', mode='w')
        hk_stock_capex_list = []
        for ticker in hk_fund_holding['TICKER_SYMBOL'].unique().tolist():
            hk_stock_capex_ticker = w.wsd("{0}".format(ticker),
                "wgsd_capex_ff,wgsd_sales_oper",
                "{0}".format(datetime.strptime(self.report_date_list[-12:][0], "%Y%m%d").strftime("%Y-%m-%d")), "{0}".format(datetime.strptime(self.report_date, "%Y%m%d").strftime("%Y-%m-%d")), "unit=1;rptType=1;currencyType=;Period=Q", usedf=True)[1].reset_index()
            hk_stock_capex_ticker = hk_stock_capex_ticker.rename(columns={'index': 'END_DATE'})
            hk_stock_capex_ticker['END_DATE'] = hk_stock_capex_ticker['END_DATE'].apply(lambda x: x.strftime("%Y%m%d"))
            hk_stock_capex_ticker['END_DATE'] = hk_stock_capex_ticker['END_DATE'].replace('20221230', '20231231')
            hk_stock_capex_ticker['TICKER_SYMBOL'] = ticker
            hk_stock_capex_list.append(hk_stock_capex_ticker)
        hk_stock_capex = pd.concat(hk_stock_capex_list)
        hk_stock_capex.to_hdf('{0}hk_stock_capex.hdf'.format(self.data_path), key='table', mode='w')
        hk_stock_finance = pd.read_hdf('{0}hk_stock_finance.hdf'.format(self.data_path), key='table')
        hk_stock_finance = hk_stock_finance.set_index(['TICKER_SYMBOL', 'END_DATE']).reset_index()
        hk_stock_capex = pd.read_hdf('{0}hk_stock_capex.hdf'.format(self.data_path), key='table')
        hk_stock_capex = hk_stock_capex.set_index(['TICKER_SYMBOL', 'END_DATE']).reset_index()
        hk_stock_finance = hk_stock_finance.merge(hk_stock_capex, on=['TICKER_SYMBOL', 'END_DATE'], how='left')
        hk_stock_finance.columns = ['TICKER_SYMBOL', 'END_DATE', '总市值', '流通市值', 'PE_TTM', 'PB_LF', '股息率_TTM(%)',
                                    '每股收益_TTM(元／股)', '每股净资产(元／股)', '每股营业收入_TTM(元／股)', '每股现金流量净额_TTM(元／股)',
                                    '总资产收益率_TTM(%)', '净资产收益率_TTM(%)', '投入资本回报率_TTM(%)', '销售毛利率_TTM(%)', '销售净利率_TTM(%)',
                                    '流动比率', '速动比率', '利息保障倍数(倍)', '资产负债率(%)',
                                    '营业收入同比增长(%)', '归属母公司股东的净利润同比增长(%)', '经营活动产生的现金流量净额同比增长(%)', '净资产同比增长(%)', '固定资产投资扩张率(%)',
                                    '存货周转率(次)', '应收账款周转率(次)', '总资产周转率(次)', '营运资本周转率(次)',
                                    '经营活动产生的现金流量净额／营业收入_TTM(%)', '资本支出／折旧和摊销', '总资产现金回收率(%)',
                                    'CAPEX', '营业收入']
        capex = hk_stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='CAPEX')
        capex = capex.fillna(0.0)
        capex_Q1 = capex.loc[capex.index.str.slice(4, 6) == '03']
        capex = capex.sort_index().diff()
        capex = capex.loc[capex.index.str.slice(4, 6) != '03']
        capex = pd.concat([capex_Q1, capex])
        capex_ttm = capex.sort_index().rolling(4).sum()
        capex_ttm_yoy = capex_ttm.sort_index().replace(0.0, np.nan).pct_change(4)
        capex_ttm_yoy = capex_ttm_yoy.unstack().reset_index()
        capex_ttm_yoy.columns = ['TICKER_SYMBOL', 'END_DATE', 'CAPEX_TTM_YOY']
        capex_ttm = capex_ttm.unstack().reset_index()
        capex_ttm.columns = ['TICKER_SYMBOL', 'END_DATE', 'CAPEX_TTM']
        revenue = hk_stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='营业收入')
        revenue = revenue.fillna(0.0)
        revenue_Q1 = revenue.loc[revenue.index.str.slice(4, 6) == '03']
        revenue = revenue.sort_index().diff()
        revenue = revenue.loc[revenue.index.str.slice(4, 6) != '03']
        revenue = pd.concat([revenue_Q1, revenue])
        revenue_ttm = revenue.sort_index().rolling(4).sum().replace(0.0, np.nan)
        revenue_ttm = revenue_ttm.unstack().reset_index()
        revenue_ttm.columns = ['TICKER_SYMBOL', 'END_DATE', 'REVENUE_TTM']
        hk_stock_finance = hk_stock_finance.drop(['CAPEX', '营业收入'], axis=1) \
            .merge(capex_ttm.rename(columns={'CAPEX_TTM': 'CAPEX_TTM'}),
                   on=['TICKER_SYMBOL', 'END_DATE'], how='left') \
            .merge(revenue_ttm.rename(columns={'REVENUE_TTM': '营业收入_TTM'}),
                   on=['TICKER_SYMBOL', 'END_DATE'], how='left') \
            .merge(capex_ttm_yoy.rename(columns={'CAPEX_TTM_YOY': 'CAPEX同比增长(%)'}),
                   on=['TICKER_SYMBOL', 'END_DATE'], how='left')
        hk_stock_finance['CAPEX_TTM／营业收入_TTM(%)'] = hk_stock_finance['CAPEX_TTM'] / hk_stock_finance['营业收入_TTM'] * 100
        hk_stock_finance['CAPEX同比增长(%)'] = hk_stock_finance['CAPEX同比增长(%)'] * 100
        hk_stock_finance = hk_stock_finance.drop(['CAPEX_TTM', '营业收入_TTM'], axis=1)
        hk_stock_finance = hk_stock_finance[['TICKER_SYMBOL', 'END_DATE', '总市值', '流通市值', 'PE_TTM', 'PB_LF', '股息率_TTM(%)',
                                             '每股收益_TTM(元／股)', '每股净资产(元／股)', '每股营业收入_TTM(元／股)', '每股现金流量净额_TTM(元／股)',
                                             '总资产收益率_TTM(%)', '净资产收益率_TTM(%)', '投入资本回报率_TTM(%)', '销售毛利率_TTM(%)', '销售净利率_TTM(%)',
                                             '流动比率', '速动比率', '利息保障倍数(倍)', '资产负债率(%)',
                                             '营业收入同比增长(%)', '归属母公司股东的净利润同比增长(%)', '经营活动产生的现金流量净额同比增长(%)', '净资产同比增长(%)', '固定资产投资扩张率(%)',
                                             '存货周转率(次)', '应收账款周转率(次)', '总资产周转率(次)', '营运资本周转率(次)',
                                             '经营活动产生的现金流量净额／营业收入_TTM(%)', '资本支出／折旧和摊销', '总资产现金回收率(%)',
                                             'CAPEX_TTM／营业收入_TTM(%)', 'CAPEX同比增长(%)']]

        stock_finance = pd.concat([stock_finance, hk_stock_finance])
        return stock_finance

    def get_finance_feature(self):
        stock_fund_holding = self.stock_fund_holding.copy(deep=True)
        stock_fund_holding['FUND_CODE'] = '885001'
        stock_fund_holding = stock_fund_holding.groupby(
            ['FUND_CODE', 'REPORT_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']).sum().reset_index()
        stock_fund_holding_total = stock_fund_holding[['REPORT_DATE', 'HOLDING_MARKET_VALUE']].groupby(
            ['REPORT_DATE']).sum().rename(columns={'HOLDING_MARKET_VALUE': 'TOTAL_HOLDING_MARKET_VALUE'})
        stock_fund_holding = stock_fund_holding.merge(stock_fund_holding_total, on=['REPORT_DATE'], how='left')
        stock_fund_holding['MV_IN_NA'] = stock_fund_holding['HOLDING_MARKET_VALUE'] / stock_fund_holding[
            'TOTAL_HOLDING_MARKET_VALUE']
        fund_holding = pd.concat([self.mutual_fund_holding, self.private_fund_holding, stock_fund_holding])

        fund_holding = fund_holding.merge(self.finance.rename(columns={'END_DATE': 'REPORT_DATE'}),
                                          on=['TICKER_SYMBOL', 'REPORT_DATE'], how='left')
        indic_list = list(self.finance.columns)[4:-2]
        fund_holding_list = []
        for indic in indic_list:
            fund_holding_tmp = fund_holding.copy(deep=True).dropna(subset=[indic])
            fund_holding_tmp[indic] = filter_extreme_mad(fund_holding_tmp[indic])
            fund_holding_tmp_total = fund_holding_tmp[['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA']].groupby(
                ['FUND_CODE', 'REPORT_DATE']).sum().rename(columns={'MV_IN_NA': 'TOTAL_MV_IN_NA'})
            fund_holding_tmp = fund_holding_tmp.merge(fund_holding_tmp_total, on=['FUND_CODE', 'REPORT_DATE'], how='left')
            fund_holding_tmp['WEIGHT'] = fund_holding_tmp['MV_IN_NA'] / fund_holding_tmp['TOTAL_MV_IN_NA']
            fund_holding_tmp[indic] = fund_holding_tmp['WEIGHT'] * fund_holding_tmp[indic]
            fund_holding_tmp = fund_holding_tmp[['FUND_CODE', 'REPORT_DATE', indic]].groupby(
                ['FUND_CODE', 'REPORT_DATE']).sum()
            fund_holding_list.append(fund_holding_tmp)
        fund_holding = pd.concat(fund_holding_list, axis=1).reset_index()
        fund_holding = fund_holding[fund_holding['REPORT_DATE'].isin(self.report_date_list[-12:])]
        finance_feature = fund_holding.drop('REPORT_DATE', axis=1).groupby('FUND_CODE').mean()
        finance_feature = finance_feature.reset_index().rename(columns={'FUND_CODE': '基金代码'})
        return finance_feature

    def get_finance_detail(self, writer):
        finance = self.finance[self.finance['END_DATE'].isin(self.report_date_list[-12:])]
        mutual_fund_zc_holding = self.mutual_fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'],
            ascending=[True, True, False]).groupby(['FUND_CODE', 'REPORT_DATE']).head(10)
        private_fund_zc_holding = self.private_fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'],
            ascending=[True, True, False]).groupby(['FUND_CODE', 'REPORT_DATE']).head(10)
        fund_zc_holding = pd.concat([mutual_fund_zc_holding, private_fund_zc_holding])
        fund_zc_holding_max = fund_zc_holding[['FUND_CODE', 'REPORT_DATE']].groupby(
            'FUND_CODE').max().reset_index().rename(columns={'REPORT_DATE': '最新日期'})
        fund_zc_holding = fund_zc_holding_max.merge(fund_zc_holding, on=['FUND_CODE'], how='left')
        fund_zc_holding = fund_zc_holding[fund_zc_holding['REPORT_DATE'] == fund_zc_holding['最新日期']]
        fund_zc_holding['MV_IN_NA'] = fund_zc_holding['MV_IN_NA'].apply(lambda x: round(x * 100, 2) if not pd.isna(x) else x)
        fund_zc_holding = self.fund.drop(['拼接代码', '净值代码'], axis=1).merge(fund_zc_holding.rename(columns={'FUND_CODE': '基金代码'}), on=['基金代码'], how='left')
        fund_zc_holding = fund_zc_holding.dropna(subset=['REPORT_DATE']).drop('REPORT_DATE', axis=1)

        indic_list = list(finance.columns)[2:-2]
        for indic in indic_list:
            fund_zc_holding_disp = fund_zc_holding.copy(deep=True)
            indic_data = finance[['TICKER_SYMBOL', 'END_DATE', indic]]
            indic_data[indic] = indic_data[indic].apply(lambda x: round(x, 2) if not pd.isna(x) else x)
            indic_data = indic_data.pivot(index='TICKER_SYMBOL', columns='END_DATE', values=indic)
            fund_zc_holding_disp = fund_zc_holding_disp.merge(indic_data, on=['TICKER_SYMBOL'], how='left')
            fund_zc_holding_disp = fund_zc_holding_disp.rename(
                columns={'TICKER_SYMBOL': '股票代码', 'SEC_SHORT_NAME': '股票名称', 'MV_IN_NA': '占净值比例(%)'})
            fund_zc_holding_disp.to_excel(writer, sheet_name=indic)
        return writer

    def get_performance(self):
        group_size = 10
        group = int(len(self.fund) / group_size) + 1 if len(self.fund) % group_size > 0 else int(
            len(self.fund) / group_size) + 0
        nav_df_list = []
        for i in range(group):
            fund_group = self.fund.iloc[i * group_size: (i + 1) * group_size]
            mutual_codes = fund_group[fund_group['基金池'] == '公募30池']['净值代码'].unique().tolist()
            private_codes = fund_group[fund_group['基金池'] == '私募主观池']['净值代码'].unique().tolist()
            nav_df_group = HBDB().read_fund_cumret_given_codes(mutual_codes=mutual_codes, private_codes=private_codes,
                                                               start=self.start_date, end=self.end_date)
            nav_df_group = nav_df_group[['FUND_CODE', 'TRADE_DATE', 'ADJ_NAV']] if len(
                nav_df_group) != 0 else pd.DataFrame(columns=['FUND_CODE', 'TRADE_DATE', 'ADJ_NAV'])
            nav_df_list.append(nav_df_group)
        fund_nav_df = pd.concat(nav_df_list)
        fund_nav_df = fund_nav_df.drop_duplicates()
        fund_nav_df['TRADE_DATE'] = fund_nav_df['TRADE_DATE'].astype(str)
        fund_nav_df = fund_nav_df.pivot(index='TRADE_DATE', columns='FUND_CODE', values='ADJ_NAV')
        fund_nav_df = fund_nav_df.sort_index()

        stock_fund_nav_df = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['885001'])
        stock_fund_nav_df = stock_fund_nav_df.rename(
            columns={'zqdm': 'FUND_CODE', 'jyrq': 'TRADE_DATE', 'spjg': 'ADJ_NAV'})
        stock_fund_nav_df['TRADE_DATE'] = stock_fund_nav_df['TRADE_DATE'].astype(str)
        stock_fund_nav_df = stock_fund_nav_df.pivot(index='TRADE_DATE', columns='FUND_CODE', values='ADJ_NAV')
        fund_nav_df = pd.concat([fund_nav_df, stock_fund_nav_df], axis=1)

        performance = pd.DataFrame(index=self.fund['净值代码'].unique().tolist(), columns=['最新日期', '2022年以来', '2023年以来'])
        for code in list(fund_nav_df.columns):
            fund_nav_2022 = fund_nav_df[fund_nav_df.index >= '20220101'][[code]].dropna().sort_index()
            fund_nav_2023 = fund_nav_df[fund_nav_df.index >= '20230101'][[code]].dropna().sort_index()
            performance.loc[code, '最新日期'] = fund_nav_2022.index[-1]
            performance.loc[code, '2022年以来'] = fund_nav_2022[code].iloc[-1] / fund_nav_2022[code].iloc[0] - 1
            performance.loc[code, '2023年以来'] = fund_nav_2023[code].iloc[-1] / fund_nav_2023[code].iloc[0] - 1
        performance = performance.reset_index().rename(columns={'index': '净值代码'})
        return performance

    def get_result(self):
        performance = self.get_performance()
        finance_feature = self.get_finance_feature()
        result = self.fund.merge(performance, on=['净值代码'], how='left').merge(finance_feature, on=['基金代码'], how='left')
        result = result.drop(['拼接代码', '净值代码'], axis=1).T.reset_index()
        result['指标类型'] = result['index'].apply(lambda x: self.indic_dic[x] if x in self.indic_dic.keys() else '')
        result = result.set_index(['指标类型', 'index']).T
        writer = pd.ExcelWriter('{0}result.xlsx'.format(self.data_path))
        result.to_excel(writer, sheet_name='汇总')
        writer = self.get_finance_detail(writer)
        writer.save()
        return


if __name__ == '__main__':
    start_date = '20200101'
    end_date = datetime.today().strftime('%Y%m%d')
    report_date = '20230630'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/fund_performance_finance/'
    FundPerformanceFinance(start_date, end_date, report_date, data_path).get_result()