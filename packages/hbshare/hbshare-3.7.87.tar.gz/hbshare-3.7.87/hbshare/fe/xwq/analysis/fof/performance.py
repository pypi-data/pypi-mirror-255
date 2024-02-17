# -*- coding: utf-8 -*-

from hbshare.fe.CYP import cyp_functions
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

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


def cal_drawdown(ser):
    df = pd.DataFrame(ser)
    df.columns = ['NAV']
    df['HIGHEST'] = df['NAV'].cummax()
    df['DRAWDOWN'] = (df['NAV'] - df['HIGHEST']) / df['HIGHEST']
    return min(df['DRAWDOWN'])


class Performance:
    def __init__(self, start_date, end_date, dates_dict, data_path, fof_list, fof_name_dict, bmk_list, bmk_name_dict):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.dates_dict = dates_dict
        self.data_path = data_path
        self.fof_list = fof_list
        self.fof_name_dict = fof_name_dict
        self.bmk_list = bmk_list
        self.bmk_name_dict = bmk_name_dict
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date(self.start_date, self.end_date)

    def get_msci_without_881001(self):
        msci_without_881001 = cyp_functions.msci_without_881001
        msci_without_881001 = msci_without_881001(self.end_date)
        msci_without_881001 = msci_without_881001.reset_index()
        msci_without_881001.columns = ['TRADE_DATE', 'RET']
        msci_without_881001['TRADE_DATE'] = msci_without_881001['TRADE_DATE'].astype(str)
        msci_without_881001['RET'] /= 100.0
        msci_without_881001['RET'].iloc[0] = 0.0
        msci_without_881001['NAV'] = (msci_without_881001['RET'] + 1).cumprod()
        msci_without_881001.to_excel('{0}msci_without_881001.xlsx'.format(self.data_path))
        msci_without_881001['YEAR_MONTH'] = msci_without_881001['TRADE_DATE'].apply(lambda x: x[:6])
        msci_without_881001_monthly = msci_without_881001.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        msci_without_881001_monthly.to_excel('{0}msci_without_881001_monthly.xlsx'.format(self.data_path))
        return

    def get_msci_rmb_without_881001(self):
        msci_rmb_without_881001 = cyp_functions.msci_rmb_without_881001
        msci_rmb_without_881001 = msci_rmb_without_881001(self.end_date, '{0}QDII基金对(人民币-美元).xlsx'.format(self.data_path))
        msci_rmb_without_881001 = msci_rmb_without_881001.reset_index()
        msci_rmb_without_881001.columns = ['TRADE_DATE', 'RET']
        msci_rmb_without_881001['TRADE_DATE'] = msci_rmb_without_881001['TRADE_DATE'].astype(str)
        msci_rmb_without_881001['RET'] /= 100.0
        msci_rmb_without_881001['RET'].iloc[0] = 0.0
        msci_rmb_without_881001['NAV'] = (msci_rmb_without_881001['RET'] + 1).cumprod()
        msci_rmb_without_881001.to_excel('{0}msci_rmb_without_881001.xlsx'.format(self.data_path))
        msci_rmb_without_881001['YEAR_MONTH'] = msci_rmb_without_881001['TRADE_DATE'].apply(lambda x: x[:6])
        msci_rmb_without_881001_monthly = msci_rmb_without_881001.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        msci_rmb_without_881001_monthly.to_excel('{0}msci_rmb_without_881001_monthly.xlsx'.format(self.data_path))
        return

    def get_bmk_close(self):
        bmk_close_hb = HBDB().read_private_index_daily_k_given_indexs(self.bmk_list, self.start_date, self.end_date)
        bmk_close_hb['TRADE_DATE'] = bmk_close_hb['TRADE_DATE'].astype(str)
        bmk_close_hb = bmk_close_hb[(bmk_close_hb['TRADE_DATE'] >= self.start_date) & (bmk_close_hb['TRADE_DATE'] <= self.end_date)]
        bmk_close_hb = bmk_close_hb.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        bmk_close_cta = pd.read_excel('{0}5亿CTA指数.xlsx'.format(self.data_path))
        bmk_close_cta = bmk_close_cta.rename(columns={'t_date': 'TRADE_DATE'})
        bmk_close_cta['TRADE_DATE'] = bmk_close_cta['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        bmk_close_cta = bmk_close_cta.set_index('TRADE_DATE')[['5亿CTA指数']].rename(columns={'5亿CTA指数': 'CTA'})
        bmk_close_msci = pd.read_excel('{0}msci_rmb_without_881001.xlsx'.format(self.data_path), index_col=0)
        bmk_close_msci['TRADE_DATE'] = bmk_close_msci['TRADE_DATE'].astype(str)
        bmk_close_msci = bmk_close_msci.set_index('TRADE_DATE')[['NAV']].rename(columns={'NAV': 'MSCI'})
        bmk_close_w = w.wsd('H11001.CSI', "close", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1]
        bmk_close_w.columns = ['H11001.CSI']
        bmk_close_w.index = map(lambda x: x.strftime('%Y%m%d'), bmk_close_w.index)
        bmk_close = bmk_close_hb.merge(bmk_close_cta, left_index=True, right_index=True, how='left').merge(bmk_close_msci, left_index=True, right_index=True, how='left').merge(bmk_close_w, left_index=True, right_index=True, how='left')
        bmk_close = bmk_close[bmk_close.index.isin(self.calendar_df[self.calendar_df['IS_WEEK_END'] == '1']['CALENDAR_DATE'].unique().tolist())]
        bmk_close = bmk_close[self.bmk_list].rename(columns=self.bmk_name_dict)
        bmk_close.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bmk_close.index)
        bmk_close.to_excel('{0}bmk_close.xlsx'.format(self.data_path))
        return

    def get_fof_nav(self):
        fof_nav = HBDB().read_private_fund_ret_given_codes(self.fof_list)
        fof_nav = fof_nav.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': 'NAV'})
        fof_nav['TRADE_DATE'] = fof_nav['TRADE_DATE'].astype(str)
        fof_nav = fof_nav[(fof_nav['TRADE_DATE'] >= self.start_date) & (fof_nav['TRADE_DATE'] <= self.end_date)]
        fof_nav = fof_nav.pivot(index='TRADE_DATE', columns='FUND_CODE', values='NAV').sort_index()
        fof_nav.loc['20220114'] = fof_nav.loc['20220117']
        fof_nav = fof_nav.sort_index()
        fof_nav = fof_nav[fof_nav.index.isin(self.calendar_df[self.calendar_df['IS_WEEK_END'] == '1']['CALENDAR_DATE'].unique().tolist())]
        fof_nav = fof_nav[self.fof_list].rename(columns=self.fof_name_dict)
        fof_nav.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), fof_nav.index)
        fof_nav.to_excel('{0}fof_nav.xlsx'.format(self.data_path))
        return

    def get_benchmark(self, fof, nav):
        bmk_close = pd.read_excel('{0}bmk_close.xlsx'.format(self.data_path), index_col=0)
        bmk_close.index = map(lambda x: x.strftime('%Y%m%d'), bmk_close.index)
        bmk_close = bmk_close[(bmk_close.index >= nav['TRADE_DATE'].iloc[0]) & (bmk_close.index <= nav['TRADE_DATE'].iloc[-1])]
        bmk_ret = bmk_close.pct_change()
        bmk_ret['人民币存款利率'] = 0.0035 / 52.0
        bmk_ret['人民币存款利率'].iloc[0] = np.nan

        if fof in ('STQ402', 'STQ404'):
            bmk_ret['稳健类_old'] = 0.60 * bmk_ret['中证全债指数']
            bmk_ret['平衡类_old'] = 0.25 * bmk_ret['五亿CTA指数']
            bmk_ret['进取类_old'] = 0.15 * bmk_ret['好买股票指数']
            bmk_ret[fof + '_old'] = bmk_ret['稳健类_old'] + bmk_ret['平衡类_old'] + bmk_ret['进取类_old']
            bmk_ret['稳健类_new'] = 0.55 * bmk_ret['中证全债指数']
            bmk_ret['平衡类_new'] = 0.25 * bmk_ret['好买管理期货指数']
            bmk_ret['进取类（国内）_new'] = 0.14 * bmk_ret['好买股票指数']
            bmk_ret['进取类（海外）_new'] = 0.06 * (0.90 * bmk_ret['以人民币计价的MSCI全球指数（剔除中国部分）'] + 0.10 * bmk_ret['人民币存款利率'])
            bmk_ret['进取类_new'] = bmk_ret['进取类（国内）_new'] + bmk_ret['进取类（海外）_new']
            bmk_ret[fof + '_new'] = bmk_ret['稳健类_new'] + bmk_ret['平衡类_new'] + bmk_ret['进取类_new']
            bmk_ret[fof] = bmk_ret[fof + '_old']
            # bmk_ret.loc[bmk_ret.index >= '20231101', fof] = bmk_ret.loc[bmk_ret.index >= '20231101', fof + '_new']
            bmk_nav = (bmk_ret.fillna(0.0) + 1.0).cumprod()
            bmk_nav = bmk_nav[[fof]].reset_index().rename(columns={'index': 'TRADE_DATE'})
        elif fof in ('SSD164'):
            bmk_ret['稳健类_old'] = 1.0 / 3.0 * bmk_ret['中证全债指数']
            bmk_ret['平衡类_old'] = 1.0 / 3.0 * bmk_ret['五亿CTA指数']
            bmk_ret['进取类_old'] = 1.0 / 3.0 * bmk_ret['好买股票指数']
            bmk_ret[fof + '_old'] = bmk_ret['稳健类_old'] + bmk_ret['平衡类_old'] + bmk_ret['进取类_old']
            bmk_ret['稳健类_new'] = 1.0 / 3.0 * bmk_ret['中证全债指数']
            bmk_ret['平衡类_new'] = 1.0 / 3.0 * bmk_ret['好买管理期货指数']
            bmk_ret['进取类_new'] = 1.0 / 3.0 * bmk_ret['好买股票指数']
            bmk_ret[fof + '_new'] = bmk_ret['稳健类_new'] + bmk_ret['平衡类_new'] + bmk_ret['进取类_new']
            bmk_ret[fof] = bmk_ret[fof + '_old']
            # bmk_ret.loc[bmk_ret.index >= '20231101', fof] = bmk_ret.loc[bmk_ret.index >= '20231101', fof + '_new']
            bmk_nav = (bmk_ret.fillna(0.0) + 1.0).cumprod()
            bmk_nav = bmk_nav[[fof]].reset_index().rename(columns={'index': 'TRADE_DATE'})
        elif fof in ('STR813', 'STS126'):
            bmk_ret['稳健类_old'] = 0.10 * bmk_ret['中证全债指数']
            bmk_ret['平衡类_old'] = 0.30 * bmk_ret['五亿CTA指数']
            bmk_ret['进取类_old'] = 0.60 * bmk_ret['好买股票指数']
            bmk_ret[fof + '_old'] = bmk_ret['稳健类_old'] + bmk_ret['平衡类_old'] + bmk_ret['进取类_old']
            bmk_ret['稳健类_new'] = 0.10 * bmk_ret['中证全债指数']
            bmk_ret['平衡类_new'] = 0.20 * bmk_ret['好买管理期货指数']
            bmk_ret['进取类（国内）_new'] = 0.49 * bmk_ret['好买股票指数']
            bmk_ret['进取类（海外）_new'] = 0.21 * (0.90 * bmk_ret['以人民币计价的MSCI全球指数（剔除中国部分）'] + 0.10 * bmk_ret['人民币存款利率'])
            bmk_ret['进取类_new'] = bmk_ret['进取类（国内）_new'] + bmk_ret['进取类（海外）_new']
            bmk_ret[fof + '_new'] = bmk_ret['稳健类_new'] + bmk_ret['平衡类_new'] + bmk_ret['进取类_new']
            bmk_ret[fof] = bmk_ret[fof + '_old']
            # bmk_ret.loc[bmk_ret.index >= '20231101', fof] = bmk_ret.loc[bmk_ret.index >= '20231101', fof + '_new']
            bmk_nav = (bmk_ret.fillna(0.0) + 1.0).cumprod()
            bmk_nav = bmk_nav[[fof]].reset_index().rename(columns={'index': 'TRADE_DATE'})
        else:
            bmk_nav = pd.DataFrame()
            bmk_ret = pd.DataFrame()
        return bmk_nav, bmk_ret

    def get_performance(self, fof, nav):
        ### 月度收益率 ###
        nav_monthly = nav.copy(deep=True)
        nav_monthly['YEAR_MONTH'] = nav_monthly['TRADE_DATE'].apply(lambda x: x[:6])
        nav_monthly = nav_monthly.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        nav_monthly = nav_monthly.drop(['TRADE_DATE'], axis=1).set_index('YEAR_MONTH')
        ret_monthly = nav_monthly.pct_change()
        ### 年度收益率 ###
        nav_yearly = nav.copy(deep=True)
        nav_yearly['YEAR'] = nav_yearly['TRADE_DATE'].apply(lambda x: x[:4])
        nav_yearly = nav_yearly.sort_values('TRADE_DATE').drop_duplicates('YEAR', keep='last')
        nav_yearly = nav_yearly.drop(['TRADE_DATE'], axis=1).set_index('YEAR')
        ret_yearly = nav_yearly.pct_change()
        ### 区间收益率 ###
        nav_period = nav.copy(deep=True).set_index('TRADE_DATE')
        ret_period = pd.DataFrame(index=['成立以来', '近三年', '近两年', '近一年', '今年以来', '近三月'], columns=[fof])
        ret_period.loc['成立以来', fof] = nav_period[fof].iloc[-1] / nav_period[fof].iloc[0] - 1
        ret_period.loc['近三年', fof] = nav_monthly[fof].loc[self.dates_dict['近三年'][-1]] / nav_monthly[fof].loc[self.dates_dict['近三年'][0]] - 1 if self.dates_dict['近三年'][0] in nav_monthly.index.tolist() else np.nan
        ret_period.loc['近两年', fof] = nav_monthly[fof].loc[self.dates_dict['近两年'][-1]] / nav_monthly[fof].loc[self.dates_dict['近两年'][0]] - 1 if self.dates_dict['近两年'][0] in nav_monthly.index.tolist() else np.nan
        ret_period.loc['近一年', fof] = nav_monthly[fof].loc[self.dates_dict['近一年'][-1]] / nav_monthly[fof].loc[self.dates_dict['近一年'][0]] - 1 if self.dates_dict['近一年'][0] in nav_monthly.index.tolist() else np.nan
        ret_period.loc['今年以来', fof] = nav_monthly[fof].loc[self.dates_dict['今年以来'][-1]] / nav_monthly[fof].loc[self.dates_dict['今年以来'][0]] - 1 if self.dates_dict['今年以来'][0] in nav_monthly.index.tolist() else np.nan
        ret_period.loc['近三月', fof] = nav_monthly[fof].loc[self.dates_dict['近三月'][-1]] / nav_monthly[fof].loc[self.dates_dict['近三月'][0]] - 1 if self.dates_dict['近三月'][0] in nav_monthly.index.tolist() else np.nan
        ### 风险收益指标 ###
        nav_risk = nav.copy(deep=True).set_index('TRADE_DATE')
        nav_risk = nav_risk[nav_risk.index.isin(self.calendar_df[self.calendar_df['IS_WEEK_END'] == '1']['CALENDAR_DATE'].unique().tolist())]
        nav_risk['RET'] = nav_risk[fof].pct_change()
        nav_risk = nav_risk.sort_index()
        ret_risk = pd.DataFrame(index=['年化收益率', '年化波动率', '历史最大回撤', 'Sharpe比率', 'Calmar比率', '投资胜率（周度收益率大于0）', '平均损益比'], columns=[fof])
        ret_risk.loc['年化收益率', fof] = (nav_risk[fof].iloc[-1] / nav_risk[fof].iloc[0]) ** (365.0 / (datetime.strptime(nav_risk.index[-1], '%Y%m%d') - datetime.strptime(nav_risk.index[0], '%Y%m%d')).days) - 1.0
        ret_risk.loc['年化波动率', fof] = np.std(nav_risk['RET'].dropna(), ddof=1) * np.sqrt(52.0)
        ret_risk.loc['历史最大回撤', fof] = cal_drawdown(nav[fof])
        ret_risk.loc['Sharpe比率', fof] = (ret_risk.loc['年化收益率', fof] - 0.015) / ret_risk.loc['年化波动率', fof]
        ret_risk.loc['Calmar比率', fof] = ret_risk.loc['年化收益率', fof] / abs(ret_risk.loc['历史最大回撤', fof])
        nav_risk = nav_risk.dropna(subset=['RET'])
        nav_risk = nav_risk[nav_risk['RET'] != 0.0]
        ret_risk.loc['投资胜率（周度收益率大于0）', fof] = len(nav_risk[nav_risk['RET'] > 0]) / float(len(nav_risk))
        ret_risk.loc['平均损益比', fof] = nav_risk[nav_risk['RET'] > 0]['RET'].mean() / nav_risk[nav_risk['RET'] < 0]['RET'].mean() * (-1.0)
        performance = pd.concat([ret_monthly, ret_yearly, ret_period, ret_risk])
        return performance

    def get_all_performance(self):
        performance_list = []
        for fof in self.fof_list:
            nav = HBDB().read_private_fund_ret_given_codes([fof])
            nav = nav.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': fof})
            nav['TRADE_DATE'] = nav['TRADE_DATE'].astype(str)
            nav = nav[(nav['TRADE_DATE'] >= self.start_date) & (nav['TRADE_DATE'] <= self.end_date)]
            nav = nav[['TRADE_DATE', fof]].dropna(subset=[fof])
            if fof == 'SSD164':
                nav = nav.set_index('TRADE_DATE')
                nav.loc['20220114'] = nav.loc['20220117']
                nav = nav.sort_index().reset_index()
            bmk, bmk_ret = self.get_benchmark(fof, nav)
            bmk_ret.to_excel('{0}bmk_ret_{1}.xlsx'.format(self.data_path, self.fof_name_dict[fof]))
            fof_performance = self.get_performance(fof, nav).rename(columns={fof: self.fof_name_dict[fof]})
            bmk_performance = self.get_performance(fof, bmk).rename(columns={fof: self.fof_name_dict[fof] + '基准'})
            performance = pd.concat([fof_performance, bmk_performance], axis=1)
            nav_bmk = nav.merge(bmk.rename(columns={fof: fof + '_bmk'}), left_on=['TRADE_DATE'], right_on=['TRADE_DATE'], how='right')
            nav_bmk = nav_bmk.fillna(1.0).set_index('TRADE_DATE')
            nav_bmk_ret = nav_bmk.pct_change().dropna()
            performance.loc['投资胜率（周度收益率大于基准）', self.fof_name_dict[fof]] = len(nav_bmk_ret[nav_bmk_ret[fof] > nav_bmk_ret[fof + '_bmk']]) / float(len(nav_bmk_ret))
            performance_list.append(performance)
        performance = pd.concat(performance_list, axis=1)
        performance.to_excel('{0}performance.xlsx'.format(self.data_path))
        return

    def fund_attribution(self):
        trading_info = pd.read_excel('{0}trading_info.xlsx'.format(self.data_path))
        trading_info['基金代码'] = trading_info['基金代码'].apply(lambda x: str(x).zfill(6))
        trading_info['交易日期'] = trading_info['交易日期'].astype(str)
        trading_info['期间收益率'] = np.nan
        trading_info['期间损益'] = np.nan
        trading_info = trading_info.reset_index().drop('index', axis=1)
        mutual_nav = HBDB().read_fund_nav_adj_given_date_and_codes('20210101', trading_info['基金代码'].unique().tolist())
        private_nav = HBDB().read_private_fund_ret_given_codes(trading_info['基金代码'].unique().tolist())
        nav = pd.concat([mutual_nav[['jjdm', 'jzrq', 'fqdwjz']], private_nav[['jjdm', 'jzrq', 'fqdwjz']]])
        nav['jzrq'] = nav['jzrq'].astype(str)
        nav = nav.pivot(index='jzrq', columns='jjdm', values='fqdwjz').sort_index()
        nav = nav[(nav.index >= '20210903') & (nav.index <= '20211105')]
        nav = nav[nav.index.isin(self.calendar_df[self.calendar_df['IS_WEEK_END'] == '1']['CALENDAR_DATE'].unique().tolist())]
        nav = nav.fillna(method='ffill')
        nav = nav.sort_index()
        for idx, row in trading_info.iterrows():
            print(idx, row['基金名称'])
            fund_nav = nav[[row['基金代码']]]
            fund_nav = fund_nav[fund_nav.index >= row['交易日期']]
            trading_info.loc[idx, '期间收益率'] = fund_nav[row['基金代码']].iloc[-1] / fund_nav[row['基金代码']].iloc[0] - 1
            trading_info.loc[idx, '期间损益'] = row['申购金额'] * trading_info.loc[idx, '期间收益率']
        trading_info.to_excel('{0}trading_info_pl.xlsx'.format(self.data_path))
        return

    def get_all(self):
        self.get_msci_without_881001()
        self.get_msci_rmb_without_881001()
        self.get_bmk_close()
        self.get_fof_nav()
        self.get_all_performance()
        self.fund_attribution()
        return


