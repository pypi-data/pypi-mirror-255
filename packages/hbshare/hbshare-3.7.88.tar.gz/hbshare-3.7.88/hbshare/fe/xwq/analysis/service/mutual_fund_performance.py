# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
line_color_list = ['#F04950', '#6268A2', '#959595', '#333335', '#EE703F', '#7E4A9B', '#8A662C',
                   '#44488E', '#BA67E9', '#3FAEEE']


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


# def get_performance(df, q):
#     df = df.dropna()
#     compute_excess = True if df.shape[1] == 2 else False
#     if compute_excess:
#         df.columns = ['P_NAV', 'B_NAV']
#         df['P_RET'] = df['P_NAV'].pct_change()
#         df['B_RET'] = df['B_NAV'].pct_change()
#         df['E_RET'] = df['P_RET'] - df['B_RET']
#         df['E_NAV'] = (df['E_RET'].fillna(0.0) + 1).cumprod()
#         performance = pd.DataFrame(index=['年化收益率', '年化波动率', '最大回撤', '夏普比率', '卡玛比率', '投资胜率', '投资损益比'], columns=['指标值', '基准指标值', '超额指标值'])
#     else:
#         df.columns = ['P_NAV']
#         df['P_RET'] = df['P_NAV'].pct_change()
#         performance = pd.DataFrame(index=['年化收益率', '年化波动率', '最大回撤', '夏普比率', '卡玛比率', '投资胜率', '投资损益比'], columns=['指标值'])
#
#     performance.loc['年化收益率', '指标值'] = (df['P_NAV'].iloc[-1] / df['P_NAV'].iloc[0]) ** (q / float(len(df))) - 1.0
#     performance.loc['年化波动率', '指标值'] = np.std(df['P_RET'].dropna(), ddof=1) * np.sqrt(q)
#     performance.loc['最大回撤', '指标值'] = max([(min(df['P_NAV'].iloc[i:]) / df['P_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['P_NAV']))])
#     performance.loc['夏普比率', '指标值'] = (performance.loc['年化收益率', '指标值'] - 0.015) / performance.loc['年化波动率', '指标值']
#     performance.loc['卡玛比率', '指标值'] = performance.loc['年化收益率', '指标值'] / performance.loc['最大回撤', '指标值']
#     performance.loc['投资胜率', '指标值'] = len(df[df['P_RET'] >= 0]) / float(len(df.dropna()))
#     performance.loc['投资损益比', '指标值'] = df[df['P_RET'] >= 0]['P_RET'].mean() / df[df['P_RET'] < 0]['P_RET'].mean() * (-1.0)
#
#     if compute_excess:
#         performance.loc['年化收益率', '基准指标值'] = (df['B_NAV'].iloc[-1] / df['B_NAV'].iloc[0]) ** (q / float(len(df))) - 1.0
#         performance.loc['年化波动率', '基准指标值'] = np.std(df['B_RET'].dropna(), ddof=1) * np.sqrt(q)
#         performance.loc['最大回撤', '基准指标值'] = max([(min(df['B_NAV'].iloc[i:]) / df['B_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['B_NAV']))])
#         performance.loc['夏普比率', '基准指标值'] = (performance.loc['年化收益率', '基准指标值'] - 0.015) / performance.loc['年化波动率', '基准指标值']
#         performance.loc['卡玛比率', '基准指标值'] = performance.loc['年化收益率', '基准指标值'] / performance.loc['最大回撤', '基准指标值']
#         performance.loc['投资胜率', '基准指标值'] = len(df[df['B_RET'] >= 0]) / float(len(df.dropna()))
#         performance.loc['投资损益比', '基准指标值'] = df[df['B_RET'] >= 0]['B_RET'].mean() / df[df['B_RET'] < 0]['B_RET'].mean() * (-1.0)
#
#         performance.loc['年化收益率', '超额指标值'] = (df['E_NAV'].iloc[-1] / df['E_NAV'].iloc[0]) ** (q / float(len(df))) - 1.0
#         performance.loc['年化波动率', '超额指标值'] = np.std(df['E_RET'].dropna(), ddof=1) * np.sqrt(q)
#         performance.loc['最大回撤', '超额指标值'] = max([(min(df['E_NAV'].iloc[i:]) / df['E_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['E_NAV']))])
#         performance.loc['夏普比率', '超额指标值'] = (performance.loc['年化收益率', '超额指标值']) / performance.loc['年化波动率', '超额指标值']
#         performance.loc['卡玛比率', '超额指标值'] = performance.loc['年化收益率', '超额指标值'] / performance.loc['最大回撤', '超额指标值']
#         performance.loc['投资胜率', '超额指标值'] = len(df[df['E_RET'] >= 0]) / float(len(df.dropna()))
#         performance.loc['投资损益比', '超额指标值'] = df[df['E_RET'] >= 0]['E_RET'].mean() / df[df['E_RET'] < 0]['E_RET'].mean() * (-1.0)
#     return performance

