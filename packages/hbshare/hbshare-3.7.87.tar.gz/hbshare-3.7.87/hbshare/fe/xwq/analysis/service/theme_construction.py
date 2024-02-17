# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
import numpy as np
import pandas as pd


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


class ThemeConsturction():
    def __init__(self, start_date, end_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date(self.start_date, self.end_date)
        self.theme_industry = {'TMT': ['通信', '计算机', '电子', '传媒'],
                               '交运及公用事业': ['交通运输', '公用事业', '环保'],
                               '医药': ['医药生物'],
                               '周期': ['钢铁', '有色金属', '建筑装饰', '建筑材料', '基础化工', '石油石化', '煤炭'],
                               '消费': ['食品饮料', '家用电器', '社会服务', '农林牧渔', '商贸零售', '美容护理'],
                               '金融地产': ['银行', '非银金融', '房地产'],
                               '高端制造': ['国防军工', '机械设备', '汽车', '纺织服饰', '轻工制造', '电力设备']}
        self.theme_weight = pd.read_excel('{0}主题权重分布.xlsx'.format(self.data_path), index_col=0).T
        self.theme_weight.index = map(lambda x: x.strftime('%Y%m%d'), self.theme_weight.index)
        # 行业相关
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

    def get_result(self):
        theme_nav = self.theme_nav.reset_index()
        theme_nav['YEAR_MONTH'] = theme_nav['TRADE_DATE'].apply(lambda x: x[:6])
        theme_nav = theme_nav.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        theme_nav = theme_nav.drop('TRADE_DATE', axis=1).set_index('YEAR_MONTH')
        theme_ret = theme_nav.pct_change()
        theme_list = list(theme_ret.columns)
        theme_weight = self.theme_weight.reset_index().rename(columns={'index': 'TRADE_DATE'})
        theme_weight['YEAR_MONTH'] = theme_weight['TRADE_DATE'].apply(lambda x: x[:6])
        theme_weight = theme_weight.drop('TRADE_DATE', axis=1).set_index('YEAR_MONTH')
        theme_weight = theme_weight.rolling(2).mean()
        theme_weight.loc['202201'] = self.theme_weight.loc['20220131']
        theme_weight.loc['202112'] = np.nan
        theme_weight = theme_weight.sort_index()
        theme_weight = theme_weight[theme_list]
        theme_ret = theme_ret * theme_weight
        theme_ret.to_excel('{0}theme_ret.xlsx'.format(self.data_path))
        result = pd.DataFrame(theme_ret.sum(axis=1), columns=['RET'])
        result['NAV'] = (result['RET'] + 1).cumprod()
        result.to_excel('{0}result.xlsx'.format(self.data_path))
        return

if __name__ == '__main__':
    start_date = '20211231'
    end_date = '20230531'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/theme_consturction/'
    ThemeConsturction(start_date, end_date, data_path).get_result()