if __name__ == '__main__':
    start_date = '20200101'
    end_date = '20231231'
    dates_dict = {
        '近三年': ['202012', '202312'],
        '近两年': ['202112', '202312'],
        '近一年': ['202212', '202312'],
        '今年以来': ['202212', '202312'],
        '近三月': ['202309', '202312'],
    }
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/fof/'
    fof_list = ['SSD164', 'STQ402', 'STQ404', 'STR813', 'STS126']
    fof_name_dict = {
        'SSD164': '新方程大类配置二号',
        'STQ402': '新方程大类配置稳健型母基金',
        'STQ404': '新方程大类配置稳健型二号',
        'STR813': '新方程大类配置进取型母基金',
        'STS126': '新方程大类配置进取型二号'
    }
    bmk_list = ['H11001.CSI', 'CTA', 'HB0018', 'MSCI', 'HB0011']
    bmk_name_dict = {
        'H11001.CSI': '中证全债指数',
        'CTA': '五亿CTA指数',
        'HB0018': '好买管理期货指数',
        'MSCI': '以人民币计价的MSCI全球指数（剔除中国部分）',
        'HB0011': '好买股票指数'
    }
    Performance(start_date, end_date, dates_dict, data_path, fof_list, fof_name_dict, bmk_list, bmk_name_dict).get_all()