def get_performance(df, q):
    df = df.dropna()
    df.columns = ['P_NAV']
    df['P_RET'] = df['P_NAV'].pct_change()
    performance = pd.DataFrame(index=['年化收益率', '年化波动率', '最大回撤', '夏普比率', '卡玛比率', '投资胜率', '投资损益比'], columns=['指标值'])
    performance.loc['年化收益率', '指标值'] = (df['P_NAV'].iloc[-1] / df['P_NAV'].iloc[0]) ** (q / float(len(df))) - 1.0
    performance.loc['年化波动率', '指标值'] = np.std(df['P_RET'].dropna(), ddof=1) * np.sqrt(q)
    performance.loc['最大回撤', '指标值'] = max([(min(df['P_NAV'].iloc[i:]) / df['P_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['P_NAV']))])
    performance.loc['夏普比率', '指标值'] = (performance.loc['年化收益率', '指标值'] - 0.015) / performance.loc['年化波动率', '指标值']
    performance.loc['卡玛比率', '指标值'] = performance.loc['年化收益率', '指标值'] / performance.loc['最大回撤', '指标值']
    performance.loc['投资胜率', '指标值'] = len(df[df['P_RET'] >= 0]) / float(len(df.dropna()))
    performance.loc['投资损益比', '指标值'] = df[df['P_RET'] >= 0]['P_RET'].mean() / df[df['P_RET'] < 0]['P_RET'].mean() * (-1.0)
    return performance

class ThemeConsturction():
    def __init__(self, start_date, end_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date(self.start_date, self.end_date)
        self.theme_industry = {
                    '制造': ['交通运输', '机械设备', '汽车', '纺织服饰', '轻工制造', '电力设备', '公用事业', '环保'],
                    '消费': ['食品饮料', '家用电器', '社会服务', '农林牧渔', '商贸零售', '美容护理'],
                    '大金融': ['银行', '非银金融', '房地产'],
                    '医药': ['医药生物'],
                    'TMT': ['通信', '计算机', '电子', '传媒'],
                    '周期': ['钢铁', '有色金属', '建筑装饰', '建筑材料', '基础化工', '石油石化', '煤炭']}
        self.industry_info = get_industry_info()
        self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == 1]
        self.industry_info = self.industry_info[self.industry_info['IS_NEW'] == 1]
        self.industry_info = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.industry_list = self.industry_info['INDUSTRY_ID'].unique().tolist()
        self.industry_daily_k = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, self.industry_list)
        self.industry_daily_k = self.industry_daily_k.rename(columns={'jyrq': 'TRADE_DATE', 'zqdm': 'INDUSTRY_ID', 'spjg': 'CLOSE_INDEX', 'ltsz': 'NEG_MARKET_VALUE'})
        self.industry_daily_k['TRADE_DATE'] = self.industry_daily_k['TRADE_DATE'].astype(str)
        self.industry_daily_k = self.industry_daily_k.sort_values(['TRADE_DATE', 'INDUSTRY_ID'])
        self.industry_daily_k = self.industry_daily_k.reset_index().drop('index', axis=1)
        self.industry_daily_k = self.industry_daily_k[['TRADE_DATE', 'INDUSTRY_ID', 'CLOSE_INDEX', 'NEG_MARKET_VALUE']]
        self.industry_daily_k = self.industry_daily_k.merge(self.industry_info, on=['INDUSTRY_ID'], how='left')
        self.industry_daily_k = self.industry_daily_k[(self.industry_daily_k['TRADE_DATE'] >= self.start_date) & (self.industry_daily_k['TRADE_DATE'] <= self.end_date)]
        self.theme_ret, self.theme_nav = self.fit_theme_index()

    def fit_theme_index(self):
        theme_ret_dic = {}
        for theme in self.theme_industry.keys():
            print('dealing {0}...'.format(theme))
            industry_list = self.theme_industry[theme]
            industry_daily_k = self.industry_daily_k[self.industry_daily_k['INDUSTRY_NAME'].isin(industry_list)]
            industry_daily_r = industry_daily_k.pivot(index='TRADE_DATE', columns='INDUSTRY_NAME', values='CLOSE_INDEX').sort_index().fillna(method='ffill').pct_change().fillna(0.0)
            industry_daily_nmv = industry_daily_k.pivot(index='TRADE_DATE', columns='INDUSTRY_NAME', values='NEG_MARKET_VALUE').sort_index().fillna(method='ffill')
            industry_daily_w = industry_daily_nmv.apply(lambda x: x / x.sum(), axis=1)
            theme_ret = (industry_daily_r[industry_list] * industry_daily_w[industry_list]).sum(axis=1)
            theme_ret_dic[theme] = theme_ret
            print('finish dealing {0}!'.format(theme))
        theme_ret = pd.DataFrame.from_dict(theme_ret_dic)
        theme_nav = (theme_ret + 1).cumprod()
        theme_nav.to_excel('{0}theme_nav.xlsx'.format(self.data_path))
        return theme_ret, theme_nav


class MutualFundPerformance:
    def __init__(self, start_date, end_date, data_path, fund_list, fund_name_dict, type_list, type_name_dict, theme_list, index_list, index_name_dict):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.fund_list = fund_list
        self.fund_name_dict = fund_name_dict
        self.type_list = type_list
        self.type_name_dict = type_name_dict
        self.theme_list = theme_list
        self.index_list = index_list
        self.index_name_dict = index_name_dict
        self.load()

    def load(self):
        self.fund_nav_adj = HBDB().read_fund_nav_adj_given_date_and_codes('19000101', self.fund_list)
        self.fund_nav_adj = self.fund_nav_adj.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': 'NAV_ADJ'})
        self.fund_nav_adj['TRADE_DATE'] = self.fund_nav_adj['TRADE_DATE'].astype(str)
        self.fund_nav_adj = self.fund_nav_adj.pivot(index='TRADE_DATE', columns='FUND_CODE', values='NAV_ADJ').sort_index()
        self.fund_nav_adj = self.fund_nav_adj[self.fund_list]
        self.fund_nav_adj = self.fund_nav_adj.rename(columns=self.fund_name_dict)
        self.fund_nav_adj.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), self.fund_nav_adj.index)
        if len(self.theme_list) == 0:
            self.type_daily_k = HBDB().read_index_daily_k_given_date_and_indexs('19000101', self.type_list)
            self.type_daily_k = self.type_daily_k.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
            self.type_daily_k['TRADE_DATE'] = self.type_daily_k['TRADE_DATE'].astype(str)
            self.type_daily_k = self.type_daily_k.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
            self.type_daily_k = self.type_daily_k[self.type_list]
            self.type_daily_k = self.type_daily_k.rename(columns=self.type_name_dict)
            self.type_daily_k.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), self.type_daily_k.index)
        else:
            self.type_daily_k = pd.read_excel('{0}theme_nav.xlsx'.format(self.data_path))
            self.type_daily_k['TRADE_DATE'] = self.type_daily_k['TRADE_DATE'].astype(str)
            self.type_daily_k = self.type_daily_k.set_index('TRADE_DATE').sort_index()
            self.type_daily_k = self.type_daily_k[self.theme_list]
            self.type_daily_k.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), self.type_daily_k.index)
        self.index_daily_k = HBDB().read_index_daily_k_given_date_and_indexs('19000101', self.index_list)
        self.index_daily_k = self.index_daily_k.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        self.index_daily_k['TRADE_DATE'] = self.index_daily_k['TRADE_DATE'].astype(str)
        self.index_daily_k = self.index_daily_k.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        self.index_daily_k = self.index_daily_k[self.index_list]
        self.index_daily_k = self.index_daily_k.rename(columns=self.index_name_dict)
        self.index_daily_k.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), self.index_daily_k.index)

    def get_result(self):
        fund_nav_adj = self.fund_nav_adj.merge(self.type_daily_k, left_index=True, right_index=True, how='left').merge(self.index_daily_k, left_index=True, right_index=True, how='left')
        fund_nav_adj = fund_nav_adj.dropna()
        fund_nav_adj = fund_nav_adj / fund_nav_adj.iloc[0]
        fig, ax = plt.subplots(figsize=(16, 8))
        for i, col in enumerate(list(fund_nav_adj.columns)):
            ax.plot(fund_nav_adj.index, fund_nav_adj[col].values, color=line_color_list[i], label=col, linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.1), ncol=len(list(fund_nav_adj.columns)), frameon=False)
        plt.title('净值', fontdict={'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}fund_compare.png'.format(data_path))
        fund_compare_list = []
        for i, col in enumerate(list(fund_nav_adj.columns)):
            fund_compare_code = get_performance(fund_nav_adj[[col]], 250)
            fund_compare_code.columns = [col]
            fund_compare_list.append(fund_compare_code)
        fund_compare = pd.concat(fund_compare_list, axis=1).T
        fund_compare.to_excel('{0}fund_compare.xlsx'.format(data_path))

        fund_nav_adj = self.fund_nav_adj.merge(self.type_daily_k, left_index=True, right_index=True, how='left').merge(self.index_daily_k, left_index=True, right_index=True, how='left')
        fund_nav_adj = fund_nav_adj.dropna()
        fund_nav_adj = fund_nav_adj / fund_nav_adj.iloc[0]
        fund_abs_ret = fund_nav_adj.fillna(method='ffill').pct_change().fillna(0.0)
        fund_excess_ret = fund_abs_ret.apply(lambda x: x - x[-1], axis=1).iloc[:, :-1]
        fund_excess_nav_adj = (fund_excess_ret + 1.0).cumprod()
        fig, ax = plt.subplots(figsize=(16, 8))
        for i, col in enumerate(list(fund_excess_nav_adj.columns)):
            ax.plot(fund_excess_nav_adj.index, fund_excess_nav_adj[col].values, color=line_color_list[i], label=col, linewidth=2)
        ax.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=len(list(fund_excess_nav_adj.columns)), frameon=False)
        ax.set_title('相对{0}超额净值'.format(self.index_name_dict[self.index_list[0]]), fontdict={'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}fund_index_compare.png'.format(data_path))
        fund_compare_list = []
        for i, col in enumerate(list(fund_excess_nav_adj.columns)):
            fund_compare_code = get_performance(fund_excess_nav_adj[[col]], 250)
            fund_compare_code.columns = [col]
            fund_compare_list.append(fund_compare_code)
        fund_compare = pd.concat(fund_compare_list, axis=1).T
        fund_compare.to_excel('{0}fund_index_compare.xlsx'.format(data_path))

        fund_nav_adj = self.fund_nav_adj.merge(self.type_daily_k, left_index=True, right_index=True, how='left')
        fund_nav_adj = fund_nav_adj.dropna()
        fund_nav_adj = fund_nav_adj / fund_nav_adj.iloc[0]
        fund_abs_ret = fund_nav_adj.fillna(method='ffill').pct_change().fillna(0.0)
        fund_excess_ret = fund_abs_ret.apply(lambda x: x - x[-1], axis=1).iloc[:, :-1]
        fund_excess_nav_adj = (fund_excess_ret + 1.0).cumprod()
        fig, ax = plt.subplots(figsize=(16, 8))
        for i, col in enumerate(list(fund_excess_nav_adj.columns)):
            ax.plot(fund_excess_nav_adj.index, fund_excess_nav_adj[col].values, color=line_color_list[i], label=col, linewidth=2)
            ax.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=len(list(fund_excess_nav_adj.columns)), frameon=False)
            ax.set_title('相对{0}超额净值'.format(self.type_name_dict[self.type_list[0]]), fontdict={'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}fund_type_compare.png'.format(data_path))
        fund_compare_list = []
        for i, col in enumerate(list(fund_excess_nav_adj.columns)):
            fund_compare_code = get_performance(fund_excess_nav_adj[[col]], 250)
            fund_compare_code.columns = [col]
            fund_compare_list.append(fund_compare_code)
        fund_compare = pd.concat(fund_compare_list, axis=1).T
        fund_compare.to_excel('{0}fund_type_compare.xlsx'.format(data_path))
        return

class MutualFundFeatures:
    from hbshare.fe.xwq.analysis.orm.fedb import FEDB
    sql = "SELECT a.jjdm, a.基金简称, a.规模偏好, b.风格偏好 FROM jjpic_size_p_hbs a LEFT JOIN jjpic_value_p_hbs b ON a.jjdm=b.jjdm AND a.asofdate=b.asofdate WHERE a.规模偏好='中小盘' AND b.风格偏好='价值' AND a.asofdate=(SELECT MAX(asofdate) FROM jjpic_size_p_hbs)"
    samekind_funds = FEDB().get_df(sql)
    samekind_funds = samekind_funds['jjdm'].unique().tolist()

    size_property = FEDB().read_hbs_size_property_given_codes(samekind_funds)
    size_property = size_property.set_index(['jjdm', 'asofdate']).mean()
    style_property = FEDB().read_hbs_style_property_given_codes(samekind_funds)
    style_property = style_property.set_index(['jjdm', 'asofdate']).mean()
    theme_industry_property = FEDB().read_hbs_theme_industry_property_given_codes(samekind_funds)
    theme_industry_property = theme_industry_property.set_index(['jjdm', 'asofdate', 'top5']).mean()
    pass


if __name__ == '__main__':
    # start_date = '20180101'
    # end_date = '20230728'
    # data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/mutual_fund_performance/'
    # fund_list = ['008328', '001287', '005241', '001832', '001382', '270006']
    # fund_name_dict = {'008328': '诺安新兴产业', '001287': '安信优势增长', '005241': '中欧时代智慧', '001832': '易方达瑞恒', '001382': '易方达国企改革', '270006': '广发策略优选'}
    # type_list = ['399372']
    # type_name_dict = {'399372': '大盘成长'}
    # theme_list = []
    # index_list = ['885001']
    # index_name_dict = {'885001': '公募偏股混'}
    # ThemeConsturction(start_date, end_date, data_path)
    # MutualFundFeatures()
    # MutualFundPerformance(start_date, end_date, data_path, fund_list, fund_name_dict, type_list, type_name_dict, theme_list, index_list, index_name_dict).get_result()

    start_date = '20180101'
    end_date = '20230728'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/mutual_fund_performance/'
    fund_list = ['090019', '001810', '161222', '008060', '006195', '007130']
    fund_name_dict = {'090019': '大成景恒混合', '001810': '中欧潜力价值', '161222': '国投瑞银瑞利', '008060': '景顺长城价值边际', '006195': '国金量化多因子', '007130': '中庚小盘价值'}
    type_list = ['399377']
    type_name_dict = {'399377': '小盘价值'}
    theme_list = []
    index_list = ['885001']
    index_name_dict = {'885001': '公募偏股混'}
    ThemeConsturction(start_date, end_date, data_path)
    MutualFundFeatures()
    MutualFundPerformance(start_date, end_date, data_path, fund_list, fund_name_dict, type_list, type_name_dict, theme_list, index_list, index_name_dict).get_result()