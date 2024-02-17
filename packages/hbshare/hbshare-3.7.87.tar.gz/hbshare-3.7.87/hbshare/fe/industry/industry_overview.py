# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
import os
import numpy as np
import pandas as pd

from WindPy import w
w.start()  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
w.isconnected()  # 判断WindPy是否已经登录成功


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


def get_stock_info():
    stock_info = HBDB().read_stock_info()
    stock_info = stock_info.rename(columns={'zqdm': 'TICKER_SYMBOL', 'zqjc': 'SEC_SHORT_NAME', 'ssrq': 'ESTABLISH_DATE'})
    stock_info['ESTABLISH_DATE'] = stock_info['ESTABLISH_DATE'].dropna()
    stock_info['ESTABLISH_DATE'] = stock_info['ESTABLISH_DATE'].astype(int).astype(str)
    stock_info = stock_info.loc[stock_info['TICKER_SYMBOL'].str.len() == 6]
    stock_info = stock_info.loc[stock_info['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
    return stock_info


def filter_extreme_mad(ser, n=3):
    median = ser.quantile(0.5)
    new_median = ((ser - median).abs()).quantile(0.5)
    max_range = median + n * new_median
    min_range = median - n * new_median
    ser = np.clip(ser, min_range, max_range)
    return ser


def get_weighted_data_d(data_nodups, data, data_nodups_weight, data_weight, stock_info, sub_remove, sub_setor_list, target_col, weight_col, target_name):
    result = data_nodups[['TICKER_SYMBOL', 'TRADE_DATE', target_col]].merge(data_nodups_weight[['TICKER_SYMBOL', 'TRADE_DATE', weight_col]], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner').merge(stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
    result = result[result['TRADE_DATE'] >= result['SAMPLE_DATE']]
    result = result.dropna(subset=['TICKER_SYMBOL', 'TRADE_DATE', target_col, weight_col])
    result_filter = pd.DataFrame(result.groupby('TRADE_DATE').apply(lambda x: filter_extreme_mad(x[target_col])), columns=[target_col]).reset_index().rename(columns={'level_1': 'index'})
    result = result.reset_index().drop(target_col, axis=1).merge(result_filter, on=['TRADE_DATE', 'index'], how='inner').drop('index', axis=1)
    total_weight = result[['TRADE_DATE', weight_col]].groupby('TRADE_DATE').sum().reset_index().rename(columns={weight_col: 'TOTAL_' + weight_col})
    result = result.merge(total_weight, on=['TRADE_DATE'], how='inner')
    result['WEIGHT_' + target_col] = result[target_col] * result[weight_col] / result['TOTAL_' + weight_col]
    result = result[['TRADE_DATE', 'WEIGHT_' + target_col]].groupby('TRADE_DATE').sum().rename(columns={'WEIGHT_' + target_col: target_name})

    result_sub = data[['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE', target_col]].merge(data_weight[['TICKER_SYMBOL', 'TRADE_DATE', weight_col]], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner').merge(stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
    if sub_remove:
        result_sub = result_sub[result_sub['TRADE_DATE'] >= result_sub['SAMPLE_DATE']]
    result_sub = result_sub.dropna(subset=['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE', target_col, weight_col])
    result_sub_filter = pd.DataFrame(result_sub.groupby('TRADE_DATE').apply(lambda x: filter_extreme_mad(x[target_col])), columns=[target_col]).reset_index().rename(columns={'level_1': 'index'})
    result_sub = result_sub.reset_index().drop(target_col, axis=1).merge(result_sub_filter, on=['TRADE_DATE', 'index'], how='inner').drop('index', axis=1)
    total_weight_sub = result_sub[['TRADE_DATE', 'SUB_SECTOR', weight_col]].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum().reset_index().rename(columns={weight_col: 'TOTAL_' + weight_col})
    result_sub = result_sub.merge(total_weight_sub, on=['TRADE_DATE', 'SUB_SECTOR'], how='inner')
    result_sub['WEIGHT_' + target_col] = result_sub[target_col] * result_sub[weight_col] / result_sub['TOTAL_' + weight_col]
    result_sub = result_sub[['TRADE_DATE', 'SUB_SECTOR', 'WEIGHT_' + target_col]].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
    result_sub = result_sub.reset_index()
    result_sub = result_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='WEIGHT_' + target_col).sort_index()
    result_sub = result_sub.T.reindex(sub_setor_list).T
    result_sub.columns = [target_name + '_' + col for col in list(result_sub.columns)]
    return result, result_sub


def get_weighted_data_q(data_nodups, data, data_nodups_weight, data_weight, sub_setor_list, target_col, weight_col, target_name):
    result = data_nodups[['TICKER_SYMBOL', 'END_DATE', 'TRADE_DATE', target_col]].merge(data_nodups_weight[['TICKER_SYMBOL', 'TRADE_DATE', weight_col]], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner')
    total_weight = result[['END_DATE', weight_col]].groupby('END_DATE').sum().reset_index().rename(columns={weight_col: 'TOTAL_' + weight_col})
    result = result.merge(total_weight, on=['END_DATE'], how='inner')
    result['WEIGHT_' + target_col] = result[target_col] * result[weight_col] / result['TOTAL_' + weight_col]
    result = result[['END_DATE', 'WEIGHT_' + target_col]].groupby('END_DATE').sum().rename(columns={'WEIGHT_' + target_col: target_name})

    result_sub = data[['TICKER_SYMBOL', 'SUB_SECTOR', 'END_DATE', 'TRADE_DATE', target_col]].merge(data_weight[['TICKER_SYMBOL', 'TRADE_DATE', weight_col]], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner')
    total_weight_sub = result_sub[['END_DATE', 'SUB_SECTOR', weight_col]].groupby(['END_DATE', 'SUB_SECTOR']).sum().reset_index().rename(columns={weight_col: 'TOTAL_' + weight_col})
    result_sub = result_sub.merge(total_weight_sub, on=['END_DATE', 'SUB_SECTOR'], how='inner')
    result_sub['WEIGHT_' + target_col] = result_sub[target_col] * result_sub[weight_col] / result_sub['TOTAL_' + weight_col]
    result_sub = result_sub[['END_DATE', 'SUB_SECTOR', 'WEIGHT_' + target_col]].groupby(['END_DATE', 'SUB_SECTOR']).sum()
    result_sub = result_sub.reset_index()
    result_sub = result_sub.pivot(index='END_DATE', columns='SUB_SECTOR', values='WEIGHT_' + target_col).sort_index()
    result_sub = result_sub.T.reindex(sub_setor_list).T
    result_sub.columns = [target_name + '_' + col for col in list(result_sub.columns)]
    return result, result_sub


def quantile_definition(idxs, col, daily_df):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    q = (1.0 - np.count_nonzero(part_df[col].iloc[-1] < part_df[col]) / len(part_df)) if len(part_df[col].dropna()) != 0 else np.nan
    return q


class IndustryMulta:
    def __init__(self, industry_name, start_date, end_date, report_date, data_path, sub_remove=True):
        self.industry_name = industry_name
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date
        self.data_path = data_path
        self.sub_remove = sub_remove
        self.industry_universe = pd.read_excel('{0}{1}/{2}_信息.xlsx'.format(self.data_path, self.industry_name, self.industry_name), sheet_name='股票池')
        self.industry_universe.columns = ['SUB_SECTOR', 'SEC_SHORT_NAME', 'TICKER_SYMBOL', 'HK_STOCK']
        self.industry_universe = self.industry_universe[self.industry_universe['HK_STOCK'] == 0]
        self.industry_universe['TICKER_SYMBOL'] = self.industry_universe['TICKER_SYMBOL'].apply(lambda x: str(x).zfill(6))
        self.sub_setor_list = self.industry_universe['SUB_SECTOR'].unique().tolist()
        self.load()

    def load(self):
        # 日历
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

        # 股票信息
        self.stock_info = get_stock_info()
        self.stock_info = self.stock_info[self.stock_info['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_info['SAMPLE_DATE'] = self.stock_info['ESTABLISH_DATE'].apply(lambda x: self.trade_df[self.trade_df['TRADE_DATE'] >= x]['TRADE_DATE'].iloc[124] if len(self.trade_df[self.trade_df['TRADE_DATE'] >= x]) >= 125 else '29990101')

        # 股票收盘价、涨跌幅、成交金额、换手率、流通市值、总市值
        stock_daily_k_path = '{0}stock_daily_k.hdf'.format(self.data_path)
        if os.path.isfile(stock_daily_k_path):
            existed_stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
            max_date = max(existed_stock_daily_k['TDATE'])
            start_date = max(str(max_date), '20071231')
        else:
            existed_stock_daily_k = pd.DataFrame()
            start_date = '20071231'
        trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.end_date)]
        stock_daily_k_list = []
        for date in trade_df['TRADE_DATE'].unique().tolist():
            stock_daily_k_date = HBDB().read_stock_daily_k_ch(int(date))
            stock_daily_k_list.append(stock_daily_k_date)
            print(date)
        self.stock_daily_k = pd.concat([existed_stock_daily_k] + stock_daily_k_list, ignore_index=True)
        self.stock_daily_k.to_hdf(stock_daily_k_path, key='table', mode='w')
        #################################
        # self.stock_daily_k = pd.read_hdf('{0}stock_daily_k.hdf'.format(self.data_path), key='table')
        self.stock_daily_k_all = self.stock_daily_k.copy(deep=True)
        self.stock_daily_k_all = self.stock_daily_k_all.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'MARKET_VALUE'})
        self.stock_daily_k_all['TRADE_DATE'] = self.stock_daily_k_all['TRADE_DATE'].astype(str)
        self.stock_daily_k_all = self.stock_daily_k_all.loc[self.stock_daily_k_all['TICKER_SYMBOL'].str.len() == 6]
        self.stock_daily_k_all = self.stock_daily_k_all.loc[self.stock_daily_k_all['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        self.stock_daily_k_all = self.stock_daily_k_all[(self.stock_daily_k_all['TRADE_DATE'] >= self.start_date) & (self.stock_daily_k_all['TRADE_DATE'] <= self.end_date)]
        self.stock_daily_k = self.stock_daily_k.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'MARKET_VALUE'})
        self.stock_daily_k['TRADE_DATE'] = self.stock_daily_k['TRADE_DATE'].astype(str)
        self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
        self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        self.stock_daily_k = self.stock_daily_k[self.stock_daily_k['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_daily_k = self.stock_daily_k[(self.stock_daily_k['TRADE_DATE'] >= self.start_date) & (self.stock_daily_k['TRADE_DATE'] <= self.end_date)]
        self.stock_daily_k.to_hdf('{0}{1}/stock_daily_k_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table', mode='w')
        # self.stock_daily_k = pd.read_hdf('{0}{1}/stock_daily_k_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table')

        # 股票估值数据
        stock_valuation_path = '{0}stock_valuation.hdf'.format(self.data_path)
        if os.path.isfile(stock_valuation_path):
            existed_stock_valuation = pd.read_hdf(stock_valuation_path, key='table')
            max_date = max(existed_stock_valuation['TRADE_DATE'])
            start_date = max(str(max_date), '20071231')
        else:
            existed_stock_valuation = pd.DataFrame()
            start_date = '20071231'
        trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.end_date)]
        stock_valuation_list = []
        for date in trade_df['TRADE_DATE'].unique().tolist():
            stock_valuation_date = HBDB().read_stock_valuation_given_date(date)
            stock_valuation_date = stock_valuation_date[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'PE_TTM', 'PB_LF', 'PEG', 'DIVIDEND_RATIO_TTM']] if len(stock_valuation_date) > 0 else pd.DataFrame(columns=['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'PE_TTM', 'PB_LF', 'PEG', 'DIVIDEND_RATIO_TTM'])
            star_stock_valuation_date = HBDB().read_star_stock_valuation_given_date(date)
            star_stock_valuation_date = star_stock_valuation_date[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'PE_TTM', 'PB_LF', 'PEG', 'DIVIDEND_RATIO_TTM']] if len(star_stock_valuation_date) > 0 else pd.DataFrame(columns=['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'PE_TTM', 'PB_LF', 'PEG', 'DIVIDEND_RATIO_TTM'])
            stock_valuation_date = pd.concat([stock_valuation_date, star_stock_valuation_date])
            stock_valuation_list.append(stock_valuation_date)
            print(date)
        self.stock_valuation = pd.concat([existed_stock_valuation] + stock_valuation_list, ignore_index=True)
        self.stock_valuation.to_hdf(stock_valuation_path, key='table', mode='w')
        #################################
        # self.stock_valuation = pd.read_hdf('{0}stock_valuation.hdf'.format(self.data_path), key='table')
        self.stock_valuation['TRADE_DATE'] = self.stock_valuation['TRADE_DATE'].astype(str)
        self.stock_valuation = self.stock_valuation.loc[self.stock_valuation['TICKER_SYMBOL'].str.len() == 6]
        self.stock_valuation = self.stock_valuation.loc[self.stock_valuation['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        self.stock_valuation = self.stock_valuation[self.stock_valuation['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_valuation = self.stock_valuation[(self.stock_valuation['TRADE_DATE'] >= self.start_date) & (self.stock_valuation['TRADE_DATE'] <= self.end_date)]
        self.stock_valuation.to_hdf('{0}{1}/stock_valuation_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table', mode='w')
        # self.stock_valuation = pd.read_hdf('{0}{1}/stock_valuation_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table')

        # 股票财务数据
        stock_finance_path = '{0}stock_finance.hdf'.format(self.data_path)
        if os.path.isfile(stock_finance_path):
            existed_stock_finance = pd.read_hdf(stock_finance_path, key='table')
            max_date = max(existed_stock_finance['END_DATE'])
            start_date = max(str(max_date), '20071231')
        else:
            existed_stock_finance = pd.DataFrame()
            start_date = '20071231'
        report_df = self.report_df[(self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.report_date)]
        stock_finance_list = []
        for date in report_df['REPORT_DATE'].unique().tolist():
            stock_finance_date = HBDB().read_stock_finance_jy2(date)
            stock_finance_date = stock_finance_date[['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM', 'ROA_TTM', 'ROIC_TTM', 'GrossIncomeRatio'.upper(), 'NetProfitRatio'.upper(), 'NPParentCompanyYOY'.upper(), 'NPParentCompanyCutYOY'.upper(), 'OperProfitGrowRate'.upper(), 'TotalAssetGrowRate'.upper(), 'CashRateOfSalesTTM'.upper()]] if len(stock_finance_date) > 0 else pd.DataFrame(columns=['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM', 'ROA_TTM', 'ROIC_TTM', 'GrossIncomeRatio'.upper(), 'NetProfitRatio'.upper(), 'NPParentCompanyYOY'.upper(), 'NPParentCompanyCutYOY'.upper(), 'OperProfitGrowRate'.upper(), 'TotalAssetGrowRate'.upper(), 'CashRateOfSalesTTM'.upper()])
            star_stock_finance_date = HBDB().read_star_stock_finance_jy2(date)
            star_stock_finance_date = star_stock_finance_date[['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM', 'ROA_TTM', 'ROIC_TTM', 'GrossIncomeRatio'.upper(), 'NetProfitRatio'.upper(), 'NPParentCompanyYOY'.upper(), 'NPParentCompanyCutYOY'.upper(), 'OperProfitGrowRate'.upper(), 'TotalAssetGrowRate'.upper(), 'CashRateOfSalesTTM'.upper()]] if len(star_stock_finance_date) > 0 else pd.DataFrame(columns=['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM', 'ROA_TTM', 'ROIC_TTM', 'GrossIncomeRatio'.upper(), 'NetProfitRatio'.upper(), 'NPParentCompanyYOY'.upper(), 'NPParentCompanyCutYOY'.upper(), 'OperProfitGrowRate'.upper(), 'TotalAssetGrowRate'.upper(), 'CashRateOfSalesTTM'.upper()])
            stock_finance_date = pd.concat([stock_finance_date, star_stock_finance_date])
            stock_finance_list.append(stock_finance_date)
            print(date)
        self.stock_finance = pd.concat([existed_stock_finance] + stock_finance_list, ignore_index=True)
        self.stock_finance.to_hdf(stock_finance_path, key='table', mode='w')
        #################################
        # self.stock_finance = pd.read_hdf('{0}stock_finance.hdf'.format(self.data_path), key='table')
        self.stock_finance['END_DATE'] = self.stock_finance['END_DATE'].astype(str)
        self.stock_finance['PUBLISH_DATE'] = self.stock_finance['PUBLISH_DATE'].astype(str)
        self.stock_finance = self.stock_finance.loc[self.stock_finance['TICKER_SYMBOL'].str.len() == 6]
        self.stock_finance = self.stock_finance.loc[self.stock_finance['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        self.stock_finance = self.stock_finance[self.stock_finance['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_finance = self.stock_finance[(self.stock_finance['END_DATE'] >= self.start_date) & (self.stock_finance['END_DATE'] <= self.end_date)]
        self.stock_finance.to_hdf('{0}{1}/stock_finance_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table', mode='w')
        # self.stock_finance = pd.read_hdf('{0}{1}/stock_finance_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table')

        # 股票一致预期数据
        stock_consensus_path = '{0}stock_consensus_FY1.hdf'.format(self.data_path)
        if os.path.isfile(stock_consensus_path):
            existed_stock_consensus = pd.read_hdf(stock_consensus_path, key='table')
            max_date = max(existed_stock_consensus['EST_DT'])
            start_date = max(str(max_date), '20071231')
        else:
            existed_stock_consensus = pd.DataFrame()
            start_date = '20071231'
        calendar_df = self.calendar_df[(self.calendar_df['CALENDAR_DATE'] > start_date) & (self.calendar_df['CALENDAR_DATE'] <= self.end_date)]
        stock_consensus_list = []
        for date in calendar_df['CALENDAR_DATE'].unique().tolist():
            stock_consensus_date = HBDB().read_consensus_given_date(date, 'FY1')
            stock_consensus_list.append(stock_consensus_date)
            print(date)
        self.stock_consensus = pd.concat([existed_stock_consensus] + stock_consensus_list, ignore_index=True)
        self.stock_consensus = self.stock_consensus.sort_values(['EST_DT', 'TICKER_SYMBOL'])
        self.stock_consensus = self.stock_consensus.reset_index().drop('index', axis=1)
        self.stock_consensus.to_hdf(stock_consensus_path, key='table', mode='w')
        #################################
        # self.stock_consensus = pd.read_hdf('{0}stock_consensus_FY1.hdf'.format(self.data_path), key='table')
        self.stock_consensus['EST_DT'] = self.stock_consensus['EST_DT'].astype(str)
        self.stock_consensus['TICKER_SYMBOL'] = self.stock_consensus['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
        self.stock_consensus = self.stock_consensus.loc[self.stock_consensus['TICKER_SYMBOL'].str.len() == 6]
        self.stock_consensus = self.stock_consensus.loc[self.stock_consensus['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        self.stock_consensus = self.stock_consensus[self.stock_consensus['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_consensus = self.stock_consensus[(self.stock_consensus['EST_DT'] >= self.start_date) & (self.stock_consensus['EST_DT'] <= self.end_date)]
        self.stock_consensus.to_hdf('{0}{1}/stock_consensus_FY1_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table', mode='w')
        # self.stock_consensus = pd.read_hdf('{0}{1}/stock_consensus_FY1_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table')

        # 公募基金持仓数据
        fund_holding_path = '{0}fund_holding.hdf'.format(self.data_path)
        self.fund_holding = pd.read_hdf(fund_holding_path, key='table')
        #################################
        # self.fund_holding = pd.read_hdf('{0}fund_holding.hdf'.format(self.data_path), key='table')
        self.fund_holding_all = self.fund_holding.copy(deep=True)
        self.fund_holding_all = self.fund_holding_all.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME', 'ccsz': 'HOLDING_MARKET_VALUE', 'ccsl': 'HOLDING_AMOUNT', 'zjbl': 'MV_IN_NA'})
        self.fund_holding_all['REPORT_DATE'] = self.fund_holding_all['REPORT_DATE'].astype(str)
        self.fund_holding_all = self.fund_holding_all.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'], ascending=[True, True, False]).groupby(['FUND_CODE', 'REPORT_DATE']).head(10)
        self.fund_holding_all = self.fund_holding_all.loc[self.fund_holding_all['TICKER_SYMBOL'].str.len() == 6]
        self.fund_holding_all = self.fund_holding_all.loc[self.fund_holding_all['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        self.fund_holding = self.fund_holding.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME', 'ccsz': 'HOLDING_MARKET_VALUE', 'ccsl': 'HOLDING_AMOUNT', 'zjbl': 'MV_IN_NA'})
        self.fund_holding['REPORT_DATE'] = self.fund_holding['REPORT_DATE'].astype(str)
        self.fund_holding = self.fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'], ascending=[True, True, False]).groupby(['FUND_CODE', 'REPORT_DATE']).head(10)
        self.fund_holding = self.fund_holding.loc[self.fund_holding['TICKER_SYMBOL'].str.len() == 6]
        self.fund_holding = self.fund_holding.loc[self.fund_holding['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        self.fund_holding = self.fund_holding[self.fund_holding['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.fund_holding = self.fund_holding[(self.fund_holding['REPORT_DATE'] >= self.start_date) & (self.fund_holding['REPORT_DATE'] <= self.end_date)]
        self.fund_holding.to_hdf('{0}{1}/fund_holding_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table', mode='w')
        # self.fund_holding = pd.read_hdf('{0}{1}/fund_holding_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name), key='table')
        return

    def get_index(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        stock_ret = stock_daily_k_nodups.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PCT_CHANGE')
        stock_ret = stock_ret.fillna(0.0) / 100.0
        stock_ret = stock_ret.unstack().reset_index().rename(columns={0: 'RET'})

        ret = stock_ret.merge(stock_daily_k_nodups[['TICKER_SYMBOL', 'TRADE_DATE', 'NEG_MARKET_VALUE']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner').merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
        ret = ret[ret['TRADE_DATE'] >= ret['SAMPLE_DATE']]
        ret = ret.dropna()
        total_weight = ret[['TRADE_DATE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum().reset_index().rename(columns={'NEG_MARKET_VALUE': 'TOTAL_NEG_MARKET_VALUE'})
        ret = ret.merge(total_weight, on=['TRADE_DATE'], how='inner')
        ret['WEIGHT_RET'] = ret['RET'] * ret['NEG_MARKET_VALUE'] / ret['TOTAL_NEG_MARKET_VALUE']
        ret = ret[['TRADE_DATE', 'WEIGHT_RET']].groupby('TRADE_DATE').sum()
        nav = (ret + 1).cumprod().rename(columns={'WEIGHT_RET': '净值'})
        nav = nav.apply(lambda x: x / x.dropna().values[0])

        ret_sub = stock_ret.merge(stock_daily_k[['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE', 'NEG_MARKET_VALUE']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner').merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
        if self.sub_remove:
            ret_sub = ret_sub[ret_sub['TRADE_DATE'] >= ret_sub['SAMPLE_DATE']]
        ret_sub = ret_sub.dropna()
        total_weight_sub = ret_sub[['TRADE_DATE', 'SUB_SECTOR', 'NEG_MARKET_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum().reset_index().rename(columns={'NEG_MARKET_VALUE': 'TOTAL_NEG_MARKET_VALUE'})
        ret_sub = ret_sub.merge(total_weight_sub, on=['TRADE_DATE', 'SUB_SECTOR'], how='inner')
        ret_sub['WEIGHT_RET'] = ret_sub['RET'] * ret_sub['NEG_MARKET_VALUE'] / ret_sub['TOTAL_NEG_MARKET_VALUE']
        ret_sub = ret_sub[['TRADE_DATE', 'SUB_SECTOR', 'WEIGHT_RET']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
        ret_sub = ret_sub.reset_index()
        ret_sub = ret_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='WEIGHT_RET').sort_index()
        nav_sub = (ret_sub + 1).cumprod()
        nav_sub = nav_sub.apply(lambda x: x / x.dropna().values[0])
        nav_sub = nav_sub.T.reindex(self.sub_setor_list).T
        nav_sub.columns = ['净值_' + col for col in list(nav_sub.columns)]

        index = nav.merge(nav_sub, left_index=True, right_index=True, how='left')

        excess_index_list = []
        sub_sector_list = [col.split('_')[1] for col in list(nav_sub.columns)]
        for col in sub_sector_list:
            index_col = index[['净值', '净值_' + col]].sort_index()
            index_col['超额收益_' + col] = index_col['净值_' + col].pct_change() - index_col['净值'].pct_change()
            index_col = index_col.dropna(subset='净值_' + col)
            index_col['超额收益_' + col] = index_col['超额收益_' + col].fillna(0.0)
            index_col['超额净值_' + col] = (index_col['超额收益_' + col] + 1).cumprod()
            excess_index_list.append(index_col[['超额净值_' + col]])
        excess_index = pd.concat(excess_index_list, axis=1)

        index = index.merge(excess_index, left_index=True, right_index=True, how='left')
        index = index.sort_index()
        index.index.name = '交易日期'
        index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), index.index)
        return index

    def get_marketvalue(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        total_mv = stock_daily_k_nodups[['TRADE_DATE', 'MARKET_VALUE']].groupby('TRADE_DATE').sum()
        total_mv.columns = ['总市值']

        total_mv_sub = stock_daily_k[['TRADE_DATE', 'SUB_SECTOR', 'MARKET_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
        total_mv_sub = total_mv_sub.reset_index()
        total_mv_sub = total_mv_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='MARKET_VALUE')
        total_mv_sub = total_mv_sub.T.reindex(self.sub_setor_list).T
        total_mv_sub.columns = ['总市值_' + col for col in list(total_mv_sub.columns)]

        neg_mv = stock_daily_k_nodups[['TRADE_DATE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum()
        neg_mv = neg_mv.rename(columns={'NEG_MARKET_VALUE': '流通市值'})

        neg_mv_sub = stock_daily_k[['TRADE_DATE', 'SUB_SECTOR', 'NEG_MARKET_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
        neg_mv_sub = neg_mv_sub.reset_index()
        neg_mv_sub = neg_mv_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='NEG_MARKET_VALUE')
        neg_mv_sub = neg_mv_sub.T.reindex(self.sub_setor_list).T
        neg_mv_sub.columns = ['流通市值_' + col for col in list(neg_mv_sub.columns)]

        mv = total_mv.merge(total_mv_sub, left_index=True, right_index=True, how='left')\
             .merge(neg_mv, left_index=True, right_index=True, how='left').merge(neg_mv_sub, left_index=True, right_index=True, how='left')
        mv = mv.sort_index()
        mv.index.name = '交易日期'
        mv.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), mv.index)
        return mv

    def get_valuation(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')
        stock_valuation = self.stock_valuation.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_valuation_nodups = stock_valuation.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        pe_ttm, pe_ttm_sub = get_weighted_data_d(stock_valuation_nodups, stock_valuation, stock_daily_k_nodups, stock_daily_k, self.stock_info, self.sub_remove, self.sub_setor_list, 'PE_TTM', 'NEG_MARKET_VALUE', 'PE_TTM')
        pb_lf, pb_lf_sub = get_weighted_data_d(stock_valuation_nodups, stock_valuation, stock_daily_k_nodups, stock_daily_k, self.stock_info, self.sub_remove, self.sub_setor_list, 'PB_LF', 'NEG_MARKET_VALUE', 'PB_LF')
        peg, peg_sub = get_weighted_data_d(stock_valuation_nodups, stock_valuation, stock_daily_k_nodups, stock_daily_k, self.stock_info, self.sub_remove, self.sub_setor_list, 'PEG', 'NEG_MARKET_VALUE', 'PEG')
        div_ttm, div_ttm_sub = get_weighted_data_d(stock_valuation_nodups, stock_valuation, stock_daily_k_nodups, stock_daily_k, self.stock_info, self.sub_remove, self.sub_setor_list, 'DIVIDEND_RATIO_TTM', 'NEG_MARKET_VALUE', '股息率_TTM（%）')

        valuation = pe_ttm.merge(pe_ttm_sub, left_index=True, right_index=True, how='left')\
                    .merge(pb_lf, left_index=True, right_index=True, how='left').merge(pb_lf_sub, left_index=True, right_index=True, how='left') \
                    .merge(peg, left_index=True, right_index=True, how='left').merge(peg_sub, left_index=True, right_index=True, how='left')\
                    .merge(div_ttm, left_index=True, right_index=True, how='left').merge(div_ttm_sub, left_index=True, right_index=True, how='left')
        valuation = valuation.sort_index()
        valuation.index.name = '交易日期'
        valuation.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), valuation.index)
        return valuation

    def get_finance(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')
        stock_finance = self.stock_finance.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner')
        stock_finance = stock_finance[stock_finance['END_DATE'].isin(self.report_df['REPORT_DATE'].unique().tolist())]
        stock_finance = stock_finance.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'END_DATE'}), on=['END_DATE'], how='inner')
        stock_finance = stock_finance.sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'END_DATE'], keep='last')
        stock_finance_nodups = stock_finance.sort_values(['TICKER_SYMBOL', 'END_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')

        roettm, roettm_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'ROE_TTM', 'NEG_MARKET_VALUE', 'ROE_TTM（%）')
        roattm, roattm_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'ROA_TTM', 'NEG_MARKET_VALUE', 'ROA_TTM（%）')
        roicttm, roicttm_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'ROIC_TTM', 'NEG_MARKET_VALUE', 'ROIC_TTM（%）')
        gpr, gpr_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'GrossIncomeRatio'.upper(), 'NEG_MARKET_VALUE', '销售毛利率（%）')
        npr, npr_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'NetProfitRatio'.upper(), 'NEG_MARKET_VALUE', '销售净利率（%）')
        oryoy, oryoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'OPER_REVENUE_YOY'.upper(), 'NEG_MARKET_VALUE', '营业收入同比增长（%）')
        opyoy, opyoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'OperProfitGrowRate'.upper(), 'NEG_MARKET_VALUE', '营业利润同比增长（%）')
        nppyoy, nppyoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'NPParentCompanyYOY'.upper(), 'NEG_MARKET_VALUE', '归母净利润同比增长（%）')
        nppcutyoy, nppcutyoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'NPParentCompanyCutYOY'.upper(), 'NEG_MARKET_VALUE', '扣非归母净利润同比增长（%）')
        tayoy, tayoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'TotalAssetGrowRate'.upper(), 'NEG_MARKET_VALUE', '总资产同比增长（%）')
        ocftoor, ocftoor_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, self.sub_setor_list, 'CashRateOfSalesTTM'.upper(), 'NEG_MARKET_VALUE', '经营活动产生的现金流量净额/营业收入_TTM(%)')

        finance = roettm.merge(roettm_sub, left_index=True, right_index=True, how='left')\
                  .merge(roattm, left_index=True, right_index=True, how='left').merge(roattm_sub, left_index=True, right_index=True, how='left')\
                  .merge(roicttm, left_index=True, right_index=True, how='left').merge(roicttm_sub, left_index=True, right_index=True, how='left')\
                  .merge(gpr, left_index=True, right_index=True, how='left').merge(gpr_sub, left_index=True, right_index=True, how='left')\
                  .merge(npr, left_index=True, right_index=True, how='left').merge(npr_sub, left_index=True, right_index=True, how='left')\
                  .merge(oryoy, left_index=True, right_index=True, how='left').merge(oryoy_sub, left_index=True, right_index=True, how='left')\
                  .merge(opyoy, left_index=True, right_index=True, how='left').merge(opyoy_sub, left_index=True, right_index=True, how='left')\
                  .merge(nppyoy, left_index=True, right_index=True, how='left').merge(nppyoy_sub, left_index=True, right_index=True, how='left')\
                  .merge(nppcutyoy, left_index=True, right_index=True, how='left').merge(nppcutyoy_sub, left_index=True, right_index=True, how='left')\
                  .merge(tayoy, left_index=True, right_index=True, how='left').merge(tayoy_sub, left_index=True, right_index=True, how='left') \
                  .merge(ocftoor, left_index=True, right_index=True, how='left').merge(ocftoor_sub, left_index=True, right_index=True, how='left')
        finance = finance.sort_index()
        finance.index.name = '报告日期'
        finance.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), finance.index)
        return finance

    def get_consensus(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')
        stock_consensus = self.stock_consensus.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'EST_DT']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'EST_DT'], keep='last')
        stock_consensus = stock_consensus[stock_consensus['EST_DT'].isin(self.trade_df['TRADE_DATE'].unique().tolist())].rename(columns={'EST_DT': 'TRADE_DATE'})
        stock_consensus_nodups = stock_consensus.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        con_or = stock_consensus_nodups[['TRADE_DATE', 'EST_OPER_REVENUE']].groupby('TRADE_DATE').sum()
        con_or = con_or.rename(columns={'EST_OPER_REVENUE': '一致预期营业收入'})

        con_or_sub = stock_consensus[['TRADE_DATE', 'SUB_SECTOR', 'EST_OPER_REVENUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
        con_or_sub = con_or_sub.reset_index()
        con_or_sub = con_or_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='EST_OPER_REVENUE')
        con_or_sub.columns = ['一致预期营业收入_' + col for col in list(con_or_sub.columns)]

        con_np = stock_consensus_nodups[['TRADE_DATE', 'EST_NET_PROFIT']].groupby('TRADE_DATE').sum()
        con_np = con_np.rename(columns={'EST_NET_PROFIT': '一致预期净利润'})

        con_np_sub = stock_consensus[['TRADE_DATE', 'SUB_SECTOR', 'EST_NET_PROFIT']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
        con_np_sub = con_np_sub.reset_index()
        con_np_sub = con_np_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='EST_NET_PROFIT')
        con_np_sub.columns = ['一致预期净利润_' + col for col in list(con_np_sub.columns)]

        con_eps, con_eps_sub = get_weighted_data_d(stock_consensus_nodups, stock_consensus, stock_daily_k_nodups, stock_daily_k, self.stock_info, self.sub_remove, self.sub_setor_list, 'EST_EPS', 'NEG_MARKET_VALUE', '一致预期EPS')
        con_roe, con_roe_sub = get_weighted_data_d(stock_consensus_nodups, stock_consensus, stock_daily_k_nodups, stock_daily_k, self.stock_info, self.sub_remove, self.sub_setor_list, 'EST_ROE', 'NEG_MARKET_VALUE', '一致预期ROE（%）')
        con_pe, con_pe_sub = get_weighted_data_d(stock_consensus_nodups, stock_consensus, stock_daily_k_nodups, stock_daily_k, self.stock_info, self.sub_remove, self.sub_setor_list, 'EST_PE', 'NEG_MARKET_VALUE', '一致预期PE')

        consensus = con_or.merge(con_or_sub, left_index=True, right_index=True, how='left')\
                    .merge(con_np, left_index=True, right_index=True, how='left').merge(con_np_sub, left_index=True, right_index=True, how='left') \
                    .merge(con_eps, left_index=True, right_index=True, how='left').merge(con_eps_sub, left_index=True, right_index=True, how='left')\
                    .merge(con_roe, left_index=True, right_index=True, how='left').merge(con_roe_sub, left_index=True, right_index=True, how='left')\
                    .merge(con_pe, left_index=True, right_index=True, how='left').merge(con_pe_sub, left_index=True, right_index=True, how='left')
        consensus = consensus.sort_index()
        consensus.index.name = '交易日期'
        consensus.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), consensus.index)
        return consensus

    def get_fundholding(self):
        fund_holding = self.fund_holding.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']],on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'REPORT_DATE', 'FUND_CODE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'REPORT_DATE', 'FUND_CODE'], keep='last')
        fund_holding_nodups = fund_holding.sort_values(['TICKER_SYMBOL', 'REPORT_DATE', 'FUND_CODE']).drop_duplicates(['TICKER_SYMBOL', 'REPORT_DATE', 'FUND_CODE'], keep='last')

        holding_amount = fund_holding_nodups[['REPORT_DATE', 'HOLDING_AMOUNT']].groupby('REPORT_DATE').sum()
        holding_amount = holding_amount.rename(columns={'HOLDING_AMOUNT': '持仓数量'})

        holding_amount_sub = fund_holding[['REPORT_DATE', 'SUB_SECTOR', 'HOLDING_AMOUNT']].groupby(['REPORT_DATE', 'SUB_SECTOR']).sum()
        holding_amount_sub = holding_amount_sub.reset_index()
        holding_amount_sub = holding_amount_sub.pivot(index='REPORT_DATE', columns='SUB_SECTOR', values='HOLDING_AMOUNT')
        holding_amount_sub = holding_amount_sub.T.reindex(self.sub_setor_list).T
        holding_amount_sub.columns = ['持仓数量_' + col for col in list(holding_amount_sub.columns)]

        holding_mv = fund_holding_nodups[['REPORT_DATE', 'HOLDING_MARKET_VALUE']].groupby('REPORT_DATE').sum()
        holding_mv.columns = ['持仓市值']

        holding_mv_sub = fund_holding[['REPORT_DATE', 'SUB_SECTOR', 'HOLDING_MARKET_VALUE']].groupby(['REPORT_DATE', 'SUB_SECTOR']).sum()
        holding_mv_sub = holding_mv_sub.reset_index()
        holding_mv_sub = holding_mv_sub.pivot(index='REPORT_DATE', columns='SUB_SECTOR', values='HOLDING_MARKET_VALUE')
        holding_mv_sub = holding_mv_sub.T.reindex(self.sub_setor_list).T
        holding_mv_sub.columns = ['持仓市值_' + col for col in list(holding_mv_sub.columns)]

        total_fund_holding = self.fund_holding_all[['REPORT_DATE', 'HOLDING_MARKET_VALUE']].groupby('REPORT_DATE').sum()
        total_fund_holding.columns = ['总持仓市值']
        holding_ratio = holding_mv.merge(total_fund_holding, left_index=True, right_index=True, how='left')
        holding_ratio['持仓市值占比（%）'] = holding_ratio['持仓市值'] / holding_ratio['总持仓市值'] * 100
        holding_ratio = holding_ratio[['持仓市值占比（%）']]

        holding_ratio_sub = holding_mv_sub.merge(total_fund_holding, left_index=True, right_index=True, how='left')
        holding_ratio_sub = holding_ratio_sub.apply(lambda x: x / x['总持仓市值'] * 100, axis=1).iloc[:, :-1]
        holding_ratio_sub.columns = ['持仓市值占比（%）_' + col for col in list(holding_ratio_sub.columns)]

        fundholding = holding_amount.merge(holding_amount_sub, left_index=True, right_index=True, how='left')\
                      .merge(holding_mv, left_index=True, right_index=True, how='left').merge(holding_mv_sub, left_index=True, right_index=True, how='left') \
                      .merge(holding_ratio, left_index=True, right_index=True, how='left').merge(holding_ratio_sub, left_index=True, right_index=True, how='left')
        fundholding = fundholding.sort_index()
        fundholding.index.name = '交易日期'
        fundholding.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), fundholding.index)
        return fundholding

    def get_sentiment(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')
        stock_daily_k_all_nodups = self.stock_daily_k_all.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        turnover_value = stock_daily_k_nodups[['TRADE_DATE', 'TURNOVER_VALUE']].groupby('TRADE_DATE').sum()
        total_turnover_value = stock_daily_k_all_nodups[['TRADE_DATE', 'TURNOVER_VALUE']].groupby('TRADE_DATE').sum().rename(columns={'TURNOVER_VALUE': 'TOTAL_TURNOVER_VALUE'})
        turnover_value = turnover_value.merge(total_turnover_value, left_index=True, right_index=True, how='left')
        turnover_value['TURNOVER_VALUE_PROPORTION'] = turnover_value['TURNOVER_VALUE'] / turnover_value['TOTAL_TURNOVER_VALUE'] * 100.0
        turnover_value = turnover_value[['TURNOVER_VALUE_PROPORTION']]
        turnover_value.columns = ['成交额占比（%）']

        turnover_value_sub = stock_daily_k[['TRADE_DATE', 'SUB_SECTOR', 'TURNOVER_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum().reset_index()
        total_turnover_value = stock_daily_k_all_nodups[['TRADE_DATE', 'TURNOVER_VALUE']].groupby('TRADE_DATE').sum().rename(columns={'TURNOVER_VALUE': 'TOTAL_TURNOVER_VALUE'}).reset_index()
        turnover_value_sub = turnover_value_sub.merge(total_turnover_value, on=['TRADE_DATE'], how='left')
        turnover_value_sub['TURNOVER_VALUE_PROPORTION'] = turnover_value_sub['TURNOVER_VALUE'] / turnover_value_sub['TOTAL_TURNOVER_VALUE'] * 100.0
        turnover_value_sub = turnover_value_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='TURNOVER_VALUE_PROPORTION')
        turnover_value_sub = turnover_value_sub.T.reindex(self.sub_setor_list).T
        turnover_value_sub.columns = ['成交额占比（%）_' + col for col in list(turnover_value_sub.columns)]

        turnover_rate = stock_daily_k_nodups[['TRADE_DATE', 'TURNOVER_VALUE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum()
        turnover_rate['TURNOVER_RATE'] = turnover_rate['TURNOVER_VALUE'] / turnover_rate['NEG_MARKET_VALUE'] * 100.0
        turnover_rate = turnover_rate[['TURNOVER_RATE']]
        turnover_rate.columns = ['换手率（%）']

        turnover_rate_sub = stock_daily_k[['TRADE_DATE', 'SUB_SECTOR', 'TURNOVER_VALUE', 'NEG_MARKET_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum().reset_index()
        turnover_rate_sub['TURNOVER_RATE'] = turnover_rate_sub['TURNOVER_VALUE'] / turnover_rate_sub['NEG_MARKET_VALUE'] * 100.0
        turnover_rate_sub = turnover_rate_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='TURNOVER_RATE')
        turnover_rate_sub = turnover_rate_sub.T.reindex(self.sub_setor_list).T
        turnover_rate_sub.columns = ['换手率（%）_' + col for col in list(turnover_rate_sub.columns)]

        # 价格：行业内创60日新高个股数量及占比
        n = 60
        new_high = stock_daily_k_nodups[['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE']].merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
        new_high = new_high[new_high['TRADE_DATE'] >= new_high['SAMPLE_DATE']]
        new_high = new_high.dropna(subset=['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE'])
        new_high_max = new_high.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CLOSE_PRICE').sort_index()
        new_high_max = new_high_max.rolling(n).max()
        new_high_max = new_high_max.unstack().reset_index()
        new_high_max.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE_MAX']
        new_high = new_high.merge(new_high_max, on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left').dropna()
        new_high['NEW_HIGH'] = (new_high['CLOSE_PRICE'] >= new_high['CLOSE_PRICE_MAX']).astype(int)
        new_high_count = new_high[['TRADE_DATE', 'NEW_HIGH']].groupby('TRADE_DATE').count().reset_index().rename(columns={'NEW_HIGH': 'COUNT'})
        new_high = new_high[['TRADE_DATE', 'NEW_HIGH']].groupby('TRADE_DATE').sum().reset_index()
        new_high = new_high.merge(new_high_count, on=['TRADE_DATE'], how='left')
        new_high['NEW_HIGH_RATIO'] = new_high['NEW_HIGH'] / new_high['COUNT'] * 100.0
        new_high = new_high[['TRADE_DATE', 'NEW_HIGH_RATIO']].set_index('TRADE_DATE')
        new_high.columns = ['创60日新高个股占行业内个股比例（%）']

        # 价格：行业内20日均线上个股数量及占比
        n = 20
        mean_above = stock_daily_k_nodups[['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE']].merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
        mean_above = mean_above[mean_above['TRADE_DATE'] >= mean_above['SAMPLE_DATE']]
        mean_above = mean_above.dropna(subset=['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE'])
        mean_above_mean = mean_above.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CLOSE_PRICE').sort_index()
        mean_above_mean = mean_above_mean.rolling(n).mean()
        mean_above_mean = mean_above_mean.unstack().reset_index()
        mean_above_mean.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE_MEAN']
        mean_above = mean_above.merge(mean_above_mean, on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left').dropna()
        mean_above['MEAN_ABOVE'] = (mean_above['CLOSE_PRICE'] >= mean_above['CLOSE_PRICE_MEAN']).astype(int)
        mean_above_count = mean_above[['TRADE_DATE', 'MEAN_ABOVE']].groupby('TRADE_DATE').count().reset_index().rename(columns={'MEAN_ABOVE': 'COUNT'})
        mean_above = mean_above[['TRADE_DATE', 'MEAN_ABOVE']].groupby('TRADE_DATE').sum().reset_index()
        mean_above = mean_above.merge(mean_above_count, on=['TRADE_DATE'], how='left')
        mean_above['MEAN_ABOVE_RATIO'] = mean_above['MEAN_ABOVE'] / mean_above['COUNT'] * 100.0
        mean_above = mean_above[['TRADE_DATE', 'MEAN_ABOVE_RATIO']].set_index('TRADE_DATE')
        mean_above.columns = ['20日均线上个股占行业内个股比例（%）']

        sentiment = turnover_value.merge(turnover_value_sub, left_index=True, right_index=True, how='left')\
                    .merge(turnover_rate, left_index=True, right_index=True, how='left').merge(turnover_rate_sub, left_index=True, right_index=True, how='left')\
                    .merge(new_high, left_index=True, right_index=True, how='left')\
                    .merge(mean_above, left_index=True, right_index=True, how='left')
        sentiment = sentiment.sort_index()
        sentiment.index.name = '交易日期'
        sentiment.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), sentiment.index)
        return sentiment

    def get_all(self):
        index = self.get_index()
        marketvalue = self.get_marketvalue()
        valuation = self.get_valuation()
        finance = self.get_finance()
        consensus = self.get_consensus()
        fundholding = self.get_fundholding()
        sentiment = self.get_sentiment()

        import xlwings
        filename = '{0}{1}/{2}_多维度数据.xlsx'.format(self.data_path, self.industry_name, self.industry_name)
        if os.path.exists(filename):
            app = xlwings.App(visible=False)
            wookbook = app.books.open(filename)
        else:
            app = xlwings.App(visible=False)
            wookbook = app.books.add()
            wookbook.sheets.add('情绪')
            wookbook.sheets.add('基金持仓')
            wookbook.sheets.add('一致预期')
            wookbook.sheets.add('财务')
            wookbook.sheets.add('估值')
            wookbook.sheets.add('市值')
            wookbook.sheets.add('指数')
        index_wooksheet = wookbook.sheets['指数']
        index_wooksheet.clear()
        index_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = index
        marketvalue_wooksheet = wookbook.sheets['市值']
        marketvalue_wooksheet.clear()
        marketvalue_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = marketvalue
        valuation_wooksheet = wookbook.sheets['估值']
        valuation_wooksheet.clear()
        valuation_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = valuation
        finance_wooksheet = wookbook.sheets['财务']
        finance_wooksheet.clear()
        finance_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = finance
        consensus_wooksheet = wookbook.sheets['一致预期']
        consensus_wooksheet.clear()
        consensus_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = consensus
        fundholding_wooksheet = wookbook.sheets['基金持仓']
        fundholding_wooksheet.clear()
        fundholding_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = fundholding
        sentiment_wooksheet = wookbook.sheets['情绪']
        sentiment_wooksheet.clear()
        sentiment_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = sentiment
        wookbook.save(filename)
        wookbook.close()
        app.quit()
        return


class IndustryStockFinance:
    def __init__(self, industry_name, start_date, end_date, report_date, data_path):
        self.industry_name = industry_name
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date
        self.data_path = data_path
        self.industry_universe = pd.read_excel('{0}{1}/{2}_信息.xlsx'.format(self.data_path, self.industry_name, self.industry_name), sheet_name='股票池')
        self.industry_universe.columns = ['SUB_SECTOR', 'SEC_SHORT_NAME', 'TICKER_SYMBOL', 'HK_STOCK']
        self.industry_universe['IDX'] = range(len(self.industry_universe))
        self.industry_universe_A = self.industry_universe[self.industry_universe['HK_STOCK'] == 0]
        self.industry_universe_A['TICKER_SYMBOL'] = self.industry_universe_A['TICKER_SYMBOL'].apply(lambda x: str(x).zfill(6))
        self.industry_universe_HK = self.industry_universe[self.industry_universe['HK_STOCK'] == 1]
        self.industry_universe_HK['TICKER_SYMBOL'] = self.industry_universe_HK['TICKER_SYMBOL'].apply(lambda x: str(x).zfill(4) + '.HK')
        self.industry_universe = pd.concat([self.industry_universe_A, self.industry_universe_HK])
        self.industry_universe = self.industry_universe.sort_values('IDX').drop('IDX', axis=1)
        self.load()

    def load(self):
        # 日历
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

        stock_finance_A_path = '{0}stock_finance_A.hdf'.format(self.data_path)
        if os.path.isfile(stock_finance_A_path):
            existed_stock_finance_A = pd.read_hdf(stock_finance_A_path, key='table')
            max_date = max(existed_stock_finance_A['END_DATE'])
            start_date = max(str(max_date), '20071231')
        else:
            existed_stock_finance_A = pd.DataFrame()
            start_date = '20071231'
        report_df = self.report_df[(self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.report_date)]
        stock_finance_A_list = []
        for date in report_df['REPORT_DATE'].unique().tolist():
            stock_finance_A_date = HBDB().read_stock_finance_jy3(date)
            star_stock_finance_A_date = HBDB().read_star_stock_finance_jy3(date)
            stock_finance_A_date = pd.concat([stock_finance_A_date, star_stock_finance_A_date])
            stock_finance_A_list.append(stock_finance_A_date)
            print(date)
        self.stock_finance_A = pd.concat([existed_stock_finance_A] + stock_finance_A_list, ignore_index=True)
        self.stock_finance_A.to_hdf(stock_finance_A_path, key='table', mode='w')
        self.stock_finance_A = pd.read_hdf(stock_finance_A_path, key='table')
        self.stock_finance_A = self.stock_finance_A.rename(
            columns={'EPSTTM'.upper(): '每股收益_TTM(元／股)', 'NetAssetPS'.upper(): '每股净资产(元／股)', 'OperatingRevenuePSTTM'.upper(): '每股营业收入_TTM(元／股)', 'CashFlowPSTTM'.upper(): '每股现金流量净额_TTM(元／股)',
                     'ROATTM'.upper(): '总资产收益率_TTM(%)', 'ROETTM'.upper(): '净资产收益率_TTM(%)', 'ROICTTM'.upper(): '投入资本回报率_TTM(%)', 'GrossIncomeRatioTTM'.upper(): '销售毛利率_TTM(%)', 'NetProfitRatioTTM'.upper(): '销售净利率_TTM(%)',
                     'CurrentRatio'.upper(): '流动比率', 'QuickRatio'.upper(): '速动比率', 'InterestCover'.upper(): '利息保障倍数(倍)', 'DebtAssetsRatio'.upper(): '资产负债率(%)',
                     'OperatingRevenueGrowRate'.upper(): '营业收入同比增长(%)',  'NPParentCompanyYOY'.upper(): '归属母公司股东的净利润同比增长(%)', 'NetOperateCashFlowYOY'.upper(): '经营活动产生的现金流量净额同比增长(%)', 'NetAssetGrowRate'.upper(): '净资产同比增长(%)', 'FAExpansionRate'.upper(): '固定资产投资扩张率(%)',
                     'InventoryTRate'.upper(): '存货周转率(次)', 'ARTRate'.upper(): '应收账款周转率(次)', 'TotalAssetTRate'.upper(): '总资产周转率(次)', 'WorkingCaitalTRate'.upper(): '营运资本周转率(次)',
                     'CashRateOfSalesTTM'.upper(): '经营活动产生的现金流量净额／营业收入_TTM(%)', 'CapitalExpenditureToDM'.upper(): '资本支出／折旧和摊销', 'OperCashInToAsset'.upper(): '总资产现金回收率(%)',
                     'DividendPaidRatio'.upper(): '股利支付率(%)', 'RetainedEarningRatio'.upper(): '留存盈余比率(%)'})
        self.stock_finance_A['END_DATE'] = self.stock_finance_A['END_DATE'].astype(str)
        self.stock_finance_A['PUBLISH_DATE'] = self.stock_finance_A['PUBLISH_DATE'].astype(str)
        self.stock_finance_A = self.stock_finance_A.sort_values(['TICKER_SYMBOL', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')
        self.stock_finance_A = self.stock_finance_A[['TICKER_SYMBOL', 'END_DATE',
            '每股收益_TTM(元／股)', '每股净资产(元／股)', '每股营业收入_TTM(元／股)', '每股现金流量净额_TTM(元／股)',
            '总资产收益率_TTM(%)', '净资产收益率_TTM(%)', '投入资本回报率_TTM(%)', '销售毛利率_TTM(%)', '销售净利率_TTM(%)',
            '流动比率', '速动比率', '利息保障倍数(倍)', '资产负债率(%)',
            '营业收入同比增长(%)', '归属母公司股东的净利润同比增长(%)', '经营活动产生的现金流量净额同比增长(%)', '净资产同比增长(%)', '固定资产投资扩张率(%)',
            '存货周转率(次)', '应收账款周转率(次)', '总资产周转率(次)', '营运资本周转率(次)',
            '经营活动产生的现金流量净额／营业收入_TTM(%)', '资本支出／折旧和摊销', '总资产现金回收率(%)',
            '股利支付率(%)', '留存盈余比率(%)']]

        if len(self.industry_universe_HK) != 0:
            stock_finance_HK_path = '{0}{1}/stock_finance_HK_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name)
            stock_finance_HK_list = []
            for ticker in self.industry_universe_HK['TICKER_SYMBOL'].unique().tolist():
                stock_finance_HK_ticker = w.wsd("{0}".format(ticker),
                    "eps_ttm,bps,orps_ttm,cfps_ttm,roa_ttm2,roe_ttm3,roic_ttm3,grossprofitmargin_ttm3,netprofitmargin_ttm3,wgsd_current,wgsd_quick,wgsd_ebittointerest,wgsd_debttoassets,wgsd_yoy_or,wgsd_yoynetprofit,wgsd_yoyocf,yoy_equity,yoy_fixedassets,wgsd_invturn,wgsd_arturn,wgsd_assetsturn,operatecaptialturn,ocftosales_ttm2,wgsd_capitalizedtoda,ocftoassets",
                    "{0}".format(datetime.strptime('20161231', "%Y%m%d").strftime("%Y-%m-%d")), "{0}".format(datetime.strptime(self.report_date, "%Y%m%d").strftime("%Y-%m-%d")), "unit=1;currencyType=;Period=Q", usedf=True)[1].reset_index()
                stock_finance_HK_ticker = stock_finance_HK_ticker.rename(columns={'index': 'END_DATE'})
                stock_finance_HK_ticker['END_DATE'] = stock_finance_HK_ticker['END_DATE'].apply(lambda x: x.strftime("%Y%m%d"))
                stock_finance_HK_ticker['TICKER_SYMBOL'] = ticker
                stock_finance_HK_list.append(stock_finance_HK_ticker)
            self.stock_finance_HK = pd.concat(stock_finance_HK_list)
            self.stock_finance_HK.to_hdf(stock_finance_HK_path, key='table', mode='w')
            self.stock_finance_HK = pd.read_hdf(stock_finance_HK_path, key='table')
            self.stock_finance_HK = self.stock_finance_HK.set_index(['TICKER_SYMBOL', 'END_DATE']).reset_index()
            self.stock_finance_HK.columns = ['TICKER_SYMBOL', 'END_DATE',
                '每股收益_TTM(元／股)', '每股净资产(元／股)', '每股营业收入_TTM(元／股)', '每股现金流量净额_TTM(元／股)',
                '总资产收益率_TTM(%)', '净资产收益率_TTM(%)', '投入资本回报率_TTM(%)', '销售毛利率_TTM(%)', '销售净利率_TTM(%)',
                '流动比率', '速动比率', '利息保障倍数(倍)', '资产负债率(%)',
                '营业收入同比增长(%)', '归属母公司股东的净利润同比增长(%)', '经营活动产生的现金流量净额同比增长(%)', '净资产同比增长(%)', '固定资产投资扩张率(%)',
                '存货周转率(次)', '应收账款周转率(次)', '总资产周转率(次)', '营运资本周转率(次)',
                '经营活动产生的现金流量净额／营业收入_TTM(%)', '资本支出／折旧和摊销', '总资产现金回收率(%)']
            self.stock_finance_HK['END_DATE'] = self.stock_finance_HK['END_DATE'].apply(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30')

        self.stock_finance = pd.concat([self.stock_finance_A, self.stock_finance_HK]) if len(self.industry_universe_HK) != 0 else self.stock_finance_A
        return

    def get_all(self):
        writer = pd.ExcelWriter('{0}{1}/{2}_个股财务数据.xlsx'.format(self.data_path, self.industry_name, self.industry_name))
        indic_list = list(self.stock_finance.columns)[2:-2]
        for indic in indic_list:
            industry_universe = self.industry_universe.copy(deep=True)
            indic_data = self.stock_finance[['TICKER_SYMBOL', 'END_DATE', indic]]
            indic_data[indic] = indic_data[indic].apply(lambda x: round(x, 2) if not pd.isna(x) else x)
            indic_data = indic_data.pivot(index='TICKER_SYMBOL', columns='END_DATE', values=indic)
            industry_universe = industry_universe.merge(indic_data, on=['TICKER_SYMBOL'], how='left')
            industry_universe = industry_universe.rename(columns={'SUB_SECTOR': '一级分类', 'SUB_SUB_SECTOR': '二级分类', 'SEC_SHORT_NAME': '公司名称', 'TICKER_SYMBOL': '代码', 'HK_STOCK': '是否港股'})
            industry_universe.to_excel(writer, sheet_name=indic)
        writer.save()
        return


class IndustryFinance:
    def __init__(self, industry_name, start_date, end_date, report_date, data_path):
        self.industry_name = industry_name
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date
        self.data_path = data_path

    def get_all(self):
        if self.industry_name in ('光伏', '动力电池', '汽车', '半导体'):
            from hbshare.fe.industry.industry_finance.advanced_manufacturing import IndustryFinanceData
            IndustryFinanceData(self.industry_name, self.start_date, self.end_date, self.report_date, self.data_path).get_all()
        if self.industry_name in ('纺服'):
            from hbshare.fe.industry.industry_finance.textile_apparel import IndustryFinanceData
            IndustryFinanceData(self.industry_name, self.start_date, self.end_date, self.report_date, self.data_path).get_all()
        if self.industry_name in ('煤炭'):
            from hbshare.fe.industry.industry_finance.coal import IndustryFinanceData
            IndustryFinanceData(self.industry_name, self.start_date, self.end_date, self.report_date, self.data_path).get_all()
        if self.industry_name in ('火电'):
            from hbshare.fe.industry.industry_finance.thermal_electricity import IndustryFinanceData
            IndustryFinanceData(self.industry_name, self.start_date, self.end_date, self.report_date, self.data_path).get_all()
        return


class IndustryOverview:
    def __init__(self, industry_name, start_date, end_date, report_date, data_path):
        self.industry_name = industry_name
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date
        self.data_path = data_path
        self.adj_dict = {'光伏': 10, '动力电池': 10, '汽车': 20, '半导体': 50,
                         '纺服': 20, '煤炭':10, '火电':10}
        # 日历
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

    def get_all(self):
        industry_multa_filename = '{0}{1}/{2}_多维度数据.xlsx'.format(self.data_path, self.industry_name, self.industry_name)
        industry_finance_filename = '{0}{1}/{2}_关键财务数据.xlsx'.format(self.data_path, self.industry_name, self.industry_name)
        index = pd.read_excel(industry_multa_filename, sheet_name='指数', index_col=0)
        marketvalue = pd.read_excel(industry_multa_filename, sheet_name='市值', index_col=0)
        valuation = pd.read_excel(industry_multa_filename, sheet_name='估值', index_col=0)
        finance = pd.read_excel(industry_multa_filename, sheet_name='财务', index_col=0)
        consensus = pd.read_excel(industry_multa_filename, sheet_name='一致预期', index_col=0)
        fundholding = pd.read_excel(industry_multa_filename, sheet_name='基金持仓', index_col=0)
        sentiment = pd.read_excel(industry_multa_filename, sheet_name='情绪', index_col=0)
        industry_finance = pd.read_excel(industry_finance_filename, sheet_name='行业关键财务数据', index_col=0)
        index_Q = index.copy(deep=True)
        index_Q.index = map(lambda x: x.strftime('%Y%m%d'), index_Q.index)
        index_Q = index_Q[index_Q.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
        index_Q.index =map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30', index_Q.index)
        index_Q.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), index_Q.index)
        index_Q = index_Q * self.adj_dict[self.industry_name]
        index_Q = index_Q[['净值']].rename(columns={'净值': '净值（右轴）'})
        valuation_Q = valuation.copy(deep=True)
        valuation_Q.index = map(lambda x: x.strftime('%Y%m%d'), valuation_Q.index)
        valuation_Q = valuation_Q[valuation_Q.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
        valuation_Q.index =map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30', valuation_Q.index)
        valuation_Q.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), valuation_Q.index)
        valuation_Q = valuation_Q[['PE_TTM']].rename(columns={'PE_TTM': '估值（右轴）'})
        industry_finance = industry_finance.merge(index_Q, left_index=True, right_index=True, how='left').merge(valuation_Q, left_index=True, right_index=True, how='left')
        stock_finance = pd.read_excel(industry_finance_filename, sheet_name='个股关键财务数据', index_col=0)

        # 产业周期数据 & 多因子打分
        if self.industry_name in ('光伏', '动力电池', '汽车', '半导体'):
            industry_data = (index[['净值']] * 10).merge(valuation[['PE_TTM']], left_index=True, right_index=True,
                                                         how='left')
            industry_data.index = map(lambda x: x.strftime('%Y%m%d'), industry_data.index)
            industry_finance_data = industry_finance[['盈利增速', '资本开支增速', '产业链内部杠杆']]
            industry_finance_data.index = map(lambda x: x.strftime('%Y%m%d'), industry_finance_data.index)
            report_trade_df = self.report_trade_df.copy(deep=True)
            report_trade_df['REPORT_DATE'] = report_trade_df['TRADE_DATE'].apply(
                lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30')
            industry_finance_data = industry_finance_data.merge(
                report_trade_df.set_index('REPORT_DATE')[['TRADE_DATE']], left_index=True, right_index=True,
                how='left').set_index('TRADE_DATE')
            industry_data = industry_data.merge(industry_finance_data, left_index=True, right_index=True, how='left')
            industry_data['盈利增速（右轴）'] = industry_data['盈利增速'].interpolate()
            industry_data['资本开支增速（右轴）'] = industry_data['资本开支增速'].interpolate()
            industry_data['产业链内部杠杆（右轴）'] = industry_data['产业链内部杠杆'].interpolate()
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['盈利增速']).index[-1], '盈利增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['资本开支增速']).index[-1], '资本开支增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['产业链内部杠杆']).index[-1], '产业链内部杠杆（右轴）'] = np.nan
            industry_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), industry_data.index)

            ##################
            score_pettm = valuation[['PE_TTM']].copy(deep=True)
            score_pettm['IDX'] = range(len(score_pettm))
            score_pettm['PE_TTM_分位水平'] = score_pettm['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, 'PE_TTM', score_pettm))
            score_pettm['PE_TTM'] = score_pettm['PE_TTM_分位水平'].apply(lambda
                                                                             x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_pettm.index = map(lambda x: x.strftime('%Y%m%d'), score_pettm.index)
            score_pettm = score_pettm[score_pettm.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_pettm.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                    score_pettm.index)
            score_pettm.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_pettm.index)
            ##################
            score_pblf = valuation[['PB_LF']].copy(deep=True)
            score_pblf['IDX'] = range(len(score_pblf))
            score_pblf['PB_LF_分位水平'] = score_pblf['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, 'PB_LF', score_pblf))
            score_pblf['PB_LF'] = score_pblf['PB_LF_分位水平'].apply(lambda
                                                                         x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_pblf.index = map(lambda x: x.strftime('%Y%m%d'), score_pblf.index)
            score_pblf = score_pblf[score_pblf.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_pblf.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                   score_pblf.index)
            score_pblf.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_pblf.index)
            ##################
            score_sentiment = sentiment[['成交额占比（%）', '换手率（%）', '创60日新高个股占行业内个股比例（%）',
                                         '20日均线上个股占行业内个股比例（%）']].copy(deep=True)
            score_sentiment['IDX'] = range(len(score_sentiment))
            score_sentiment['成交额占比（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '成交额占比（%）', score_sentiment))
            score_sentiment['换手率（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '换手率（%）', score_sentiment))
            score_sentiment['创60日新高个股占行业内个股比例（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '创60日新高个股占行业内个股比例（%）', score_sentiment))
            score_sentiment['20日均线上个股占行业内个股比例（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '20日均线上个股占行业内个股比例（%）', score_sentiment))
            score_sentiment['拥挤度_分位水平'] = score_sentiment[
                ['成交额占比（%）_分位水平', '换手率（%）_分位水平', '创60日新高个股占行业内个股比例（%）_分位水平',
                 '20日均线上个股占行业内个股比例（%）_分位水平']].mean(axis=1)
            score_sentiment['拥挤度'] = score_sentiment['拥挤度_分位水平'].apply(lambda
                                                                                     x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_sentiment.index = map(lambda x: x.strftime('%Y%m%d'), score_sentiment.index)
            score_sentiment = score_sentiment[
                score_sentiment.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_sentiment.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                        score_sentiment.index)
            score_sentiment.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_sentiment.index)
            ##################
            score_fundholding = fundholding[['持仓市值占比（%）']].copy(deep=True)
            score_fundholding['IDX'] = range(len(score_fundholding))
            score_fundholding['持仓市值占比（%）_分位水平'] = score_fundholding['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '持仓市值占比（%）', score_fundholding))
            score_fundholding['公募持仓'] = score_fundholding['持仓市值占比（%）_分位水平'].apply(lambda
                                                                                                    x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_earnings = finance[['ROE_TTM（%）', '销售毛利率（%）', '销售净利率（%）']].copy(deep=True)
            score_earnings['IDX'] = range(len(score_earnings))
            score_earnings['ROE_TTM（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, 'ROE_TTM（%）', score_earnings))
            score_earnings['销售毛利率（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '销售毛利率（%）', score_earnings))
            score_earnings['销售净利率（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '销售净利率（%）', score_earnings))
            score_earnings['盈利_分位水平'] = score_earnings[
                ['ROE_TTM（%）_分位水平', '销售毛利率（%）_分位水平', '销售净利率（%）_分位水平']].mean(axis=1)
            score_earnings['盈利'] = score_earnings['盈利_分位水平'].apply(lambda
                                                                               x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_growth = industry_finance[['营收增速', '盈利增速']].copy(deep=True)
            score_growth['IDX'] = range(len(score_growth))
            score_growth['营收增速_分位水平'] = score_growth['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '营收增速', score_growth))
            score_growth['盈利增速_分位水平'] = score_growth['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '盈利增速', score_growth))
            score_growth['成长_分位水平'] = score_growth[['营收增速_分位水平', '盈利增速_分位水平']].mean(axis=1)
            score_growth['成长'] = score_growth['成长_分位水平'].apply(lambda
                                                                           x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_capex = industry_finance[['资本开支增速', 'CAPEX / DA']].copy(deep=True)
            score_capex['IDX'] = range(len(score_capex))
            score_capex['资本开支增速_分位水平'] = score_capex['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '资本开支增速', score_capex))
            score_capex['CAPEX / DA_分位水平'] = score_capex['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, 'CAPEX / DA', score_capex))
            score_capex['资本开支_分位水平'] = score_capex[['资本开支增速_分位水平', 'CAPEX / DA_分位水平']].mean(
                axis=1)
            score_capex['资本开支'] = score_capex['资本开支_分位水平'].apply(lambda
                                                                                 x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_rd = industry_finance[['研发增速', '研发投入占比']].copy(deep=True)
            score_rd['IDX'] = range(len(score_rd))
            score_rd['研发增速_分位水平'] = score_rd['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '研发增速', score_rd))
            score_rd['研发投入占比_分位水平'] = score_rd['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '研发投入占比', score_rd))
            score_rd['研发投入_分位水平'] = score_rd[['研发增速_分位水平', '研发投入占比_分位水平']].mean(axis=1)
            score_rd['研发投入'] = score_rd['研发投入_分位水平'].apply(lambda
                                                                           x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_innerleverage = industry_finance[['产业链内部杠杆']].copy(deep=True)
            score_innerleverage['IDX'] = range(len(score_innerleverage))
            score_innerleverage['产业链内部杠杆_分位水平'] = score_innerleverage['IDX'].rolling(5).apply(
                lambda x: quantile_definition(x, '产业链内部杠杆', score_innerleverage))
            score_innerleverage['内部杠杆'] = score_innerleverage['产业链内部杠杆_分位水平'].apply(lambda
                                                                                                       x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_cashflow = finance[['经营活动产生的现金流量净额/营业收入_TTM(%)']].copy(deep=True)
            score_cashflow['IDX'] = range(len(score_cashflow))
            score_cashflow['经营活动产生的现金流量净额/营业收入_TTM(%)_分位水平'] = score_cashflow['IDX'].rolling(
                5).apply(lambda x: quantile_definition(x, '经营活动产生的现金流量净额/营业收入_TTM(%)', score_cashflow))
            score_cashflow['现金流'] = score_cashflow['经营活动产生的现金流量净额/营业收入_TTM(%)_分位水平'].apply(
                lambda
                    x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_data = pd.concat([score_pettm[['PE_TTM']], score_pblf[['PB_LF']], score_sentiment[['拥挤度']],
                                    score_fundholding[['公募持仓']], score_earnings[['盈利']], score_growth[['成长']],
                                    score_capex[['资本开支']], score_rd[['研发投入']],
                                    score_innerleverage[['内部杠杆']], score_cashflow[['现金流']]], axis=1)
            score_data = score_data.dropna(how='all').fillna('-')

        elif self.industry_name in ('纺服'):
            industry_data = (index[['净值']] * self.adj_dict[self.industry_name]).merge(valuation[['PE_TTM']], left_index=True, right_index=True, how='left')
            industry_data.index = map(lambda x: x.strftime('%Y%m%d'), industry_data.index)
            industry_finance_data = industry_finance[['营收增速','销售费用 / 营业收入', '盈利增速' ,'存货周转率','应收账款周转率','流动比率','速动比率',]]
            industry_finance_data.index =map(lambda x: x.strftime('%Y%m%d'), industry_finance_data.index)
            report_trade_df = self.report_trade_df.copy(deep=True)
            report_trade_df['REPORT_DATE'] = report_trade_df['TRADE_DATE'].apply(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30')
            industry_finance_data = industry_finance_data.merge(report_trade_df.set_index('REPORT_DATE')[['TRADE_DATE']], left_index=True, right_index=True, how='left').set_index('TRADE_DATE')
            industry_data = industry_data.merge(industry_finance_data, left_index=True, right_index=True, how='left')
            industry_data.loc[industry_data[industry_data['盈利增速']>5].index,'盈利增速'] = np.nan #由于ttm的处理方法，使得盈利增速在某些时点非常大（分母小导致的）,去掉极端值
            industry_data['营收增速（右轴）'] = industry_data['营收增速'].interpolate()
            industry_data['盈利增速（右轴）'] = industry_data['盈利增速'].interpolate()
            industry_data['销售费用 / 营业收入（右轴）'] = industry_data['销售费用 / 营业收入'].interpolate()
            industry_data['存货周转率（右轴）'] = industry_data['存货周转率'].interpolate()
            industry_data['应收账款周转率（右轴）'] = industry_data['应收账款周转率'].interpolate()
            industry_data['流动比率（右轴）'] = industry_data['流动比率'].interpolate()
            industry_data['速动比率（右轴）'] = industry_data['速动比率'].interpolate()
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['营收增速']).index[-1], '营收增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['盈利增速']).index[-1], '盈利增速（右轴）'] = np.nan
            # industry_data['盈利增速'] = industry_data['盈利增速'].rolling(window=500).mean() #由于ttm的处理方法，使得盈利增速在某些时点非常大（分母小导致的），平滑掉极端值
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['销售费用 / 营业收入']).index[-1], '销售费用 / 营业收入（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['存货周转率']).index[-1], '存货周转率（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['应收账款周转率']).index[-1], '应收账款周转率（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['流动比率']).index[-1], '流动比率（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['速动比率']).index[-1], '速动比率（右轴）'] = np.nan

            #计算超额收益率净值曲线881001
            sql = '''
                select cast(jyrq as char) as date, spjg 最新价 from st_market.t_st_zs_hqql
                where  zqdm = '881001'
                '''
            windA_trade_data = HBDB().get_df(sql, "alluser", page_size=5000)
            windA_trade_data['wind_ret'] = windA_trade_data['最新价'].pct_change()
            industry_data = industry_data.reset_index().rename(columns = {'index':'date'})
            industry_data = pd.merge(industry_data,windA_trade_data[['date','wind_ret']],how ='left' , on =['date'])
            industry_data['ret'] = industry_data['净值'].pct_change()
            industry_data['excess_ret'] = industry_data['ret'] - industry_data['wind_ret']
            industry_data['超额净值'] = np.nan
            industry_data.loc[0,'超额净值'] = 1
            for i in industry_data.index[1:]:
                industry_data.loc[i,'超额净值'] = industry_data.loc[i-1,'超额净值'] * (1+  industry_data.loc[i,'excess_ret'])

            industry_data['超额净值'] = industry_data['超额净值'] * self.adj_dict[self.industry_name]
            industry_data = industry_data.set_index('date')
            industry_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), industry_data.index)

            ##################
            score_pettm = valuation[['PE_TTM']].copy(deep=True)
            score_pettm['IDX'] = range(len(score_pettm))
            score_pettm['PE_TTM_分位水平'] = score_pettm['IDX'].rolling(250).apply(lambda x: quantile_definition(x, 'PE_TTM', score_pettm))
            score_pettm['PE_TTM'] = score_pettm['PE_TTM_分位水平'].apply(lambda x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_pettm.index = map(lambda x: x.strftime('%Y%m%d'), score_pettm.index)
            score_pettm = score_pettm[score_pettm.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_pettm.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30', score_pettm.index)
            score_pettm.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_pettm.index)
            ##################
            score_pblf = valuation[['PB_LF']].copy(deep=True)
            score_pblf['IDX'] = range(len(score_pblf))
            score_pblf['PB_LF_分位水平'] = score_pblf['IDX'].rolling(250).apply(lambda x: quantile_definition(x, 'PB_LF', score_pblf))
            score_pblf['PB_LF'] = score_pblf['PB_LF_分位水平'].apply(lambda x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_pblf.index = map(lambda x: x.strftime('%Y%m%d'), score_pblf.index)
            score_pblf = score_pblf[score_pblf.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_pblf.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30', score_pblf.index)
            score_pblf.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_pblf.index)
            ##################
            score_sentiment = sentiment[['成交额占比（%）', '换手率（%）', '创60日新高个股占行业内个股比例（%）', '20日均线上个股占行业内个股比例（%）']].copy(deep=True)
            score_sentiment['IDX'] = range(len(score_sentiment))
            score_sentiment['成交额占比（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '成交额占比（%）', score_sentiment))
            score_sentiment['换手率（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '换手率（%）', score_sentiment))
            score_sentiment['创60日新高个股占行业内个股比例（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '创60日新高个股占行业内个股比例（%）', score_sentiment))
            score_sentiment['20日均线上个股占行业内个股比例（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '20日均线上个股占行业内个股比例（%）', score_sentiment))
            score_sentiment['拥挤度_分位水平'] = score_sentiment[['成交额占比（%）_分位水平', '换手率（%）_分位水平', '创60日新高个股占行业内个股比例（%）_分位水平', '20日均线上个股占行业内个股比例（%）_分位水平']].mean(axis=1)
            score_sentiment['拥挤度'] = score_sentiment['拥挤度_分位水平'].apply(lambda x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_sentiment.index = map(lambda x: x.strftime('%Y%m%d'), score_sentiment.index)
            score_sentiment = score_sentiment[score_sentiment.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_sentiment.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30', score_sentiment.index)
            score_sentiment.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_sentiment.index)
            ##################
            score_fundholding = fundholding[['持仓市值占比（%）']].copy(deep=True)
            score_fundholding['IDX'] = range(len(score_fundholding))
            score_fundholding['持仓市值占比（%）_分位水平'] = score_fundholding['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '持仓市值占比（%）', score_fundholding))
            score_fundholding['公募持仓'] = score_fundholding['持仓市值占比（%）_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_earnings = finance[['ROE_TTM（%）', '销售毛利率（%）', '销售净利率（%）']].copy(deep=True)
            score_earnings['IDX'] = range(len(score_earnings))
            score_earnings['ROE_TTM（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, 'ROE_TTM（%）', score_earnings))
            score_earnings['销售毛利率（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '销售毛利率（%）', score_earnings))
            score_earnings['销售净利率（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '销售净利率（%）', score_earnings))
            score_earnings['盈利_分位水平'] = score_earnings[['ROE_TTM（%）_分位水平', '销售毛利率（%）_分位水平', '销售净利率（%）_分位水平']].mean(axis=1)
            score_earnings['盈利'] = score_earnings['盈利_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_growth = industry_finance[['营收增速', '盈利增速']].copy(deep=True)
            score_growth['IDX'] = range(len(score_growth))
            score_growth['营收增速_分位水平'] = score_growth['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '营收增速', score_growth))
            score_growth['盈利增速_分位水平'] = score_growth['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '盈利增速', score_growth))
            score_growth['成长_分位水平'] = score_growth[['营收增速_分位水平','盈利增速_分位水平']].mean(axis=1)
            score_growth['成长'] = score_growth['成长_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_sale_exp = industry_finance[['销售费用 / 营业收入']].copy(deep=True)
            score_sale_exp['IDX'] = range(len(score_sale_exp))
            score_sale_exp['销售费用 / 营业收入_分位水平'] = score_sale_exp['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '销售费用 / 营业收入', score_sale_exp))
            score_sale_exp['销售费用占比_分位水平'] = score_sale_exp[['销售费用 / 营业收入_分位水平']].mean(axis=1)
            score_sale_exp['营销'] = score_sale_exp['销售费用占比_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_efficiency = industry_finance[['存货周转率', '应收账款周转率']].copy(deep=True)
            score_efficiency['IDX'] = range(len(score_efficiency))
            score_efficiency['存货周转率_分位水平'] = score_efficiency['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '存货周转率', score_efficiency))
            score_efficiency['应收账款周转率_分位水平'] = score_efficiency['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '应收账款周转率', score_efficiency))
            score_efficiency['营运效率_分位水平'] = score_efficiency[['存货周转率_分位水平', '应收账款周转率_分位水平']].mean(axis=1)
            score_efficiency['营运效率'] = score_efficiency['营运效率_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_liquidity = industry_finance[['流动比率', '速动比率']].copy(deep=True)
            score_liquidity['IDX'] = range(len(score_liquidity))
            score_liquidity['流动比率_分位水平'] = score_liquidity['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '流动比率', score_liquidity))
            score_liquidity['速动比率_分位水平'] = score_liquidity['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '速动比率', score_liquidity))
            score_liquidity['流动性_分位水平'] = score_liquidity[['流动比率_分位水平', '速动比率_分位水平']].mean(axis=1)
            score_liquidity['流动性'] = score_liquidity['流动性_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_cashflow = finance[['经营活动产生的现金流量净额/营业收入_TTM(%)']].copy(deep=True)
            score_cashflow['IDX'] = range(len(score_cashflow))
            score_cashflow['经营活动产生的现金流量净额/营业收入_TTM(%)_分位水平'] = score_cashflow['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '经营活动产生的现金流量净额/营业收入_TTM(%)', score_cashflow))
            score_cashflow['现金流'] = score_cashflow['经营活动产生的现金流量净额/营业收入_TTM(%)_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_data = pd.concat([score_pettm[['PE_TTM']], score_pblf[['PB_LF']], score_sentiment[['拥挤度']], score_fundholding[['公募持仓']], score_earnings[['盈利']], score_growth[['成长']], score_efficiency[['营运效率']], score_liquidity[['流动性']],score_sale_exp[['营销']], score_cashflow[['现金流']]], axis=1)
            score_data = score_data.dropna(how='all').fillna('-')

        elif self.industry_name in ('煤炭'):
            industry_data = (index[['净值']] * self.adj_dict[self.industry_name]).merge(valuation[['PE_TTM']], left_index=True, right_index=True,how='left')
            industry_data.index = map(lambda x: x.strftime('%Y%m%d'), industry_data.index)
            industry_finance_data = industry_finance[['盈利增速', '资本开支增速', '营收增速','固定资产占比','CAPEX / DA','存货周转率','存货 / 总资产','资本开支 / 营业收入']]
            industry_finance_data.index = map(lambda x: x.strftime('%Y%m%d'), industry_finance_data.index)
            report_trade_df = self.report_trade_df.copy(deep=True)
            report_trade_df['REPORT_DATE'] = report_trade_df['TRADE_DATE'].apply(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30')
            industry_finance_data = industry_finance_data.merge(report_trade_df.set_index('REPORT_DATE')[['TRADE_DATE']], left_index=True, right_index=True,how='left').set_index('TRADE_DATE')
            industry_data = industry_data.merge(industry_finance_data, left_index=True, right_index=True, how='left')
            industry_data['盈利增速（右轴）'] = industry_data['盈利增速'].interpolate()
            industry_data['资本开支增速（右轴）'] = industry_data['资本开支增速'].interpolate()
            industry_data['营收增速（右轴）'] = industry_data['营收增速'].interpolate()
            industry_data['固定资产占比（右轴）'] = industry_data['固定资产占比'].interpolate()
            industry_data['CAPEX / DA（右轴）'] = industry_data['CAPEX / DA'].interpolate()
            industry_data['存货周转率（右轴）'] = industry_data['存货周转率'].interpolate()
            industry_data['存货 / 总资产（右轴）'] = industry_data['存货 / 总资产'].interpolate()
            industry_data['资本开支 / 营业收入（右轴）'] = industry_data['资本开支 / 营业收入'].interpolate()
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['盈利增速']).index[-1], '盈利增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['资本开支增速']).index[-1], '资本开支增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['营收增速']).index[-1], '营收增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['固定资产占比']).index[-1], '固定资产占比（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['CAPEX / DA']).index[-1], 'CAPEX / DA（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['存货周转率']).index[-1], '存货周转率（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['存货 / 总资产']).index[-1], '存货 / 总资产（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['资本开支 / 营业收入']).index[-1], '资本开支 / 营业收入（右轴）'] = np.nan
            # 计算超额收益率净值曲线881001
            sql = '''
                        select cast(jyrq as char) as date, spjg 最新价 from st_market.t_st_zs_hqql
                        where  zqdm = '881001'
                        '''
            windA_trade_data = HBDB().get_df(sql, "alluser", page_size=5000)
            windA_trade_data['wind_ret'] = windA_trade_data['最新价'].pct_change()
            industry_data = industry_data.reset_index().rename(columns={'index': 'date'})
            industry_data = pd.merge(industry_data, windA_trade_data[['date', 'wind_ret']], how='left', on=['date'])
            industry_data['ret'] = industry_data['净值'].pct_change()
            industry_data['excess_ret'] = industry_data['ret'] - industry_data['wind_ret']
            industry_data['超额净值'] = np.nan
            industry_data.loc[0, '超额净值'] = 1
            for i in industry_data.index[1:]:
                industry_data.loc[i, '超额净值'] = industry_data.loc[i - 1, '超额净值'] * (
                            1 + industry_data.loc[i, 'excess_ret'])
            industry_data['超额净值'] = industry_data['超额净值'] * self.adj_dict[self.industry_name]
            industry_data = industry_data.set_index('date')
            industry_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), industry_data.index)

            ##################
            score_pettm = valuation[['PE_TTM']].copy(deep=True)
            score_pettm['IDX'] = range(len(score_pettm))
            score_pettm['PE_TTM_分位水平'] = score_pettm['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, 'PE_TTM', score_pettm))
            score_pettm['PE_TTM'] = score_pettm['PE_TTM_分位水平'].apply(lambda
                                                                             x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_pettm.index = map(lambda x: x.strftime('%Y%m%d'), score_pettm.index)
            score_pettm = score_pettm[score_pettm.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_pettm.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                    score_pettm.index)
            score_pettm.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_pettm.index)
            ##################
            score_pblf = valuation[['PB_LF']].copy(deep=True)
            score_pblf['IDX'] = range(len(score_pblf))
            score_pblf['PB_LF_分位水平'] = score_pblf['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, 'PB_LF', score_pblf))
            score_pblf['PB_LF'] = score_pblf['PB_LF_分位水平'].apply(lambda
                                                                         x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_pblf.index = map(lambda x: x.strftime('%Y%m%d'), score_pblf.index)
            score_pblf = score_pblf[score_pblf.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_pblf.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                   score_pblf.index)
            score_pblf.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_pblf.index)
            ##################
            score_sentiment = sentiment[['成交额占比（%）', '换手率（%）', '创60日新高个股占行业内个股比例（%）',
                                         '20日均线上个股占行业内个股比例（%）']].copy(deep=True)
            score_sentiment['IDX'] = range(len(score_sentiment))
            score_sentiment['成交额占比（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '成交额占比（%）', score_sentiment))
            score_sentiment['换手率（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '换手率（%）', score_sentiment))
            score_sentiment['创60日新高个股占行业内个股比例（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '创60日新高个股占行业内个股比例（%）', score_sentiment))
            score_sentiment['20日均线上个股占行业内个股比例（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '20日均线上个股占行业内个股比例（%）', score_sentiment))
            score_sentiment['拥挤度_分位水平'] = score_sentiment[
                ['成交额占比（%）_分位水平', '换手率（%）_分位水平', '创60日新高个股占行业内个股比例（%）_分位水平',
                 '20日均线上个股占行业内个股比例（%）_分位水平']].mean(axis=1)
            score_sentiment['拥挤度'] = score_sentiment['拥挤度_分位水平'].apply(lambda
                                                                                     x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_sentiment.index = map(lambda x: x.strftime('%Y%m%d'), score_sentiment.index)
            score_sentiment = score_sentiment[
                score_sentiment.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_sentiment.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                        score_sentiment.index)
            score_sentiment.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_sentiment.index)
            ##################
            score_fundholding = fundholding[['持仓市值占比（%）']].copy(deep=True)
            score_fundholding['IDX'] = range(len(score_fundholding))
            score_fundholding['持仓市值占比（%）_分位水平'] = score_fundholding['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '持仓市值占比（%）', score_fundholding))
            score_fundholding['公募持仓'] = score_fundholding['持仓市值占比（%）_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_earnings = finance[['ROE_TTM（%）', '销售毛利率（%）', '销售净利率（%）']].copy(deep=True)
            score_earnings['IDX'] = range(len(score_earnings))
            score_earnings['ROE_TTM（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, 'ROE_TTM（%）', score_earnings))
            score_earnings['销售毛利率（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '销售毛利率（%）', score_earnings))
            score_earnings['销售净利率（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '销售净利率（%）', score_earnings))
            score_earnings['盈利_分位水平'] = score_earnings[['ROE_TTM（%）_分位水平', '销售毛利率（%）_分位水平', '销售净利率（%）_分位水平']].mean(axis=1)
            score_earnings['盈利'] = score_earnings['盈利_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_growth = industry_finance[['营收增速', '盈利增速']].copy(deep=True)
            score_growth['IDX'] = range(len(score_growth))
            score_growth['营收增速_分位水平'] = score_growth['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '营收增速', score_growth))
            score_growth['盈利增速_分位水平'] = score_growth['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '盈利增速', score_growth))
            score_growth['成长_分位水平'] = score_growth[['营收增速_分位水平', '盈利增速_分位水平']].mean(axis=1)
            score_growth['成长'] = score_growth['成长_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_capex = industry_finance[['资本开支增速', 'CAPEX / DA','资本开支 / 营业收入']].copy(deep=True)
            score_capex['IDX'] = range(len(score_capex))
            score_capex['资本开支增速_分位水平'] = score_capex['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '资本开支增速', score_capex))
            score_capex['CAPEX / DA_分位水平'] = score_capex['IDX'].rolling(5).apply(lambda x: quantile_definition(x, 'CAPEX / DA', score_capex))
            score_capex['资本开支 / 营业收入_分位水平'] = score_capex['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '资本开支 / 营业收入', score_capex))
            score_capex['资本开支_分位水平'] = score_capex[['资本开支增速_分位水平', 'CAPEX / DA_分位水平','资本开支 / 营业收入_分位水平']].mean(axis=1)
            score_capex['资本开支'] = score_capex['资本开支_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_efficiency = industry_finance[['存货周转率']].copy(deep=True)
            score_efficiency['IDX'] = range(len(score_efficiency))
            score_efficiency['存货周转率_分位水平'] = score_efficiency['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '存货周转率', score_efficiency))
            score_efficiency['存货周转_分位水平'] = score_efficiency[['存货周转率_分位水平']].mean(axis=1)
            score_efficiency['存货周转'] = score_efficiency['存货周转_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_cashflow = finance[['经营活动产生的现金流量净额/营业收入_TTM(%)']].copy(deep=True)
            score_cashflow['IDX'] = range(len(score_cashflow))
            score_cashflow['经营活动产生的现金流量净额/营业收入_TTM(%)_分位水平'] = score_cashflow['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '经营活动产生的现金流量净额/营业收入_TTM(%)', score_cashflow))
            score_cashflow['现金流'] = score_cashflow['经营活动产生的现金流量净额/营业收入_TTM(%)_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_data = pd.concat([score_pettm[['PE_TTM']], score_pblf[['PB_LF']], score_sentiment[['拥挤度']],
                                    score_fundholding[['公募持仓']], score_earnings[['盈利']], score_growth[['成长']],
                                    score_capex[['资本开支']],score_efficiency['存货周转'],
                                     score_cashflow[['现金流']]], axis=1)
            score_data = score_data.dropna(how='all').fillna('-')

        elif self.industry_name in ('火电'):
            industry_data = (index[['净值']] * self.adj_dict[self.industry_name]).merge(valuation[['PE_TTM']], left_index=True, right_index=True,how='left')
            industry_data.index = map(lambda x: x.strftime('%Y%m%d'), industry_data.index)
            industry_finance_data = industry_finance[['营收增速', '毛利增速', '盈利增速','营业成本增速','CAPEX / DA','应付股利 / 流通股数','资本开支增速']]
            industry_finance_data.index = map(lambda x: x.strftime('%Y%m%d'), industry_finance_data.index)
            report_trade_df = self.report_trade_df.copy(deep=True)
            report_trade_df['REPORT_DATE'] = report_trade_df['TRADE_DATE'].apply(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30')
            industry_finance_data = industry_finance_data.merge(report_trade_df.set_index('REPORT_DATE')[['TRADE_DATE']], left_index=True, right_index=True,how='left').set_index('TRADE_DATE')
            industry_data = industry_data.merge(industry_finance_data, left_index=True, right_index=True, how='left')
            industry_data['营收增速（右轴）'] = industry_data['营收增速'].interpolate()
            industry_data['毛利增速（右轴）'] = industry_data['毛利增速'].interpolate()
            industry_data['盈利增速（右轴）'] = industry_data['盈利增速'].interpolate()
            industry_data['营业成本增速（右轴）'] = industry_data['营业成本增速'].interpolate()
            industry_data['CAPEX / DA（右轴）'] = industry_data['CAPEX / DA'].interpolate()
            industry_data['应付股利 / 流通股数（右轴）'] = industry_data['应付股利 / 流通股数'].interpolate()
            industry_data['资本开支增速（右轴）'] = industry_data['资本开支增速'].interpolate()
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['营收增速']).index[-1], '营收增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['毛利增速']).index[-1], '毛利增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['盈利增速']).index[-1], '盈利增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['营业成本增速']).index[-1], '营业成本增速（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['CAPEX / DA']).index[-1], 'CAPEX / DA（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['应付股利 / 流通股数']).index[-1], '应付股利 / 流通股数（右轴）'] = np.nan
            industry_data.loc[industry_data.index > industry_data.dropna(subset=['资本开支增速']).index[-1], '资本开支增速（右轴）'] = np.nan
            # 计算超额收益率净值曲线881001
            sql = '''
                        select cast(jyrq as char) as date, spjg 最新价 from st_market.t_st_zs_hqql
                        where  zqdm = '881001'
                        '''
            windA_trade_data = HBDB().get_df(sql, "alluser", page_size=5000)
            windA_trade_data['wind_ret'] = windA_trade_data['最新价'].pct_change()
            industry_data = industry_data.reset_index().rename(columns={'index': 'date'})
            industry_data = pd.merge(industry_data, windA_trade_data[['date', 'wind_ret']], how='left', on=['date'])
            industry_data['ret'] = industry_data['净值'].pct_change()
            industry_data['excess_ret'] = industry_data['ret'] - industry_data['wind_ret']
            industry_data['超额净值'] = np.nan
            industry_data.loc[0, '超额净值'] = 1
            for i in industry_data.index[1:]:
                industry_data.loc[i, '超额净值'] = industry_data.loc[i - 1, '超额净值'] * (
                            1 + industry_data.loc[i, 'excess_ret'])
            industry_data['超额净值'] = industry_data['超额净值'] * self.adj_dict[self.industry_name]
            industry_data = industry_data.set_index('date')
            industry_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), industry_data.index)

            ##################
            score_pettm = valuation[['PE_TTM']].copy(deep=True)
            score_pettm['IDX'] = range(len(score_pettm))
            score_pettm['PE_TTM_分位水平'] = score_pettm['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, 'PE_TTM', score_pettm))
            score_pettm['PE_TTM'] = score_pettm['PE_TTM_分位水平'].apply(lambda
                                                                             x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_pettm.index = map(lambda x: x.strftime('%Y%m%d'), score_pettm.index)
            score_pettm = score_pettm[score_pettm.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_pettm.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                    score_pettm.index)
            score_pettm.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_pettm.index)
            ##################
            score_pblf = valuation[['PB_LF']].copy(deep=True)
            score_pblf['IDX'] = range(len(score_pblf))
            score_pblf['PB_LF_分位水平'] = score_pblf['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, 'PB_LF', score_pblf))
            score_pblf['PB_LF'] = score_pblf['PB_LF_分位水平'].apply(lambda
                                                                         x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_pblf.index = map(lambda x: x.strftime('%Y%m%d'), score_pblf.index)
            score_pblf = score_pblf[score_pblf.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_pblf.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                   score_pblf.index)
            score_pblf.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_pblf.index)
            ##################
            score_sentiment = sentiment[['成交额占比（%）', '换手率（%）', '创60日新高个股占行业内个股比例（%）',
                                         '20日均线上个股占行业内个股比例（%）']].copy(deep=True)
            score_sentiment['IDX'] = range(len(score_sentiment))
            score_sentiment['成交额占比（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '成交额占比（%）', score_sentiment))
            score_sentiment['换手率（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '换手率（%）', score_sentiment))
            score_sentiment['创60日新高个股占行业内个股比例（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '创60日新高个股占行业内个股比例（%）', score_sentiment))
            score_sentiment['20日均线上个股占行业内个股比例（%）_分位水平'] = score_sentiment['IDX'].rolling(250).apply(
                lambda x: quantile_definition(x, '20日均线上个股占行业内个股比例（%）', score_sentiment))
            score_sentiment['拥挤度_分位水平'] = score_sentiment[
                ['成交额占比（%）_分位水平', '换手率（%）_分位水平', '创60日新高个股占行业内个股比例（%）_分位水平',
                 '20日均线上个股占行业内个股比例（%）_分位水平']].mean(axis=1)
            score_sentiment['拥挤度'] = score_sentiment['拥挤度_分位水平'].apply(lambda
                                                                                     x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1 if x <= 1.0 else np.nan)
            score_sentiment.index = map(lambda x: x.strftime('%Y%m%d'), score_sentiment.index)
            score_sentiment = score_sentiment[
                score_sentiment.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
            score_sentiment.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30',
                                        score_sentiment.index)
            score_sentiment.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), score_sentiment.index)
            ##################
            score_fundholding = fundholding[['持仓市值占比（%）']].copy(deep=True)
            score_fundholding['IDX'] = range(len(score_fundholding))
            score_fundholding['持仓市值占比（%）_分位水平'] = score_fundholding['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '持仓市值占比（%）', score_fundholding))
            score_fundholding['公募持仓'] = score_fundholding['持仓市值占比（%）_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_earnings = finance[['ROE_TTM（%）', '销售毛利率（%）', '销售净利率（%）']].copy(deep=True)
            score_earnings['IDX'] = range(len(score_earnings))
            score_earnings['ROE_TTM（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, 'ROE_TTM（%）', score_earnings))
            score_earnings['销售毛利率（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '销售毛利率（%）', score_earnings))
            score_earnings['销售净利率（%）_分位水平'] = score_earnings['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '销售净利率（%）', score_earnings))
            score_earnings['盈利_分位水平'] = score_earnings[['ROE_TTM（%）_分位水平', '销售毛利率（%）_分位水平', '销售净利率（%）_分位水平']].mean(axis=1)
            score_earnings['盈利'] = score_earnings['盈利_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_growth = industry_finance[['营收增速','毛利增速', '盈利增速']].copy(deep=True)
            score_growth['IDX'] = range(len(score_growth))
            score_growth['营收增速_分位水平'] = score_growth['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '营收增速', score_growth))
            score_growth['毛利增速_分位水平'] = score_growth['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '毛利增速', score_growth))
            score_growth['盈利增速_分位水平'] = score_growth['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '盈利增速', score_growth))
            score_growth['成长_分位水平'] = score_growth[['营收增速_分位水平','毛利增速_分位水平','盈利增速_分位水平']].mean(axis=1)
            score_growth['成长'] = score_growth['成长_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_capex = industry_finance[['资本开支增速', 'CAPEX / DA']].copy(deep=True)
            score_capex['IDX'] = range(len(score_capex))
            score_capex['资本开支增速_分位水平'] = score_capex['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '资本开支增速', score_capex))
            score_capex['CAPEX / DA_分位水平'] = score_capex['IDX'].rolling(5).apply(lambda x: quantile_definition(x, 'CAPEX / DA', score_capex))
            score_capex['资本开支_分位水平'] = score_capex[['资本开支增速_分位水平', 'CAPEX / DA_分位水平']].mean(axis=1)
            score_capex['资本开支'] = score_capex['资本开支_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            # score_efficiency = industry_finance[['存货周转率']].copy(deep=True)
            # score_efficiency['IDX'] = range(len(score_efficiency))
            # score_efficiency['存货周转率_分位水平'] = score_efficiency['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '存货周转率', score_efficiency))
            # score_efficiency['存货周转_分位水平'] = score_efficiency[['存货周转率_分位水平']].mean(axis=1)
            # score_efficiency['存货周转'] = score_efficiency['存货周转_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            # ##################
            score_cashflow = finance[['经营活动产生的现金流量净额/营业收入_TTM(%)']].copy(deep=True)
            score_cashflow['IDX'] = range(len(score_cashflow))
            score_cashflow['经营活动产生的现金流量净额/营业收入_TTM(%)_分位水平'] = score_cashflow['IDX'].rolling(5).apply(lambda x: quantile_definition(x, '经营活动产生的现金流量净额/营业收入_TTM(%)', score_cashflow))
            score_cashflow['现金流'] = score_cashflow['经营活动产生的现金流量净额/营业收入_TTM(%)_分位水平'].apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5 if x <= 1.0 else np.nan)
            ##################
            score_data = pd.concat([score_pettm[['PE_TTM']], score_pblf[['PB_LF']], score_sentiment[['拥挤度']],
                                    score_fundholding[['公募持仓']], score_earnings[['盈利']], score_growth[['成长']],
                                    score_capex[['资本开支']], score_cashflow[['现金流']]], axis=1)
            score_data = score_data.dropna(how='all').fillna('-')

        else:
            industry_data = pd.DataFrame()
            score_data = pd.DataFrame()

        import xlwings
        filename = '{0}{1}/{2}行业数据跟踪.xlsx'.format(self.data_path, self.industry_name, self.industry_name)
        if os.path.exists(filename):
            app = xlwings.App(visible=False)
            wookbook = app.books.open(filename)
        else:
            app = xlwings.App(visible=False)
            wookbook = app.books.add()
            wookbook.sheets.add('产业周期数据')
            wookbook.sheets.add('个股关键财务数据')
            wookbook.sheets.add('行业关键财务数据')
            wookbook.sheets.add('情绪')
            wookbook.sheets.add('基金持仓')
            wookbook.sheets.add('一致预期')
            wookbook.sheets.add('财务')
            wookbook.sheets.add('估值')
            wookbook.sheets.add('市值')
            wookbook.sheets.add('指数')
        index_wooksheet = wookbook.sheets['指数']
        index_wooksheet.clear()
        index_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = index
        marketvalue_wooksheet = wookbook.sheets['市值']
        marketvalue_wooksheet.clear()
        marketvalue_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = marketvalue
        valuation_wooksheet = wookbook.sheets['估值']
        valuation_wooksheet.clear()
        valuation_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = valuation
        finance_wooksheet = wookbook.sheets['财务']
        finance_wooksheet.clear()
        finance_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = finance
        consensus_wooksheet = wookbook.sheets['一致预期']
        consensus_wooksheet.clear()
        consensus_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = consensus
        fundholding_wooksheet = wookbook.sheets['基金持仓']
        fundholding_wooksheet.clear()
        fundholding_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = fundholding
        sentiment_wooksheet = wookbook.sheets['情绪']
        sentiment_wooksheet.clear()
        sentiment_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = sentiment
        industry_finance_wooksheet = wookbook.sheets['行业关键财务数据']
        industry_finance_wooksheet.clear()
        industry_finance_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = industry_finance
        stock_finance_wooksheet = wookbook.sheets['个股关键财务数据']
        stock_finance_wooksheet.clear()
        stock_finance_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = stock_finance
        industry_data_wooksheet = wookbook.sheets['产业周期数据']
        industry_data_wooksheet.clear()
        industry_data_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = industry_data
        score_data_wooksheet = wookbook.sheets['打分']
        score_data_wooksheet.clear()
        score_data_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = score_data
        wookbook.save(filename)
        wookbook.close()
        app.quit()
        return



if __name__ == '__main__':
    industry_name = '火电'
    start_date = '20120101'
    end_date = '20231031'
    report_date = '20230930'
    # data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/industry_overview/'
    data_path = 'D:/hbshare/hbshare/fe/TZ/data/industry_overview/'
    sub_remove = False  # 子版块是否去掉上市未满半年的股票
    # IndustryMulta(industry_name, start_date, end_date, report_date, data_path, sub_remove).get_all()
    # IndustryStockFinance(industry_name, start_date, end_date, report_date, data_path).get_all()
    IndustryFinance(industry_name, start_date, end_date, report_date, data_path).get_all()
    IndustryOverview(industry_name, start_date, end_date, report_date, data_path).get_all()

    # import openpyxl
    # import os
    # data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/industry_overview/'
    # wb = openpyxl.load_workbook('{0}申万个股行业分类.xlsx'.format(data_path))
    # sheets = wb.sheetnames
    # for industry_name in sheets:
    #     print(industry_name)
    #     if not os.path.exists(data_path + industry_name):
    #         os.makedirs(data_path + industry_name)
    #     report_date = '20230331'
    #     start_date = '20160630'
    #     end_date = '20230630'
    #     IndustryOverview(industry_name, start_date, end_date, report_date, data_path).get_all()

    # bs = pd.read_hdf(r'D:\hbshare\hbshare\fe\TZ\data\industry_overview\煤炭\stock_bs_煤炭.hdf',key= "table")
    # is1 = pd.read_hdf(r'D:\hbshare\hbshare\fe\TZ\data\industry_overview\煤炭\stock_is_煤炭.hdf',key= "table")
    # cf = pd.read_hdf(r'D:\hbshare\hbshare\fe\TZ\data\industry_overview\煤炭\stock_cf_煤炭.hdf',key= "table")
    # stock_daily_k = pd.read_pickle(r'D:/hbshare/hbshare/fe/TZ/data/industry_overview/stock_daily_k.pkl')
    # stock_daily_k_path = 'D:/hbshare/hbshare/fe/TZ/data/industry_overview/stock_daily_k.hdf'
    # stock_daily_k.to_hdf(stock_daily_k_path, key='table', mode='w')
