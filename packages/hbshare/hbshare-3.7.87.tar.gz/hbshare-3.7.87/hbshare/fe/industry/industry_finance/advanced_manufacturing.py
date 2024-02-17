# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from hbshare.fe.industry.industry_overview import get_date
from datetime import datetime
import os
import numpy as np
import pandas as pd

from WindPy import w
w.start()  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
w.isconnected()  # 判断WindPy是否已经登录成功


def cal_q(df):
    df_Q1 = df.loc[df.index.str.slice(4, 6) == '03']
    df = df.sort_index().diff()
    df = df.loc[df.index.str.slice(4, 6) != '03']
    df = pd.concat([df_Q1, df])
    df_q = df.sort_index()
    return df_q

def cal_ttm(df):
    df_Q1 = df.loc[df.index.str.slice(4, 6) == '03']
    df = df.sort_index().diff()
    df = df.loc[df.index.str.slice(4, 6) != '03']
    df = pd.concat([df_Q1, df])
    df_ttm = df.sort_index().rolling(4).sum()
    return df_ttm


class IndustryFinanceData:
    def __init__(self, industry_name, start_date, end_date, report_date, data_path):
        self.industry_name = industry_name
        self.start_date = start_date
        self.end_date = end_date
        self.report_date = report_date
        self.data_path = data_path
        self.industry_universe = pd.read_excel('{0}{1}/{2}_信息.xlsx'.format(self.data_path, self.industry_name, self.industry_name), sheet_name='股票池')
        self.industry_universe.columns = ['SUB_SECTOR', 'SEC_SHORT_NAME', 'TICKER_SYMBOL', 'HK_STOCK']
        self.industry_universe = self.industry_universe[self.industry_universe['HK_STOCK'] == 0]
        self.industry_universe['TICKER_SYMBOL'] = self.industry_universe['TICKER_SYMBOL'].apply(lambda x: str(x).zfill(6))
        self.load()

    def load(self):
        def read_stock_bs_ch_given_date(date):
            sql = "SELECT CompanyCode AS COMPANY_CODE, to_char(ReportDate, 'yyyyMMdd') AS END_DATE, to_char(PublishDate, 'yyyyMMdd') AS PUBLISH_DATE, ReportStyle AS REPORT_STYLE, AdjustYear AS ADJUST_YEAR, ReportUnit AS REPORT_UNIT, \
                   CBSheet46 AS ASSET, CBSheet77 AS LIABILITY, CBSheet7 AS ACCOUNTS_RECEIVABLE, CBSheet49 AS ACCOUNTS_PAYABLE \
                   FROM finchina.CBSheet_New WHERE ReportDate=to_date('{0}', 'yyyymmdd')".format(date)
            df = HBDB().get_df(sql, db='readonly', page_size=200000)
            return df

        def read_stock_is_ch_given_date(date):
            sql = "SELECT CompanyCode AS COMPANY_CODE, to_char(ReportDate, 'yyyyMMdd') AS END_DATE, to_char(PublishDate, 'yyyyMMdd') AS PUBLISH_DATE, ReportStyle AS REPORT_STYLE, AdjustYear AS ADJUST_YEAR, ReportUnit AS REPORT_UNIT, BeginDate as BEGIN_DATE, \
                   CINST1 AS OPERATING_INCOME, CINST3 AS OPERATING_COST, CINST58 AS NP_ATTR_PC, CINST77 AS RD_EXPENSE \
                   FROM finchina.CINST_New WHERE ReportDate=to_date('{0}', 'yyyymmdd')".format(date)
            df = HBDB().get_df(sql, db='readonly', page_size=200000)
            return df

        def read_stock_cf_ch_given_date(date):
            sql = "SELECT CompanyCode AS COMPANY_CODE, to_char(ReportDate, 'yyyyMMdd') AS END_DATE, to_char(PublishDate, 'yyyyMMdd') AS PUBLISH_DATE, ReportStyle AS REPORT_STYLE, AdjustYear AS ADJUST_YEAR, ReportUnit AS REPORT_UNIT, BeginDate as BEGIN_DATE, \
                   CFST16 AS CAPEX, CFST37 AS FA_DA, CFST98 AS RE_DA, CFST38 AS IA_DA, CFST39 AS LE_DA, CFST10 AS CFO, CFST20 AS CFI, CFST30 AS CFF \
                   FROM finchina.CFST_New WHERE ReportDate=to_date('{0}', 'yyyymmdd')".format(date)
            df = HBDB().get_df(sql, db='readonly', page_size=200000)
            return df

        def read_stock_info_ch():
            sql = "SELECT Exchange AS EXCHANGE, Symbol AS TICKER_SYMBOL, SName AS SEC_SHORT_NAME, CompanyCode AS COMPANY_CODE, SType AS TYPE, Status AS STATUS, ListDate AS LIST_DATE, EndDate AS DELIST_DATE \
                   FROM finchina.SecurityCode WHERE SType IN('EQ0', 'EQA', 'EQB', 'EQH', 'EQN', 'EQS', 'HKE', 'SBA', 'SBB')"
            df = HBDB().get_df(sql, db='readonly', page_size=200000)
            return df

        # 日历
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

        # 行情数据
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
        self.stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        self.stock_daily_k = self.stock_daily_k.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'MARKET_VALUE'})
        self.stock_daily_k['TRADE_DATE'] = self.stock_daily_k['TRADE_DATE'].astype(str)
        self.stock_daily_k = self.stock_daily_k[self.stock_daily_k['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]

        # 关键财务数据
        stock_bs_path = '{0}{1}/stock_bs_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name)
        stock_is_path = '{0}{1}/stock_is_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name)
        stock_cf_path = '{0}{1}/stock_cf_{2}.hdf'.format(self.data_path, self.industry_name, self.industry_name)
        if os.path.isfile(stock_bs_path) and os.path.isfile(stock_is_path) and os.path.isfile(stock_cf_path):
            existed_stock_bs = pd.read_hdf(stock_bs_path, key='table')
            existed_stock_is = pd.read_hdf(stock_is_path, key='table')
            existed_stock_cf = pd.read_hdf(stock_cf_path, key='table')
            max_date_bs = max(existed_stock_bs['END_DATE'])
            max_date_is = max(existed_stock_is['END_DATE'])
            max_date_cf = max(existed_stock_cf['END_DATE'])
            max_date = min(max_date_bs, max_date_is, max_date_cf)
            existed_stock_bs = existed_stock_bs[existed_stock_bs['END_DATE'] <= max_date]
            existed_stock_is = existed_stock_is[existed_stock_is['END_DATE'] <= max_date]
            existed_stock_cf = existed_stock_cf[existed_stock_cf['END_DATE'] <= max_date]
            start_date = max(str(max_date), '20071231')
        else:
            existed_stock_bs = pd.DataFrame()
            existed_stock_is = pd.DataFrame()
            existed_stock_cf = pd.DataFrame()
            start_date = '20071231'
        report_df = self.report_df[(self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.report_date)]
        stock_bs_list, stock_is_list, stock_cf_list = [], [], []
        for date in report_df['REPORT_DATE'].unique().tolist():
            stock_bs_date = read_stock_bs_ch_given_date(date)
            stock_is_date = read_stock_is_ch_given_date(date)
            stock_cf_date = read_stock_cf_ch_given_date(date)
            stock_bs_list.append(stock_bs_date)
            stock_is_list.append(stock_is_date)
            stock_cf_list.append(stock_cf_date)
            print(date)
        self.stock_bs = pd.concat([existed_stock_bs] + stock_bs_list, ignore_index=True)
        self.stock_is = pd.concat([existed_stock_is] + stock_is_list, ignore_index=True)
        self.stock_cf = pd.concat([existed_stock_cf] + stock_cf_list, ignore_index=True)
        self.stock_bs.to_hdf(stock_bs_path, key='table', mode='w')
        self.stock_is.to_hdf(stock_is_path, key='table', mode='w')
        self.stock_cf.to_hdf(stock_cf_path, key='table', mode='w')
        self.stock_bs = pd.read_hdf(stock_bs_path, key='table')
        self.stock_is = pd.read_hdf(stock_is_path, key='table')
        self.stock_cf = pd.read_hdf(stock_cf_path, key='table')

        self.stock_info = read_stock_info_ch()
        self.stock_info = self.stock_info[self.stock_info['TYPE'] == 'EQA']
        self.stock_info['LIST_DATE'] = self.stock_info['LIST_DATE'].apply(lambda x: str(x)[:10].replace('-', ''))
        self.stock_info_dict = self.stock_info.set_index('COMPANY_CODE')['TICKER_SYMBOL'].to_dict()
        self.stock_bs['TICKER_SYMBOL'] = self.stock_bs['COMPANY_CODE'].apply(lambda x: self.stock_info_dict[x] if x in self.stock_info_dict.keys() else np.nan)
        self.stock_is['TICKER_SYMBOL'] = self.stock_is['COMPANY_CODE'].apply(lambda x: self.stock_info_dict[x] if x in self.stock_info_dict.keys() else np.nan)
        self.stock_cf['TICKER_SYMBOL'] = self.stock_cf['COMPANY_CODE'].apply(lambda x: self.stock_info_dict[x] if x in self.stock_info_dict.keys() else np.nan)
        self.stock_bs = self.stock_bs.dropna(subset=['TICKER_SYMBOL'])
        self.stock_is = self.stock_is.dropna(subset=['TICKER_SYMBOL'])
        self.stock_cf = self.stock_cf.dropna(subset=['TICKER_SYMBOL'])
        self.stock_bs = self.stock_bs[self.stock_bs['REPORT_STYLE'].isin(['11', '13'])]
        self.stock_is = self.stock_is[self.stock_is['REPORT_STYLE'].isin(['11', '13'])]
        self.stock_cf = self.stock_cf[self.stock_cf['REPORT_STYLE'].isin(['11', '13'])]
        self.stock_bs = self.stock_bs.sort_values(['TICKER_SYMBOL', 'END_DATE', 'REPORT_STYLE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')
        self.stock_is = self.stock_is.sort_values(['TICKER_SYMBOL', 'END_DATE', 'REPORT_STYLE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')
        self.stock_cf = self.stock_cf.sort_values(['TICKER_SYMBOL', 'END_DATE', 'REPORT_STYLE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')
        self.stock_bs = self.stock_bs[self.stock_bs['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_is = self.stock_is[self.stock_is['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_cf = self.stock_cf[self.stock_cf['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_bs = self.stock_bs[['TICKER_SYMBOL', 'END_DATE', 'ASSET', 'LIABILITY', 'ACCOUNTS_RECEIVABLE', 'ACCOUNTS_PAYABLE']]
        self.stock_is = self.stock_is[['TICKER_SYMBOL', 'END_DATE', 'OPERATING_INCOME', 'OPERATING_COST', 'NP_ATTR_PC', 'RD_EXPENSE']]
        self.stock_cf = self.stock_cf[['TICKER_SYMBOL', 'END_DATE', 'CAPEX', 'FA_DA', 'RE_DA', 'IA_DA', 'LE_DA', 'CFO', 'CFI', 'CFF']]
        self.stock_finance = self.stock_bs.merge(self.stock_is, on=['TICKER_SYMBOL', 'END_DATE'], how='left').merge(self.stock_cf, on=['TICKER_SYMBOL', 'END_DATE'], how='left')
        self.stock_finance = self.stock_finance.sort_values(['TICKER_SYMBOL', 'END_DATE'])
        self.stock_finance = self.stock_finance.fillna(np.nan)
        self.stock_finance = self.stock_finance.merge(self.stock_info[['TICKER_SYMBOL', 'LIST_DATE']], on=['TICKER_SYMBOL'], how='left')
        # self.stock_finance = self.stock_finance[self.stock_finance['END_DATE'] >= self.stock_finance['LIST_DATE']]
        self.stock_finance = self.stock_finance.drop('LIST_DATE', axis=1)
        self.stock_finance = self.stock_finance[~((self.stock_finance['TICKER_SYMBOL'] == '002459') & (self.stock_finance['END_DATE'] <= '20190930'))]
        return


    def get_all(self):
        """
        行业集中度（季度）：基于营业收入TTM计算的行业HHI
        资产负债率（季度）：负债TTM / 总资产TTM
        产业链内部杠杆（季度）：（应付增加+ 应收减少） / 营收，TTM
        营收增速（季度）：季度营业收入TTM同比增长率
        盈利增速（季度）：相对全A的归母净利润同比增速
        资本开支增速（季度）：资本开支的同比增长率
        CAPEX / DA（季度）：现金流量表中资本开支 / 折旧摊销，TTM
        研发增速（季度）： 研发费用的同比增速
        研发投入占比（年度）：研发投入 / 营业收入
        净利率（年度，季度）：归母净利润 / 营业收入
        毛利率变动（季度）：毛利率TTM（t)-毛利率TTM（t - 4）
        经营现金流（年度）：行业：用近三年的现金流均值，展示每年滚动数据，个股：用当年的数据
        投资现金流（年度）：行业：用近三年的现金流均值，展示每年滚动数据，个股：用当年的数据
        融资现金流（年度）：行业：用近三年的现金流均值，展示每年滚动数据，个股：用当年的数据
        """
        stock_nmv = self.stock_daily_k.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NEG_MARKET_VALUE').sort_index()
        stock_nmv = stock_nmv[stock_nmv.index.isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
        stock_nmv.index = map(lambda x: x[:6] + '31' if x[4:6] == '03' or x[4:6] == '12' else x[:6] + '30', stock_nmv.index)
        stock_nmv = stock_nmv.dropna(how='all', axis=0)
        stock_weight = stock_nmv.divide(stock_nmv.sum(axis=1), axis=0)

        # 行业集中度（季度）：基于营业收入TTM计算的行业HHI
        operating_income = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='OPERATING_INCOME').sort_index()
        operating_income_ttm = cal_ttm(operating_income)
        operating_income_ttm = operating_income_ttm.dropna(how='all', axis=0)
        operating_income_ttm = operating_income_ttm.divide(operating_income_ttm.sum(axis=1), axis=0)
        industry_hhi = pd.DataFrame((operating_income_ttm ** 2.0).sum(axis=1), columns=['HHI'])

        # 资产负债率（季度）：负债TTM / 总资产TTM
        asset = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='ASSET').sort_index()
        asset_ttm = cal_ttm(asset)
        liability = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='LIABILITY').sort_index()
        liability_ttm = cal_ttm(liability)
        stock_ltoa = liability_ttm / asset_ttm
        stock_ltoa = stock_ltoa.dropna(how='all', axis=0)
        industry_ltoa = pd.DataFrame((stock_ltoa * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['L_A'])

        # 产业链内部杠杆（季度）：（应付增加+ 应收减少） / 营收，TTM
        accounts_payable = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='ACCOUNTS_PAYABLE').sort_index()
        accounts_payable_ttm = cal_ttm(accounts_payable)
        accounts_receivable = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='ACCOUNTS_RECEIVABLE').sort_index()
        accounts_receivable_ttm = cal_ttm(accounts_receivable)
        operating_income = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='OPERATING_INCOME').sort_index()
        operating_income_ttm = cal_ttm(operating_income)
        stock_apartooi = (accounts_payable_ttm.diff() - accounts_receivable_ttm.diff()) / operating_income_ttm
        stock_apartooi = stock_apartooi.dropna(how='all', axis=0)
        industry_apartooi = pd.DataFrame((stock_apartooi * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['APAR_OI'])

        # 营收增速（季度）：季度营业收入TTM同比增长率
        operating_income = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='OPERATING_INCOME').sort_index()
        operating_income_ttm = cal_ttm(operating_income)
        stock_oiyoy = (operating_income_ttm - operating_income_ttm.shift(4)) / abs(operating_income_ttm.shift(4))
        stock_oiyoy = stock_oiyoy.dropna(how='all', axis=0)
        industry_oiyoy = pd.DataFrame((stock_oiyoy * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['OI_YOY'])

        # 盈利增速（季度）：相对全A的归母净利润同比增速
        np_attr_pc = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='NP_ATTR_PC').sort_index()
        np_attr_pc_ttm = cal_ttm(np_attr_pc)
        stock_npyoy = (np_attr_pc_ttm - np_attr_pc_ttm.shift(4)) / abs(np_attr_pc_ttm.shift(4))
        stock_npyoy = stock_npyoy.dropna(how='all', axis=0)
        industry_npyoy = pd.DataFrame((stock_npyoy * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['NP_YOY'])

        # 资本开支增速（季度）：资本开支的同比增长率
        capex = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='CAPEX').sort_index()
        capex_ttm = cal_ttm(capex)
        stock_capexyoy = (capex_ttm - capex_ttm.shift(4)) / abs(capex_ttm.shift(4))
        stock_capexyoy = stock_capexyoy.dropna(how='all', axis=0)
        industry_capexyoy = pd.DataFrame((stock_capexyoy * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['CAPEX_YOY'])

        # CAPEX / DA（季度）：现金流量表中资本开支 / 折旧摊销，TTM
        capex = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='CAPEX').sort_index()
        capex_ttm = cal_ttm(capex)
        da = self.stock_finance[['TICKER_SYMBOL', 'END_DATE', 'FA_DA', 'RE_DA', 'IA_DA', 'LE_DA']].fillna(0.0)
        da['DA'] = da['FA_DA'] + da['RE_DA'] + da['IA_DA'] + da['LE_DA']
        da = da.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='DA').sort_index()
        da_ttm = cal_ttm(da)
        stock_capextoda = capex_ttm / da_ttm
        stock_capextoda = stock_capextoda.dropna(how='all', axis=0)
        industry_capextoda = pd.DataFrame((stock_capextoda * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['CAPEX_DA'])

        # 研发增速（季度）： 研发费用的同比增速
        rd_exp = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='RD_EXPENSE').sort_index()
        rd_exp_ttm = cal_ttm(rd_exp)
        stock_rdexpyoy = (rd_exp_ttm - rd_exp_ttm.shift(4)) / abs(rd_exp_ttm.shift(4))
        stock_rdexpyoy = stock_rdexpyoy.dropna(how='all', axis=0)
        industry_rdexpyoy = pd.DataFrame((stock_rdexpyoy * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['RDEXP_YOY'])

        # 研发投入占比（年度）：研发投入 / 营业收入
        rd_exp = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='RD_EXPENSE').sort_index()
        rd_exp_ttm = cal_ttm(rd_exp)
        operating_income = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='OPERATING_INCOME').sort_index()
        operating_income_ttm = cal_ttm(operating_income)
        stock_rdexptooi = rd_exp_ttm / operating_income_ttm
        stock_rdexptooi = stock_rdexptooi.dropna(how='all', axis=0)
        industry_rdexptooi = pd.DataFrame((stock_rdexptooi * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['RDEXP_OI'])

        # 净利率（年度，季度）：归母净利润 / 营业收入
        np_attr_pc = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='NP_ATTR_PC').sort_index()
        np_attr_pc_ttm = cal_ttm(np_attr_pc)
        operating_income = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='OPERATING_INCOME').sort_index()
        operating_income_ttm = cal_ttm(operating_income)
        stock_nptooi = np_attr_pc_ttm / operating_income_ttm
        stock_nptooi = stock_nptooi.dropna(how='all', axis=0)
        industry_nptooi = pd.DataFrame((stock_nptooi * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['NP_OI'])

        # 毛利率变动（季度）：毛利率TTM（t)-毛利率TTM（t - 4）
        operating_income = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='OPERATING_INCOME').sort_index()
        operating_income_ttm = cal_ttm(operating_income)
        operating_cost = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='OPERATING_COST').sort_index()
        operating_cost_ttm = cal_ttm(operating_cost)
        gross_profit_ratio = (operating_income_ttm - operating_cost_ttm) / operating_income_ttm
        stock_gprdiff = gross_profit_ratio.diff(4)
        stock_gprdiff = stock_gprdiff.dropna(how='all', axis=0)
        industry_gprdiff = pd.DataFrame((stock_gprdiff * stock_weight).dropna(how='all', axis=0).sum(axis=1), columns=['GPR_DIFF'])

        # 经营现金流（年度）：行业：用近三年的现金流均值，展示每年滚动数据，个股：用当年的数据
        cfo = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='CFO').sort_index()
        stock_cfo = cfo.loc[cfo.index.str.slice(4, 6) == '12']
        stock_cfo = stock_cfo.dropna(how='all', axis=0)
        industry_cfo = pd.DataFrame(stock_cfo.sum(axis=1), columns=['CFO'])
        industry_cfo = industry_cfo.rolling(3).mean()
        industry_cfo = industry_cfo.dropna(how='all', axis=0)

        # 投资现金流（年度）：行业：用近三年的现金流均值，展示每年滚动数据，个股：用当年的数据
        cfi = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='CFI').sort_index()
        stock_cfi = cfi.loc[cfi.index.str.slice(4, 6) == '12']
        stock_cfi = stock_cfi.dropna(how='all', axis=0)
        industry_cfi = pd.DataFrame(stock_cfi.sum(axis=1), columns=['CFI'])
        industry_cfi = industry_cfi.rolling(3).mean()
        industry_cfi = industry_cfi.dropna(how='all', axis=0)

        # 融资现金流（年度）：行业：用近三年的现金流均值，展示每年滚动数据，个股：用当年的数据
        cff = self.stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='CFF').sort_index()
        stock_cff = cff.loc[cff.index.str.slice(4, 6) == '12']
        stock_cff = stock_cff.dropna(how='all', axis=0)
        industry_cff = pd.DataFrame(stock_cff.sum(axis=1), columns=['CFF'])
        industry_cff = industry_cff.rolling(3).mean()
        industry_cff = industry_cff.dropna(how='all', axis=0)

        # 写入excel
        industry_indic_name_list = ['行业集中度', '资产负债率', '产业链内部杠杆', '营收增速', '盈利增速', '资本开支增速', 'CAPEX / DA',
                                    '研发增速', '研发投入占比', '净利率', '毛利率变动', '经营现金流', '投资现金流', '融资现金流']
        industry_indic_data_list = [industry_hhi, industry_ltoa, industry_apartooi, industry_oiyoy, industry_npyoy,
                                    industry_capexyoy, industry_capextoda, industry_rdexpyoy, industry_rdexptooi,
                                    industry_nptooi, industry_gprdiff, industry_cfo, industry_cfi, industry_cff]
        stock_indic_name_list = ['资产负债率', '产业链内部杠杆', '营收增速', '盈利增速', '资本开支增速', 'CAPEX / DA',
                                 '研发增速', '研发投入占比', '净利率', '毛利率变动', '经营现金流', '投资现金流', '融资现金流']
        stock_indic_data_list = [stock_ltoa, stock_apartooi, stock_oiyoy, stock_npyoy,
                                 stock_capexyoy, stock_capextoda, stock_rdexpyoy, stock_rdexptooi,
                                 stock_nptooi, stock_gprdiff, stock_cfo, stock_cfi, stock_cff]
        writer = pd.ExcelWriter('{0}{1}/{2}_关键财务数据.xlsx'.format(self.data_path, self.industry_name, self.industry_name))
        industry_finance = pd.concat(industry_indic_data_list, axis=1)
        industry_finance.columns = industry_indic_name_list
        industry_finance.index = map(lambda x: datetime.strptime(x, '%Y%m%d').date(), industry_finance.index)
        industry_finance = industry_finance[industry_finance.index >= datetime.strptime(self.start_date, '%Y%m%d').date()]
        industry_finance.to_excel(writer, sheet_name='行业关键财务数据')
        data_list = []
        for idx, _ in enumerate(stock_indic_name_list):
            data = stock_indic_data_list[idx]
            data.index = map(lambda x: datetime.strptime(x, '%Y%m%d').date(), data.index)
            data = data[data.index >= datetime.strptime(self.start_date, '%Y%m%d').date()]
            data = data.T.reset_index()
            data['INDIC_NAME'] = stock_indic_name_list[idx]
            data = self.industry_universe[['SEC_SHORT_NAME', 'TICKER_SYMBOL']].merge(data, on=['TICKER_SYMBOL'], how='left')
            data = data.rename(columns={'INDIC_NAME': '指标名称', 'SEC_SHORT_NAME': '股票名称', 'TICKER_SYMBOL': '股票代码'})
            data = data.set_index(['指标名称', '股票名称', '股票代码'])
            data_list.append(data)
        data = pd.concat(data_list)
        data.to_excel(writer, sheet_name='个股关键财务数据')
        writer.save()
        return


if __name__ == '__main__':
    industry_name = '动力电池'
    start_date = '20190101'
    end_date = '20230922'
    report_date = '20230630'
    data_path = 'D:/hbshare/hbshare/fe/TZ/data/industry_overview/'
    IndustryFinanceData(industry_name, start_date, end_date, report_date, data_path)
    # IndustryFinanceData(industry_name, start_date, end_date, report_date, data_path).get_all()