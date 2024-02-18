# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import os
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
line_color_list = ['#F04950', '#6268A2', '#959595', '#333335', '#EE703F', '#7E4A9B', '#8A662C',
                  '#44488E', '#BA67E9', '#3FAEEE']
bar_color_list = ['#C94649', '#EEB2B4', '#E1777A', '#D57C56', '#E39A79', '#DB8A66', '#E5B88C',
                  '#8588B7', '#B4B6D1', '#55598D', '#628497', '#A9C6CB', '#866EA9', '#B79BC7',
                  '#7D7D7E', '#CACACA', '#A7A7A8', '#606063', '#C4C4C4', '#99999B', '#B7B7B7']
area_color_list = ['#D55659', '#E1777A', '#DB8A66', '#E5B88C', '#EEB2B4', '#D57C56', '#E39A79',
                   '#8588B7', '#626697', '#866EA9', '#B79BC7', '#B4B6D1', '#628497', '#A9C6CB',
                   '#7D7D7E', '#A7A7A8', '#99999B', '#B7B7B7', '#CACACA', '#969696', '#C4C4C4']
new_color_list = ['#F04950', '#959595', '#6268A2', '#333335', '#D57C56', '#628497']

from WindPy import w
w.start()  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
w.isconnected()  # 判断WindPy是否已经登录成功

engine = create_engine("mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format('admin', 'mysql', '192.168.223.152', '3306', 'fe_temp_data'))


def filter_extreme_mad(ser, n=3):
    median = ser.quantile(0.5)
    new_median = ((ser - median).abs()).quantile(0.5)
    max_range = median + n * new_median
    min_range = median - n * new_median
    ser = np.clip(ser, min_range, max_range)
    return ser

def to_percent(temp, position):
    return '%1.0f'%(temp) + '%'

def to_percent_r1(temp, position):
    return '%0.1f'%(temp) + '%'

def to_percent_r2(temp, position):
    return '%0.01f'%(temp) + '%'

def to_100percent(temp, position):
    return '%1.0f'%(temp * 100) + '%'

def to_100percent_r1(temp, position):
    return '%0.1f'%(temp * 100) + '%'

def to_100percent_r2(temp, position):
    return '%0.01f'%(temp * 100) + '%'

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
    q = (1.0 - np.count_nonzero(part_df[col].iloc[-1] <= part_df[col]) / len(part_df))
    return q

class StyleTest:
    def __init__(self, data_path, start_date, end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

    def test(self):
        style_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370', '399371'])
        style_index = style_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].astype(str)
        style_index = style_index[style_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style_index = style_index[(style_index['TRADE_DATE'] > self.start_date) & (style_index['TRADE_DATE'] <= self.end_date)]
        style_index = style_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        style_index = style_index.rename(columns={'399370': '成长', '399371': '价值'})
        style_index['成长/价值'] = style_index['成长'] / style_index['价值']
        style_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[0], label='成长/价值')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1)
        plt.title('成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值历史相对走势.png'.format(self.data_path))

        n1 = 250
        n2 = 250
        thresh1 = 0.5
        thresh15 = 1.0
        style_data = FEDB().read_timing_data(['TRADE_DATE', 'GROWTH_CROWDING', 'VALUE_CROWDING', 'GROWTH_SPREAD', 'VALUE_SPREAD', 'GROWTH_MOMENTUM', 'VALUE_MOMENTUM'], 'timing_style', self.start_date, self.end_date)
        style_data['TRADE_DATE'] = style_data['TRADE_DATE'].astype(str)
        style_data = style_data[(style_data['TRADE_DATE'] > self.start_date) & (style_data['TRADE_DATE'] <= self.end_date)]
        style_data = style_data.dropna()
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        # growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        # value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        growth_value_data= growth_data.merge(value_data, on=['TRADE_DATE'], how='left').dropna()
        growth_value_data = growth_value_data.set_index('TRADE_DATE').sort_index()
        growth_value_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data.index)
        growth_value_data_disp = growth_value_data.merge(style_index, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data_disp.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data_disp.index)
        growth_value_data_disp = growth_value_data_disp.loc[growth_value_data_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_disp.index)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_MOMENTUM'].values, color=line_color_list[0], label='成长因子动量')
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_MOMENTUM'].values, color=line_color_list[2], label='价值因子动量')
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[1], label='成长/价值（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子动量与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子动量与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_SPREAD'].values, color=line_color_list[0], label='成长因子离散度')
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_SPREAD'].values, color=line_color_list[2], label='价值因子离散度')
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[1], label='成长/价值（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子离散度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子离散度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_CROWDING'].values, color=line_color_list[0], label='成长因子拥挤度')
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_CROWDING'].values, color=line_color_list[2], label='价值因子拥挤度')
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[1], label='成长/价值（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子拥挤度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子拥挤度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_TIMING'].values, color=line_color_list[0], label='成长因子复合指标')
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_TIMING'].values, color=line_color_list[2], label='价值因子复合指标')
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[1], label='成长/价值（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子复合指标与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子复合指标与成长价值历史相对走势.png'.format(self.data_path))

        growth_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370'])
        growth_index = growth_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        growth_index = growth_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        growth_index['TRADE_DATE'] = growth_index['TRADE_DATE'].astype(str)
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        # growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        growth_data = growth_data.merge(growth_index, on=['TRADE_DATE'], how='left')
        growth_data['GROWTH_TIMING_UP1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1,  center=False).mean() + thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_UP15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_SCORE'] = growth_data.apply(lambda x: 5 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP15'] else
                                                                         4 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP1'] else
                                                                         1 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN15'] else
                                                                         2 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN1'] else 3, axis=1)
        growth_data_monthly = growth_data[growth_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        value_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399371'])
        value_index = value_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        value_index = value_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        value_index['TRADE_DATE'] = value_index['TRADE_DATE'].astype(str)
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        # value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        value_data = value_data.merge(value_index, on=['TRADE_DATE'], how='left')
        value_data['VALUE_TIMING_UP1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_UP15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_SCORE'] = value_data.apply(lambda x: 5 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP15'] else
                                                                      4 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP1'] else
                                                                      1 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN15'] else
                                                                      2 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN1'] else 3, axis=1)
        value_data_monthly = value_data[value_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        style_res = growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']].merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        style_res['GROWTH_VALUE'] = style_res['GROWTH_TIMING_SCORE'] - style_res['VALUE_TIMING_SCORE']
        style_res['VALUE_GROWTH'] = style_res['VALUE_TIMING_SCORE'] - style_res['GROWTH_TIMING_SCORE']
        style_res['MARK'] = '均衡'
        style_res.loc[(style_res['GROWTH_TIMING_SCORE'] >= 4) & (style_res['GROWTH_VALUE'] >= 1), 'MARK'] = '成长'
        style_res.loc[(style_res['VALUE_TIMING_SCORE'] >= 4) & (style_res['VALUE_GROWTH'] >= 1), 'MARK'] = '价值'
        style_stats = style_res[['TRADE_DATE', 'MARK']].groupby('MARK').count()
        print(style_stats)

        growth_data_monthly_ = growth_data_monthly.set_index('TRADE_DATE')
        growth_data_monthly_.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_data_monthly_.index)
        style_index = style_index.merge(growth_data_monthly_[['GROWTH_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        style_index['GROWTH_TIMING_SCORE'] = style_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        style_index = style_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        style_index_1 = style_index[style_index['GROWTH_TIMING_SCORE'] == 1]
        style_index_2 = style_index[style_index['GROWTH_TIMING_SCORE'] == 2]
        style_index_3 = style_index[style_index['GROWTH_TIMING_SCORE'] == 3]
        style_index_4 = style_index[style_index['GROWTH_TIMING_SCORE'] == 4]
        style_index_5 = style_index[style_index['GROWTH_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[3], label='成长/价值')
        ax.scatter(style_index_1.index, style_index_1['成长/价值'].values, color=line_color_list[1], label='得分1')
        ax.scatter(style_index_2.index, style_index_2['成长/价值'].values, color=line_color_list[9], label='得分2')
        ax.scatter(style_index_3.index, style_index_3['成长/价值'].values, color=line_color_list[3], label='得分3')
        ax.scatter(style_index_4.index, style_index_4['成长/价值'].values, color=line_color_list[4], label='得分4')
        ax.scatter(style_index_5.index, style_index_5['成长/价值'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('成长价值择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时.png'.format(self.data_path))

        growth_index = growth_index.merge(growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        growth_index['GROWTH_TIMING_SCORE'] = growth_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        growth_index = growth_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        growth_index['RET'] = growth_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        growth_index['RET_ADJ'] = growth_index.apply(lambda x: x['RET'] if x['GROWTH_TIMING_SCORE'] == 4 or x['GROWTH_TIMING_SCORE'] == 5 else 0.0, axis=1)
        growth_index['RET_ADJ'] = growth_index['RET_ADJ'].fillna(0.0)
        growth_index['NAV'] = (growth_index['RET_ADJ'] + 1).cumprod()
        growth_index['CLOSE_INDEX'] = growth_index['CLOSE_INDEX'] / growth_index['CLOSE_INDEX'].iloc[0]
        growth_index['TRADE_DATE_DISP'] = growth_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        growth_index_1 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 1]
        growth_index_2 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 2]
        growth_index_3 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 3]
        growth_index_4 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 4]
        growth_index_5 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['CLOSE_INDEX'].values, color=line_color_list[3], label='巨潮成长指数走势')
        ax.scatter(growth_index_1['TRADE_DATE_DISP'].values, growth_index_1['CLOSE_INDEX'].values, color=line_color_list[1], label='得分1')
        ax.scatter(growth_index_2['TRADE_DATE_DISP'].values, growth_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(growth_index_3['TRADE_DATE_DISP'].values, growth_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(growth_index_4['TRADE_DATE_DISP'].values, growth_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(growth_index_5['TRADE_DATE_DISP'].values, growth_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('成长择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长择时.png'.format(self.data_path))

        value_index = value_index.merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        value_index['VALUE_TIMING_SCORE'] = value_index['VALUE_TIMING_SCORE'].fillna(method='ffill')
        value_index = value_index.dropna(subset=['VALUE_TIMING_SCORE'])
        value_index['RET'] = value_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        value_index['RET_ADJ'] = value_index.apply(lambda x: x['RET'] if x['VALUE_TIMING_SCORE'] == 4 or x['VALUE_TIMING_SCORE'] == 5 else 0.0, axis=1)
        value_index['RET_ADJ'] = value_index['RET_ADJ'].fillna(0.0)
        value_index['NAV'] = (value_index['RET_ADJ'] + 1).cumprod()
        value_index['CLOSE_INDEX'] = value_index['CLOSE_INDEX'] / value_index['CLOSE_INDEX'].iloc[0]
        value_index['TRADE_DATE_DISP'] = value_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        value_index_1 = value_index[value_index['VALUE_TIMING_SCORE'] == 1]
        value_index_2 = value_index[value_index['VALUE_TIMING_SCORE'] == 2]
        value_index_3 = value_index[value_index['VALUE_TIMING_SCORE'] == 3]
        value_index_4 = value_index[value_index['VALUE_TIMING_SCORE'] == 4]
        value_index_5 = value_index[value_index['VALUE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['CLOSE_INDEX'].values, color=line_color_list[3], label='巨潮价值指数走势')
        ax.scatter(value_index_1['TRADE_DATE_DISP'].values, value_index_1['CLOSE_INDEX'].values, color=line_color_list[1], label='得分1')
        ax.scatter(value_index_2['TRADE_DATE_DISP'].values, value_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(value_index_3['TRADE_DATE_DISP'].values, value_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(value_index_4['TRADE_DATE_DISP'].values, value_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(value_index_5['TRADE_DATE_DISP'].values, value_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('价值择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}价值择时.png'.format(self.data_path))

        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001', '399370', '399371'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].astype(str)
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(style_res.set_index('TRADE_DATE')[['MARK']], left_index=True, right_index=True, how='left')
        index = index.reset_index()
        index['MARK'] = index['MARK'].fillna(method='ffill')
        index = index.dropna(subset=['MARK'])
        index['RET_ADJ'] = index.apply(lambda x: x['399370_RET'] if x['MARK'] == '成长' else x['399371_RET'] if x['MARK'] == '价值' else x['881001_RET'], axis=1)
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index = index.dropna()
        index[['399370', '399371', '881001']] = index[['399370', '399371', '881001']] / index[['399370', '399371', '881001']].iloc[0]
        index['TRADE_DATE_DISP'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        index_growth = index[index['MARK'] == '成长']
        index_balance = index[index['MARK'] == '均衡']
        index_value = index[index['MARK'] == '价值']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(index['TRADE_DATE_DISP'].values, index['881001'].values, color=line_color_list[3], label='万得全A走势')
        ax.scatter(index_growth['TRADE_DATE_DISP'].values, index_growth['881001'].values,  color=line_color_list[0], label='成长')
        ax.scatter(index_balance['TRADE_DATE_DISP'].values, index_balance['881001'].values, color=line_color_list[3], label='均衡')
        ax.scatter(index_value['TRADE_DATE_DISP'].values, index_value['881001'].values, color=line_color_list[1], label='价值')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('成长价值择时策略', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时策略.png'.format(self.data_path))

        index_res = index[index['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        index_res = index_res[['TRADE_DATE', '399370', '399371']].sort_values('TRADE_DATE')
        index_res['399370_RET'] = index_res['399370'].pct_change()
        index_res['399371_RET'] = index_res['399371'].pct_change()
        index_res['399370_RET_diff'] = index_res['399370_RET'].diff()
        index_res['399371_RET_diff'] = index_res['399371_RET'].diff()
        index_res['399370_399371'] = index_res['399370_RET'] - index_res['399371_RET']
        index_res['399371_399370'] = index_res['399371_RET'] - index_res['399370_RET']
        index_res['399370/399371'] = index_res['399370'] / index_res['399371']
        index_res['399370/399371_RET'] = index_res['399370/399371'].pct_change()
        index_res['399371/399370'] = index_res['399371'] / index_res['399370']
        index_res['399371/399370_RET'] = index_res['399371/399370'].pct_change()
        index_res['INDEX_MARK'] = '均衡'
        index_res.loc[(index_res['399370_399371'] > 0.05) | (index_res['399370/399371_RET'] > 0.05), 'INDEX_MARK'] = '成长'
        index_res.loc[(index_res['399371_399370'] > 0.05) | (index_res['399371/399370_RET'] > 0.05), 'INDEX_MARK'] = '价值'
        res = style_res[['TRADE_DATE', 'MARK']].merge(index_res, on=['TRADE_DATE'], how='left').dropna()
        res['INDEX_MARK'] = res['INDEX_MARK'].shift(-1)
        win_rate = len(res[res['MARK'] == res['INDEX_MARK']]) / float(len(res))
        print(win_rate)
        return

    def test_3(self):
        style_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370', '399371'])
        style_index = style_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].astype(str)
        style_index = style_index[style_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style_index = style_index[(style_index['TRADE_DATE'] > self.start_date) & (style_index['TRADE_DATE'] <= self.end_date)]
        style_index = style_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        style_index = style_index.rename(columns={'399370': '成长', '399371': '价值'})
        style_index['成长/价值'] = style_index['成长'] / style_index['价值']
        style_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[0], label='成长/价值', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1)
        plt.title('成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值历史相对走势.png'.format(self.data_path))

        n1 = 250
        n2 = 250
        thresh1 = 0.5
        thresh15 = 1.0
        style_data = FEDB().read_timing_data(['TRADE_DATE', 'GROWTH_CROWDING', 'VALUE_CROWDING', 'GROWTH_SPREAD', 'VALUE_SPREAD', 'GROWTH_MOMENTUM', 'VALUE_MOMENTUM'], 'timing_style', self.start_date, self.end_date)
        style_data['TRADE_DATE'] = style_data['TRADE_DATE'].astype(str)
        style_data = style_data[(style_data['TRADE_DATE'] > self.start_date) & (style_data['TRADE_DATE'] <= self.end_date)]
        style_data = style_data.dropna()
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        growth_value_data = growth_data.merge(value_data, on=['TRADE_DATE'], how='left').dropna()
        growth_value_data = growth_value_data.set_index('TRADE_DATE').sort_index()
        growth_value_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data.index)
        growth_value_data_disp = growth_value_data.merge(style_index, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data_disp.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data_disp.index)
        growth_value_data_disp = growth_value_data_disp.loc[growth_value_data_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_disp.index)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_MOMENTUM'].values, color=line_color_list[0], label='成长因子动量', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_MOMENTUM'].values, color=line_color_list[1], label='价值因子动量', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子动量与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子动量与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_SPREAD'].values, color=line_color_list[0], label='成长因子离散度', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_SPREAD'].values, color=line_color_list[1], label='价值因子离散度', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子离散度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子离散度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_CROWDING'].values, color=line_color_list[0], label='成长因子拥挤度', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_CROWDING'].values, color=line_color_list[1], label='价值因子拥挤度', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子拥挤度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子拥挤度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_TIMING'].values, color=line_color_list[0], label='成长因子复合指标', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_TIMING'].values, color=line_color_list[1], label='价值因子复合指标', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子复合指标与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子复合指标与成长价值历史相对走势.png'.format(self.data_path))

        growth_value_data = growth_value_data[['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']]
        for factor_name in ['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']:
            growth_value_data[factor_name + '_UP1'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() + thresh1 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_DOWN1'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() - thresh1 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_UP15'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() + thresh15 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_DOWN15'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2,  center=False).mean() - thresh15 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_SCORE'] = growth_value_data.apply(
                lambda x: 5 if x[factor_name] >= x[factor_name + '_UP15'] else
                4 if x[factor_name] >= x[factor_name + '_UP1'] else
                1 if x[factor_name] <= x[factor_name + '_DOWN15'] else
                2 if x[factor_name] <= x[factor_name + '_DOWN1'] else 3, axis=1)
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data.index)
        growth_value_data_monthly = growth_value_data.loc[growth_value_data.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_monthly.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_monthly.index)
        growth_value_data_monthly = growth_value_data_monthly[['GROWTH_MOMENTUM_SCORE', 'GROWTH_SPREAD_SCORE', 'GROWTH_CROWDING_SCORE', 'GROWTH_TIMING_SCORE', 'VALUE_MOMENTUM_SCORE', 'VALUE_SPREAD_SCORE', 'VALUE_CROWDING_SCORE', 'VALUE_TIMING_SCORE']]
        growth_value_data_monthly = growth_value_data_monthly.merge(style_index, left_index=True, right_index=True, how='left')
        growth_value_data_monthly['成长月度收益率'] = growth_value_data_monthly['成长'].pct_change().shift(-1)
        growth_value_data_monthly['价值月度收益率'] = growth_value_data_monthly['价值'].pct_change().shift(-1)
        growth_value_data_monthly['成长/价值月度收益率'] = growth_value_data_monthly['成长/价值'].pct_change().shift(-1)
        growth_value_data_monthly_stat_list = []
        for factor_name in ['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']:
            growth_value_data_monthly_stat = pd.DataFrame(growth_value_data_monthly[[factor_name + '_SCORE', '成长月度收益率', '价值月度收益率', '成长/价值月度收益率']].dropna().groupby(factor_name + '_SCORE').median())
            growth_value_data_monthly_stat['FACTOR'] = factor_name + '_SCORE'
            growth_value_data_monthly_stat_list.append(growth_value_data_monthly_stat)
        growth_value_data_monthly_stat = pd.concat(growth_value_data_monthly_stat_list)

        growth_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370'])
        growth_index = growth_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        growth_index = growth_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        growth_index['TRADE_DATE'] = growth_index['TRADE_DATE'].astype(str)
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        # growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        growth_data = growth_data.merge(growth_index, on=['TRADE_DATE'], how='left')
        growth_data['GROWTH_TIMING_UP1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_UP15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_SCORE'] = growth_data.apply(
            lambda x: 5 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP15'] else
            4 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP1'] else
            1 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN15'] else
            2 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN1'] else 3, axis=1)
        growth_data_monthly = growth_data[growth_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        value_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399371'])
        value_index = value_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        value_index = value_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        value_index['TRADE_DATE'] = value_index['TRADE_DATE'].astype(str)
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        # value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        value_data = value_data.merge(value_index, on=['TRADE_DATE'], how='left')
        value_data['VALUE_TIMING_UP1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_UP15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_SCORE'] = value_data.apply(
            lambda x: 5 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP15'] else
            4 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP1'] else
            1 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN15'] else
            2 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN1'] else 3, axis=1)
        value_data_monthly = value_data[value_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        market_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001'])
        market_index = market_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        market_index = market_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        market_index['TRADE_DATE'] = market_index['TRADE_DATE'].astype(str)

        growth_index = growth_index.merge(market_index[['TRADE_DATE', 'CLOSE_INDEX']].rename(columns={'CLOSE_INDEX': 'BMK_CLOSE_INDEX'}), on=['TRADE_DATE'], how='left').merge(growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        growth_index['GROWTH_TIMING_SCORE'] = growth_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        growth_index = growth_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        growth_index['RET'] = growth_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        growth_index['BMK_RET'] = growth_index['BMK_CLOSE_INDEX'].pct_change().fillna(0.0)
        growth_index['RET_ADJ'] = growth_index.apply(lambda x: x['RET'] if x['GROWTH_TIMING_SCORE'] == 4 or x['GROWTH_TIMING_SCORE'] == 5 else x['BMK_RET'], axis=1)
        growth_index['RET_ADJ'] = growth_index['RET_ADJ'].fillna(0.0)
        growth_index['NAV'] = (growth_index['RET_ADJ'] + 1).cumprod()
        growth_index['CLOSE_INDEX'] = growth_index['CLOSE_INDEX'] / growth_index['CLOSE_INDEX'].iloc[0]
        growth_index['TRADE_DATE_DISP'] = growth_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['NAV'].values, color=line_color_list[0], label='成长择时', linewidth=3)
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['CLOSE_INDEX'].values, color=line_color_list[2], label='巨潮成长', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('成长择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长择时.png'.format(self.data_path))

        value_index = value_index.merge(market_index[['TRADE_DATE', 'CLOSE_INDEX']].rename(columns={'CLOSE_INDEX': 'BMK_CLOSE_INDEX'})).merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        value_index['VALUE_TIMING_SCORE'] = value_index['VALUE_TIMING_SCORE'].fillna(method='ffill')
        value_index = value_index.dropna(subset=['VALUE_TIMING_SCORE'])
        value_index['RET'] = value_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        value_index['BMK_RET'] = value_index['BMK_CLOSE_INDEX'].pct_change().fillna(0.0)
        value_index['RET_ADJ'] = value_index.apply(lambda x: x['RET'] if x['VALUE_TIMING_SCORE'] == 4 or x['VALUE_TIMING_SCORE'] == 5 else x['BMK_RET'], axis=1)
        value_index['RET_ADJ'] = value_index['RET_ADJ'].fillna(0.0)
        value_index['NAV'] = (value_index['RET_ADJ'] + 1).cumprod()
        value_index['CLOSE_INDEX'] = value_index['CLOSE_INDEX'] / value_index['CLOSE_INDEX'].iloc[0]
        value_index['TRADE_DATE_DISP'] = value_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['NAV'].values, color=line_color_list[0], label='价值择时', linewidth=3)
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['CLOSE_INDEX'].values, color=line_color_list[2], label='巨潮价值', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('价值择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}价值择时.png'.format(self.data_path))

        style_timing = growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']].merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        style_timing['成长_WEIGHT'] = style_timing['GROWTH_TIMING_SCORE'].replace({5: 0.9, 4: 0.7, 3: 0.5, 2: 0.3, 1: 0.1})
        style_timing['价值_WEIGHT'] = style_timing['VALUE_TIMING_SCORE'].replace({5: 0.9, 4: 0.7, 3: 0.5, 2: 0.3, 1: 0.1})
        style_timing['TRADE_DATE'] = style_timing['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        style_timing = style_timing.set_index('TRADE_DATE').sort_index()
        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370', '399371'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(style_timing[['成长_WEIGHT', '价值_WEIGHT']], left_index=True, right_index=True, how='left')
        index['成长_WEIGHT'] = index['成长_WEIGHT'].fillna(method='ffill')
        index['价值_WEIGHT'] = index['价值_WEIGHT'].fillna(method='ffill')
        index = index.dropna(subset=['成长_WEIGHT'])
        index = index.dropna(subset=['价值_WEIGHT'])
        index['成长_WEIGHT'] = index['成长_WEIGHT'] / (index['成长_WEIGHT'] + index['价值_WEIGHT'])
        index['价值_WEIGHT'] = index['价值_WEIGHT'] / (index['成长_WEIGHT'] + index['价值_WEIGHT'])
        index['RET_ADJ'] = index['成长_WEIGHT'] * index['399370_RET'] + index['价值_WEIGHT'] * index['399371_RET']
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index['RET_AVERAGE'] = 0.5 * index['399370_RET'] + 0.5 * index['399371_RET']
        index['RET_AVERAGE'] = index['RET_AVERAGE'].fillna(0.0)
        index['RET_AVERAGE'].iloc[0] = 0.0
        index['NAV_AVERAGE'] = (index['RET_AVERAGE'] + 1).cumprod()
        index = index.dropna()
        index[['NAV_AVERAGE', 'NAV']] = index[['NAV_AVERAGE', 'NAV']] / index[['NAV_AVERAGE', 'NAV']].iloc[0]
        index = index.reset_index()
        index['TRADE_DATE_DISP'] = index['TRADE_DATE']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='成长/价值择时', linewidth=3)
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV_AVERAGE'].values, color=line_color_list[2], label='成长/价值等权', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('成长/价值仓位打分调仓组合回测图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时策略.png'.format(self.data_path))

        style_index = style_index.merge(style_timing[['GROWTH_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        style_index['GROWTH_TIMING_SCORE'] = style_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        style_index = style_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        style_index_1 = style_index[style_index['GROWTH_TIMING_SCORE'] == 1]
        style_index_2 = style_index[style_index['GROWTH_TIMING_SCORE'] == 2]
        style_index_3 = style_index[style_index['GROWTH_TIMING_SCORE'] == 3]
        style_index_4 = style_index[style_index['GROWTH_TIMING_SCORE'] == 4]
        style_index_5 = style_index[style_index['GROWTH_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[3], label='成长/价值')
        ax.scatter(style_index_1.index, style_index_1['成长/价值'].values, color=line_color_list[1], label='成长评分1')
        ax.scatter(style_index_2.index, style_index_2['成长/价值'].values, color=line_color_list[9], label='成长评分2')
        ax.scatter(style_index_3.index, style_index_3['成长/价值'].values, color=line_color_list[3], label='成长评分3')
        ax.scatter(style_index_4.index, style_index_4['成长/价值'].values, color=line_color_list[4], label='成长评分4')
        ax.scatter(style_index_5.index, style_index_5['成长/价值'].values, color=line_color_list[0], label='成长评分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('成长评分及成长/价值走势图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时.png'.format(self.data_path))
        return

class SizeTest:
    def __init__(self, data_path, start_date, end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

    def test(self):
        size_data = FEDB().read_timing_data(['TRADE_DATE', 'SIZE_CROWDING', 'SIZE_SPREAD', 'SIZE_MOMENTUM'], 'timing_style', self.start_date, self.end_date)
        size_data.columns = ['TRADE_DATE', 'LARGE_CROWDING', 'LARGE_SPREAD', 'LARGE_MOMENTUM']
        size_data = size_data[(size_data['TRADE_DATE'] > self.start_date) & (size_data['TRADE_DATE'] <= self.end_date)]
        size_data = size_data.dropna()
        size_data['TRADE_DATE'] = size_data['TRADE_DATE'].astype(str)
        size_data_ = pd.read_hdf('{0}style_timing.hdf'.format(self.data_path), key='table')
        size_data_ = size_data_[['TRADE_DATE', 'SIZE_CROWDING', 'SIZE_SPREAD', 'SIZE_MOMENTUM']]
        size_data_.columns = ['TRADE_DATE', 'SMALL_CROWDING', 'SMALL_SPREAD', 'SMALL_MOMENTUM']
        size_data_ = size_data_[(size_data_['TRADE_DATE'] > self.start_date) & (size_data_['TRADE_DATE'] <= self.end_date)]
        size_data_ = size_data_.dropna()
        size_data_['TRADE_DATE'] = size_data_['TRADE_DATE'].astype(str)
        size_data = size_data.merge(size_data_, on=['TRADE_DATE'], how='left')

        large_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['000300'])
        large_index = large_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        large_index = large_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        large_index['TRADE_DATE'] = large_index['TRADE_DATE'].astype(str)
        large_data = size_data[['TRADE_DATE', 'LARGE_CROWDING', 'LARGE_SPREAD', 'LARGE_MOMENTUM']]
        large_data['LARGE_TIMING'] = (large_data['LARGE_CROWDING'] * (-1.0) + large_data['LARGE_MOMENTUM']) / 2.0
        # large_data['LARGE_TIMING'] = large_data['LARGE_CROWDING'] * (-1.0)
        # large_data['LARGE_TIMING'] = large_data['LARGE_TIMING'].rolling(window=20, min_periods=1, center=False).mean()
        large_data = large_data.merge(large_index, on=['TRADE_DATE'], how='left')
        large_data_disp = large_data[large_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        # large_data_disp = large_data.copy(deep=True)
        large_data_disp['TRADE_DATE_DISP'] = large_data_disp['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))

        small_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['000905'])
        small_index = small_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        small_index = small_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        small_index['TRADE_DATE'] = small_index['TRADE_DATE'].astype(str)
        small_data = size_data[['TRADE_DATE', 'SMALL_CROWDING', 'SMALL_SPREAD', 'SMALL_MOMENTUM']]
        small_data['SMALL_TIMING'] = (small_data['SMALL_CROWDING'] * (-1.0) + small_data['SMALL_MOMENTUM']) / 2.0
        # small_data['SMALL_TIMING'] = small_data['SMALL_CROWDING'] * (-1.0)
        # small_data['SMALL_TIMING'] = small_data['SMALL_TIMING'].rolling(window=20, min_periods=1, center=False).mean()
        small_data = small_data.merge(small_index, on=['TRADE_DATE'], how='left')
        small_data_disp = small_data[small_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        # small_data_disp = small_data.copy(deep=True)
        small_data_disp['TRADE_DATE_DISP'] = small_data_disp['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        ax1.plot(large_data_disp['TRADE_DATE_DISP'].values, large_data_disp['LARGE_TIMING'].values, color=line_color_list[4], label='大盘择时因子')
        ax2.plot(large_data_disp['TRADE_DATE_DISP'].values, large_data_disp['CLOSE_INDEX'].values, color=line_color_list[0], label='沪深300指数走势（右轴）')
        ax1.plot(small_data_disp['TRADE_DATE_DISP'].values, small_data_disp['SMALL_TIMING'].values, color=line_color_list[9], label='中小盘择时因子')
        ax2.plot(small_data_disp['TRADE_DATE_DISP'].values, small_data_disp['CLOSE_INDEX'].values, color=line_color_list[1], label='中证500指数走势（右轴）')
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4)
        plt.title('规模择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}size_timing.png'.format(self.data_path))

        large_data['LARGE_TIMING_UP1'] = large_data['LARGE_TIMING'].rolling(window=250, min_periods=1,  center=False).mean() + 0.5 * large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        large_data['LARGE_TIMING_DOWN1'] = large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        large_data['LARGE_TIMING_UP15'] = large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        large_data['LARGE_TIMING_DOWN15'] = large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        large_data['LARGE_TIMING_SCORE'] = large_data.apply(lambda x: 5 if x['LARGE_TIMING'] >= x['LARGE_TIMING_UP15'] else
                                                                     4 if x['LARGE_TIMING'] >= x['LARGE_TIMING_UP1'] else
                                                                     1 if x['LARGE_TIMING'] <= x['LARGE_TIMING_DOWN15'] else
                                                                     2 if x['LARGE_TIMING'] <= x['LARGE_TIMING_DOWN1'] else 3, axis=1)
        large_data_monthly = large_data[large_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        large_index = large_index.merge(large_data_monthly[['TRADE_DATE', 'LARGE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        large_index['LARGE_TIMING_SCORE'] = large_index['LARGE_TIMING_SCORE'].fillna(method='ffill')
        large_index = large_index.dropna(subset=['LARGE_TIMING_SCORE'])
        large_index['RET'] = large_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        large_index['RET_ADJ'] = large_index.apply(lambda x: x['RET'] if x['LARGE_TIMING_SCORE'] == 4 or x['LARGE_TIMING_SCORE'] == 5 else 0.0, axis=1)
        large_index['RET_ADJ'] = large_index['RET_ADJ'].fillna(0.0)
        large_index['NAV'] = (large_index['RET_ADJ'] + 1).cumprod()
        large_index['CLOSE_INDEX'] = large_index['CLOSE_INDEX'] / large_index['CLOSE_INDEX'].iloc[0]
        large_index['TRADE_DATE_DISP'] = large_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        large_index_1 = large_index[large_index['LARGE_TIMING_SCORE'] == 1]
        large_index_2 = large_index[large_index['LARGE_TIMING_SCORE'] == 2]
        large_index_3 = large_index[large_index['LARGE_TIMING_SCORE'] == 3]
        large_index_4 = large_index[large_index['LARGE_TIMING_SCORE'] == 4]
        large_index_5 = large_index[large_index['LARGE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(large_index['TRADE_DATE_DISP'].values, large_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(large_index['TRADE_DATE_DISP'].values, large_index['CLOSE_INDEX'].values, color=line_color_list[3], label='沪深300指数走势')
        ax.scatter(large_index_1['TRADE_DATE_DISP'].values, large_index_1['CLOSE_INDEX'].values, color=line_color_list[1], label='得分1')
        ax.scatter(large_index_2['TRADE_DATE_DISP'].values, large_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(large_index_3['TRADE_DATE_DISP'].values, large_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(large_index_4['TRADE_DATE_DISP'].values, large_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(large_index_5['TRADE_DATE_DISP'].values, large_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('大盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}large_timing.png'.format(self.data_path))

        small_data['SMALL_TIMING_UP1'] = small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).mean() + 0.5 * small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        small_data['SMALL_TIMING_DOWN1'] = small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        small_data['SMALL_TIMING_UP15'] = small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        small_data['SMALL_TIMING_DOWN15'] = small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        small_data['SMALL_TIMING_SCORE'] = small_data.apply(lambda x: 5 if x['SMALL_TIMING'] >= x['SMALL_TIMING_UP15'] else
                                                                      4 if x['SMALL_TIMING'] >= x['SMALL_TIMING_UP1'] else
                                                                      1 if x['SMALL_TIMING'] <= x['SMALL_TIMING_DOWN15'] else
                                                                      2 if x['SMALL_TIMING'] <= x['SMALL_TIMING_DOWN1'] else 3, axis=1)
        small_data_monthly = small_data[small_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        small_index = small_index.merge(small_data_monthly[['TRADE_DATE', 'SMALL_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        small_index['SMALL_TIMING_SCORE'] = small_index['SMALL_TIMING_SCORE'].fillna(method='ffill')
        small_index = small_index.dropna(subset=['SMALL_TIMING_SCORE'])
        small_index['RET'] = small_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        small_index['RET_ADJ'] = small_index.apply(lambda x: x['RET'] if x['SMALL_TIMING_SCORE'] == 4 or x['SMALL_TIMING_SCORE'] == 5 else 0.0, axis=1)
        small_index['RET_ADJ'] = small_index['RET_ADJ'].fillna(0.0)
        small_index['NAV'] = (small_index['RET_ADJ'] + 1).cumprod()
        small_index['CLOSE_INDEX'] = small_index['CLOSE_INDEX'] / small_index['CLOSE_INDEX'].iloc[0]
        small_index['TRADE_DATE_DISP'] = small_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        small_index_1 = small_index[small_index['SMALL_TIMING_SCORE'] == 1]
        small_index_2 = small_index[small_index['SMALL_TIMING_SCORE'] == 2]
        small_index_3 = small_index[small_index['SMALL_TIMING_SCORE'] == 3]
        small_index_4 = small_index[small_index['SMALL_TIMING_SCORE'] == 4]
        small_index_5 = small_index[small_index['SMALL_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(small_index['TRADE_DATE_DISP'].values, small_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(small_index['TRADE_DATE_DISP'].values, small_index['CLOSE_INDEX'].values, color=line_color_list[3], label='中证500指数走势')
        ax.scatter(small_index_1['TRADE_DATE_DISP'].values, small_index_1['CLOSE_INDEX'].values,  color=line_color_list[1], label='得分1')
        ax.scatter(small_index_2['TRADE_DATE_DISP'].values, small_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(small_index_3['TRADE_DATE_DISP'].values, small_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(small_index_4['TRADE_DATE_DISP'].values, small_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(small_index_5['TRADE_DATE_DISP'].values, small_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('中小盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}small_timing.png'.format(self.data_path))

        size_res = large_data_monthly[['TRADE_DATE', 'LARGE_TIMING_SCORE']].merge(small_data_monthly[['TRADE_DATE', 'SMALL_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        size_res['LARGE_SMALL'] = size_res['LARGE_TIMING_SCORE'] - size_res['SMALL_TIMING_SCORE']
        size_res['SMALL_LARGE'] = size_res['SMALL_TIMING_SCORE'] - size_res['LARGE_TIMING_SCORE']
        size_res['MARK'] = '均衡'
        size_res.loc[(size_res['LARGE_TIMING_SCORE'] >= 4) & (size_res['LARGE_SMALL'] >= 1), 'MARK'] = '大盘'
        size_res.loc[(size_res['SMALL_TIMING_SCORE'] >= 4) & (size_res['SMALL_LARGE'] >= 1), 'MARK'] = '中小盘'
        size_stats = size_res[['TRADE_DATE', 'MARK']].groupby('MARK').count()
        print(size_stats)

        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001', '000300', '000905'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].astype(str)
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(size_res.set_index('TRADE_DATE')[['MARK']], left_index=True, right_index=True, how='left')
        index = index.reset_index()
        index['MARK'] = index['MARK'].fillna(method='ffill')
        index = index.dropna(subset=['MARK'])
        index['RET_ADJ'] = index.apply(lambda x: x['000300_RET'] if x['MARK'] == '大盘' else x['000905_RET'] if x['MARK'] == '中小盘' else x['881001_RET'], axis=1)
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index[['000300', '000905', '881001']] = index[['000300', '000905', '881001']] / index[['000300', '000905', '881001']].iloc[0]
        index['TRADE_DATE_DISP'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        index_large = index[index['MARK'] == '大盘']
        index_balance = index[index['MARK'] == '均衡']
        index_small = index[index['MARK'] == '中小盘']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(index['TRADE_DATE_DISP'].values, index['881001'].values, color=line_color_list[3], label='万得全A走势')
        ax.scatter(index_large['TRADE_DATE_DISP'].values, index_large['881001'].values,  color=line_color_list[0], label='大盘')
        ax.scatter(index_balance['TRADE_DATE_DISP'].values, index_balance['881001'].values, color=line_color_list[3], label='均衡')
        ax.scatter(index_small['TRADE_DATE_DISP'].values, index_small['881001'].values, color=line_color_list[1], label='中小盘')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('规模择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}size_timing_strategy.png'.format(self.data_path))
        return

    def test_2(self):
        size_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        size_index = size_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_index['TRADE_DATE'] = size_index['TRADE_DATE'].astype(str)
        size_index = size_index[size_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_index = size_index[(size_index['TRADE_DATE'] > self.start_date) & (size_index['TRADE_DATE'] <= self.end_date)]
        size_index = size_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_index = size_index.rename(columns={'399314': '大盘', '399401': '中小盘'})
        size_index['大盘/中小盘'] = size_index['大盘'] / size_index['中小盘']
        size_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1)
        plt.title('大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘中小盘历史相对走势.png'.format(self.data_path))

        # 期限利差
        # bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期长端国债利率', '1年期短端国债利率']
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield = bond_yield[(bond_yield.index > self.start_date) & (bond_yield.index <= self.end_date)]
        bond_yield['期限利差'] = bond_yield['10年期长端国债利率'] - bond_yield['1年期短端国债利率']
        bond_yield.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield.index)
        bond_yield_disp = size_index.merge(bond_yield, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_yield_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_yield_disp.index)
        bond_yield_disp = bond_yield_disp.loc[bond_yield_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['期限利差'].values, color=line_color_list[0], label='期限利差')
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('期限利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 经济增长
        # economic_growth = w.edb("M0039354,S0029657", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # economic_growth.to_hdf('{0}economic_growth.hdf'.format(self.data_path), key='table', mode='w')
        economic_growth = pd.read_hdf('{0}economic_growth.hdf'.format(self.data_path), key='table')
        economic_growth.columns = ['TRADE_DATE', 'GDP实际同比', '房地产开发投资完成额累计同比']
        economic_growth['TRADE_DATE'] = economic_growth['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        economic_growth = economic_growth.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        economic_growth = economic_growth[economic_growth.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        economic_growth = economic_growth[(economic_growth.index > self.start_date) & (economic_growth.index <= self.end_date)]
        economic_growth.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), economic_growth.index)
        economic_growth_disp = size_index.merge(economic_growth, left_index=True, right_index=True, how='left').sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        economic_growth_disp.index = map(lambda x: x.strftime('%Y%m%d'), economic_growth_disp.index)
        economic_growth_disp = economic_growth_disp.loc[economic_growth_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        economic_growth_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), economic_growth_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(economic_growth_disp.index, economic_growth_disp['房地产开发投资完成额累计同比'].values, color=line_color_list[0], label='房地产开发投资完成额累计同比')
        ax.plot(economic_growth_disp.index, economic_growth_disp['GDP实际同比'].values, color=line_color_list[2], label='GDP实际同比')
        ax_r.plot(economic_growth_disp.index, economic_growth_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.title('经济增长与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}经济增长与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 外资北向持股
        # sh_cash = w.wset("shhktransactionstatistics", "startdate={0};enddate={1};cycle=day;currency=hkd;field=date,sh_net_purchases".format(self.start_date_hyphen, self.end_date_hyphen), usedf=True)[1].reset_index()
        # sh_cash.to_hdf('{0}sh_cash.hdf'.format(self.data_path), key='table', mode='w')
        sh_cash = pd.read_hdf('{0}sh_cash.hdf'.format(self.data_path), key='table')
        sh_cash = sh_cash.drop('index', axis=1)
        sh_cash.columns = ['TRADE_DATE', 'SH_NET_PURCHASE']
        # sz_cash = w.wset("szhktransactionstatistics", "startdate={0};enddate={1};cycle=day;currency=hkd;field=date,sz_net_purchases".format(self.start_date_hyphen, self.end_date_hyphen), usedf=True)[1].reset_index()
        # sz_cash.to_hdf('{0}sz_cash.hdf'.format(self.data_path), key='table', mode='w')
        sz_cash = pd.read_hdf('{0}sz_cash.hdf'.format(self.data_path), key='table')
        sz_cash = sz_cash.drop('index', axis=1)
        sz_cash.columns = ['TRADE_DATE', 'SZ_NET_PURCHASE']
        north_cash = sh_cash.merge(sz_cash, on=['TRADE_DATE'], how='left')
        north_cash['NORTH_NET_PURCHASE'] = north_cash['SH_NET_PURCHASE'].fillna(0.0) + north_cash['SZ_NET_PURCHASE'].fillna(0.0)
        north_cash['TRADE_DATE'] = north_cash['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        north_cash = north_cash.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        north_cash = north_cash[north_cash.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        north_cash = north_cash[(north_cash.index > self.start_date) & (north_cash.index <= self.end_date)]
        north_cash['北向资金近一月净买入'] = north_cash['NORTH_NET_PURCHASE'].rolling(20).sum()
        north_cash.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), north_cash.index)
        north_cash_disp = size_index.merge(north_cash, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        north_cash_disp.index = map(lambda x: x.strftime('%Y%m%d'), north_cash_disp.index)
        north_cash_disp = north_cash_disp.loc[north_cash_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        north_cash_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), north_cash_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(north_cash_disp.index, north_cash_disp['北向资金近一月净买入'].values, color=line_color_list[0], label='北向资金近一月成交净买入（亿元）')
        ax_r.plot(north_cash_disp.index, north_cash_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('北向资金与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}北向资金与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 动量效应
        size_momentum = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        size_momentum = size_momentum.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_momentum['TRADE_DATE'] = size_momentum['TRADE_DATE'].astype(str)
        size_momentum = size_momentum[size_momentum['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_momentum = size_momentum[(size_momentum['TRADE_DATE'] > self.start_date) & (size_momentum['TRADE_DATE'] <= self.end_date)]
        size_momentum = size_momentum.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_momentum = size_momentum.rename(columns={'399314': '大盘', '399401': '中小盘'})
        size_momentum['大盘/中小盘'] = size_momentum['大盘'] / size_momentum['中小盘']
        size_momentum['大盘/中小盘_MA20'] = size_momentum['大盘/中小盘'].rolling(20).mean()
        size_momentum.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum.index)
        size_momentum_disp = size_momentum.copy(deep=True)
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp = size_momentum_disp.loc[size_momentum_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_momentum_disp.index, size_momentum_disp['大盘/中小盘_MA20'].values, color=line_color_list[0], label='大盘/中小盘近一月移动平均')
        ax_r.plot(size_momentum_disp.index, size_momentum_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('动量效应与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}动量效应与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 风格关注度
        # size_turnover = w.wsd("399314.sz,399401.sz", "dq_amtturnover", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # size_turnover.to_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table', mode='w')
        size_turnover = pd.read_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table')
        size_turnover.columns = ['TRADE_DATE', '大盘换手率', '中小盘换手率']
        size_turnover['TRADE_DATE'] = size_turnover['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        size_turnover = size_turnover.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_turnover = size_turnover[size_turnover.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_turnover = size_turnover[(size_turnover.index > self.start_date) & (size_turnover.index <= self.end_date)]
        size_turnover['相对换手率'] = size_turnover['大盘换手率'] / size_turnover['中小盘换手率']
        size_turnover['风格关注度'] = size_turnover['相对换手率'].rolling(60).sum()
        size_turnover.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover.index)
        size_turnover_disp = size_index.merge(size_turnover, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp = size_turnover_disp.loc[size_turnover_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度'].values, color=line_color_list[0], label='风格关注度')
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('风格关注度与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}风格关注度与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 因子动量离散拥挤度
        size_factor = FEDB().read_timing_data(['TRADE_DATE', 'SIZE_MOMENTUM', 'SIZE_SPREAD', 'SIZE_CROWDING'], 'timing_style', '20071231', self.end_date)
        size_factor.columns = ['TRADE_DATE', 'LARGE_MOMENTUM', 'LARGE_SPREAD', 'LARGE_CROWDING']
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_SPREAD'] = size_factor['LARGE_SPREAD'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_CROWDING'] = size_factor['LARGE_CROWDING'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['因子动量离散拥挤度'] = (size_factor['LARGE_MOMENTUM'] + size_factor['LARGE_SPREAD'] + size_factor['LARGE_CROWDING'] * (-1.0)) / 3.0
        size_factor['TRADE_DATE'] = size_factor['TRADE_DATE'].astype(str)
        size_factor = size_factor.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_factor = size_factor[size_factor.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_factor = size_factor[(size_factor.index > self.start_date) & (size_factor.index <= self.end_date)]
        size_factor.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor.index)
        size_factor_disp = size_index.merge(size_factor, left_index=True, right_index=True, how='left').sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_factor_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_factor_disp.index)
        size_factor_disp = size_factor_disp.loc[size_factor_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_factor_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_factor_disp.index, size_factor_disp['因子动量离散拥挤度'].values, color=line_color_list[0], label='因子动量离散拥挤度复合指标')
        ax_r.plot(size_factor_disp.index, size_factor_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('因子动量离散拥挤度复合指标与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子动量离散拥挤度复合指标与大盘中小盘历史相对走势.png'.format(self.data_path))

        size_data_ori = size_index.merge(bond_yield[['期限利差']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(economic_growth[['房地产开发投资完成额累计同比']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(north_cash[['北向资金近一月净买入']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(size_momentum[['大盘/中小盘_MA20']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(size_turnover[['风格关注度']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(size_factor[['因子动量离散拥挤度']], left_index=True, right_index=True, how='left').sort_index()
        #######################################################################
        # 标准化后加权
        size_data = size_data_ori.drop(['大盘', '中小盘', '大盘/中小盘', '大盘/中小盘_MA20'], axis=1)
        for col in list(size_data.columns):
            size_data[col] = size_data[col].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_data['期限利差'] = size_data['期限利差'] * (-1)
        size_data['风格关注度'] = size_data['风格关注度'] * (-1)
        size_data['SIZE_TIMING'] = size_data.apply(lambda x: np.nanmean(x), axis=1)
        size_data_disp = size_index.merge(size_data[['SIZE_TIMING']], left_index=True, right_index=True, how='left').dropna()
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        ax1.plot(size_data_disp.index, size_data_disp['SIZE_TIMING'].values, color=line_color_list[0], label='大中小盘择时因子')
        ax2.plot(size_data_disp.index, size_data_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('风格择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}size_timing.png'.format(self.data_path))

        size_data['SIZE_TIMING_UP1'] = size_data['SIZE_TIMING'].rolling(window=250, min_periods=1,  center=False).mean() + 0.5 * size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        size_data['SIZE_TIMING_DOWN1'] = size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        size_data['SIZE_TIMING_UP15'] = size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        size_data['SIZE_TIMING_DOWN15'] = size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        size_data['SIZE_TIMING_SCORE'] = size_data.apply(lambda x: 5 if x['SIZE_TIMING'] >= x['SIZE_TIMING_UP15'] else
                                                                   4 if x['SIZE_TIMING'] >= x['SIZE_TIMING_UP1'] else
                                                                   1 if x['SIZE_TIMING'] <= x['SIZE_TIMING_DOWN15'] else
                                                                   2 if x['SIZE_TIMING'] <= x['SIZE_TIMING_DOWN1'] else 3, axis=1)
        size_data_monthly = size_data[size_data.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        size_index = size_index.merge(size_data_monthly[['SIZE_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        size_index['SIZE_TIMING_SCORE'] = size_index['SIZE_TIMING_SCORE'].fillna(method='ffill')
        size_index = size_index.dropna(subset=['SIZE_TIMING_SCORE'])
        size_index_1 = size_index[size_index['SIZE_TIMING_SCORE'] == 1]
        size_index_2 = size_index[size_index['SIZE_TIMING_SCORE'] == 2]
        size_index_3 = size_index[size_index['SIZE_TIMING_SCORE'] == 3]
        size_index_4 = size_index[size_index['SIZE_TIMING_SCORE'] == 4]
        size_index_5 = size_index[size_index['SIZE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[3], label='大盘/中小盘')
        ax.scatter(size_index_1.index, size_index_1['大盘/中小盘'].values, color=line_color_list[1], label='得分1')
        ax.scatter(size_index_2.index, size_index_2['大盘/中小盘'].values, color=line_color_list[9], label='得分2')
        ax.scatter(size_index_3.index, size_index_3['大盘/中小盘'].values, color=line_color_list[3], label='得分3')
        ax.scatter(size_index_4.index, size_index_4['大盘/中小盘'].values, color=line_color_list[4], label='得分4')
        ax.scatter(size_index_5.index, size_index_5['大盘/中小盘'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('大中小盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时.png'.format(self.data_path))
        ##########################################################
        size_data = size_data_ori.sort_index()
        size_data['IDX'] = range(len(size_data))
        size_data['期限利差'] = size_data['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '期限利差', size_data))
        size_data['风格关注度'] = size_data['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '风格关注度', size_data))
        size_data['因子动量离散拥挤度'] = size_data['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '因子动量离散拥挤度', size_data))
        size_data_monthly = size_data[size_data.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        size_data_monthly['房地产开发投资完成额累计同比_diff'] = size_data_monthly['房地产开发投资完成额累计同比'].diff()
        size_data_monthly['期限利差_large_score'] = size_data['期限利差'].apply(lambda x: 1 if x < 0.5 else 0)
        size_data_monthly['房地产开发投资完成额累计同比_large_score'] = size_data_monthly['房地产开发投资完成额累计同比_diff'].apply(lambda x: 1 if x > 0 else 0)
        size_data_monthly['大盘/中小盘_MA20_large_score'] = size_data_monthly.apply(lambda x: 1 if x['大盘/中小盘'] > x['大盘/中小盘_MA20'] else 0, axis=1)
        size_data_monthly['风格关注度_large_score'] = size_data_monthly['风格关注度'].apply(lambda x: 1 if x < 0.5 else 0)
        size_data_monthly['因子动量离散拥挤度_large_score'] = size_data_monthly['因子动量离散拥挤度'].apply(lambda x: 1 if x > 0.5 else 0)
        size_data_monthly['LARGE_TIMING_SCORE'] = size_data_monthly['期限利差_large_score'] + size_data_monthly['房地产开发投资完成额累计同比_large_score'] + size_data_monthly['大盘/中小盘_MA20_large_score'] + size_data_monthly['风格关注度_large_score'] + size_data_monthly['因子动量离散拥挤度_large_score']
        size_data_monthly['期限利差_small_score'] = size_data['期限利差'].apply(lambda x: 1 if x > 0.5 else 0)
        size_data_monthly['房地产开发投资完成额累计同比_small_score'] = size_data_monthly['房地产开发投资完成额累计同比_diff'].apply(lambda x: 1 if x < 0 else 0)
        size_data_monthly['大盘/中小盘_MA20_small_score'] = size_data_monthly.apply(lambda x: 1 if x['大盘/中小盘'] < x['大盘/中小盘_MA20'] else 0, axis=1)
        size_data_monthly['风格关注度_small_score'] = size_data_monthly['风格关注度'].apply(lambda x: 1 if x > 0.5 else 0)
        size_data_monthly['因子动量离散拥挤度_small_score'] = size_data_monthly['因子动量离散拥挤度'].apply(lambda x: 1 if x < 0.5 else 0)
        size_data_monthly['SMALL_TIMING_SCORE'] = size_data_monthly['期限利差_small_score'] + size_data_monthly['房地产开发投资完成额累计同比_small_score'] + size_data_monthly['大盘/中小盘_MA20_small_score'] + size_data_monthly['风格关注度_small_score'] + size_data_monthly['因子动量离散拥挤度_small_score']

        size_res = size_data_monthly[['LARGE_TIMING_SCORE', 'SMALL_TIMING_SCORE']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        size_res['TRADE_DATE'] = size_res['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        size_res['LARGE_SMALL'] = size_res['LARGE_TIMING_SCORE'] - size_res['SMALL_TIMING_SCORE']
        size_res['SMALL_LARGE'] = size_res['SMALL_TIMING_SCORE'] - size_res['LARGE_TIMING_SCORE']
        size_res['MARK'] = '均衡'
        size_res.loc[(size_res['LARGE_TIMING_SCORE'] >= 4) & (size_res['LARGE_SMALL'] >= 1), 'MARK'] = '大盘'
        size_res.loc[(size_res['SMALL_TIMING_SCORE'] >= 4) & (size_res['SMALL_LARGE'] >= 1), 'MARK'] = '中小盘'
        size_stats = size_res[['TRADE_DATE', 'MARK']].groupby('MARK').count()
        print(size_stats)

        size_index = size_index.merge(size_data_monthly[['LARGE_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        size_index['LARGE_TIMING_SCORE'] = size_index['LARGE_TIMING_SCORE'].fillna(method='ffill')
        size_index = size_index.dropna(subset=['SIZE_TIMING_SCORE'])
        size_index_1 = size_index[size_index['LARGE_TIMING_SCORE'] == 1]
        size_index_2 = size_index[size_index['LARGE_TIMING_SCORE'] == 2]
        size_index_3 = size_index[size_index['LARGE_TIMING_SCORE'] == 3]
        size_index_4 = size_index[size_index['LARGE_TIMING_SCORE'] == 4]
        size_index_5 = size_index[size_index['LARGE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[3], label='大盘/中小盘')
        ax.scatter(size_index_1.index, size_index_1['大盘/中小盘'].values, color=line_color_list[1], label='得分1')
        ax.scatter(size_index_2.index, size_index_2['大盘/中小盘'].values, color=line_color_list[9], label='得分2')
        ax.scatter(size_index_3.index, size_index_3['大盘/中小盘'].values, color=line_color_list[3], label='得分3')
        ax.scatter(size_index_4.index, size_index_4['大盘/中小盘'].values, color=line_color_list[4], label='得分4')
        ax.scatter(size_index_5.index, size_index_5['大盘/中小盘'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('大中小盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时.png'.format(self.data_path))

        large_data_monthly = size_data_monthly[['LARGE_TIMING_SCORE']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        large_data_monthly['TRADE_DATE'] = large_data_monthly['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        large_index = size_data[['大盘']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        large_index['TRADE_DATE'] = large_index['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        large_index = large_index.merge(large_data_monthly[['TRADE_DATE', 'LARGE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        large_index['LARGE_TIMING_SCORE'] = large_index['LARGE_TIMING_SCORE'].fillna(method='ffill')
        large_index = large_index.dropna(subset=['LARGE_TIMING_SCORE'])
        large_index['RET'] = large_index['大盘'].pct_change().fillna(0.0)
        large_index['RET_ADJ'] = large_index.apply(lambda x: x['RET'] if x['LARGE_TIMING_SCORE'] == 4 or x['LARGE_TIMING_SCORE'] == 5 else 0.0, axis=1)
        large_index['RET_ADJ'] = large_index['RET_ADJ'].fillna(0.0)
        large_index['NAV'] = (large_index['RET_ADJ'] + 1).cumprod()
        large_index['大盘'] = large_index['大盘'] / large_index['大盘'].iloc[0]
        large_index['TRADE_DATE_DISP'] = large_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        large_index_1 = large_index[large_index['LARGE_TIMING_SCORE'] == 1]
        large_index_2 = large_index[large_index['LARGE_TIMING_SCORE'] == 2]
        large_index_3 = large_index[large_index['LARGE_TIMING_SCORE'] == 3]
        large_index_4 = large_index[large_index['LARGE_TIMING_SCORE'] == 4]
        large_index_5 = large_index[large_index['LARGE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(large_index['TRADE_DATE_DISP'].values, large_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(large_index['TRADE_DATE_DISP'].values, large_index['大盘'].values, color=line_color_list[3], label='巨潮大盘指数走势')
        ax.scatter(large_index_1['TRADE_DATE_DISP'].values, large_index_1['大盘'].values, color=line_color_list[1], label='得分1')
        ax.scatter(large_index_2['TRADE_DATE_DISP'].values, large_index_2['大盘'].values, color=line_color_list[9], label='得分2')
        ax.scatter(large_index_3['TRADE_DATE_DISP'].values, large_index_3['大盘'].values, color=line_color_list[3], label='得分3')
        ax.scatter(large_index_4['TRADE_DATE_DISP'].values, large_index_4['大盘'].values, color=line_color_list[4], label='得分4')
        ax.scatter(large_index_5['TRADE_DATE_DISP'].values, large_index_5['大盘'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('大盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘择时.png'.format(self.data_path))

        small_data_monthly = size_data_monthly[['SMALL_TIMING_SCORE']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        small_data_monthly['TRADE_DATE'] = small_data_monthly['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        small_index = size_data[['中小盘']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        small_index['TRADE_DATE'] = small_index['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        small_index = small_index.merge(small_data_monthly[['TRADE_DATE', 'SMALL_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        small_index['SMALL_TIMING_SCORE'] = small_index['SMALL_TIMING_SCORE'].fillna(method='ffill')
        small_index = small_index.dropna(subset=['SMALL_TIMING_SCORE'])
        small_index['RET'] = small_index['中小盘'].pct_change().fillna(0.0)
        small_index['RET_ADJ'] = small_index.apply(lambda x: x['RET'] if x['SMALL_TIMING_SCORE'] == 4 or x['SMALL_TIMING_SCORE'] == 5 else 0.0, axis=1)
        small_index['RET_ADJ'] = small_index['RET_ADJ'].fillna(0.0)
        small_index['NAV'] = (small_index['RET_ADJ'] + 1).cumprod()
        small_index['中小盘'] = small_index['中小盘'] / small_index['中小盘'].iloc[0]
        small_index['TRADE_DATE_DISP'] = small_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        small_index_1 = small_index[small_index['SMALL_TIMING_SCORE'] == 1]
        small_index_2 = small_index[small_index['SMALL_TIMING_SCORE'] == 2]
        small_index_3 = small_index[small_index['SMALL_TIMING_SCORE'] == 3]
        small_index_4 = small_index[small_index['SMALL_TIMING_SCORE'] == 4]
        small_index_5 = small_index[small_index['SMALL_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(small_index['TRADE_DATE_DISP'].values, small_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(small_index['TRADE_DATE_DISP'].values, small_index['中小盘'].values, color=line_color_list[3], label='巨潮中小盘指数走势')
        ax.scatter(small_index_1['TRADE_DATE_DISP'].values, small_index_1['中小盘'].values, color=line_color_list[1], label='得分1')
        ax.scatter(small_index_2['TRADE_DATE_DISP'].values, small_index_2['中小盘'].values, color=line_color_list[9], label='得分2')
        ax.scatter(small_index_3['TRADE_DATE_DISP'].values, small_index_3['中小盘'].values, color=line_color_list[3], label='得分3')
        ax.scatter(small_index_4['TRADE_DATE_DISP'].values, small_index_4['中小盘'].values, color=line_color_list[4], label='得分4')
        ax.scatter(small_index_5['TRADE_DATE_DISP'].values, small_index_5['中小盘'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('中小盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}中小盘择时.png'.format(self.data_path))

        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001', '399314', '399401'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].astype(str)
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(size_res.set_index('TRADE_DATE')[['MARK']], left_index=True, right_index=True, how='left')
        index = index.reset_index()
        index['MARK'] = index['MARK'].fillna(method='ffill')
        index = index.dropna(subset=['MARK'])
        index['RET_ADJ'] = index.apply(lambda x: x['399314_RET'] if x['MARK'] == '大盘' else x['399401_RET'] if x['MARK'] == '中小盘' else x['881001_RET'], axis=1)
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index = index.dropna()
        index[['399314', '399401', '881001']] = index[['399314', '399401', '881001']] / index[['399314', '399401', '881001']].iloc[0]
        index['TRADE_DATE_DISP'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        index_large = index[index['MARK'] == '大盘']
        index_balance = index[index['MARK'] == '均衡']
        index_small = index[index['MARK'] == '中小盘']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(index['TRADE_DATE_DISP'].values, index['881001'].values, color=line_color_list[3], label='万得全A走势')
        ax.scatter(index_large['TRADE_DATE_DISP'].values, index_large['881001'].values, color=line_color_list[0], label='大盘')
        ax.scatter(index_balance['TRADE_DATE_DISP'].values, index_balance['881001'].values, color=line_color_list[3], label='均衡')
        ax.scatter(index_small['TRADE_DATE_DISP'].values, index_small['881001'].values, color=line_color_list[1], label='中小盘')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('大中小盘择时策略', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时策略.png'.format(self.data_path))

        index_res = index[index['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        index_res = index_res[['TRADE_DATE', '399314', '399401']].sort_values('TRADE_DATE')
        index_res['399314_RET'] = index_res['399314'].pct_change()
        index_res['399401_RET'] = index_res['399401'].pct_change()
        index_res['399314_RET_diff'] = index_res['399314_RET'].diff()
        index_res['399401_RET_diff'] = index_res['399401_RET'].diff()
        index_res['399314_399401'] = index_res['399314_RET'] - index_res['399401_RET']
        index_res['399401_399314'] = index_res['399401_RET'] - index_res['399314_RET']
        index_res['399314/399401'] = index_res['399314'] / index_res['399401']
        index_res['399314/399401_RET'] = index_res['399314/399401'].pct_change()
        index_res['399401/399314'] = index_res['399401'] / index_res['399314']
        index_res['399401/399314_RET'] = index_res['399401/399314'].pct_change()
        index_res['INDEX_MARK'] = '均衡'
        index_res.loc[(index_res['399314_399401'] > 0.05) | (index_res['399314/399401_RET'] > 0.05), 'INDEX_MARK'] = '大盘'
        index_res.loc[(index_res['399401_399314'] > 0.05) | (index_res['399401/399314_RET'] > 0.05), 'INDEX_MARK'] = '中小盘'
        res = size_res[['TRADE_DATE', 'MARK']].merge(index_res[['TRADE_DATE', 'INDEX_MARK']], on=['TRADE_DATE'], how='left').dropna()
        res['INDEX_MARK'] = res['INDEX_MARK'].shift(-1)
        win_rate = len(res[res['MARK'] == res['INDEX_MARK']]) / float(len(res))
        print(win_rate)
        return

    def test_3(self):
        size_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401', '881001'])
        size_index = size_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_index['TRADE_DATE'] = size_index['TRADE_DATE'].astype(str)
        size_index = size_index[size_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_index = size_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_index = size_index.rename(columns={'399314': '大盘', '399401': '中小盘', '881001': '万得全A'})
        size_index['大盘/中小盘'] = size_index['大盘'] / size_index['中小盘']
        size_index = size_index[(size_index.index > self.start_date) & (size_index.index <= self.end_date)]
        size_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1)
        plt.title('大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘中小盘历史相对走势.png'.format(self.data_path))

        # # 经济增长
        # economic_growth = w.edb("M0039354,S0029657", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # economic_growth.to_hdf('{0}economic_growth.hdf'.format(self.data_path), key='table', mode='w')
        # economic_growth = pd.read_hdf('{0}economic_growth.hdf'.format(self.data_path), key='table')
        # economic_growth.columns = ['TRADE_DATE', 'GDP实际同比', '房地产开发投资完成额累计同比']
        # economic_growth['TRADE_DATE'] = economic_growth['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        # economic_growth['房地产开发投资完成额累计同比'] = economic_growth['房地产开发投资完成额累计同比'].shift()
        # economic_growth = economic_growth.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        # economic_growth = economic_growth[economic_growth.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        # economic_growth = economic_growth[(economic_growth.index > self.start_date) & (economic_growth.index <= self.end_date)]
        # economic_growth.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), economic_growth.index)
        # economic_growth_disp = size_index.merge(economic_growth, left_index=True, right_index=True, how='left').sort_index()
        # month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        # economic_growth_disp.index = map(lambda x: x.strftime('%Y%m%d'), economic_growth_disp.index)
        # economic_growth_disp = economic_growth_disp.loc[economic_growth_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        # economic_growth_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), economic_growth_disp.index)
        # ##########################
        # economic_growth_disp['房地产开发投资完成额累计同比变化'] = economic_growth_disp['房地产开发投资完成额累计同比'].pct_change()
        # economic_growth_disp['大盘月度收益率'] = economic_growth_disp['大盘'].pct_change()#.shift(-1)
        # economic_growth_disp['中小盘月度收益率'] = economic_growth_disp['中小盘'].pct_change()#.shift(-1)
        # economic_growth_disp['大盘/中小盘月度收益率'] = economic_growth_disp['大盘/中小盘'].pct_change()#.shift(-1)
        # economic_growth_disp = economic_growth_disp.dropna(subset=['房地产开发投资完成额累计同比变化'])
        # economic_growth_disp['分组'] = economic_growth_disp['房地产开发投资完成额累计同比变化'].apply(lambda x: '经济上行' if x > 0 else '经济下行')
        # economic_growth_disp_stat = economic_growth_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        # economic_growth_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        # economic_growth_disp.loc[economic_growth_disp['房地产开发投资完成额累计同比变化'] < 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        # len(economic_growth_disp.loc[(economic_growth_disp['房地产开发投资完成额累计同比变化'] < 0.5) & (economic_growth_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(economic_growth_disp.loc[economic_growth_disp['房地产开发投资完成额累计同比变化'] < 0.5].dropna()))
        # ##########################
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.plot(economic_growth_disp.index, economic_growth_disp['房地产开发投资完成额累计同比'].values, color=line_color_list[0], label='房地产开发投资完成额累计同比')
        # ax.plot(economic_growth_disp.index, economic_growth_disp['GDP实际同比'].values, color=line_color_list[2], label='GDP实际同比')
        # ax_r.plot(economic_growth_disp.index, economic_growth_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        # ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        # plt.title('经济增长与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}经济增长与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 期限利差
        # bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期长端国债利率', '1年期短端国债利率']
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield = bond_yield[(bond_yield.index > self.start_date) & (bond_yield.index <= self.end_date)].dropna()
        bond_yield['期限利差'] = bond_yield['10年期长端国债利率'] - bond_yield['1年期短端国债利率']
        bond_yield['期限利差'] = bond_yield['期限利差'].rolling(20).mean()
        bond_yield['IDX'] = range(len(bond_yield))
        bond_yield['期限利差_Q'] = bond_yield['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '期限利差', bond_yield))
        bond_yield = bond_yield.drop('IDX', axis=1)
        bond_yield.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield.index)
        ##########################
        bond_yield_disp = size_index.merge(bond_yield, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_yield_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_yield_disp.index)
        bond_yield_disp = bond_yield_disp.loc[bond_yield_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        ##########################
        bond_yield_disp['大盘月度收益率'] = bond_yield_disp['大盘'].pct_change()#.shift(-1)
        bond_yield_disp['中小盘月度收益率'] = bond_yield_disp['中小盘'].pct_change()#.shift(-1)
        bond_yield_disp['大盘/中小盘月度收益率'] = bond_yield_disp['大盘/中小盘'].pct_change()#.shift(-1)
        bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        len(bond_yield_disp.loc[(bond_yield_disp['期限利差_Q'] < 0.5) & (bond_yield_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5].dropna()))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['期限利差'].values, color=line_color_list[0], label='期限利差', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('期限利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 信用利差
        bond_spread = pd.read_excel('{0}bond_spread.xlsx'.format(self.data_path))
        bond_spread = bond_spread.rename(columns={'指标名称': 'TRADE_DATE'})
        bond_spread['TRADE_DATE'] = bond_spread['TRADE_DATE'].apply(lambda x: str(x)[:10].replace('-', ''))
        bond_spread = bond_spread.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_spread = bond_spread[bond_spread.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_spread = bond_spread[(bond_spread.index > self.start_date) & (bond_spread.index <= self.end_date)].dropna()
        bond_spread['信用利差'] = bond_spread['中债企业债到期收益率(AA+):5年'] - bond_spread['中债国开债到期收益率:5年']
        bond_spread['信用利差'] = bond_spread['信用利差'].rolling(20).mean()
        bond_spread['IDX'] = range(len(bond_spread))
        bond_spread['信用利差_Q'] = bond_spread['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '信用利差', bond_spread))
        bond_spread = bond_spread.drop('IDX', axis=1)
        bond_spread.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread.index)
        ##########################
        bond_spread_disp = size_index.merge(bond_spread, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_spread_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_spread_disp.index)
        bond_spread_disp = bond_spread_disp.loc[bond_spread_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_spread_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread_disp.index)
        ##########################
        bond_spread_disp['大盘月度收益率'] = bond_spread_disp['大盘'].pct_change()#.shift(-1)
        bond_spread_disp['中小盘月度收益率'] = bond_spread_disp['中小盘'].pct_change()#.shift(-1)
        bond_spread_disp['大盘/中小盘月度收益率'] = bond_spread_disp['大盘/中小盘'].pct_change()#.shift(-1)
        bond_spread_disp.loc[bond_spread_disp['信用利差_Q'] > 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        len(bond_spread_disp.loc[(bond_spread_disp['信用利差_Q'] > 0.5) & (bond_spread_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(bond_spread_disp.loc[bond_spread_disp['信用利差_Q'] > 0.5].dropna()))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_spread_disp.index, bond_spread_disp['信用利差'].values, color=line_color_list[0], label='信用利差', linewidth=3)
        ax_r.plot(bond_spread_disp.index, bond_spread_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('信用利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}信用利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 风格关注度
        # size_turnover = w.wsd("399314.sz,399401.sz", "dq_amtturnover", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # size_turnover.to_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table', mode='w')
        size_turnover = pd.read_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table')
        size_turnover.columns = ['TRADE_DATE', '大盘换手率', '中小盘换手率']
        size_turnover['TRADE_DATE'] = size_turnover['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        size_turnover = size_turnover.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_turnover = size_turnover[size_turnover.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_turnover = size_turnover[(size_turnover.index > self.start_date) & (size_turnover.index <= self.end_date)]
        size_turnover['相对换手率'] = size_turnover['大盘换手率'] / size_turnover['中小盘换手率']
        size_turnover['风格关注度'] = size_turnover['相对换手率'].rolling(60).mean()
        size_turnover['IDX'] = range(len(size_turnover))
        size_turnover['风格关注度_Q'] = size_turnover['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '风格关注度', size_turnover))
        size_turnover = size_turnover.drop('IDX', axis=1)
        size_turnover.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover.index)
        ##########################
        size_turnover_disp = size_index.merge(size_turnover, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp = size_turnover_disp.loc[size_turnover_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp['低分位水平线'] = 0.2
        size_turnover_disp['中分位水平线'] = 0.5
        size_turnover_disp['高分位水平线'] = 0.8
        ##########################
        size_turnover_disp['大盘月度收益率'] = size_turnover_disp['大盘'].pct_change().shift(-1)
        size_turnover_disp['中小盘月度收益率'] = size_turnover_disp['中小盘'].pct_change().shift(-1)
        size_turnover_disp['大盘/中小盘月度收益率'] = size_turnover_disp['大盘/中小盘'].pct_change().shift(-1)
        # size_turnover_disp = size_turnover_disp.dropna()
        size_turnover_disp['分组'] = size_turnover_disp['风格关注度_Q'].apply(lambda x: '0%-50%' if x >= 0.0 and x < 0.5 else '50%-100%')
        size_turnover_disp_stat = size_turnover_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_turnover_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度'].values, color=line_color_list[0], label='关注程度', linewidth=3)
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('关注程度与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}关注程度与大盘中小盘历史相对走势.png'.format(self.data_path))
        ##########################
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp_yes = size_turnover_disp.copy(deep=True)
        size_turnover_disp_no = size_turnover_disp.copy(deep=True)
        size_turnover_disp_yes['分组_SCORE'] = size_turnover_disp_yes['分组'].apply(lambda x: 1.0 if x == '0%-50%' else 0)
        size_turnover_disp_no['分组_SCORE'] = size_turnover_disp_no['分组'].apply(lambda x: 1.0 if x == '50%-100%' else 0)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度_Q'].values, color=line_color_list[0], label='关注程度近一年历史分位', linewidth=3)
        ax.plot(size_turnover_disp.index, size_turnover_disp['中分位水平线'].values, color=line_color_list[3], label='中位水平', linewidth=2, linestyle='--')
        ax.bar(np.arange(len(size_turnover_disp_yes)), size_turnover_disp_yes['分组_SCORE'].values, label='低于中位水平', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(size_turnover_disp_no)), size_turnover_disp_no['分组_SCORE'].values, label='高于中位水平', color=line_color_list[2], alpha=0.3)
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        ax.set_xticks(np.arange(len(size_turnover_disp))[::6])
        ax.set_xticklabels(labels=size_turnover_disp.index.tolist()[::6], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4)
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=5)
        plt.title('关注程度近一年历史分位与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}关注程度近一年历史分位与大盘中小盘历史相对走势.png'.format(self.data_path))
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_turnover_disp_stat)) - 0.5 * bar_width, size_turnover_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_turnover_disp_stat)) + 0.5 * bar_width, size_turnover_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        ax.set_xticks(np.arange(len(size_turnover_disp_stat)))
        ax.set_xticklabels(labels=size_turnover_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}关注程度测试.png'.format(self.data_path))

        # 动量效应
        size_momentum = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        size_momentum = size_momentum.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_momentum['TRADE_DATE'] = size_momentum['TRADE_DATE'].astype(str)
        size_momentum = size_momentum[size_momentum['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_momentum = size_momentum[(size_momentum['TRADE_DATE'] > self.start_date) & (size_momentum['TRADE_DATE'] <= self.end_date)]
        size_momentum = size_momentum.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_momentum = size_momentum.rename(columns={'399314': '大盘', '399401': '中小盘'})
        size_momentum['大盘/中小盘'] = size_momentum['大盘'] / size_momentum['中小盘']
        size_momentum['大盘/中小盘_MA20'] = size_momentum['大盘/中小盘'].rolling(20).mean()
        size_momentum = size_momentum.dropna()
        size_momentum.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum.index)
        size_momentum_disp = size_momentum.copy(deep=True)
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp = size_momentum_disp.loc[size_momentum_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        ##########################
        size_momentum_disp['大盘月度收益率'] = size_momentum_disp['大盘'].pct_change().shift(-1)
        size_momentum_disp['中小盘月度收益率'] = size_momentum_disp['中小盘'].pct_change().shift(-1)
        size_momentum_disp['大盘/中小盘月度收益率'] = size_momentum_disp['大盘/中小盘'].pct_change().shift(-1)
        # size_momentum_disp = size_momentum_disp.dropna()
        size_momentum_disp['分组'] = size_momentum_disp.apply(lambda x: '突破' if x['大盘/中小盘'] > x['大盘/中小盘_MA20'] else '未突破', axis=1)
        size_momentum_disp_stat = size_momentum_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_momentum_disp_stat = size_momentum_disp_stat.loc[['突破', '未突破']]
        size_momentum_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp_yes = size_momentum_disp.copy(deep=True)
        size_momentum_disp_no = size_momentum_disp.copy(deep=True)
        size_momentum_disp_yes['分组_SCORE'] = size_momentum_disp_yes['分组'].apply(lambda x: 1.5 if x == '突破' else 0)
        size_momentum_disp_no['分组_SCORE'] = size_momentum_disp_no['分组'].apply(lambda x: 1.5 if x == '未突破' else 0)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(np.arange(len(size_momentum_disp)), size_momentum_disp['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘', linewidth=3)
        ax.plot(np.arange(len(size_momentum_disp)), size_momentum_disp['大盘/中小盘_MA20'].values, color=line_color_list[2], label='大盘/中小盘近一月移动平均', linewidth=3)
        ax.bar(np.arange(len(size_momentum_disp_yes)), size_momentum_disp_yes['分组_SCORE'].values,  label='突破', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(size_momentum_disp_no)), size_momentum_disp_no['分组_SCORE'].values, label='未突破', color=line_color_list[2], alpha=0.3)
        ax.set_xticks(np.arange(len(size_momentum_disp))[::6])
        ax.set_xticklabels(labels=size_momentum_disp.index.tolist()[::6], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4)
        plt.title('动量突破与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}动量突破与大盘中小盘历史相对走势.png'.format(self.data_path))
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_momentum_disp_stat)) - 0.5 * bar_width, size_momentum_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_momentum_disp_stat)) + 0.5 * bar_width, size_momentum_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        ax.set_xticks(np.arange(len(size_momentum_disp_stat)))
        ax.set_xticklabels(labels=size_momentum_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}动量突破测试.png'.format(self.data_path))

        # 因子动量离散拥挤度
        size_factor = FEDB().read_timing_data(['TRADE_DATE', 'SIZE_MOMENTUM', 'SIZE_SPREAD', 'SIZE_CROWDING'], 'timing_style', '20071231', self.end_date)
        size_factor.columns = ['TRADE_DATE', 'LARGE_MOMENTUM', 'LARGE_SPREAD', 'LARGE_CROWDING']
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_SPREAD'] = size_factor['LARGE_SPREAD'].rolling(250).apply( lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_CROWDING'] = size_factor['LARGE_CROWDING'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['因子动量离散拥挤度'] = (size_factor['LARGE_MOMENTUM'] + size_factor['LARGE_SPREAD'] + size_factor['LARGE_CROWDING'] * (-1.0)) / 3.0
        size_factor['TRADE_DATE'] = size_factor['TRADE_DATE'].astype(str)
        size_factor = size_factor.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_factor['IDX'] = range(len(size_factor))
        size_factor['因子动量离散拥挤度_Q'] = size_factor['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '因子动量离散拥挤度', size_factor))
        size_factor = size_factor.drop('IDX', axis=1)
        size_factor = size_factor[size_factor.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_factor = size_factor[(size_factor.index > self.start_date) & (size_factor.index <= self.end_date)]
        size_factor.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor.index)
        size_factor_disp = size_index.merge(size_factor, left_index=True, right_index=True, how='left').sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_factor_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_factor_disp.index)
        size_factor_disp = size_factor_disp.loc[size_factor_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_factor_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor_disp.index)
        ##########################
        size_factor_disp['大盘月度收益率'] = size_factor_disp['大盘'].pct_change().shift(-1)
        size_factor_disp['中小盘月度收益率'] = size_factor_disp['中小盘'].pct_change().shift(-1)
        size_factor_disp['大盘/中小盘月度收益率'] = size_factor_disp['大盘/中小盘'].pct_change().shift(-1)
        size_factor_disp = size_factor_disp.iloc[8:]
        size_factor_disp['分组'] = size_factor_disp['因子动量离散拥挤度_Q'].apply(lambda x: '0%-50%' if x >= 0.0 and x <= 0.5 else '50%-100%')
        size_factor_disp_stat = size_factor_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_factor_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_factor_disp.index, size_factor_disp['因子动量离散拥挤度'].values, color=line_color_list[0], label='因子特征', linewidth=3)
        ax_r.plot(size_factor_disp.index, size_factor_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('因子特征与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子特征与大盘中小盘历史相对走势.png'.format(self.data_path))
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_factor_disp_stat)) - 0.5 * bar_width, size_factor_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_factor_disp_stat)) + 0.5 * bar_width, size_factor_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        ax.set_xticks(np.arange(len(size_factor_disp_stat)))
        ax.set_xticklabels(labels=size_factor_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}因子特征测试.png'.format(self.data_path))

        bond_yield_disp['期限利差_SCORE'] = bond_yield_disp['期限利差_Q'].apply(lambda x: 1 if x < 0.5 else 0)
        bond_spread_disp['信用利差_SCORE'] = bond_spread_disp['信用利差_Q'].apply(lambda x: 1 if x > 0.5 else 0)
        size_turnover_disp['风格关注度_SCORE'] = size_turnover_disp['分组'].apply(lambda x: 1 if x == '0%-50%' else 0)
        size_momentum_disp['动量突破_SCORE'] = size_momentum_disp['分组'].apply(lambda x: 1 if x == '突破' else 0)
        size_factor_disp['因子特征_SCORE'] = size_factor_disp['分组'].apply(lambda x: 1 if x == '50%-100%' else 0)
        size_timing = bond_yield_disp[['期限利差_SCORE']].merge(bond_spread_disp[['信用利差_SCORE']], left_index=True, right_index=True, how='inner')\
                                                        .merge(size_turnover_disp[['风格关注度_SCORE']], left_index=True, right_index=True, how='inner')\
                                                        .merge(size_momentum_disp[['动量突破_SCORE']], left_index=True, right_index=True, how='inner')\
                                                        .merge(size_factor_disp[['因子特征_SCORE']], left_index=True, right_index=True, how='inner')
        size_timing['大盘_SCORE'] = size_timing.sum(axis=1)
        size_timing['中小盘_SCORE'] = 5 - size_timing['大盘_SCORE']
        size_timing['大盘_WEIGHT'] = size_timing['大盘_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        size_timing['中小盘_WEIGHT'] = size_timing['中小盘_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(size_timing[['大盘_WEIGHT', '中小盘_WEIGHT']], left_index=True, right_index=True, how='left')
        index['大盘_WEIGHT'] = index['大盘_WEIGHT'].fillna(method='ffill')
        index['中小盘_WEIGHT'] = index['中小盘_WEIGHT'].fillna(method='ffill')
        index = index.dropna(subset=['大盘_WEIGHT'])
        index = index.dropna(subset=['中小盘_WEIGHT'])
        index['RET_ADJ'] = index['大盘_WEIGHT'] * index['399314_RET'] + index['中小盘_WEIGHT'] * index['399401_RET']
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index['RET_AVERAGE'] = 0.5 * index['399314_RET'] + 0.5 * index['399401_RET']
        index['RET_AVERAGE'] = index['RET_AVERAGE'].fillna(0.0)
        index['RET_AVERAGE'].iloc[0] = 0.0
        index['NAV_AVERAGE'] = (index['RET_AVERAGE'] + 1).cumprod()
        index = index.dropna()
        index[['NAV_AVERAGE', 'NAV']] = index[['NAV_AVERAGE', 'NAV']] / index[['NAV_AVERAGE', 'NAV']].iloc[0]
        index = index.reset_index()
        index['TRADE_DATE_DISP'] = index['TRADE_DATE']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='大盘/中小盘择时', linewidth=3)
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV_AVERAGE'].values, color=line_color_list[2], label='大盘/中小盘等权', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('大盘/中小盘仓位打分调仓组合回测图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时策略.png'.format(self.data_path))

        size_index = size_index.merge(size_timing[['大盘_SCORE']], left_index=True, right_index=True, how='left')
        size_index['大盘_SCORE'] = size_index['大盘_SCORE'].fillna(method='ffill')
        size_index = size_index.dropna(subset=['大盘_SCORE'])
        size_index_1 = size_index[size_index['大盘_SCORE'] == 1]
        size_index_2 = size_index[size_index['大盘_SCORE'] == 2]
        size_index_3 = size_index[size_index['大盘_SCORE'] == 3]
        size_index_4 = size_index[size_index['大盘_SCORE'] == 4]
        size_index_5 = size_index[size_index['大盘_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[3], label='大盘/中小盘')
        ax.scatter(size_index_1.index, size_index_1['大盘/中小盘'].values, color=line_color_list[1], label='大盘评分1')
        ax.scatter(size_index_2.index, size_index_2['大盘/中小盘'].values, color=line_color_list[9], label='大盘评分2')
        ax.scatter(size_index_3.index, size_index_3['大盘/中小盘'].values, color=line_color_list[3], label='大盘评分3')
        ax.scatter(size_index_4.index, size_index_4['大盘/中小盘'].values, color=line_color_list[4], label='大盘评分4')
        ax.scatter(size_index_5.index, size_index_5['大盘/中小盘'].values, color=line_color_list[0], label='大盘评分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('大盘评分及大盘/中小盘走势图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时.png'.format(self.data_path))
        return

class IndustryTest:
    def __init__(self, data_path, start_date, end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

    def test(self, index, index_name):
        industry_data = FEDB().read_timing_data(['TRADE_DATE', 'INDEX_SYMBOL', 'TURNOVER_PROPORTION', 'TURNOVER_RATE', 'CORR', 'NEW_HIGH', 'NEW_HIGH_RATIO', 'MEAN_ABOVE', 'MEAN_ABOVE_RATIO', 'MAIN_CASH_PROPORTION', 'MARGIN_PROPORTION', 'CONSENSUS_UP', 'CONSENSUS_UP_RATIO', 'CONSENSUS_DOWN', 'CONSENSUS_DOWN_RATIO', 'INDUSTRY_MOMENTUM', 'OPER_REVENUE_YOY_DIFF', 'NET_PROFIT_YOY_DIFF', 'ROE_TTM_DIFF'], 'timing_industry', self.start_date, self.end_date)
        industry_data = industry_data[(industry_data['TRADE_DATE'] > self.start_date) & (industry_data['TRADE_DATE'] <= self.end_date)]
        industry_data = industry_data[industry_data['INDEX_SYMBOL'] == index]
        industry_data['TRADE_DATE'] = industry_data['TRADE_DATE'].astype(str)

        industry_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, [index])
        industry_index = industry_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        industry_index = industry_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        industry_index['TRADE_DATE'] = industry_index['TRADE_DATE'].astype(str)
        industry_data = industry_data[['TRADE_DATE', 'TURNOVER_PROPORTION', 'TURNOVER_RATE', 'CORR', 'NEW_HIGH_RATIO', 'MEAN_ABOVE_RATIO', 'MAIN_CASH_PROPORTION', 'MARGIN_PROPORTION', 'CONSENSUS_UP_RATIO', 'INDUSTRY_MOMENTUM', 'OPER_REVENUE_YOY_DIFF', 'NET_PROFIT_YOY_DIFF', 'ROE_TTM_DIFF']]
        industry_data = industry_data.fillna(method='ffill').dropna()
        industry_data = industry_data.sort_values('TRADE_DATE')
        industry_data['IDX'] = range(len(industry_data))
        for col in list(industry_data.columns[1:-1]):
            industry_data[col] = industry_data['IDX'].rolling(window=250, min_periods=250, center=False).apply(lambda x: quantile_definition(x, col, industry_data))
        # industry_data['INDUSTRY_TECHNIQUE'] = (industry_data[['TURNOVER_PROPORTION', 'TURNOVER_RATE', 'CORR', 'NEW_HIGH_RATIO', 'MEAN_ABOVE_RATIO', 'MAIN_CASH_PROPORTION', 'MARGIN_PROPORTION', 'CONSENSUS_UP_RATIO']].mean(axis=1) * (-1.0) + industry_data['INDUSTRY_MOMENTUM']) / 2.0
        industry_data['INDUSTRY_MOMENTUM'] = industry_data['INDUSTRY_MOMENTUM'] * (-1.0)
        industry_data['CONSENSUS_UP_RATIO'] = industry_data['CONSENSUS_UP_RATIO'] * (-1.0)
        industry_data['NEW_HIGH_RATIO'] = industry_data['NEW_HIGH_RATIO'] * (-1.0)
        industry_data['INDUSTRY_TECHNIQUE'] = industry_data[['TURNOVER_PROPORTION', 'TURNOVER_RATE', 'CORR', 'NEW_HIGH_RATIO', 'MEAN_ABOVE_RATIO', 'MAIN_CASH_PROPORTION', 'MARGIN_PROPORTION', 'CONSENSUS_UP_RATIO', 'INDUSTRY_MOMENTUM']].mean(axis=1) * (-1.0)
        industry_data['INDUSTRY_FUNDAMENTAL'] = industry_data[['OPER_REVENUE_YOY_DIFF', 'NET_PROFIT_YOY_DIFF', 'ROE_TTM_DIFF']].mean(axis=1)

        technique_data = industry_data[['TRADE_DATE', 'INDUSTRY_TECHNIQUE']]
        technique_data = technique_data.merge(industry_index, on=['TRADE_DATE'], how='left').dropna()
        technique_data_disp = technique_data[technique_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        technique_data_disp['TRADE_DATE_DISP'] = technique_data_disp['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))

        fundamental_data = industry_data[['TRADE_DATE', 'INDUSTRY_FUNDAMENTAL']]
        fundamental_data = fundamental_data.merge(industry_index, on=['TRADE_DATE'], how='left').dropna()
        fundamental_data_disp = fundamental_data[fundamental_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        fundamental_data_disp['TRADE_DATE_DISP'] = fundamental_data_disp['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        ax1.plot(technique_data_disp['TRADE_DATE_DISP'].values, technique_data_disp['INDUSTRY_TECHNIQUE'].values, color=line_color_list[0], label='{0}行业量价资金维度择时因子'.format(index_name))
        ax1.plot(fundamental_data_disp['TRADE_DATE_DISP'].values, fundamental_data_disp['INDUSTRY_FUNDAMENTAL'].values, color=line_color_list[1], label='{0}行业基本面维度择时因子'.format(index_name))
        ax2.plot(technique_data_disp['TRADE_DATE_DISP'].values, technique_data_disp['CLOSE_INDEX'].values, color=line_color_list[3], label='{0}行业指数走势（右轴）'.format(index_name))
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('{0}行业择时'.format(index_name), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}{1}_industry_timing.png'.format(self.data_path, index))

        technique_data['INDUSTRY_TECHNIQUE_UP1'] = technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).mean() + 0.5 * technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        technique_data['INDUSTRY_TECHNIQUE_DOWN1'] = technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        technique_data['INDUSTRY_TECHNIQUE_UP15'] = technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        technique_data['INDUSTRY_TECHNIQUE_DOWN15'] = technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        technique_data['INDUSTRY_TECHNIQUE_SCORE'] = technique_data.apply(lambda x: 5 if x['INDUSTRY_TECHNIQUE'] >= x['INDUSTRY_TECHNIQUE_UP15'] else
                                                                                    4 if x['INDUSTRY_TECHNIQUE'] >= x['INDUSTRY_TECHNIQUE_UP1'] else
                                                                                    1 if x['INDUSTRY_TECHNIQUE'] <= x['INDUSTRY_TECHNIQUE_DOWN15'] else
                                                                                    2 if x['INDUSTRY_TECHNIQUE'] <= x['INDUSTRY_TECHNIQUE_DOWN1'] else 3, axis=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_UP1'] = fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).mean() + 0.5 * fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_DOWN1'] = fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_UP15'] = fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_DOWN15'] = fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_SCORE'] = fundamental_data.apply(lambda x: 5 if x['INDUSTRY_FUNDAMENTAL'] >= x['INDUSTRY_FUNDAMENTAL_UP15'] else
                                                                                          4 if x['INDUSTRY_FUNDAMENTAL'] >= x['INDUSTRY_FUNDAMENTAL_UP1'] else
                                                                                          1 if x['INDUSTRY_FUNDAMENTAL'] <= x['INDUSTRY_FUNDAMENTAL_DOWN15'] else
                                                                                          2 if x['INDUSTRY_FUNDAMENTAL'] <= x['INDUSTRY_FUNDAMENTAL_DOWN1'] else 3, axis=1)
        industry_data = technique_data[['TRADE_DATE', 'INDUSTRY_TECHNIQUE_SCORE']].merge(fundamental_data[['TRADE_DATE', 'INDUSTRY_FUNDAMENTAL_SCORE']], on=['TRADE_DATE'], how='left')
        industry_data['INDUSTRY_TIMING_SCORE'] = industry_data['INDUSTRY_TECHNIQUE_SCORE'] * 0.5 + industry_data['INDUSTRY_FUNDAMENTAL_SCORE'] * 0.5
        # industry_data['INDUSTRY_TIMING_SCORE'] = industry_data['INDUSTRY_TIMING_SCORE'].apply(lambda x: round(x, 0))
        industry_data_monthly = industry_data[industry_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        industry_index = industry_index.merge(industry_data_monthly[['TRADE_DATE', 'INDUSTRY_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        industry_index['INDUSTRY_TIMING_SCORE'] = industry_index['INDUSTRY_TIMING_SCORE'].fillna(method='ffill')
        industry_index = industry_index.dropna(subset=['INDUSTRY_TIMING_SCORE'])
        industry_index['RET'] = industry_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        industry_index['RET_ADJ'] = industry_index.apply(lambda x: x['RET'] if x['INDUSTRY_TIMING_SCORE'] > 3.5 else 0.0, axis=1)
        industry_index['RET_ADJ'] = industry_index['RET_ADJ'].fillna(0.0)
        industry_index['NAV'] = (industry_index['RET_ADJ'] + 1).cumprod()
        industry_index['CLOSE_INDEX'] = industry_index['CLOSE_INDEX'] / industry_index['CLOSE_INDEX'].iloc[0]
        industry_index['TRADE_DATE_DISP'] = industry_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        industry_index_1 = industry_index[industry_index['INDUSTRY_TIMING_SCORE'] <= 1.5]
        industry_index_2 = industry_index[(industry_index['INDUSTRY_TIMING_SCORE'] > 1.5) & (industry_index['INDUSTRY_TIMING_SCORE'] <= 2.5)]
        industry_index_3 = industry_index[(industry_index['INDUSTRY_TIMING_SCORE'] > 2.5) & (industry_index['INDUSTRY_TIMING_SCORE'] <= 3.5)]
        industry_index_4 = industry_index[(industry_index['INDUSTRY_TIMING_SCORE'] > 3.5) & (industry_index['INDUSTRY_TIMING_SCORE'] <= 4.5)]
        industry_index_5 = industry_index[industry_index['INDUSTRY_TIMING_SCORE'] > 4.5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(industry_index['TRADE_DATE_DISP'].values, industry_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(industry_index['TRADE_DATE_DISP'].values, industry_index['CLOSE_INDEX'].values, color=line_color_list[3], label='{0}行业指数走势'.format(index_name))
        ax.scatter(industry_index_1['TRADE_DATE_DISP'].values, industry_index_1['CLOSE_INDEX'].values, color=line_color_list[1], label='得分1')
        ax.scatter(industry_index_2['TRADE_DATE_DISP'].values, industry_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(industry_index_3['TRADE_DATE_DISP'].values, industry_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(industry_index_4['TRADE_DATE_DISP'].values, industry_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(industry_index_5['TRADE_DATE_DISP'].values, industry_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('{0}行业择时'.format(index_name), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}{1}_timing.png'.format(self.data_path, index))
        return

class SizeTAA:
    def __init__(self, data_path, start_date, end_date, tracking_end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.tracking_end_date = tracking_end_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.tracking_end_date_hyphen = datetime.strptime(tracking_end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.tracking_end_date)

    def get_signal(self):
        size_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401', '881001'])
        size_index.to_hdf('{0}size_index.hdf'.format(self.data_path), key='table', mode='w')
        size_index = pd.read_hdf('{0}size_index.hdf'.format(self.data_path), key='table')
        size_index = size_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_index['TRADE_DATE'] = size_index['TRADE_DATE'].astype(str)
        size_index = size_index[size_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_index = size_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_index = size_index.rename(columns={'399314': '大盘', '399401': '中小盘', '881001': '万得全A'})
        size_index['大盘/中小盘'] = size_index['大盘'] / size_index['中小盘']
        size_index = size_index[(size_index.index > self.start_date) & (size_index.index <= self.end_date)]
        size_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1, frameon=False)
        plt.title('大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘中小盘历史相对走势.png'.format(self.data_path))

        # 期限利差
        bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期长端国债利率', '1年期短端国债利率']
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield = bond_yield[(bond_yield.index > self.start_date) & (bond_yield.index <= self.end_date)].dropna()
        bond_yield['期限利差'] = bond_yield['10年期长端国债利率'] - bond_yield['1年期短端国债利率']
        bond_yield['期限利差'] = bond_yield['期限利差'].rolling(20).mean()
        bond_yield['IDX'] = range(len(bond_yield))
        bond_yield['期限利差_Q'] = bond_yield['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '期限利差', bond_yield))
        bond_yield = bond_yield.drop('IDX', axis=1)
        bond_yield.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield.index)
        ##########################
        bond_yield_disp = size_index.merge(bond_yield, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_yield_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_yield_disp.index)
        bond_yield_disp = bond_yield_disp.loc[bond_yield_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        ##########################
        bond_yield_disp['大盘月度收益率'] = bond_yield_disp['大盘'].pct_change()  # .shift(-1)
        bond_yield_disp['中小盘月度收益率'] = bond_yield_disp['中小盘'].pct_change()  # .shift(-1)
        bond_yield_disp['大盘/中小盘月度收益率'] = bond_yield_disp['大盘/中小盘'].pct_change()  # .shift(-1)
        bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        len(bond_yield_disp.loc[(bond_yield_disp['期限利差_Q'] < 0.5) & (bond_yield_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5].dropna()))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['期限利差'].values, color=line_color_list[0], label='期限利差', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('期限利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 信用利差
        bond_spread = FEDB().read_ytm_zhongzhai()
        bond_spread['TRADE_DATE'] = bond_spread['TRADE_DATE'].astype(str)
        bond_spread = bond_spread.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_spread = bond_spread[bond_spread.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_spread = bond_spread[(bond_spread.index > self.start_date) & (bond_spread.index <= self.end_date)].dropna()
        bond_spread['信用利差'] = bond_spread['中债企业债到期收益率(AA+):5年'] - bond_spread['中债国开债到期收益率:5年']
        bond_spread['信用利差'] = bond_spread['信用利差'].rolling(20).mean()
        bond_spread['IDX'] = range(len(bond_spread))
        bond_spread['信用利差_Q'] = bond_spread['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '信用利差', bond_spread))
        bond_spread = bond_spread.drop('IDX', axis=1)
        bond_spread.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread.index)
        ##########################
        bond_spread_disp = size_index.merge(bond_spread, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_spread_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_spread_disp.index)
        bond_spread_disp = bond_spread_disp.loc[bond_spread_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_spread_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread_disp.index)
        ##########################
        bond_spread_disp['大盘月度收益率'] = bond_spread_disp['大盘'].pct_change()  # .shift(-1)
        bond_spread_disp['中小盘月度收益率'] = bond_spread_disp['中小盘'].pct_change()  # .shift(-1)
        bond_spread_disp['大盘/中小盘月度收益率'] = bond_spread_disp['大盘/中小盘'].pct_change()  # .shift(-1)
        bond_spread_disp.loc[bond_spread_disp['信用利差_Q'] > 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        len(bond_spread_disp.loc[(bond_spread_disp['信用利差_Q'] > 0.5) & (bond_spread_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(bond_spread_disp.loc[bond_spread_disp['信用利差_Q'] > 0.5].dropna()))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_spread_disp.index, bond_spread_disp['信用利差'].values, color=line_color_list[0], label='信用利差', linewidth=3)
        ax_r.plot(bond_spread_disp.index, bond_spread_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('信用利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}信用利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 风格关注度
        size_turnover = w.wsd("399314.sz,399401.sz", "dq_amtturnover", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        size_turnover.to_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table', mode='w')
        size_turnover = pd.read_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table')
        size_turnover.columns = ['TRADE_DATE', '大盘换手率', '中小盘换手率']
        size_turnover['TRADE_DATE'] = size_turnover['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        size_turnover = size_turnover.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_turnover = size_turnover[size_turnover.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_turnover = size_turnover[(size_turnover.index > self.start_date) & (size_turnover.index <= self.end_date)]
        size_turnover['相对换手率'] = size_turnover['大盘换手率'] / size_turnover['中小盘换手率']
        size_turnover['风格关注度'] = size_turnover['相对换手率'].rolling(60).mean()
        size_turnover['IDX'] = range(len(size_turnover))
        size_turnover['风格关注度_Q'] = size_turnover['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '风格关注度', size_turnover))
        size_turnover = size_turnover.drop('IDX', axis=1)
        size_turnover.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover.index)
        ##########################
        size_turnover_disp = size_index.merge(size_turnover, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp = size_turnover_disp.loc[size_turnover_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp['低分位水平线'] = 0.2
        size_turnover_disp['中分位水平线'] = 0.5
        size_turnover_disp['高分位水平线'] = 0.8
        ##########################
        size_turnover_disp['大盘月度收益率'] = size_turnover_disp['大盘'].pct_change().shift(-1)
        size_turnover_disp['中小盘月度收益率'] = size_turnover_disp['中小盘'].pct_change().shift(-1)
        size_turnover_disp['大盘/中小盘月度收益率'] = size_turnover_disp['大盘/中小盘'].pct_change().shift(-1)
        # size_turnover_disp = size_turnover_disp.dropna()
        size_turnover_disp['分组'] = size_turnover_disp['风格关注度_Q'].apply(lambda x: '0%-50%' if x >= 0.0 and x < 0.5 else '50%-100%')
        size_turnover_disp_stat = size_turnover_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_turnover_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度'].values, color=line_color_list[0], label='关注程度', linewidth=3)
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('关注程度与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}关注程度与大盘中小盘历史相对走势.png'.format(self.data_path))
        ##########################
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp_yes = size_turnover_disp.copy(deep=True)
        size_turnover_disp_no = size_turnover_disp.copy(deep=True)
        size_turnover_disp_yes['分组_SCORE'] = size_turnover_disp_yes['分组'].apply(lambda x: 1.0 if x == '0%-50%' else 0)
        size_turnover_disp_no['分组_SCORE'] = size_turnover_disp_no['分组'].apply(lambda x: 1.0 if x == '50%-100%' else 0)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度_Q'].values, color=line_color_list[0], label='关注程度近一年历史分位', linewidth=3)
        ax.plot(size_turnover_disp.index, size_turnover_disp['中分位水平线'].values, color=line_color_list[3], label='中位水平', linewidth=2, linestyle='--')
        ax.bar(np.arange(len(size_turnover_disp_yes)), size_turnover_disp_yes['分组_SCORE'].values, label='低于中位水平', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(size_turnover_disp_no)), size_turnover_disp_no['分组_SCORE'].values, label='高于中位水平', color=line_color_list[2], alpha=0.3)
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        ax.set_xticks(np.arange(len(size_turnover_disp))[::6])
        ax.set_xticklabels(labels=size_turnover_disp.index.tolist()[::6], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False)
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=5, frameon=False)
        plt.title('关注程度近一年历史分位与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}关注程度近一年历史分位与大盘中小盘历史相对走势.png'.format(self.data_path))
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_turnover_disp_stat)) - 0.5 * bar_width, size_turnover_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_turnover_disp_stat)) + 0.5 * bar_width, size_turnover_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        ax.set_xticks(np.arange(len(size_turnover_disp_stat)))
        ax.set_xticklabels(labels=size_turnover_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}关注程度测试.png'.format(self.data_path))

        # 动量效应
        size_momentum = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        size_momentum = size_momentum.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_momentum['TRADE_DATE'] = size_momentum['TRADE_DATE'].astype(str)
        size_momentum = size_momentum[size_momentum['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_momentum = size_momentum[(size_momentum['TRADE_DATE'] > self.start_date) & (size_momentum['TRADE_DATE'] <= self.end_date)]
        size_momentum = size_momentum.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_momentum = size_momentum.rename(columns={'399314': '大盘', '399401': '中小盘'})
        size_momentum['大盘/中小盘'] = size_momentum['大盘'] / size_momentum['中小盘']
        size_momentum['大盘/中小盘_MA20'] = size_momentum['大盘/中小盘'].rolling(20).mean()
        size_momentum = size_momentum.dropna()
        size_momentum.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum.index)
        size_momentum_disp = size_momentum.copy(deep=True)
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp = size_momentum_disp.loc[size_momentum_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        ##########################
        size_momentum_disp['大盘月度收益率'] = size_momentum_disp['大盘'].pct_change().shift(-1)
        size_momentum_disp['中小盘月度收益率'] = size_momentum_disp['中小盘'].pct_change().shift(-1)
        size_momentum_disp['大盘/中小盘月度收益率'] = size_momentum_disp['大盘/中小盘'].pct_change().shift(-1)
        # size_momentum_disp = size_momentum_disp.dropna()
        size_momentum_disp['分组'] = size_momentum_disp.apply(lambda x: '突破' if x['大盘/中小盘'] > x['大盘/中小盘_MA20'] else '未突破', axis=1)
        size_momentum_disp_stat = size_momentum_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_momentum_disp_stat = size_momentum_disp_stat.loc[['突破', '未突破']]
        size_momentum_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp_yes = size_momentum_disp.copy(deep=True)
        size_momentum_disp_no = size_momentum_disp.copy(deep=True)
        size_momentum_disp_yes['分组_SCORE'] = size_momentum_disp_yes['分组'].apply(lambda x: 1.5 if x == '突破' else 0)
        size_momentum_disp_no['分组_SCORE'] = size_momentum_disp_no['分组'].apply(lambda x: 1.5 if x == '未突破' else 0)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(np.arange(len(size_momentum_disp)), size_momentum_disp['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘', linewidth=3)
        ax.plot(np.arange(len(size_momentum_disp)), size_momentum_disp['大盘/中小盘_MA20'].values, color=line_color_list[2], label='大盘/中小盘近一月移动平均', linewidth=3)
        ax.bar(np.arange(len(size_momentum_disp_yes)), size_momentum_disp_yes['分组_SCORE'].values, label='突破', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(size_momentum_disp_no)), size_momentum_disp_no['分组_SCORE'].values, label='未突破', color=line_color_list[2], alpha=0.3)
        ax.set_xticks(np.arange(len(size_momentum_disp))[::6])
        ax.set_xticklabels(labels=size_momentum_disp.index.tolist()[::6], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False)
        plt.title('动量突破与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}动量突破与大盘中小盘历史相对走势.png'.format(self.data_path))
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_momentum_disp_stat)) - 0.5 * bar_width, size_momentum_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_momentum_disp_stat)) + 0.5 * bar_width, size_momentum_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        ax.set_xticks(np.arange(len(size_momentum_disp_stat)))
        ax.set_xticklabels(labels=size_momentum_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}动量突破测试.png'.format(self.data_path))

        # 因子动量离散拥挤度
        size_factor = FEDB().read_timing_data(['TRADE_DATE', 'SIZE_MOMENTUM', 'SIZE_SPREAD', 'SIZE_CROWDING'], 'timing_style', '20071231', self.end_date)
        size_factor.columns = ['TRADE_DATE', 'LARGE_MOMENTUM', 'LARGE_SPREAD', 'LARGE_CROWDING']
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_SPREAD'] = size_factor['LARGE_SPREAD'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_CROWDING'] = size_factor['LARGE_CROWDING'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['因子动量离散拥挤度'] = (size_factor['LARGE_MOMENTUM'] + size_factor['LARGE_SPREAD'] + size_factor['LARGE_CROWDING'] * (-1.0)) / 3.0
        size_factor['TRADE_DATE'] = size_factor['TRADE_DATE'].astype(str)
        size_factor = size_factor.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_factor['IDX'] = range(len(size_factor))
        size_factor['因子动量离散拥挤度_Q'] = size_factor['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '因子动量离散拥挤度', size_factor))
        size_factor = size_factor.drop('IDX', axis=1)
        size_factor = size_factor[size_factor.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_factor = size_factor[(size_factor.index > self.start_date) & (size_factor.index <= self.end_date)]
        size_factor.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor.index)
        size_factor_disp = size_index.merge(size_factor, left_index=True, right_index=True, how='left').sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_factor_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_factor_disp.index)
        size_factor_disp = size_factor_disp.loc[size_factor_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_factor_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor_disp.index)
        ##########################
        size_factor_disp['大盘月度收益率'] = size_factor_disp['大盘'].pct_change().shift(-1)
        size_factor_disp['中小盘月度收益率'] = size_factor_disp['中小盘'].pct_change().shift(-1)
        size_factor_disp['大盘/中小盘月度收益率'] = size_factor_disp['大盘/中小盘'].pct_change().shift(-1)
        size_factor_disp = size_factor_disp.iloc[8:]
        size_factor_disp['分组'] = size_factor_disp['因子动量离散拥挤度_Q'].apply(lambda x: '0%-50%' if x >= 0.0 and x <= 0.5 else '50%-100%')
        size_factor_disp_stat = size_factor_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_factor_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_factor_disp.index, size_factor_disp['因子动量离散拥挤度'].values, color=line_color_list[0], label='因子特征', linewidth=3)
        ax_r.plot(size_factor_disp.index, size_factor_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('因子特征与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子特征与大盘中小盘历史相对走势.png'.format(self.data_path))
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_factor_disp_stat)) - 0.5 * bar_width, size_factor_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_factor_disp_stat)) + 0.5 * bar_width, size_factor_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        ax.set_xticks(np.arange(len(size_factor_disp_stat)))
        ax.set_xticklabels(labels=size_factor_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}因子特征测试.png'.format(self.data_path))

        bond_yield_disp['期限利差_SCORE'] = bond_yield_disp['期限利差_Q'].apply(lambda x: 1 if x < 0.5 else 0)
        bond_spread_disp['信用利差_SCORE'] = bond_spread_disp['信用利差_Q'].apply(lambda x: 1 if x > 0.5 else 0)
        size_turnover_disp['风格关注度_SCORE'] = size_turnover_disp['分组'].apply(lambda x: 1 if x == '0%-50%' else 0)
        size_momentum_disp['动量突破_SCORE'] = size_momentum_disp['分组'].apply(lambda x: 1 if x == '突破' else 0)
        size_factor_disp['因子特征_SCORE'] = size_factor_disp['分组'].apply(lambda x: 1 if x == '50%-100%' else 0)
        size_timing = bond_yield_disp[['期限利差_SCORE']].merge(bond_spread_disp[['信用利差_SCORE']], left_index=True, right_index=True, how='inner') \
                                                        .merge(size_turnover_disp[['风格关注度_SCORE']], left_index=True, right_index=True, how='inner') \
                                                        .merge(size_momentum_disp[['动量突破_SCORE']], left_index=True, right_index=True, how='inner') \
                                                        .merge(size_factor_disp[['因子特征_SCORE']], left_index=True, right_index=True, how='inner')
        size_timing['大盘_SCORE'] = size_timing.sum(axis=1)
        size_timing['中小盘_SCORE'] = 5 - size_timing['大盘_SCORE']
        size_timing['大盘_WEIGHT'] = size_timing['大盘_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        size_timing['中小盘_WEIGHT'] = size_timing['中小盘_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(size_timing[['大盘_WEIGHT', '中小盘_WEIGHT']], left_index=True, right_index=True, how='left')
        index['大盘_WEIGHT'] = index['大盘_WEIGHT'].fillna(method='ffill')
        index['中小盘_WEIGHT'] = index['中小盘_WEIGHT'].fillna(method='ffill')
        index = index.dropna(subset=['大盘_WEIGHT'])
        index = index.dropna(subset=['中小盘_WEIGHT'])
        index['RET_ADJ'] = index['大盘_WEIGHT'] * index['399314_RET'] + index['中小盘_WEIGHT'] * index['399401_RET']
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index['RET_AVERAGE'] = 0.5 * index['399314_RET'] + 0.5 * index['399401_RET']
        index['RET_AVERAGE'] = index['RET_AVERAGE'].fillna(0.0)
        index['RET_AVERAGE'].iloc[0] = 0.0
        index['NAV_AVERAGE'] = (index['RET_AVERAGE'] + 1).cumprod()
        index = index.dropna()
        index[['NAV_AVERAGE', 'NAV']] = index[['NAV_AVERAGE', 'NAV']] / index[['NAV_AVERAGE', 'NAV']].iloc[0]
        index = index.reset_index()
        index['TRADE_DATE_DISP'] = index['TRADE_DATE']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='大盘/中小盘择时', linewidth=3)
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV_AVERAGE'].values, color=line_color_list[2], label='大盘/中小盘等权', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5, frameon=False)
        plt.title('大盘/中小盘仓位打分调仓组合回测图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时策略.png'.format(self.data_path))

        size_index = size_index.merge(size_timing[['大盘_SCORE']], left_index=True, right_index=True, how='left')
        size_index['大盘_SCORE'] = size_index['大盘_SCORE'].fillna(method='ffill')
        size_index = size_index.dropna(subset=['大盘_SCORE'])
        size_index_1 = size_index[size_index['大盘_SCORE'] == 1]
        size_index_2 = size_index[size_index['大盘_SCORE'] == 2]
        size_index_3 = size_index[size_index['大盘_SCORE'] == 3]
        size_index_4 = size_index[size_index['大盘_SCORE'] == 4]
        size_index_5 = size_index[size_index['大盘_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[3], label='大盘/中小盘')
        ax.scatter(size_index_1.index, size_index_1['大盘/中小盘'].values, color=line_color_list[1], label='大盘评分1')
        ax.scatter(size_index_2.index, size_index_2['大盘/中小盘'].values, color=line_color_list[9], label='大盘评分2')
        ax.scatter(size_index_3.index, size_index_3['大盘/中小盘'].values, color=line_color_list[3], label='大盘评分3')
        ax.scatter(size_index_4.index, size_index_4['大盘/中小盘'].values, color=line_color_list[4], label='大盘评分4')
        ax.scatter(size_index_5.index, size_index_5['大盘/中小盘'].values, color=line_color_list[0], label='大盘评分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6, frameon=False)
        plt.title('大盘评分及大盘/中小盘走势图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时.png'.format(self.data_path))
        return

    def get_result(self):
        size_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401', '881001'])
        size_index.to_hdf('{0}size_index.hdf'.format(self.data_path), key='table', mode='w')
        size_index = pd.read_hdf('{0}size_index.hdf'.format(self.data_path), key='table')
        size_index = size_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_index['TRADE_DATE'] = size_index['TRADE_DATE'].astype(str)
        size_index = size_index[size_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_index = size_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_index = size_index.rename(columns={'399314': '大盘', '399401': '中小盘', '881001': '万得全A'})
        size_index['大盘/中小盘'] = size_index['大盘'] / size_index['中小盘']
        size_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_index.index)
        size_index_disp = size_index[(size_index.index >= datetime.strptime(self.end_date, '%Y%m%d')) & (size_index.index <= datetime.strptime(self.tracking_end_date, '%Y%m%d'))]
        size_index_disp = size_index_disp / size_index_disp.iloc[0]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index_disp.index, size_index_disp['大盘'].values, color=line_color_list[0], label='大盘', linewidth=3)
        ax.plot(size_index_disp.index, size_index_disp['中小盘'].values, color=line_color_list[1], label='中小盘', linewidth=3)
        ax.plot(size_index_disp.index, size_index_disp['万得全A'].values, color=line_color_list[2], label='万得全A', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('大盘/中小盘/万得全A走势', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘中小盘万得全A走势.png'.format(self.data_path))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index_disp.index, size_index_disp['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1, frameon=False)
        plt.title('大盘/中小盘相对走势', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘中小盘相对走势.png'.format(self.data_path))

        start = datetime.strptime('20200101', '%Y%m%d')
        end = datetime.strptime(self.tracking_end_date, '%Y%m%d')

        # 期限利差
        bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.tracking_end_date_hyphen, usedf=True)[1].reset_index()
        bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期长端国债利率', '1年期短端国债利率']
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield['期限利差'] = bond_yield['10年期长端国债利率'] - bond_yield['1年期短端国债利率']
        bond_yield['期限利差'] = bond_yield['期限利差'].rolling(20).mean()
        bond_yield['IDX'] = range(len(bond_yield))
        bond_yield['期限利差_Q'] = bond_yield['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '期限利差', bond_yield))
        bond_yield = bond_yield.drop('IDX', axis=1)
        bond_yield.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield.index)
        ##########################
        bond_yield_disp = size_index.merge(bond_yield, left_index=True, right_index=True, how='left').dropna().sort_index()
        bond_yield_disp = bond_yield_disp[(bond_yield_disp.index >= start) & (bond_yield_disp.index <= end)].dropna()
        month_df = self.trade_df[self.trade_df['IS_WEEK_END'] == '1']
        bond_yield_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_yield_disp.index)
        bond_yield_disp = bond_yield_disp.loc[bond_yield_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        ##########################
        bond_yield_disp['大盘月度收益率'] = bond_yield_disp['大盘'].pct_change()  # .shift(-1)
        bond_yield_disp['中小盘月度收益率'] = bond_yield_disp['中小盘'].pct_change()  # .shift(-1)
        bond_yield_disp['大盘/中小盘月度收益率'] = bond_yield_disp['大盘/中小盘'].pct_change()  # .shift(-1)
        bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        len(bond_yield_disp.loc[(bond_yield_disp['期限利差_Q'] < 0.5) & (bond_yield_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5].dropna()))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['期限利差'].values, color=line_color_list[0], label='期限利差', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('期限利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 信用利差
        bond_spread = FEDB().read_ytm_zhongzhai()
        bond_spread['TRADE_DATE'] = bond_spread['TRADE_DATE'].astype(str)
        bond_spread = bond_spread.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_spread = bond_spread[bond_spread.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_spread['信用利差'] = bond_spread['中债企业债到期收益率(AA+):5年'] - bond_spread['中债国开债到期收益率:5年']
        bond_spread['信用利差'] = bond_spread['信用利差'].rolling(20).mean()
        bond_spread['IDX'] = range(len(bond_spread))
        bond_spread['信用利差_Q'] = bond_spread['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '信用利差', bond_spread))
        bond_spread = bond_spread.drop('IDX', axis=1)
        bond_spread.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread.index)
        ##########################
        bond_spread_disp = size_index.merge(bond_spread, left_index=True, right_index=True, how='left').dropna().sort_index()
        bond_spread_disp = bond_spread_disp[(bond_spread_disp.index >= start) & (bond_spread_disp.index <= end)].dropna()
        month_df = self.trade_df[self.trade_df['IS_WEEK_END'] == '1']
        bond_spread_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_spread_disp.index)
        bond_spread_disp = bond_spread_disp.loc[bond_spread_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_spread_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread_disp.index)
        ##########################
        bond_spread_disp['大盘月度收益率'] = bond_spread_disp['大盘'].pct_change()  # .shift(-1)
        bond_spread_disp['中小盘月度收益率'] = bond_spread_disp['中小盘'].pct_change()  # .shift(-1)
        bond_spread_disp['大盘/中小盘月度收益率'] = bond_spread_disp['大盘/中小盘'].pct_change()  # .shift(-1)
        bond_spread_disp.loc[bond_spread_disp['信用利差_Q'] > 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        len(bond_spread_disp.loc[(bond_spread_disp['信用利差_Q'] > 0.5) & (bond_spread_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(bond_spread_disp.loc[bond_spread_disp['信用利差_Q'] > 0.5].dropna()))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_spread_disp.index, bond_spread_disp['信用利差'].values, color=line_color_list[0], label='信用利差', linewidth=3)
        ax_r.plot(bond_spread_disp.index, bond_spread_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('信用利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}信用利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 风格关注度
        size_turnover = w.wsd("399314.sz,399401.sz", "dq_amtturnover", self.start_date_hyphen, self.tracking_end_date_hyphen, usedf=True)[1].reset_index()
        size_turnover.to_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table', mode='w')
        size_turnover = pd.read_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table')
        size_turnover.columns = ['TRADE_DATE', '大盘换手率', '中小盘换手率']
        size_turnover['TRADE_DATE'] = size_turnover['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        size_turnover = size_turnover.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_turnover = size_turnover[size_turnover.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_turnover['相对换手率'] = size_turnover['大盘换手率'] / size_turnover['中小盘换手率']
        size_turnover['风格关注度'] = size_turnover['相对换手率'].rolling(60).mean()
        size_turnover['IDX'] = range(len(size_turnover))
        size_turnover['风格关注度_Q'] = size_turnover['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '风格关注度', size_turnover))
        size_turnover = size_turnover.drop('IDX', axis=1)
        size_turnover.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover.index)
        ##########################
        size_turnover_disp = size_index.merge(size_turnover, left_index=True, right_index=True, how='left').dropna().sort_index()
        size_turnover_disp = size_turnover_disp[(size_turnover_disp.index >= start) & (size_turnover_disp.index <= end)]
        month_df = self.trade_df[self.trade_df['IS_WEEK_END'] == '1']
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp = size_turnover_disp.loc[size_turnover_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp['低分位水平线'] = 0.2
        size_turnover_disp['中分位水平线'] = 0.5
        size_turnover_disp['高分位水平线'] = 0.8
        ##########################
        size_turnover_disp['大盘月度收益率'] = size_turnover_disp['大盘'].pct_change().shift(-1)
        size_turnover_disp['中小盘月度收益率'] = size_turnover_disp['中小盘'].pct_change().shift(-1)
        size_turnover_disp['大盘/中小盘月度收益率'] = size_turnover_disp['大盘/中小盘'].pct_change().shift(-1)
        # size_turnover_disp = size_turnover_disp.dropna()
        size_turnover_disp['分组'] = size_turnover_disp['风格关注度_Q'].apply(lambda x: '0%-50%' if x >= 0.0 and x < 0.5 else '50%-100%')
        size_turnover_disp_stat = size_turnover_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_turnover_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度'].values, color=line_color_list[0], label='关注程度', linewidth=3)
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('关注程度与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}关注程度与大盘中小盘历史相对走势.png'.format(self.data_path))
        ##########################
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp_yes = size_turnover_disp.copy(deep=True)
        size_turnover_disp_no = size_turnover_disp.copy(deep=True)
        size_turnover_disp_yes['分组_SCORE'] = size_turnover_disp_yes['分组'].apply(lambda x: 1.0 if x == '0%-50%' else 0)
        size_turnover_disp_no['分组_SCORE'] = size_turnover_disp_no['分组'].apply(lambda x: 1.0 if x == '50%-100%' else 0)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度_Q'].values, color=line_color_list[0], label='关注程度近一年历史分位', linewidth=3)
        ax.plot(size_turnover_disp.index, size_turnover_disp['中分位水平线'].values, color=line_color_list[3], label='中位水平', linewidth=2, linestyle='--')
        ax.bar(np.arange(len(size_turnover_disp_yes)), size_turnover_disp_yes['分组_SCORE'].values, label='低于中位水平', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(size_turnover_disp_no)), size_turnover_disp_no['分组_SCORE'].values, label='高于中位水平', color=line_color_list[2], alpha=0.3)
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        ax.set_xticks(np.arange(len(size_turnover_disp))[::6])
        ax.set_xticklabels(labels=size_turnover_disp.index.tolist()[::6], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4)
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=5, frameon=False)
        plt.title('关注程度近一年历史分位与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}关注程度近一年历史分位与大盘中小盘历史相对走势.png'.format(self.data_path))
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_turnover_disp_stat)) - 0.5 * bar_width, size_turnover_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_turnover_disp_stat)) + 0.5 * bar_width, size_turnover_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        ax.set_xticks(np.arange(len(size_turnover_disp_stat)))
        ax.set_xticklabels(labels=size_turnover_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}关注程度测试.png'.format(self.data_path))

        # 动量效应
        size_momentum = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        size_momentum = size_momentum.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_momentum['TRADE_DATE'] = size_momentum['TRADE_DATE'].astype(str)
        size_momentum = size_momentum[size_momentum['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_momentum = size_momentum.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_momentum = size_momentum.rename(columns={'399314': '大盘', '399401': '中小盘'})
        size_momentum['大盘/中小盘'] = size_momentum['大盘'] / size_momentum['中小盘']
        size_momentum['大盘/中小盘_MA20'] = size_momentum['大盘/中小盘'].rolling(20).mean()
        size_momentum = size_momentum.dropna()
        size_momentum.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum.index)
        size_momentum_disp = size_momentum.copy(deep=True)
        size_momentum_disp = size_momentum_disp[(size_momentum_disp.index >= start) & (size_momentum_disp.index <= end)]
        month_df = self.trade_df[self.trade_df['IS_WEEK_END'] == '1']
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp = size_momentum_disp.loc[size_momentum_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        ##########################
        size_momentum_disp['大盘月度收益率'] = size_momentum_disp['大盘'].pct_change().shift(-1)
        size_momentum_disp['中小盘月度收益率'] = size_momentum_disp['中小盘'].pct_change().shift(-1)
        size_momentum_disp['大盘/中小盘月度收益率'] = size_momentum_disp['大盘/中小盘'].pct_change().shift(-1)
        # size_momentum_disp = size_momentum_disp.dropna()
        size_momentum_disp['分组'] = size_momentum_disp.apply(lambda x: '突破' if x['大盘/中小盘'] > x['大盘/中小盘_MA20'] else '未突破', axis=1)
        size_momentum_disp_stat = size_momentum_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_momentum_disp_stat = size_momentum_disp_stat.loc[['突破', '未突破']]
        size_momentum_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp_yes = size_momentum_disp.copy(deep=True)
        size_momentum_disp_no = size_momentum_disp.copy(deep=True)
        size_momentum_disp_yes['分组_SCORE'] = size_momentum_disp_yes['分组'].apply(lambda x: 1.5 if x == '突破' else 0)
        size_momentum_disp_no['分组_SCORE'] = size_momentum_disp_no['分组'].apply(lambda x: 1.5 if x == '未突破' else 0)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(np.arange(len(size_momentum_disp)), size_momentum_disp['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘', linewidth=3)
        ax.plot(np.arange(len(size_momentum_disp)), size_momentum_disp['大盘/中小盘_MA20'].values, color=line_color_list[2], label='大盘/中小盘近一月移动平均', linewidth=3)
        ax.bar(np.arange(len(size_momentum_disp_yes)), size_momentum_disp_yes['分组_SCORE'].values, label='突破', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(size_momentum_disp_no)), size_momentum_disp_no['分组_SCORE'].values, label='未突破', color=line_color_list[2], alpha=0.3)
        ax.set_xticks(np.arange(len(size_momentum_disp))[::6])
        ax.set_xticklabels(labels=size_momentum_disp.index.tolist()[::6], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False)
        plt.title('动量突破与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}动量突破与大盘中小盘历史相对走势.png'.format(self.data_path))
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_momentum_disp_stat)) - 0.5 * bar_width, size_momentum_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_momentum_disp_stat)) + 0.5 * bar_width, size_momentum_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        ax.set_xticks(np.arange(len(size_momentum_disp_stat)))
        ax.set_xticklabels(labels=size_momentum_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}动量突破测试.png'.format(self.data_path))

        # 因子动量离散拥挤度
        size_factor = FEDB().read_timing_data(['TRADE_DATE', 'SIZE_MOMENTUM', 'SIZE_SPREAD', 'SIZE_CROWDING'], 'timing_style', self.start_date, self.tracking_end_date)
        size_factor.columns = ['TRADE_DATE', 'LARGE_MOMENTUM', 'LARGE_SPREAD', 'LARGE_CROWDING']
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_SPREAD'] = size_factor['LARGE_SPREAD'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_CROWDING'] = size_factor['LARGE_CROWDING'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['因子动量离散拥挤度'] = (size_factor['LARGE_MOMENTUM'] + size_factor['LARGE_SPREAD'] + size_factor['LARGE_CROWDING'] * (-1.0)) / 3.0
        size_factor['TRADE_DATE'] = size_factor['TRADE_DATE'].astype(str)
        size_factor = size_factor.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_factor['IDX'] = range(len(size_factor))
        size_factor['因子动量离散拥挤度_Q'] = size_factor['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '因子动量离散拥挤度', size_factor))
        size_factor = size_factor.drop('IDX', axis=1)
        size_factor = size_factor[size_factor.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_factor.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor.index)
        size_factor_disp = size_index.merge(size_factor, left_index=True, right_index=True, how='left').sort_index()
        size_factor_disp = size_factor_disp[(size_factor_disp.index >= start) & (size_factor_disp.index <= end)]
        month_df = self.trade_df[self.trade_df['IS_WEEK_END'] == '1']
        size_factor_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_factor_disp.index)
        size_factor_disp = size_factor_disp.loc[size_factor_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_factor_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor_disp.index)
        ##########################
        size_factor_disp['大盘月度收益率'] = size_factor_disp['大盘'].pct_change().shift(-1)
        size_factor_disp['中小盘月度收益率'] = size_factor_disp['中小盘'].pct_change().shift(-1)
        size_factor_disp['大盘/中小盘月度收益率'] = size_factor_disp['大盘/中小盘'].pct_change().shift(-1)
        size_factor_disp = size_factor_disp.iloc[8:]
        size_factor_disp['分组'] = size_factor_disp['因子动量离散拥挤度_Q'].apply(lambda x: '0%-50%' if x >= 0.0 and x <= 0.5 else '50%-100%')
        size_factor_disp_stat = size_factor_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_factor_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_factor_disp.index, size_factor_disp['因子动量离散拥挤度'].values, color=line_color_list[0], label='因子特征', linewidth=3)
        ax_r.plot(size_factor_disp.index, size_factor_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('因子特征与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子特征与大盘中小盘历史相对走势.png'.format(self.data_path))
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_factor_disp_stat)) - 0.5 * bar_width, size_factor_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_factor_disp_stat)) + 0.5 * bar_width, size_factor_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        ax.set_xticks(np.arange(len(size_factor_disp_stat)))
        ax.set_xticklabels(labels=size_factor_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}因子特征测试.png'.format(self.data_path))
        return

class StyleTAA:
    def __init__(self, data_path, start_date, end_date, tracking_end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.tracking_end_date = tracking_end_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.tracking_end_date_hyphen = datetime.strptime(tracking_end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.tracking_end_date)

    def get_signal(self):
        style_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370', '399371'])
        style_index.to_hdf('{0}style_index.hdf'.format(self.data_path), key='table', mode='w')
        style_index = pd.read_hdf('{0}style_index.hdf'.format(self.data_path), key='table')
        style_index = style_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].astype(str)
        style_index = style_index[style_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style_index = style_index[(style_index['TRADE_DATE'] > self.start_date) & (style_index['TRADE_DATE'] <= self.end_date)]
        style_index = style_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        style_index = style_index.rename(columns={'399370': '成长', '399371': '价值'})
        style_index['成长/价值'] = style_index['成长'] / style_index['价值']
        style_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[0], label='成长/价值', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1, frameon=False)
        plt.title('成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值历史相对走势.png'.format(self.data_path))

        n1 = 250
        n2 = 250
        thresh1 = 0.5
        thresh15 = 1.0
        style_data = FEDB().read_timing_data(['TRADE_DATE', 'GROWTH_CROWDING', 'VALUE_CROWDING', 'GROWTH_SPREAD', 'VALUE_SPREAD', 'GROWTH_MOMENTUM', 'VALUE_MOMENTUM'], 'timing_style', self.start_date, self.end_date)
        style_data['TRADE_DATE'] = style_data['TRADE_DATE'].astype(str)
        style_data = style_data[(style_data['TRADE_DATE'] > self.start_date) & (style_data['TRADE_DATE'] <= self.end_date)]
        style_data = style_data.dropna()
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(240).apply(lambda x: x.iloc[19::20].mean() / x.iloc[19::20].std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['IDX'] = range(len(growth_data))
        growth_data['GROWTH_SPREAD'] = growth_data['IDX'].rolling(n1).apply(lambda x: quantile_definition(x, 'GROWTH_SPREAD', growth_data))
        growth_data = growth_data.drop('IDX', axis=1)
        growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(240).apply(lambda x: x.iloc[19::20].mean() / x.iloc[19::20].std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['IDX'] = range(len(value_data))
        value_data['VALUE_SPREAD'] = value_data['IDX'].rolling(n1).apply(lambda x: quantile_definition(x, 'VALUE_SPREAD', value_data))
        value_data = value_data.drop('IDX', axis=1)
        value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        growth_value_data = growth_data.merge(value_data, on=['TRADE_DATE'], how='left').dropna()
        growth_value_data = growth_value_data.set_index('TRADE_DATE').sort_index()
        growth_value_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data.index)
        growth_value_data_disp = growth_value_data.merge(style_index, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data_disp.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data_disp.index)
        growth_value_data_disp = growth_value_data_disp.loc[growth_value_data_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_disp.index)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_MOMENTUM'].values, color=line_color_list[0], label='成长因子动量', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_MOMENTUM'].values, color=line_color_list[1], label='价值因子动量', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('因子动量与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子动量与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_SPREAD'].values, color=line_color_list[0], label='成长因子离散度', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_SPREAD'].values, color=line_color_list[1], label='价值因子离散度', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('因子离散度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子离散度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_CROWDING'].values, color=line_color_list[0], label='成长因子拥挤度', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_CROWDING'].values, color=line_color_list[1], label='价值因子拥挤度', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('因子拥挤度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子拥挤度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_TIMING'].values, color=line_color_list[0], label='成长因子复合指标', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_TIMING'].values, color=line_color_list[1], label='价值因子复合指标', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('因子复合指标与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子复合指标与成长价值历史相对走势.png'.format(self.data_path))

        growth_value_data = growth_value_data[['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']]
        for factor_name in ['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']:
            growth_value_data[factor_name + '_UP1'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() + thresh1 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_DOWN1'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() - thresh1 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_UP15'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() + thresh15 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_DOWN15'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2,  center=False).mean() - thresh15 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_SCORE'] = growth_value_data.apply(
                lambda x: 5 if x[factor_name] >= x[factor_name + '_UP15'] else
                4 if x[factor_name] >= x[factor_name + '_UP1'] else
                1 if x[factor_name] <= x[factor_name + '_DOWN15'] else
                2 if x[factor_name] <= x[factor_name + '_DOWN1'] else 3, axis=1)
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data.index)
        growth_value_data_monthly = growth_value_data.loc[growth_value_data.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_monthly.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_monthly.index)
        growth_value_data_monthly = growth_value_data_monthly[['GROWTH_MOMENTUM_SCORE', 'GROWTH_SPREAD_SCORE', 'GROWTH_CROWDING_SCORE', 'GROWTH_TIMING_SCORE', 'VALUE_MOMENTUM_SCORE', 'VALUE_SPREAD_SCORE', 'VALUE_CROWDING_SCORE', 'VALUE_TIMING_SCORE']]
        growth_value_data_monthly = growth_value_data_monthly.merge(style_index, left_index=True, right_index=True, how='left')
        growth_value_data_monthly['成长月度收益率'] = growth_value_data_monthly['成长'].pct_change().shift(-1)
        growth_value_data_monthly['价值月度收益率'] = growth_value_data_monthly['价值'].pct_change().shift(-1)
        growth_value_data_monthly['成长/价值月度收益率'] = growth_value_data_monthly['成长/价值'].pct_change().shift(-1)
        growth_value_data_monthly_stat_list = []
        for factor_name in ['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']:
            growth_value_data_monthly_stat = pd.DataFrame(growth_value_data_monthly[[factor_name + '_SCORE', '成长月度收益率', '价值月度收益率', '成长/价值月度收益率']].dropna().groupby(factor_name + '_SCORE').median())
            growth_value_data_monthly_stat['FACTOR'] = factor_name + '_SCORE'
            growth_value_data_monthly_stat_list.append(growth_value_data_monthly_stat)
        growth_value_data_monthly_stat = pd.concat(growth_value_data_monthly_stat_list)

        growth_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370'])
        growth_index = growth_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        growth_index = growth_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        growth_index['TRADE_DATE'] = growth_index['TRADE_DATE'].astype(str)
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        # growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        growth_data = growth_data.merge(growth_index, on=['TRADE_DATE'], how='left')
        growth_data['GROWTH_TIMING_UP1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_UP15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_SCORE'] = growth_data.apply(
            lambda x: 5 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP15'] else
            4 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP1'] else
            1 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN15'] else
            2 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN1'] else 3, axis=1)
        growth_data_monthly = growth_data[growth_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        value_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399371'])
        value_index = value_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        value_index = value_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        value_index['TRADE_DATE'] = value_index['TRADE_DATE'].astype(str)
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        # value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        value_data = value_data.merge(value_index, on=['TRADE_DATE'], how='left')
        value_data['VALUE_TIMING_UP1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_UP15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_SCORE'] = value_data.apply(
            lambda x: 5 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP15'] else
            4 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP1'] else
            1 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN15'] else
            2 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN1'] else 3, axis=1)
        value_data_monthly = value_data[value_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        market_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001'])
        market_index = market_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        market_index = market_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        market_index['TRADE_DATE'] = market_index['TRADE_DATE'].astype(str)

        growth_index = growth_index.merge(market_index[['TRADE_DATE', 'CLOSE_INDEX']].rename(columns={'CLOSE_INDEX': 'BMK_CLOSE_INDEX'}), on=['TRADE_DATE'], how='left').merge(growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        growth_index['GROWTH_TIMING_SCORE'] = growth_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        growth_index = growth_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        growth_index['RET'] = growth_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        growth_index['BMK_RET'] = growth_index['BMK_CLOSE_INDEX'].pct_change().fillna(0.0)
        growth_index['RET_ADJ'] = growth_index.apply(lambda x: x['RET'] if x['GROWTH_TIMING_SCORE'] == 4 or x['GROWTH_TIMING_SCORE'] == 5 else x['BMK_RET'], axis=1)
        growth_index['RET_ADJ'] = growth_index['RET_ADJ'].fillna(0.0)
        growth_index['NAV'] = (growth_index['RET_ADJ'] + 1).cumprod()
        growth_index['CLOSE_INDEX'] = growth_index['CLOSE_INDEX'] / growth_index['CLOSE_INDEX'].iloc[0]
        growth_index['TRADE_DATE_DISP'] = growth_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['NAV'].values, color=line_color_list[0], label='成长择时', linewidth=3)
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['CLOSE_INDEX'].values, color=line_color_list[2], label='巨潮成长', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('成长择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长择时.png'.format(self.data_path))

        value_index = value_index.merge(market_index[['TRADE_DATE', 'CLOSE_INDEX']].rename(columns={'CLOSE_INDEX': 'BMK_CLOSE_INDEX'})).merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        value_index['VALUE_TIMING_SCORE'] = value_index['VALUE_TIMING_SCORE'].fillna(method='ffill')
        value_index = value_index.dropna(subset=['VALUE_TIMING_SCORE'])
        value_index['RET'] = value_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        value_index['BMK_RET'] = value_index['BMK_CLOSE_INDEX'].pct_change().fillna(0.0)
        value_index['RET_ADJ'] = value_index.apply(lambda x: x['RET'] if x['VALUE_TIMING_SCORE'] == 4 or x['VALUE_TIMING_SCORE'] == 5 else x['BMK_RET'], axis=1)
        value_index['RET_ADJ'] = value_index['RET_ADJ'].fillna(0.0)
        value_index['NAV'] = (value_index['RET_ADJ'] + 1).cumprod()
        value_index['CLOSE_INDEX'] = value_index['CLOSE_INDEX'] / value_index['CLOSE_INDEX'].iloc[0]
        value_index['TRADE_DATE_DISP'] = value_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['NAV'].values, color=line_color_list[0], label='价值择时', linewidth=3)
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['CLOSE_INDEX'].values, color=line_color_list[2], label='巨潮价值', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('价值择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}价值择时.png'.format(self.data_path))

        style_timing = growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']].merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        style_timing['成长_WEIGHT'] = style_timing['GROWTH_TIMING_SCORE'].replace({5: 0.9, 4: 0.7, 3: 0.5, 2: 0.3, 1: 0.1})
        style_timing['价值_WEIGHT'] = style_timing['VALUE_TIMING_SCORE'].replace({5: 0.9, 4: 0.7, 3: 0.5, 2: 0.3, 1: 0.1})
        style_timing['TRADE_DATE'] = style_timing['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        style_timing = style_timing.set_index('TRADE_DATE').sort_index()
        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370', '399371'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(style_timing[['成长_WEIGHT', '价值_WEIGHT']], left_index=True, right_index=True, how='left')
        index['成长_WEIGHT'] = index['成长_WEIGHT'].fillna(method='ffill')
        index['价值_WEIGHT'] = index['价值_WEIGHT'].fillna(method='ffill')
        index = index.dropna(subset=['成长_WEIGHT'])
        index = index.dropna(subset=['价值_WEIGHT'])
        index['成长_WEIGHT'] = index['成长_WEIGHT'] / (index['成长_WEIGHT'] + index['价值_WEIGHT'])
        index['价值_WEIGHT'] = index['价值_WEIGHT'] / (index['成长_WEIGHT'] + index['价值_WEIGHT'])
        index['RET_ADJ'] = index['成长_WEIGHT'] * index['399370_RET'] + index['价值_WEIGHT'] * index['399371_RET']
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index['RET_AVERAGE'] = 0.5 * index['399370_RET'] + 0.5 * index['399371_RET']
        index['RET_AVERAGE'] = index['RET_AVERAGE'].fillna(0.0)
        index['RET_AVERAGE'].iloc[0] = 0.0
        index['NAV_AVERAGE'] = (index['RET_AVERAGE'] + 1).cumprod()
        index = index.dropna()
        index[['NAV_AVERAGE', 'NAV']] = index[['NAV_AVERAGE', 'NAV']] / index[['NAV_AVERAGE', 'NAV']].iloc[0]
        index = index.reset_index()
        index['TRADE_DATE_DISP'] = index['TRADE_DATE']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='成长/价值择时', linewidth=3)
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV_AVERAGE'].values, color=line_color_list[2], label='成长/价值等权', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5, frameon=False)
        plt.title('成长/价值仓位打分调仓组合回测图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时策略.png'.format(self.data_path))

        style_index = style_index.merge(style_timing[['GROWTH_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        style_index['GROWTH_TIMING_SCORE'] = style_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        style_index = style_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        style_index_1 = style_index[style_index['GROWTH_TIMING_SCORE'] == 1]
        style_index_2 = style_index[style_index['GROWTH_TIMING_SCORE'] == 2]
        style_index_3 = style_index[style_index['GROWTH_TIMING_SCORE'] == 3]
        style_index_4 = style_index[style_index['GROWTH_TIMING_SCORE'] == 4]
        style_index_5 = style_index[style_index['GROWTH_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[3], label='成长/价值')
        ax.scatter(style_index_1.index, style_index_1['成长/价值'].values, color=line_color_list[1], label='成长评分1')
        ax.scatter(style_index_2.index, style_index_2['成长/价值'].values, color=line_color_list[9], label='成长评分2')
        ax.scatter(style_index_3.index, style_index_3['成长/价值'].values, color=line_color_list[3], label='成长评分3')
        ax.scatter(style_index_4.index, style_index_4['成长/价值'].values, color=line_color_list[4], label='成长评分4')
        ax.scatter(style_index_5.index, style_index_5['成长/价值'].values, color=line_color_list[0], label='成长评分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6, frameon=False)
        plt.title('成长评分及成长/价值走势图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时.png'.format(self.data_path))
        return

    def get_result(self):
        style_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399371', '399370', '881001'])
        style_index.to_hdf('{0}style_index.hdf'.format(self.data_path), key='table', mode='w')
        style_index = pd.read_hdf('{0}style_index.hdf'.format(self.data_path), key='table')
        style_index = style_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].astype(str)
        style_index = style_index[style_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style_index = style_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        style_index = style_index.rename(columns={'399370': '成长', '399371': '价值', '881001': '万得全A'})
        style_index['成长/价值'] = style_index['成长'] / style_index['价值']
        style_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index.index)
        style_index_disp = style_index[(style_index.index >= datetime.strptime(self.end_date, '%Y%m%d')) & (style_index.index <= datetime.strptime(self.tracking_end_date, '%Y%m%d'))]
        style_index_disp = style_index_disp / style_index_disp.iloc[0]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index_disp.index, style_index_disp['成长'].values, color=line_color_list[0], label='成长',linewidth=3)
        ax.plot(style_index_disp.index, style_index_disp['价值'].values, color=line_color_list[1], label='价值', linewidth=3)
        ax.plot(style_index_disp.index, style_index_disp['万得全A'].values, color=line_color_list[2], label='万得全A', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('成长/价值/万得全A走势', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值万得全A走势.png'.format(self.data_path))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index_disp.index, style_index_disp['成长/价值'].values, color=line_color_list[0], label='成长/价值', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1, frameon=False)
        plt.title('成长/价值相对走势', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值相对走势.png'.format(self.data_path))

        start = datetime.strptime('20200101', '%Y%m%d')
        end = datetime.strptime(self.tracking_end_date, '%Y%m%d')

        n1 = 250
        n2 = 250
        thresh1 = 0.5
        thresh15 = 1.0
        style_data = FEDB().read_timing_data(['TRADE_DATE', 'GROWTH_CROWDING', 'VALUE_CROWDING', 'GROWTH_SPREAD', 'VALUE_SPREAD', 'GROWTH_MOMENTUM', 'VALUE_MOMENTUM'], 'timing_style', self.start_date, self.tracking_end_date)
        style_data['TRADE_DATE'] = style_data['TRADE_DATE'].astype(str)
        style_data = style_data.dropna()
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(240).apply(lambda x: x.iloc[19::20].mean() / x.iloc[19::20].std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['IDX'] = range(len(growth_data))
        growth_data['GROWTH_SPREAD'] = growth_data['IDX'].rolling(n1).apply(lambda x: quantile_definition(x, 'GROWTH_SPREAD', growth_data))
        growth_data = growth_data.drop('IDX', axis=1)
        growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(240).apply(lambda x: x.iloc[19::20].mean() / x.iloc[19::20].std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['IDX'] = range(len(value_data))
        value_data['VALUE_SPREAD'] = value_data['IDX'].rolling(n1).apply(lambda x: quantile_definition(x, 'VALUE_SPREAD', value_data))
        value_data = value_data.drop('IDX', axis=1)
        value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        growth_value_data = growth_data.merge(value_data, on=['TRADE_DATE'], how='left').dropna()
        growth_value_data = growth_value_data.set_index('TRADE_DATE').sort_index()
        growth_value_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data.index)
        growth_value_data_disp = growth_value_data.merge(style_index, left_index=True, right_index=True, how='left').dropna().sort_index()
        growth_value_data_disp = growth_value_data_disp[(growth_value_data_disp.index >= start) & (growth_value_data_disp.index <= end)]
        month_df = self.trade_df[self.trade_df['IS_WEEK_END'] == '1']
        growth_value_data_disp.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data_disp.index)
        growth_value_data_disp = growth_value_data_disp.loc[growth_value_data_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_disp.index)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_MOMENTUM'].values, color=line_color_list[0], label='成长因子动量', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_MOMENTUM'].values, color=line_color_list[1], label='价值因子动量', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('因子动量与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子动量与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_SPREAD'].values, color=line_color_list[0], label='成长因子离散度', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_SPREAD'].values, color=line_color_list[1], label='价值因子离散度', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('因子离散度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子离散度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_CROWDING'].values, color=line_color_list[0], label='成长因子拥挤度', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_CROWDING'].values, color=line_color_list[1], label='价值因子拥挤度', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('因子拥挤度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子拥挤度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_TIMING'].values, color=line_color_list[0], label='成长因子复合指标', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_TIMING'].values, color=line_color_list[1], label='价值因子复合指标', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('因子复合指标与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子复合指标与成长价值历史相对走势.png'.format(self.data_path))
        return

    def get_signal_new(self):
        style_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399371', '399370', '881001'])
        style_index.to_hdf('{0}style_index.hdf'.format(self.data_path), key='table', mode='w')
        style_index = pd.read_hdf('{0}style_index.hdf'.format(self.data_path), key='table')
        style_index = style_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].astype(str)
        style_index = style_index[style_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style_index = style_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        style_index = style_index.rename(columns={'399370': '成长', '399371': '价值', '881001': '万得全A'})
        style_index['成长/价值'] = style_index['成长'] / style_index['价值']
        style_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index.index)
        style_index_disp = style_index[(style_index.index >= datetime.strptime(self.start_date, '%Y%m%d')) & (style_index.index <= datetime.strptime(self.tracking_end_date, '%Y%m%d'))]
        style_index_disp = style_index_disp / style_index_disp.iloc[0]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index_disp.index, style_index_disp['成长'].values, color=line_color_list[0], label='成长',linewidth=3)
        ax.plot(style_index_disp.index, style_index_disp['价值'].values, color=line_color_list[1], label='价值', linewidth=3)
        ax.plot(style_index_disp.index, style_index_disp['万得全A'].values, color=line_color_list[2], label='万得全A', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('成长/价值/万得全A走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值万得全A走势.png'.format(self.data_path))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index_disp.index, style_index_disp['成长/价值'].values, color=line_color_list[0], label='成长/价值', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1, frameon=False)
        plt.title('成长/价值相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值相对走势.png'.format(self.data_path))

        # 期限利差
        bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期长端国债利率', '1年期短端国债利率']
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield = bond_yield[(bond_yield.index > self.start_date) & (bond_yield.index <= self.end_date)].dropna()
        bond_yield['期限利差'] = bond_yield['10年期长端国债利率'] - bond_yield['1年期短端国债利率']
        bond_yield['期限利差'] = bond_yield['期限利差'].rolling(20).mean()
        bond_yield['IDX'] = range(len(bond_yield))
        bond_yield['期限利差_Q'] = bond_yield['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '期限利差', bond_yield))
        bond_yield = bond_yield.drop('IDX', axis=1)
        bond_yield.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield.index)
        ##########################
        bond_yield_disp = style_index.merge(bond_yield, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_yield_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_yield_disp.index)
        bond_yield_disp = bond_yield_disp.loc[bond_yield_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        ##########################
        bond_yield_disp['成长月度收益率'] = bond_yield_disp['成长'].pct_change()  # .shift(-1)
        bond_yield_disp['价值月度收益率'] = bond_yield_disp['价值'].pct_change()  # .shift(-1)
        bond_yield_disp['成长/价值月度收益率'] = bond_yield_disp['成长/价值'].pct_change()  # .shift(-1)
        bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5, ['成长月度收益率', '价值月度收益率', '成长/价值月度收益率']].dropna().mean()
        len(bond_yield_disp.loc[(bond_yield_disp['期限利差_Q'] < 0.5) & (bond_yield_disp['成长月度收益率'] > 0.0)].dropna()) / float(len(bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5].dropna()))
        ##########################
        bond_yield_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_yield_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['期限利差'].values, color=line_color_list[0], label='期限利差', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('期限利差与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差与成长价值历史相对走势.png'.format(self.data_path))

        # CPI-PPI
        cpi_ppi = w.edb("M0000612,M0001227", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        cpi_ppi.to_hdf('{0}cpi_ppi.hdf'.format(self.data_path), key='table', mode='w')
        cpi_ppi = pd.read_hdf('{0}cpi_ppi.hdf'.format(self.data_path), key='table')
        cpi_ppi.columns = ['CALENDAR_DATE', 'CPI_当月同比', 'PPI_当月同比']
        cpi_ppi['CALENDAR_DATE'] = cpi_ppi['CALENDAR_DATE'].shift(-1).fillna(self.end_date_hyphen)
        cpi_ppi['CALENDAR_DATE'] = cpi_ppi['CALENDAR_DATE'].apply(lambda x: str(x).replace('-', ''))
        cpi_ppi = cpi_ppi.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        cpi_ppi['CPI_PPI'] = cpi_ppi['CPI_当月同比'] - cpi_ppi['PPI_当月同比']
        cpi_ppi = cpi_ppi.set_index('TRADE_DATE').sort_index()
        cpi_ppi.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), cpi_ppi.index)
        ##########################
        cpi_ppi_disp = style_index.merge(cpi_ppi, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        cpi_ppi_disp.index = map(lambda x: x.strftime('%Y%m%d'), cpi_ppi_disp.index)
        cpi_ppi_disp = cpi_ppi_disp[(cpi_ppi_disp.index >= self.start_date) & (cpi_ppi_disp.index <= self.end_date)].dropna()
        cpi_ppi_disp = cpi_ppi_disp.loc[cpi_ppi_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        cpi_ppi_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), cpi_ppi_disp.index)
        ##########################
        cpi_ppi_disp['CPI_PPI_ST'] = cpi_ppi_disp['CPI_PPI'].rolling(3).mean()
        cpi_ppi_disp['CPI_PPI_LT'] = cpi_ppi_disp['CPI_PPI'].rolling(12).mean()
        cpi_ppi_disp['CPI_PPI_DIFF'] = cpi_ppi_disp['CPI_PPI_ST'] - cpi_ppi_disp['CPI_PPI_LT']
        cpi_ppi_disp = cpi_ppi_disp.dropna()
        cpi_ppi_disp['MODEL_MARK'] = cpi_ppi_disp.apply(lambda x: '成长' if x['CPI_PPI_DIFF'] > 0.0 else '价值', axis=1)
        cpi_ppi_disp['MONTH_RETURN'] = cpi_ppi_disp['成长/价值'].pct_change().shift(-1)
        cpi_ppi_disp['ACTUAL_MARK'] = cpi_ppi_disp.apply(lambda x: '成长' if x['MONTH_RETURN'] > 0.0 else '价值', axis=1)
        cpi_ppi_disp.index = map(lambda x: x.strftime('%Y%m%d'), cpi_ppi_disp.index)
        # cpi_ppi_disp = cpi_ppi_disp.dropna()
        # print(round(len(cpi_ppi_disp[cpi_ppi_disp['MODEL_MARK'] == cpi_ppi_disp['ACTUAL_MARK']]) / float(len(cpi_ppi_disp)), 2))
        cpi_ppi_disp_yes = cpi_ppi_disp.copy(deep=True)
        cpi_ppi_disp_no = cpi_ppi_disp.copy(deep=True)
        cpi_ppi_disp_yes['分组_SCORE'] = cpi_ppi_disp_yes.apply(lambda x: 1.0 if x['CPI_PPI_DIFF'] > 0.0 else 0.0, axis=1)
        cpi_ppi_disp_no['分组_SCORE'] = cpi_ppi_disp_no.apply(lambda x: 1.0 if x['CPI_PPI_DIFF'] < 0.0 else 0.0, axis=1)
        # cpi_ppi_disp_yes['分组_SCORE'] = cpi_ppi_disp_yes['分组_SCORE'] * max(max(cpi_ppi_disp['CPI_当月同比']), max(cpi_ppi_disp['PPI_当月同比']))
        # cpi_ppi_disp_no['分组_SCORE'] = cpi_ppi_disp_no['分组_SCORE'] * max(max(cpi_ppi_disp['CPI_当月同比']), max(cpi_ppi_disp['PPI_当月同比']))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.bar(np.arange(len(cpi_ppi_disp_yes)), cpi_ppi_disp_yes['分组_SCORE'].values, label='短均值大于长均值', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(cpi_ppi_disp_no)), cpi_ppi_disp_no['分组_SCORE'].values, label='短均值小于长均值', color=line_color_list[2], alpha=0.3)
        ax_r.plot(cpi_ppi_disp.index, cpi_ppi_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        ax.set_xticks(np.arange(len(cpi_ppi_disp))[::6])
        ax.set_xticklabels(labels=cpi_ppi_disp.index.tolist()[::6], rotation=45)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
        plt.title('CPI-PPI剪刀差与成长价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}CPI-PPI剪刀差与成长价值历史相对走势.png'.format(self.data_path))

        # 指数成分股（每半年更新）
        cons_399370_path = '{0}399370_cons.hdf'.format(self.data_path)
        cons_399371_path = '{0}399371_cons.hdf'.format(self.data_path)
        if os.path.isfile(cons_399370_path) and os.path.isfile(cons_399371_path):
            existed_cons_399370 = pd.read_hdf(cons_399370_path, key='table')
            existed_cons_399371 = pd.read_hdf(cons_399371_path, key='table')
            max_date_399370 = max(existed_cons_399370['date'])
            max_date_399371 = max(existed_cons_399371['date'])
            start_date = max(str(max_date_399370)[:10].replace('-', ''), str(max_date_399371)[:10].replace('-', ''), '20071231')
        else:
            existed_cons_399370 = pd.DataFrame()
            existed_cons_399371 = pd.DataFrame()
            start_date = '20071231'
        report_df = self.report_df[(self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.end_date)]
        semiyear_df = report_df[report_df['MONTH'].isin(['06', '12'])]
        date_list = semiyear_df['REPORT_DATE'].unique().tolist()
        cons_399370_list, cons_399371_list = [], []
        for date in date_list:
            date_hyphen = datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d')
            cons_399370_date = w.wset("sectorconstituent", "date={0};windcode={1}".format(date_hyphen, '399370.SZ'), usedf=True)[1]
            cons_399371_date = w.wset("sectorconstituent", "date={0};windcode={1}".format(date_hyphen, '399371.SZ'), usedf=True)[1]
            cons_399370_list.append(cons_399370_date)
            cons_399371_list.append(cons_399371_date)
        cons_399370 = pd.concat([existed_cons_399370] + cons_399370_list)
        cons_399371 = pd.concat([existed_cons_399371] + cons_399371_list)
        cons_399370.to_hdf('{0}399370_cons.hdf'.format(self.data_path), key='table', mode='w')
        cons_399371.to_hdf('{0}399371_cons.hdf'.format(self.data_path), key='table', mode='w')
        cons_399370 = pd.read_hdf('{0}399370_cons.hdf'.format(self.data_path), key='table')
        cons_399370.columns = ['REPORT_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']
        cons_399370['INDEX_SYMBOL'] = '399370'
        cons_399370['REPORT_DATE'] = cons_399370['REPORT_DATE'].apply(lambda x: str(x.date()).replace('-', ''))
        cons_399370['TICKER_SYMBOL'] = cons_399370['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
        cons_399370 = cons_399370[['INDEX_SYMBOL', 'REPORT_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']]
        cons_399371 = pd.read_hdf('{0}399371_cons.hdf'.format(self.data_path), key='table')
        cons_399371.columns = ['REPORT_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']
        cons_399371['INDEX_SYMBOL'] = '399371'
        cons_399371['REPORT_DATE'] = cons_399371['REPORT_DATE'].apply(lambda x: str(x.date()).replace('-', ''))
        cons_399371['TICKER_SYMBOL'] = cons_399371['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
        cons_399371 = cons_399371[['INDEX_SYMBOL', 'REPORT_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME']]
        style_cons = pd.concat([cons_399370, cons_399371])
        # 股票收盘价、涨跌幅、成交金额、换手率、流通市值、总市值
        stock_daily_k_path = '{0}stock_daily_k.hdf'.format(self.data_path)
        if os.path.isfile(stock_daily_k_path):
            existed_stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
            max_date = max(existed_stock_daily_k['TDATE'])
            start_date = max(str(max_date), '20071231')
        else:
            existed_stock_daily_k = pd.DataFrame()
            start_date = '20071231'
        trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.tracking_end_date)]
        stock_daily_k_list = []
        for date in trade_df['TRADE_DATE'].unique().tolist():
            stock_daily_k_date = HBDB().read_stock_daily_k_ch(int(date))
            stock_daily_k_list.append(stock_daily_k_date)
            print(date)
        stock_daily_k = pd.concat([existed_stock_daily_k] + stock_daily_k_list, ignore_index=True)
        stock_daily_k.to_hdf(stock_daily_k_path, key='table', mode='w')
        stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        stock_daily_k = stock_daily_k.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'MARKET_VALUE'})
        stock_daily_k['TRADE_DATE'] = stock_daily_k['TRADE_DATE'].astype(str)
        stock_daily_k = stock_daily_k.loc[stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
        stock_daily_k = stock_daily_k.loc[stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
        stock_daily_k = stock_daily_k.sort_values(['TRADE_DATE', 'TICKER_SYMBOL'])
        stock_daily_k = stock_daily_k.reset_index().drop('index', axis=1)
        stock_daily_k = stock_daily_k[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'CLOSE_PRICE', 'PCT_CHANGE', 'TURNOVER_VALUE', 'TURNOVER_RATE', 'NEG_MARKET_VALUE', 'MARKET_VALUE']]
        semiyear_df = self.report_df[self.report_df['MONTH'].isin(['06', '12'])]
        semiyear_df = semiyear_df.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'REPORT_DATE'}), on=['REPORT_DATE'], how='left')
        trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] >= self.start_date) & (self.trade_df['TRADE_DATE'] <= self.end_date)]
        month_df = trade_df[trade_df['IS_MONTH_END'] == '1']
        powerful_stock_ratio = pd.DataFrame(index=month_df['TRADE_DATE'].unique().tolist(), columns=['399370', '399371'])
        for date in month_df['TRADE_DATE'].unique().tolist():
            sample_date = semiyear_df[semiyear_df['TRADE_DATE'] <= date]['REPORT_DATE'].iloc[-1]
            style_cons_date = style_cons[style_cons['REPORT_DATE'] == sample_date]
            cons_399370_date = cons_399370[cons_399370['REPORT_DATE'] == sample_date]
            cons_399371_date = cons_399371[cons_399371['REPORT_DATE'] == sample_date]
            if len(style_cons_date) == 0:
                continue
            stock_daily_k_399370_date = stock_daily_k[stock_daily_k['TICKER_SYMBOL'].isin(cons_399370_date['TICKER_SYMBOL'].unique().tolist())]
            stock_daily_k_399370_date = stock_daily_k_399370_date.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CLOSE_PRICE')
            stock_daily_k_399370_date = stock_daily_k_399370_date.sort_index().replace(0.0, np.nan).fillna(method='ffill')
            stock_daily_k_399370_date = stock_daily_k_399370_date[stock_daily_k_399370_date.index <= date]
            stock_daily_k_399370_date_ma5 = stock_daily_k_399370_date.rolling(5).mean()
            stock_daily_k_399370_date_ma5 = stock_daily_k_399370_date_ma5.unstack().reset_index()
            stock_daily_k_399370_date_ma5.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'MA5']
            stock_daily_k_399370_date_ma5 = stock_daily_k_399370_date_ma5[stock_daily_k_399370_date_ma5['TRADE_DATE'] == date]
            stock_daily_k_399370_date_ma20 = stock_daily_k_399370_date.rolling(20).mean()
            stock_daily_k_399370_date_ma20 = stock_daily_k_399370_date_ma20.unstack().reset_index()
            stock_daily_k_399370_date_ma20.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'MA20']
            stock_daily_k_399370_date_ma20 = stock_daily_k_399370_date_ma20[stock_daily_k_399370_date_ma20['TRADE_DATE'] == date]
            stock_daily_k_399370_date = stock_daily_k_399370_date_ma5.merge(stock_daily_k_399370_date_ma20, on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left')
            powerful_stock_ratio.loc[date, '399370'] = len(stock_daily_k_399370_date[stock_daily_k_399370_date['MA5'] > stock_daily_k_399370_date['MA20']]) / float(len(stock_daily_k_399370_date))
            stock_daily_k_399371_date = stock_daily_k[stock_daily_k['TICKER_SYMBOL'].isin(cons_399371_date['TICKER_SYMBOL'].unique().tolist())]
            stock_daily_k_399371_date = stock_daily_k_399371_date.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CLOSE_PRICE')
            stock_daily_k_399371_date = stock_daily_k_399371_date.sort_index().replace(0.0, np.nan).fillna(method='ffill')
            stock_daily_k_399371_date = stock_daily_k_399371_date[stock_daily_k_399371_date.index <= date]
            stock_daily_k_399371_date_ma5 = stock_daily_k_399371_date.rolling(5).mean()
            stock_daily_k_399371_date_ma5 = stock_daily_k_399371_date_ma5.unstack().reset_index()
            stock_daily_k_399371_date_ma5.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'MA5']
            stock_daily_k_399371_date_ma5 = stock_daily_k_399371_date_ma5[stock_daily_k_399371_date_ma5['TRADE_DATE'] == date]
            stock_daily_k_399371_date_ma20 = stock_daily_k_399371_date.rolling(20).mean()
            stock_daily_k_399371_date_ma20 = stock_daily_k_399371_date_ma20.unstack().reset_index()
            stock_daily_k_399371_date_ma20.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'MA20']
            stock_daily_k_399371_date_ma20 = stock_daily_k_399371_date_ma20[stock_daily_k_399371_date_ma20['TRADE_DATE'] == date]
            stock_daily_k_399371_date = stock_daily_k_399371_date_ma5.merge(stock_daily_k_399371_date_ma20, on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left')
            powerful_stock_ratio.loc[date, '399371'] = len(stock_daily_k_399371_date[stock_daily_k_399371_date['MA5'] > stock_daily_k_399371_date['MA20']]) / float(len(stock_daily_k_399371_date))
            print(date)
        powerful_stock_ratio.to_hdf('{0}powerful_stock_ratio.hdf'.format(self.data_path), key='table', mode='w')
        powerful_stock_ratio = pd.read_hdf('{0}powerful_stock_ratio.hdf'.format(self.data_path), key='table')
        powerful_stock_ratio.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), powerful_stock_ratio.index)
        ##########################
        powerful_stock_ratio_disp = style_index.merge(powerful_stock_ratio, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        powerful_stock_ratio_disp.index = map(lambda x: x.strftime('%Y%m%d'), powerful_stock_ratio_disp.index)
        powerful_stock_ratio_disp = powerful_stock_ratio_disp[(powerful_stock_ratio_disp.index >= self.start_date) & (powerful_stock_ratio_disp.index <= self.end_date)]
        powerful_stock_ratio_disp = powerful_stock_ratio_disp.loc[powerful_stock_ratio_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        powerful_stock_ratio_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), powerful_stock_ratio_disp.index)
        ##########################
        powerful_stock_ratio_disp['MODEL_MARK'] = powerful_stock_ratio_disp.apply(lambda x: '成长' if x['399370'] > x['399371'] else '价值', axis=1)
        powerful_stock_ratio_disp['MONTH_RETURN'] = powerful_stock_ratio_disp['成长/价值'].pct_change().shift(-1)
        powerful_stock_ratio_disp['ACTUAL_MARK'] = powerful_stock_ratio_disp.apply(lambda x: '成长' if x['MONTH_RETURN'] > 0.0 else '价值', axis=1)
        # powerful_stock_ratio_disp = powerful_stock_ratio_disp.dropna()
        print(round(len(powerful_stock_ratio_disp[powerful_stock_ratio_disp['MODEL_MARK'] == powerful_stock_ratio_disp['ACTUAL_MARK']]) / float(len(powerful_stock_ratio_disp)), 2))
        powerful_stock_ratio_disp.index = map(lambda x: x.strftime('%Y%m%d'), powerful_stock_ratio_disp.index)
        powerful_stock_ratio_disp_yes = powerful_stock_ratio_disp.copy(deep=True)
        powerful_stock_ratio_disp_no = powerful_stock_ratio_disp.copy(deep=True)
        powerful_stock_ratio_disp_yes['分组_SCORE'] = powerful_stock_ratio_disp_yes.apply(lambda x: 1.0 if x['399370'] > x['399371'] else 0, axis=1)
        powerful_stock_ratio_disp_no['分组_SCORE'] = powerful_stock_ratio_disp_no.apply(lambda x: 1.0 if x['399371'] > x['399370'] else 0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax_r.plot(np.arange(len(powerful_stock_ratio_disp)), powerful_stock_ratio_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        ax.bar(np.arange(len(powerful_stock_ratio_disp_yes)), powerful_stock_ratio_disp_yes['分组_SCORE'].values, label='成长强势', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(powerful_stock_ratio_disp_no)), powerful_stock_ratio_disp_no['分组_SCORE'].values, label='价值强势', color=line_color_list[2], alpha=0.3)
        ax.set_xticks(np.arange(len(powerful_stock_ratio_disp))[::6])
        ax.set_xticklabels(labels=powerful_stock_ratio_disp.index.tolist()[::6], rotation=45)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
        plt.title('强势股与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}强势股与成长价值历史相对走势.png'.format(self.data_path))

        # 估值偏好
        organ_investigation_path = '{0}organ_investigation.hdf'.format(self.data_path)
        if os.path.isfile(organ_investigation_path):
            existed_organ_investigation = pd.read_hdf(organ_investigation_path, key='table')
            max_date = max(existed_organ_investigation['TRADE_DATE']).replace('-', '')
            start_date = max(str(max_date), '20150101')
        else:
            existed_organ_investigation = pd.DataFrame()
            start_date = '20150101'
        if start_date < self.trade_df[self.trade_df['TRADE_DATE'] <= self.end_date]['TRADE_DATE'].iloc[-1]:
            month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
            month_df = month_df[(month_df['TRADE_DATE'] >= start_date) & (month_df['TRADE_DATE'] <= self.end_date)]
            date_list = month_df['TRADE_DATE'].unique().tolist()
            organ_investigation_list = []
            for idx in range(len(date_list) - 1):
                start_date_hyphen = datetime.strptime(date_list[idx], '%Y%m%d').strftime('%Y-%m-%d')
                end_date_hyphen = datetime.strptime(date_list[idx + 1], '%Y%m%d').strftime('%Y-%m-%d')
                organ_investigation = w.wset("researchstaticsbysecurity","startdate={0};enddate={1};sectorid=a001010100000000;windcode=;field=wind_code,sec_name,investigation_count".format(start_date_hyphen, end_date_hyphen), usedf=True)[1].reset_index()
                organ_investigation['TRADE_DATE'] = end_date_hyphen
                organ_investigation_list.append(organ_investigation)
                print(end_date_hyphen)
            organ_investigation = pd.concat([existed_organ_investigation] + organ_investigation_list)
            organ_investigation.to_hdf(organ_investigation_path, key='table', mode='w')
        organ_investigation = pd.read_hdf(organ_investigation_path, key='table')
        organ_investigation = organ_investigation.drop('index', axis=1)
        organ_investigation.columns = ['TICKER_SYMBOL', 'SEC_SHORT_NAME', 'INVESTIGATION_COUNT', 'TRADE_DATE']
        organ_investigation['TICKER_SYMBOL'] = organ_investigation['TICKER_SYMBOL'].apply(lambda x: str(x).split('.')[0])
        organ_investigation['TRADE_DATE'] = organ_investigation['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        value = pd.read_hdf('{0}value.hdf'.format(self.data_path), key='table')
        value = value[value['TRADE_DATE'].isin(organ_investigation['TRADE_DATE'].unique().tolist())]
        organ_investigation = organ_investigation.merge(value, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left')
        organ_investigation = organ_investigation[['TRADE_DATE', 'VALUE']].groupby('TRADE_DATE').median().reset_index().rename(columns={'VALUE': 'ORGAN_INVESTGATION_VALUE'})
        organ_investigation = value.merge(organ_investigation, on=['TRADE_DATE'], how='left')
        organ_investigation = organ_investigation.sort_values(['TRADE_DATE', 'TICKER_SYMBOL']).dropna()
        organ_investigation_value = pd.DataFrame(index=organ_investigation['TRADE_DATE'].unique().tolist(), columns=['ORGAN_INVESTGATION_VALUE_Q'])
        for date in organ_investigation['TRADE_DATE'].unique().tolist():
            organ_investigation_date = organ_investigation[organ_investigation['TRADE_DATE'] == date]
            q = (1.0 - np.count_nonzero(organ_investigation_date['ORGAN_INVESTGATION_VALUE'].iloc[-1] <= organ_investigation_date['VALUE']) / len(organ_investigation_date))
            organ_investigation_value.loc[date, 'ORGAN_INVESTGATION_VALUE_Q'] = q
        organ_investigation_value.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), organ_investigation_value.index)
        ##########################
        organ_investigation_value_disp = style_index.merge(organ_investigation_value, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        organ_investigation_value_disp.index = map(lambda x: x.strftime('%Y%m%d'), organ_investigation_value_disp.index)
        organ_investigation_value_disp = organ_investigation_value_disp[(organ_investigation_value_disp.index >= self.start_date) & (organ_investigation_value_disp.index <= self.end_date)]
        organ_investigation_value_disp = organ_investigation_value_disp.loc[organ_investigation_value_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        organ_investigation_value_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), organ_investigation_value_disp.index)
        ##########################
        organ_investigation_value_disp['MODEL_MARK'] = organ_investigation_value_disp.apply(lambda x: '成长' if x['ORGAN_INVESTGATION_VALUE_Q'] < 0.5 else '价值', axis=1)
        organ_investigation_value_disp['MONTH_RETURN'] = organ_investigation_value_disp['成长/价值'].pct_change().shift(-1)
        organ_investigation_value_disp['ACTUAL_MARK'] = organ_investigation_value_disp.apply(lambda x: '成长' if x['MONTH_RETURN'] > 0.0 else '价值', axis=1)
        # organ_investigation_value_disp = organ_investigation_value_disp.dropna()
        print(round(len(organ_investigation_value_disp[organ_investigation_value_disp['MODEL_MARK'] == organ_investigation_value_disp['ACTUAL_MARK']]) / float(len(organ_investigation_value_disp)), 2))
        organ_investigation_value_disp.index = map(lambda x: x.strftime('%Y%m%d'), organ_investigation_value_disp.index)
        organ_investigation_value_disp_yes = organ_investigation_value_disp.copy(deep=True)
        organ_investigation_value_disp_no = organ_investigation_value_disp.copy(deep=True)
        organ_investigation_value_disp_yes['分组_SCORE'] = organ_investigation_value_disp_yes.apply(lambda x: 1.0 if x['ORGAN_INVESTGATION_VALUE_Q'] < 0.5 else 0, axis=1)
        organ_investigation_value_disp_no['分组_SCORE'] = organ_investigation_value_disp_no.apply(lambda x: 1.0 if x['ORGAN_INVESTGATION_VALUE_Q'] > 0.5 else 0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax_r.plot(np.arange(len(organ_investigation_value_disp)), organ_investigation_value_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        ax.bar(np.arange(len(organ_investigation_value_disp_yes)), organ_investigation_value_disp_yes['分组_SCORE'].values, label='偏好成长', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(organ_investigation_value_disp_no)), organ_investigation_value_disp_no['分组_SCORE'].values, label='偏好价值', color=line_color_list[2], alpha=0.3)
        ax.set_xticks(np.arange(len(organ_investigation_value_disp))[::6])
        ax.set_xticklabels(labels=organ_investigation_value_disp.index.tolist()[::6], rotation=45)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
        plt.title('机构调研估值偏好与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}机构调研估值偏好与成长价值历史相对走势.png'.format(self.data_path))

        hk_cash_path = '{0}hk_cash.hdf'.format(self.data_path)
        if os.path.isfile(hk_cash_path):
            existed_hk_cash = pd.read_hdf(hk_cash_path, key='table')
            max_date = max(existed_hk_cash['TRADE_DATE']).replace('-', '')
            start_date = max(str(max_date), '20150101')
        else:
            existed_hk_cash = pd.DataFrame()
            start_date = '20150101'
        if start_date < self.trade_df[self.trade_df['TRADE_DATE'] <= self.end_date]['TRADE_DATE'].iloc[-1]:
            month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
            month_df = month_df[(month_df['TRADE_DATE'] > start_date) & (month_df['TRADE_DATE'] <= self.end_date)]
            date_list = month_df['TRADE_DATE'].unique().tolist()
            hk_cash_list = []
            for date in date_list:
                date_hyphen = datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d')
                sh_cash = w.wset("shstockholdings","date={0};field=wind_code,sec_name,holding_marketvalue".format(date_hyphen), usedf=True)[1].reset_index()
                sh_cash['TRADE_DATE'] = date_hyphen
                sz_cash = w.wset("szstockholdings", "date={0};field=wind_code,sec_name,holding_marketvalue".format(date_hyphen), usedf=True)[1].reset_index()
                sz_cash['TRADE_DATE'] = date_hyphen
                hk_cash = pd.concat([sh_cash, sz_cash])
                hk_cash_list.append(hk_cash)
                print(date_hyphen)
            hk_cash = pd.concat([existed_hk_cash] + hk_cash_list)
            hk_cash.to_hdf(hk_cash_path, key='table', mode='w')
        hk_cash = pd.read_hdf(hk_cash_path, key='table')
        hk_cash = hk_cash.drop('index', axis=1)
        hk_cash.columns = ['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'HOLDING_MARKET']
        hk_cash['TICKER_SYMBOL'] = hk_cash['TICKER_SYMBOL'].apply(lambda x: str(x).split('.')[0])
        hk_cash['TRADE_DATE'] = hk_cash['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        hk_cash = hk_cash.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='HOLDING_MARKET')
        hk_cash = hk_cash.reindex(self.calendar_df['CALENDAR_DATE'].unique().tolist()).sort_index().fillna(method='ffill')
        hk_cash = hk_cash[hk_cash.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        hk_cash = hk_cash.pct_change().unstack().reset_index()
        hk_cash.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'HOLDING_MARKET_CHANGE']
        value = pd.read_hdf('{0}value.hdf'.format(self.data_path), key='table')
        value = value[value['TRADE_DATE'].isin(hk_cash['TRADE_DATE'].unique().tolist())]
        hk_cash_q = hk_cash[['TRADE_DATE', 'HOLDING_MARKET_CHANGE']].groupby('TRADE_DATE').quantile(0.90).reset_index().rename(columns={'HOLDING_MARKET_CHANGE': 'HOLDING_MARKET_CHANGE_Q'})
        hk_cash = hk_cash.merge(hk_cash_q, on=['TRADE_DATE'], how='left')
        hk_cash = hk_cash[hk_cash['HOLDING_MARKET_CHANGE'] > hk_cash['HOLDING_MARKET_CHANGE_Q']]
        hk_cash = hk_cash.merge(value, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left')
        hk_cash = hk_cash[['TRADE_DATE', 'VALUE']].groupby('TRADE_DATE').median().reset_index().rename(columns={'VALUE': 'HK_CASH_VALUE'})
        hk_cash = value.merge(hk_cash, on=['TRADE_DATE'], how='left')
        hk_cash = hk_cash.sort_values(['TRADE_DATE', 'TICKER_SYMBOL']).dropna()
        hk_cash_value = pd.DataFrame(index=hk_cash['TRADE_DATE'].unique().tolist(), columns=['HK_CASH_VALUATION_Q'])
        for date in hk_cash['TRADE_DATE'].unique().tolist():
            hk_cash_date = hk_cash[hk_cash['TRADE_DATE'] == date]
            q = (1.0 - np.count_nonzero(hk_cash_date['HK_CASH_VALUE'].iloc[-1] <= hk_cash_date['VALUE']) / len(hk_cash_date))
            hk_cash_value.loc[date, 'HK_CASH_VALUATION_Q'] = q
        hk_cash_value.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), hk_cash_value.index)
        ##########################
        hk_cash_value_disp = style_index.merge(hk_cash_value, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        hk_cash_value_disp.index = map(lambda x: x.strftime('%Y%m%d'), hk_cash_value_disp.index)
        hk_cash_value_disp = hk_cash_value_disp[(hk_cash_value_disp.index >= self.start_date) & (hk_cash_value_disp.index <= self.end_date)]
        hk_cash_value_disp = hk_cash_value_disp.loc[hk_cash_value_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        hk_cash_value_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), hk_cash_value_disp.index)
        ##########################
        hk_cash_value_disp['MODEL_MARK'] = hk_cash_value_disp.apply(lambda x: '成长' if x['HK_CASH_VALUATION_Q'] < 0.5 else '价值', axis=1)
        hk_cash_value_disp['MONTH_RETURN'] = hk_cash_value_disp['成长/价值'].pct_change().shift(-1)
        hk_cash_value_disp['ACTUAL_MARK'] = hk_cash_value_disp.apply(lambda x: '成长' if x['MONTH_RETURN'] > 0.0 else '价值', axis=1)
        # hk_cash_value_disp = hk_cash_value_disp.dropna()
        print(round(len(hk_cash_value_disp[hk_cash_value_disp['MODEL_MARK'] == hk_cash_value_disp['ACTUAL_MARK']]) / float(len(hk_cash_value_disp)), 2))
        hk_cash_value_disp.index = map(lambda x: x.strftime('%Y%m%d'), hk_cash_value_disp.index)
        hk_cash_value_disp_yes = hk_cash_value_disp.copy(deep=True)
        hk_cash_value_disp_no = hk_cash_value_disp.copy(deep=True)
        hk_cash_value_disp_yes['分组_SCORE'] = hk_cash_value_disp_yes.apply(lambda x: 1.0 if x['HK_CASH_VALUATION_Q'] < 0.5 else 0, axis=1)
        hk_cash_value_disp_no['分组_SCORE'] = hk_cash_value_disp_no.apply(lambda x: 1.0 if x['HK_CASH_VALUATION_Q'] > 0.5 else 0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax_r.plot(np.arange(len(hk_cash_value_disp)), hk_cash_value_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        ax.bar(np.arange(len(hk_cash_value_disp_yes)), hk_cash_value_disp_yes['分组_SCORE'].values, label='成长强势', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(hk_cash_value_disp_no)), hk_cash_value_disp_no['分组_SCORE'].values, label='价值强势', color=line_color_list[2], alpha=0.3)
        ax.set_xticks(np.arange(len(hk_cash_value_disp))[::6])
        ax.set_xticklabels(labels=hk_cash_value_disp.index.tolist()[::6], rotation=45)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
        plt.title('北向资金估值偏好与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}北向资金估值偏好与成长价值历史相对走势.png'.format(self.data_path))

        value_prefer_disp = hk_cash_value_disp[['成长/价值', 'HK_CASH_VALUATION_Q']].merge(organ_investigation_value_disp[['ORGAN_INVESTGATION_VALUE_Q']], left_index=True, right_index=True, how='left')
        value_prefer_disp['VALUATION_PREFER_Q'] = value_prefer_disp['HK_CASH_VALUATION_Q'] * 0.5 + value_prefer_disp['ORGAN_INVESTGATION_VALUE_Q'] * 0.5
        value_prefer_disp['MODEL_MARK'] = value_prefer_disp.apply(lambda x: '成长' if x['VALUATION_PREFER_Q'] < 0.5 else '价值', axis=1)
        value_prefer_disp['MONTH_RETURN'] = value_prefer_disp['成长/价值'].pct_change().shift(-1)
        value_prefer_disp['ACTUAL_MARK'] = value_prefer_disp.apply(lambda x: '成长' if x['MONTH_RETURN'] > 0.0 else '价值', axis=1)
        # value_prefer_disp = value_prefer_disp.dropna()
        print(round(len(value_prefer_disp[value_prefer_disp['MODEL_MARK'] == value_prefer_disp['ACTUAL_MARK']]) / float(len(value_prefer_disp)), 2))
        value_prefer_disp_yes = value_prefer_disp.copy(deep=True)
        value_prefer_disp_no = value_prefer_disp.copy(deep=True)
        value_prefer_disp_yes['分组_SCORE'] = value_prefer_disp_yes.apply(lambda x: 1.0 if x['VALUATION_PREFER_Q'] < 0.5 else 0, axis=1)
        value_prefer_disp_no['分组_SCORE'] = value_prefer_disp_no.apply(lambda x: 1.0 if x['VALUATION_PREFER_Q'] > 0.5 else 0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax_r.plot(np.arange(len(value_prefer_disp)), value_prefer_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        ax.bar(np.arange(len(value_prefer_disp_yes)), value_prefer_disp_yes['分组_SCORE'].values, label='成长强势', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(value_prefer_disp_no)), value_prefer_disp_no['分组_SCORE'].values, label='价值强势', color=line_color_list[2], alpha=0.3)
        ax.set_xticks(np.arange(len(value_prefer_disp))[::6])
        ax.set_xticklabels(labels=value_prefer_disp.index.tolist()[::6], rotation=45)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
        plt.title('估值偏好与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}估值偏好与成长价值历史相对走势.png'.format(self.data_path))

        n1 = 250
        n2 = 250
        thresh1 = 0.5
        thresh15 = 1.0
        style_data = FEDB().read_timing_data(['TRADE_DATE', 'GROWTH_CROWDING', 'VALUE_CROWDING', 'GROWTH_SPREAD', 'VALUE_SPREAD', 'GROWTH_MOMENTUM', 'VALUE_MOMENTUM'], 'timing_style', self.start_date, self.end_date)
        style_data['TRADE_DATE'] = style_data['TRADE_DATE'].astype(str)
        style_data = style_data[(style_data['TRADE_DATE'] > self.start_date) & (style_data['TRADE_DATE'] <= self.end_date)]
        style_data = style_data.dropna()
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(240).apply(lambda x: x.iloc[19::20].mean() / x.iloc[19::20].std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['IDX'] = range(len(growth_data))
        growth_data['GROWTH_SPREAD'] = growth_data['IDX'].rolling(n1).apply(lambda x: quantile_definition(x, 'GROWTH_SPREAD', growth_data))
        growth_data = growth_data.drop('IDX', axis=1)
        growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(240).apply(lambda x: x.iloc[19::20].mean() / x.iloc[19::20].std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['IDX'] = range(len(value_data))
        value_data['VALUE_SPREAD'] = value_data['IDX'].rolling(n1).apply(lambda x: quantile_definition(x, 'VALUE_SPREAD', value_data))
        value_data = value_data.drop('IDX', axis=1)
        value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        growth_value_data = growth_data.merge(value_data, on=['TRADE_DATE'], how='left').dropna()
        growth_value_data = growth_value_data.set_index('TRADE_DATE').sort_index()
        growth_value_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data.index)
        growth_value_data_disp = growth_value_data.merge(style_index, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data_disp.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data_disp.index)
        growth_value_data_disp = growth_value_data_disp.loc[growth_value_data_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]

        cpi_ppi_disp['CPI-PPI剪刀差_SCORE'] = cpi_ppi_disp['CPI_PPI_DIFF'].apply(lambda x: 1 if x > 0.0 else 0)
        bond_yield_disp['期限利差_SCORE'] = bond_yield_disp['期限利差_Q'].apply(lambda x: 1 if x > 0.5 else 0)
        value_prefer_disp['价值股偏好_SCORE'] = value_prefer_disp['VALUATION_PREFER_Q'].apply(lambda x: 1 if x < 0.5 else 0)
        powerful_stock_ratio_disp['强势股_SCORE'] = powerful_stock_ratio_disp.apply(lambda x: 1 if x['399370'] > x['399371'] else 0, axis=1)
        growth_value_data_disp['因子特征_SCORE'] = growth_value_data_disp.apply(lambda x: 1 if x['GROWTH_CROWDING'] < x['VALUE_CROWDING'] else 0, axis=1)
        style_timing = cpi_ppi_disp[['CPI-PPI剪刀差_SCORE']].merge(bond_yield_disp[['期限利差_SCORE']], left_index=True, right_index=True, how='inner') \
                                                        .merge(value_prefer_disp[['价值股偏好_SCORE']], left_index=True, right_index=True, how='inner') \
                                                        .merge(powerful_stock_ratio_disp[['强势股_SCORE']], left_index=True, right_index=True, how='inner') \
                                                        .merge(growth_value_data_disp[['因子特征_SCORE']], left_index=True, right_index=True, how='inner')
        style_timing['成长_SCORE'] = style_timing.sum(axis=1)
        style_timing['价值_SCORE'] = 5 - style_timing['成长_SCORE']
        return


class OverseasTAA:
    def __init__(self, data_path, start_date, end_date, tracking_end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.tracking_end_date = tracking_end_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.tracking_end_date_hyphen = datetime.strptime(tracking_end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.tracking_end_date)

    def get_signal(self):
        # 罗素1000成长价值走势
        rlg = pd.read_excel('{0}美股成长价值/RLG Index.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlg = rlg.iloc[rlg[rlg[0] == 'Date'].index[0] + 1:, :2]
        rlg.columns = ['TRADE_DATE', 'NAV']
        rlg['TICKER_SYMBOL'] = 'RLG'
        rlg['TRADE_DATE'] = rlg['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlg = rlg.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NAV').sort_index()
        rlv = pd.read_excel('{0}美股成长价值/RLV Index.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlv = rlv.iloc[rlv[rlv[0] == 'Date'].index[0] + 1:, :2]
        rlv.columns = ['TRADE_DATE', 'NAV']
        rlv['TICKER_SYMBOL'] = 'RLV'
        rlv['TRADE_DATE'] = rlv['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlv = rlv.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NAV').sort_index()
        rlgv = rlg.merge(rlv, left_index=True, right_index=True, how='outer').dropna().sort_index()
        rlgv = rlgv.rename(columns={'RLG': '罗素1000成长', 'RLV': '罗素1000价值'})
        rlgv['罗素1000价值/成长'] = rlgv['罗素1000价值'] / rlgv['罗素1000成长']
        rlgv_disp = rlgv[(rlgv.index >= self.start_date) & (rlgv.index <= self.tracking_end_date)]
        rlgv_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), rlgv_disp.index)
        rlgv_disp['罗素1000价值'] = rlgv_disp['罗素1000价值'] / rlgv_disp['罗素1000价值'].iloc[0]
        rlgv_disp['罗素1000成长'] = rlgv_disp['罗素1000成长'] / rlgv_disp['罗素1000成长'].iloc[0]
        rlgv_disp_2022 = rlgv[(rlgv.index >= '20220101') & (rlgv.index <= self.tracking_end_date)]
        rlgv_disp_2022.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), rlgv_disp_2022.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(rlgv_disp.index, rlgv_disp['罗素1000价值'].values, color=line_color_list[0], label='罗素1000价值', linewidth=3)
        ax.plot(rlgv_disp.index, rlgv_disp['罗素1000成长'].values, color=line_color_list[1], label='罗素1000成长', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False)
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}美股成长价值/罗素1000价值成长走势.png'.format(self.data_path))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(rlgv_disp.index, rlgv_disp['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.1), ncol=1, frameon=False)
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}美股成长价值/罗素1000价值成长相对走势.png'.format(self.data_path))
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(rlgv_disp_2022.index, rlgv_disp_2022['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.25), ncol=1, frameon=False)
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}美股成长价值/罗素1000成长价值相对走势_2022.png'.format(self.data_path))

        # 罗素1000成长价值PE走势
        rlg_pe = pd.read_excel('{0}美股成长价值/RLG Index PE.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlg_pe = rlg_pe.iloc[rlg_pe[rlg_pe[0] == 'Date'].index[0] + 1:, :2]
        rlg_pe.columns = ['TRADE_DATE', 'PE']
        rlg_pe['TICKER_SYMBOL'] = 'RLG'
        rlg_pe['TRADE_DATE'] = rlg_pe['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlg_pe = rlg_pe.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PE').sort_index()
        rlv_pe = pd.read_excel('{0}美股成长价值/RLV Index PE.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlv_pe = rlv_pe.iloc[rlv_pe[rlv_pe[0] == 'Date'].index[0] + 1:, :2]
        rlv_pe.columns = ['TRADE_DATE', 'PE']
        rlv_pe['TICKER_SYMBOL'] = 'RLV'
        rlv_pe['TRADE_DATE'] = rlv_pe['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlv_pe = rlv_pe.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PE').sort_index()
        rlgv_pe = rlg_pe.merge(rlv_pe, left_index=True, right_index=True, how='outer').dropna().sort_index()
        rlgv_pe = rlgv_pe.rename(columns={'RLG': '罗素1000成长PE', 'RLV': '罗素1000价值PE'})
        rlgv_pe = rlgv_pe.reset_index()
        rlgv_pe['YEAR_MONTH'] = rlgv_pe['TRADE_DATE'].apply(lambda x: str(x)[:6])
        rlgv_pe_monthly = rlgv_pe.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        rlgv_pe_monthly = rlgv_pe_monthly.set_index('YEAR_MONTH')
        rlgv_pe_monthly_disp = rlgv_pe_monthly[(rlgv_pe_monthly.index >= self.start_date[:6]) & (rlgv_pe_monthly.index <= self.tracking_end_date[:6])]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(rlgv_pe_monthly_disp.index, rlgv_pe_monthly_disp['罗素1000价值PE'].values, color=line_color_list[0], label='罗素1000价值PE', linewidth=2)
        ax.plot(rlgv_pe_monthly_disp.index, rlgv_pe_monthly_disp['罗素1000成长PE'].values, color=line_color_list[1], label='罗素1000成长PE', linewidth=2)
        ax.set_xticks(np.arange(len(rlgv_pe_monthly_disp))[::12])
        ax.set_xticklabels(labels=rlgv_pe_monthly_disp.index.tolist()[::12], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=2, frameon=False)
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}美股成长价值/罗素1000成长价值PE走势.png'.format(self.data_path))

        # 罗素1000成长价值PE分位水平
        rlgv_pe_monthly['IDX'] = range(len(rlgv_pe_monthly))
        rlgv_pe_monthly['罗素1000成长PE分位'] = rlgv_pe_monthly['IDX'].rolling(120).apply(lambda x: quantile_definition(x, '罗素1000成长PE', rlgv_pe_monthly))
        rlgv_pe_monthly['罗素1000价值PE分位'] = rlgv_pe_monthly['IDX'].rolling(120).apply(lambda x: quantile_definition(x, '罗素1000价值PE', rlgv_pe_monthly))
        rlgv_pe_monthly_disp = rlgv_pe_monthly.dropna()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(np.arange(len(rlgv_pe_monthly_disp)), rlgv_pe_monthly_disp['罗素1000成长PE分位'].values, 1.0, label='罗素1000成长PE分位', color=line_color_list[1])
        ax.set_xticks(np.arange(len(rlgv_pe_monthly_disp))[::12])
        ax.set_xticklabels(labels=rlgv_pe_monthly_disp.index.tolist()[::12], rotation=45)
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}美股成长价值/罗素1000成长PE分位水平.png'.format(self.data_path))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(np.arange(len(rlgv_pe_monthly_disp)), rlgv_pe_monthly_disp['罗素1000价值PE分位'].values, 1.0, label='罗素1000价值PE分位', color=line_color_list[0])
        ax.set_xticks(np.arange(len(rlgv_pe_monthly_disp))[::12])
        ax.set_xticklabels(labels=rlgv_pe_monthly_disp.index.tolist()[::12], rotation=45)
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}美股成长价值/罗素1000价值PE分位水平.png'.format(self.data_path))

        # CPI-PPI
        cpi_ppi = w.edb("G0000027,G1132030", self.start_date_hyphen, self.tracking_end_date_hyphen, usedf=True)[1].reset_index()
        cpi_ppi.to_hdf('{0}us_cpi_ppi.hdf'.format(self.data_path), key='table', mode='w')
        cpi_ppi = pd.read_hdf('{0}us_cpi_ppi.hdf'.format(self.data_path), key='table')
        cpi_ppi.columns = ['CALENDAR_DATE', '美国:CPI:同比', '美国:PPI:所有商品:同比:非季调']
        cpi_ppi['CALENDAR_DATE'] = cpi_ppi['CALENDAR_DATE'].apply(lambda x: str(x).replace('-', ''))
        cpi_ppi = cpi_ppi.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        cpi_ppi = cpi_ppi.set_index('TRADE_DATE').sort_index()
        cpi_ppi = cpi_ppi.merge(rlgv, left_index=True, right_index=True, how='left')
        cpi_ppi.to_excel('{0}美股成长价值/cpi_ppi.xlsx'.format(self.data_path))

        # 期限利差
        bond_yield = w.edb("G0000891,G0000886,G0000887", self.start_date_hyphen, self.tracking_end_date_hyphen, usedf=True)[1].reset_index()
        bond_yield.to_hdf('{0}us_bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}us_bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['CALENDAR_DATE', '美国:国债收益率:10年', '美国:国债收益率:1年', '美国:国债收益率:2年']
        bond_yield['CALENDAR_DATE'] = bond_yield['CALENDAR_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        bond_yield['YEAR_MONTH'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x)[:6])
        bond_yield = bond_yield.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last').drop('YEAR_MONTH', axis=1)
        bond_yield = bond_yield.set_index('TRADE_DATE').sort_index()
        bond_yield = bond_yield.merge(rlgv, left_index=True, right_index=True, how='left')
        bond_yield.to_excel('{0}美股成长价值/bond_yield.xlsx'.format(self.data_path))

        # 罗素1000成长价值EPS走势
        rlg_eps = pd.read_excel('{0}美股成长价值/RLG Index EPS.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlg_eps = rlg_eps.iloc[rlg_eps[rlg_eps[0] == 'Date'].index[0] + 1:, :2]
        rlg_eps.columns = ['TRADE_DATE', 'EPS']
        rlg_eps['TICKER_SYMBOL'] = 'RLG'
        rlg_eps['TRADE_DATE'] = rlg_eps['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlg_eps = rlg_eps.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='EPS').sort_index()
        rlv_eps = pd.read_excel('{0}美股成长价值/RLV Index EPS.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlv_eps = rlv_eps.iloc[rlv_eps[rlv_eps[0] == 'Date'].index[0] + 1:, :2]
        rlv_eps.columns = ['TRADE_DATE', 'EPS']
        rlv_eps['TICKER_SYMBOL'] = 'RLV'
        rlv_eps['TRADE_DATE'] = rlv_eps['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlv_eps = rlv_eps.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='EPS').sort_index()
        rlgv_eps = rlg_eps.merge(rlv_eps, left_index=True, right_index=True, how='outer').dropna().sort_index()
        rlgv_eps = rlgv_eps.rename(columns={'RLG': '罗素1000成长EPS', 'RLV': '罗素1000价值EPS'})
        rlgv_eps = rlgv_eps.reset_index()
        rlgv_eps['YEAR_MONTH'] = rlgv_eps['TRADE_DATE'].apply(lambda x: str(x)[:6])
        rlgv_eps_monthly = rlgv_eps.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        rlgv_eps_monthly = rlgv_eps_monthly.set_index('YEAR_MONTH')
        rlgv_eps_monthly_disp = rlgv_eps_monthly[(rlgv_eps_monthly.index >= self.start_date[:6]) & (rlgv_eps_monthly.index <= self.tracking_end_date[:6])]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(rlgv_eps_monthly_disp.index, rlgv_eps_monthly_disp['罗素1000价值EPS'].values, color=line_color_list[0], label='罗素1000价值EPS', linewidth=2)
        ax.plot(rlgv_eps_monthly_disp.index, rlgv_eps_monthly_disp['罗素1000成长EPS'].values, color=line_color_list[1], label='罗素1000成长EPS', linewidth=2)
        ax.set_xticks(np.arange(len(rlgv_eps_monthly_disp))[::12])
        ax.set_xticklabels(labels=rlgv_eps_monthly_disp.index.tolist()[::12], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=2, frameon=False)
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}美股成长价值/罗素1000成长价值EPS走势.png'.format(self.data_path))

        # TIPS
        tips = w.edb("G0005428", self.start_date_hyphen, self.tracking_end_date_hyphen, usedf=True)[1].reset_index()
        tips.to_hdf('{0}us_tips.hdf'.format(self.data_path), key='table', mode='w')
        tips = pd.read_hdf('{0}us_tips.hdf'.format(self.data_path), key='table')
        tips.columns = ['CALENDAR_DATE', '美国:国债收益率:通胀指数国债(TIPS):10年']
        tips['CALENDAR_DATE'] = tips['CALENDAR_DATE'].apply(lambda x: str(x).replace('-', ''))
        tips = tips.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        tips['YEAR_MONTH'] = tips['TRADE_DATE'].apply(lambda x: str(x)[:6])
        tips = tips.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last').drop('YEAR_MONTH', axis=1)
        tips = tips.set_index('TRADE_DATE').sort_index()
        tips = tips.merge(rlgv, left_index=True, right_index=True, how='left')
        tips.to_excel('{0}美股成长价值/tips.xlsx'.format(self.data_path))
        return

    def get_test(self):
        # 罗素1000成长价值走势
        rlg = pd.read_excel('{0}美股成长价值/RLG Index.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlg = rlg.iloc[rlg[rlg[0] == 'Date'].index[0] + 1:, :2]
        rlg.columns = ['TRADE_DATE', 'NAV']
        rlg['TICKER_SYMBOL'] = 'RLG'
        rlg['TRADE_DATE'] = rlg['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlg = rlg.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NAV').sort_index()
        rlv = pd.read_excel('{0}美股成长价值/RLV Index.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlv = rlv.iloc[rlv[rlv[0] == 'Date'].index[0] + 1:, :2]
        rlv.columns = ['TRADE_DATE', 'NAV']
        rlv['TICKER_SYMBOL'] = 'RLV'
        rlv['TRADE_DATE'] = rlv['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlv = rlv.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NAV').sort_index()
        rlgv = rlg.merge(rlv, left_index=True, right_index=True, how='outer').dropna().sort_index()
        rlgv = rlgv.rename(columns={'RLG': '罗素1000成长', 'RLV': '罗素1000价值'})
        rlgv['罗素1000价值/成长'] = rlgv['罗素1000价值'] / rlgv['罗素1000成长']
        rlgv = rlgv.reset_index()
        rlgv['YEAR_MONTH'] = rlgv['TRADE_DATE'].apply(lambda x: str(x)[:6])
        rlgv_monthly = rlgv.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        rlgv_monthly = rlgv_monthly.set_index('YEAR_MONTH').drop('TRADE_DATE', axis=1)
        rlgv_monthly = rlgv_monthly[(rlgv_monthly.index >= self.start_date[:6]) & (rlgv_monthly.index <= self.end_date[:6])]

        # 罗素1000成长价值PE走势
        rlg_pe = pd.read_excel('{0}美股成长价值/RLG Index PE.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlg_pe = rlg_pe.iloc[rlg_pe[rlg_pe[0] == 'Date'].index[0] + 1:, [0, 2]]
        rlg_pe.columns = ['TRADE_DATE', 'PE']
        rlg_pe['TICKER_SYMBOL'] = 'RLG'
        rlg_pe['TRADE_DATE'] = rlg_pe['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlg_pe = rlg_pe.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PE').sort_index()
        rlv_pe = pd.read_excel('{0}美股成长价值/RLV Index PE.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlv_pe = rlv_pe.iloc[rlv_pe[rlv_pe[0] == 'Date'].index[0] + 1:, [0, 2]]
        rlv_pe.columns = ['TRADE_DATE', 'PE']
        rlv_pe['TICKER_SYMBOL'] = 'RLV'
        rlv_pe['TRADE_DATE'] = rlv_pe['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlv_pe = rlv_pe.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PE').sort_index()
        rlgv_pe = rlg_pe.merge(rlv_pe, left_index=True, right_index=True, how='outer').dropna().sort_index()
        rlgv_pe = rlgv_pe.rename(columns={'RLG': '罗素1000成长PE', 'RLV': '罗素1000价值PE'})
        rlgv_pe['罗素1000价值/成长PE'] = rlgv_pe['罗素1000价值PE'] / rlgv_pe['罗素1000成长PE']
        rlgv_pe = rlgv_pe.reset_index()
        rlgv_pe['YEAR_MONTH'] = rlgv_pe['TRADE_DATE'].apply(lambda x: str(x)[:6])
        rlgv_pe_monthly = rlgv_pe.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        rlgv_pe_monthly = rlgv_pe_monthly.set_index('YEAR_MONTH').drop('TRADE_DATE', axis=1)
        rlgv_pe_monthly = rlgv_pe_monthly[(rlgv_pe_monthly.index >= self.start_date[:6]) & (rlgv_pe_monthly.index <= self.end_date[:6])]
        rlgv_pe_monthly = rlgv_pe_monthly.merge(rlgv_monthly, left_index=True, right_index=True, how='left')
        rlgv_pe_monthly = rlgv_pe_monthly.dropna()
        rlgv_pe_monthly_ori = rlgv_pe_monthly.copy(deep=True)

        # rlgv_pe_monthly_q = rlgv_pe_monthly_ori.copy(deep=True)
        # for n in [1, 3, 5, 10]:
        #     rlgv_pe_monthly = rlgv_pe_monthly_ori.copy(deep=True)
        #     rlgv_pe_monthly['IDX'] = range(len(rlgv_pe_monthly))
        #     rlgv_pe_monthly_q['罗素1000成长滚动{0}年PE分位'.format(n)] = rlgv_pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, '罗素1000成长PE', rlgv_pe_monthly))
        #     rlgv_pe_monthly_q['罗素1000价值滚动{0}年PE分位'.format(n)] = rlgv_pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, '罗素1000价值PE', rlgv_pe_monthly))
        # rlgv_pe_monthly_q.to_excel('{0}/美股成长价值/rlgv_pe_monthly_q1.xlsx'.format(self.data_path))

        rlgv_pe_monthly = rlgv_pe_monthly_ori.copy(deep=True)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['罗素1000价值/成长PE'].values, color=line_color_list[0], label='罗素1000价值/成长PE', linewidth=2)
        ax_r.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
        ax.set_xticks(np.arange(len(rlgv_pe_monthly))[::18])
        ax.set_xticklabels(labels=rlgv_pe_monthly.index.tolist()[::18])
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('罗素1000价值/成长PE与罗素1000价值/成长表现', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}/美股成长价值/比值/罗素1000价值成长PE.png'.format(self.data_path))

        for n in [1, 3, 5, 10]:
            rlgv_pe_monthly = rlgv_pe_monthly_ori.copy(deep=True)
            rlgv_pe_monthly['IDX'] = range(len(rlgv_pe_monthly))
            rlgv_pe_monthly['罗素1000成长PE分位'] = rlgv_pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, '罗素1000成长PE', rlgv_pe_monthly))
            rlgv_pe_monthly['罗素1000价值PE分位'] = rlgv_pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, '罗素1000价值PE', rlgv_pe_monthly))

            rlgv_pe_monthly['罗素1000价值/成长PE分位'] = rlgv_pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, '罗素1000价值/成长PE', rlgv_pe_monthly))
            rlgv_pe_monthly['罗素1000价值/成长PE分类'] = rlgv_pe_monthly.apply(lambda x: '价值' if x['罗素1000价值/成长PE分位'] < 0.2 else '成长' if x['罗素1000价值/成长PE分位'] > 0.8 else '均衡', axis=1)
            rlgv_pe_monthly['罗素1000价值/成长PE仓位'] = rlgv_pe_monthly.apply(lambda x: 1.0 if x['罗素1000价值/成长PE分位'] < 0.2 else 0.0 if x['罗素1000价值/成长PE分位'] > 0.8 else 0.5, axis=1)
            rlgv_pe_monthly = rlgv_pe_monthly.dropna()
            rlgv_pe_monthly['FORMARD_RET'] = rlgv_pe_monthly['罗素1000价值/成长'].pct_change(1).shift(-1)
            rlgv_pe_monthly['ACTUAL_MARK'] = rlgv_pe_monthly.apply(lambda x: 1.0 if x['FORMARD_RET'] > 0.02 else 0.0 if x['FORMARD_RET'] < -0.02 else 0.5, axis=1)
            rlgv_pe_monthly['SIGNAL_MARK'] = rlgv_pe_monthly.apply(lambda x: 1.0 if x['罗素1000价值/成长PE分类'] == '价值' else 0.0 if x['罗素1000价值/成长PE分类'] == '成长' else 0.5, axis=1)
            print('罗素1000价值/成长PE过去{0}年估值分位区间'.format(n), len(rlgv_pe_monthly[rlgv_pe_monthly['SIGNAL_MARK'] == rlgv_pe_monthly['ACTUAL_MARK']]) / float(len(rlgv_pe_monthly.dropna())))

            rlgv_pe_monthly_1 = rlgv_pe_monthly.copy(deep=True)
            rlgv_pe_monthly_2 = rlgv_pe_monthly.copy(deep=True)
            rlgv_pe_monthly_3 = rlgv_pe_monthly.copy(deep=True)
            rlgv_pe_monthly_1['MARK'] = rlgv_pe_monthly_1.apply(lambda x: 1.0 if x['罗素1000价值/成长PE分类'] == '价值' else 0, axis=1)
            rlgv_pe_monthly_2['MARK'] = rlgv_pe_monthly_2.apply(lambda x: 1.0 if x['罗素1000价值/成长PE分类'] == '成长' else 0, axis=1)
            rlgv_pe_monthly_3['MARK'] = rlgv_pe_monthly_3.apply(lambda x: 1.0 if x['罗素1000价值/成长PE分类'] == '均衡' else 0, axis=1)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax_r = ax.twinx()
            ax.bar(rlgv_pe_monthly_1.index, rlgv_pe_monthly_1['MARK'].values, color=line_color_list[0], alpha=0.5, label='价值')
            ax.bar(rlgv_pe_monthly_2.index, rlgv_pe_monthly_2['MARK'].values, color=line_color_list[1], alpha=0.5, label='成长')
            ax.bar(rlgv_pe_monthly_3.index, rlgv_pe_monthly_3['MARK'].values, color=line_color_list[2], alpha=0.5, label='均衡')
            ax_r.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
            ax.set_xticks(np.arange(len(rlgv_pe_monthly))[::18])
            ax.set_xticklabels(labels=rlgv_pe_monthly.index.tolist()[::18])
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax_r.get_legend_handles_labels()
            plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7, frameon=False)
            plt.title('罗素1000价值/成长PE过去{0}年估值分位区间'.format(n), fontdict={'weight': 'bold', 'size': 16})
            plt.tight_layout()
            sns.despine(top=True, right=False, left=False, bottom=False)
            plt.savefig('{0}/美股成长价值/比值/罗素1000价值成长PE过去{1}年估值分位区间.png'.format(self.data_path, n))

            rlgv_pe_monthly['价值仓位'] = rlgv_pe_monthly.apply(lambda x: 1.0 if x['罗素1000价值/成长PE分位'] < 0.2 else 0.0 if x['罗素1000价值/成长PE分位'] > 0.8 else 0.5, axis=1)
            rlgv_pe_monthly['成长仓位'] = rlgv_pe_monthly['价值仓位'].apply(lambda x: 1.0 - x)
            rlgv_pe_monthly['价值月度收益率'] = rlgv_pe_monthly['罗素1000价值'].pct_change(1).shift(-1)
            rlgv_pe_monthly['成长月度收益率'] = rlgv_pe_monthly['罗素1000成长'].pct_change(1).shift(-1)
            rlgv_pe_monthly['价值月度收益率'].iloc[0] = 0.0
            rlgv_pe_monthly['成长月度收益率'].iloc[0] = 0.0
            rlgv_pe_monthly['平均月度收益率'] = 0.5 * rlgv_pe_monthly['成长月度收益率'] + 0.5 * rlgv_pe_monthly['价值月度收益率']
            rlgv_pe_monthly['策略月度收益率'] = rlgv_pe_monthly['价值仓位'] * rlgv_pe_monthly['价值月度收益率'] + rlgv_pe_monthly['成长仓位'] * rlgv_pe_monthly['成长月度收益率']
            rlgv_pe_monthly['基准组合净值'] = (1 + rlgv_pe_monthly['平均月度收益率']).cumprod()
            rlgv_pe_monthly['策略组合净值'] = (1 + rlgv_pe_monthly['策略月度收益率']).cumprod()
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['策略组合净值'].values, color=line_color_list[0], label='策略组合净值', linewidth=2, linestyle='-')
            ax.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['基准组合净值'].values, color=line_color_list[2], label='基准组合净值', linewidth=2, linestyle='-')
            ax.set_xticks(np.arange(len(rlgv_pe_monthly))[::18])
            ax.set_xticklabels(labels=rlgv_pe_monthly.index.tolist()[::18])
            plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
            plt.title('罗素1000价值/成长PE过去{0}年估值分位区间择时策略'.format(n), fontdict={'weight': 'bold', 'size': 16})
            plt.tight_layout()
            sns.despine(top=True, right=False, left=False, bottom=False)
            plt.savefig('{0}/美股成长价值/比值/罗素1000价值成长PE过去{1}年估值分位区间择时策略.png'.format(self.data_path, n))
            performance = get_performance(rlgv_pe_monthly[['策略组合净值', '基准组合净值']], 12)
            performance.to_excel('{0}/美股成长价值/比值/罗素1000价值成长PE过去{1}年估值分位区间择时策略表现.xlsx'.format(self.data_path, n))

            q_type = '五分组'
            # rlgv_pe_monthly['罗素1000价值PE分位档位'] = rlgv_pe_monthly['罗素1000价值PE分位'].apply(lambda x: '0%-10%' if x >= 0.0 and x < 0.1 else '10%-20%' if x >= 0.1 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-90%' if x >= 0.8 and x < 0.9 else '90%-100%')
            # rlgv_pe_monthly['罗素1000成长PE分位档位'] = rlgv_pe_monthly['罗素1000成长PE分位'].apply(lambda x: '0%-10%' if x >= 0.0 and x < 0.1 else '10%-20%' if x >= 0.1 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-90%' if x >= 0.8 and x < 0.9 else '90%-100%')
            # rlgv_pe_monthly['价值仓位'] = rlgv_pe_monthly['罗素1000价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-10%' else 0.8 if x == '10%-20%' else 0.6 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.4 if x == '60%-80%' else 0.2 if x == '80%-90%' else 0.0)
            # rlgv_pe_monthly['成长仓位'] = rlgv_pe_monthly['罗素1000成长PE分位档位'].apply(lambda x: 1.0 if x == '0%-10%' else 0.8 if x == '10%-20%' else 0.6 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.4 if x == '60%-80%' else 0.2 if x == '80%-90%' else 0.0)
            rlgv_pe_monthly['罗素1000价值PE分位档位'] = rlgv_pe_monthly['罗素1000价值PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-100%')
            rlgv_pe_monthly['罗素1000成长PE分位档位'] = rlgv_pe_monthly['罗素1000成长PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-100%')
            rlgv_pe_monthly['价值仓位'] = rlgv_pe_monthly['罗素1000价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.75 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.25 if x == '60%-80%' else 0.0)
            rlgv_pe_monthly['成长仓位'] = rlgv_pe_monthly['罗素1000成长PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.75 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.25 if x == '60%-80%' else 0.0)
            # rlgv_pe_monthly['罗素1000价值PE分位档位'] = rlgv_pe_monthly['罗素1000价值PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-80%' if x >= 0.2 and x <= 0.8 else '80%-100%')
            # rlgv_pe_monthly['罗素1000成长PE分位档位'] = rlgv_pe_monthly['罗素1000成长PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-80%' if x >= 0.2 and x <= 0.8 else '80%-100%')
            # rlgv_pe_monthly['价值仓位'] = rlgv_pe_monthly['罗素1000价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.5 if x == '20%-80%' else 0.0)
            # rlgv_pe_monthly['成长仓位'] = rlgv_pe_monthly['罗素1000成长PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.5 if x == '20%-80%' else 0.0)
            for style in ['价值', '成长']:
                rlgv_pe_monthly[style + '未来1月收益率'] = rlgv_pe_monthly['罗素1000' + style].pct_change(1).shift(-1)
                rlgv_pe_monthly[style + '未来3月收益率'] = rlgv_pe_monthly['罗素1000' + style].pct_change(3).shift(-3)
                rlgv_pe_monthly[style + '未来6月收益率'] = rlgv_pe_monthly['罗素1000' + style].pct_change(6).shift(-6)
                rlgv_pe_monthly[style + '未来1年收益率'] = rlgv_pe_monthly['罗素1000' + style].pct_change(12).shift(-12)
                rlgv_pe_monthly[style + '未来2年收益率'] = rlgv_pe_monthly['罗素1000' + style].pct_change(24).shift(-24)
                rlgv_pe_monthly[style + '未来3年收益率'] = rlgv_pe_monthly['罗素1000' + style].pct_change(36).shift(-36)
                rlgv_pe_ret = rlgv_pe_monthly[['罗素1000' + style + 'PE分位档位', style + '未来1月收益率', style + '未来3月收益率', style + '未来6月收益率', style + '未来1年收益率', style + '未来2年收益率', style + '未来3年收益率']].groupby('罗素1000' + style + 'PE分位档位').mean()
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(np.arange(len(rlgv_pe_ret)), rlgv_pe_ret[style + '未来1月收益率'].values, color=line_color_list[0], label='未来1月收益率', linewidth=2, linestyle='-')
                ax.plot(np.arange(len(rlgv_pe_ret)), rlgv_pe_ret[style + '未来3月收益率'].values, color=line_color_list[1], label='未来3月收益率', linewidth=2, linestyle='-')
                ax.plot(np.arange(len(rlgv_pe_ret)), rlgv_pe_ret[style + '未来6月收益率'].values, color=line_color_list[2], label='未来6月收益率', linewidth=2, linestyle='-')
                ax.plot(np.arange(len(rlgv_pe_ret)), rlgv_pe_ret[style + '未来1年收益率'].values, color=line_color_list[3], label='未来1年收益率', linewidth=2, linestyle='-')
                # ax.plot(np.arange(len(rlgv_pe_ret)), rlgv_pe_ret[style + '未来2年收益率'].values, color=line_color_list[1], label='未来2年收益率', linewidth=2, linestyle='--')
                # ax.plot(np.arange(len(rlgv_pe_ret)), rlgv_pe_ret[style + '未来3年收益率'].values, color=line_color_list[2], label='未来3年收益率', linewidth=2, linestyle='--')
                ax.set_xticks(np.arange(len(rlgv_pe_ret)))
                ax.set_xticklabels(labels=rlgv_pe_ret.index.tolist())
                ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
                plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6, frameon=False)
                plt.xlabel('罗素1000{0}估值分位区间'.format(style))
                plt.ylabel('罗素1000{0}持有期收益率'.format(style))
                plt.title('罗素1000{0}不同估值分位区间的平均持有期收益率统计'.format(style), fontdict={'weight': 'bold', 'size': 16})
                plt.tight_layout()
                sns.despine(top=True, right=False, left=False, bottom=False)
                plt.savefig('{0}/美股成长价值/pe/{1}/罗素1000{2}过去{3}年估值分位区间的平均持有期收益率统计.png'.format(self.data_path, q_type, style, n))

                rlgv_pe_monthly['价值月度收益率'] = rlgv_pe_monthly['罗素1000价值'].pct_change(1).shift(-1)
                rlgv_pe_monthly['成长月度收益率'] = rlgv_pe_monthly['罗素1000成长'].pct_change(1).shift(-1)
                rlgv_pe_monthly['价值月度收益率'].iloc[0] = 0.0
                rlgv_pe_monthly['成长月度收益率'].iloc[0] = 0.0
                rlgv_pe_monthly['平均月度收益率'] = 0.5 * rlgv_pe_monthly['成长月度收益率'] + 0.5 * rlgv_pe_monthly['价值月度收益率']
                if style == '价值':
                    rlgv_pe_monthly['策略月度收益率'] = rlgv_pe_monthly.apply(lambda x: x['价值仓位'] * x['价值月度收益率'] + (1 - x['价值仓位']) * x['成长月度收益率'], axis=1)
                else:
                    rlgv_pe_monthly['策略月度收益率'] = rlgv_pe_monthly.apply(lambda x: x['成长仓位'] * x['成长月度收益率'] + (1 - x['成长仓位']) * x['价值月度收益率'], axis=1)
                rlgv_pe_monthly['基准组合净值'] = (1 + rlgv_pe_monthly['平均月度收益率']).cumprod()
                rlgv_pe_monthly['策略组合净值'] = (1 + rlgv_pe_monthly['策略月度收益率']).cumprod()
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['策略组合净值'].values, color=line_color_list[0], label='策略组合净值', linewidth=2, linestyle='-')
                ax.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['基准组合净值'].values, color=line_color_list[2], label='基准组合净值', linewidth=2, linestyle='-')
                ax.set_xticks(np.arange(len(rlgv_pe_monthly))[::18])
                ax.set_xticklabels(labels=rlgv_pe_monthly.index.tolist()[::18])
                plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
                plt.title('罗素1000{0}过去{1}年估值分位择时策略'.format(style, n), fontdict={'weight': 'bold', 'size': 16})
                plt.tight_layout()
                sns.despine(top=True, right=False, left=False, bottom=False)
                plt.savefig('{0}/美股成长价值/pe/{1}/罗素1000{2}过去{3}年估值分位择时策略.png'.format(self.data_path, q_type, style, n))
                performance = get_performance(rlgv_pe_monthly[['策略组合净值', '基准组合净值']], 12)
                performance.to_excel('{0}/美股成长价值/pe/{1}/罗素1000{2}过去{3}年估值分位择时策略表现.xlsx'.format(self.data_path, q_type, style, n))

                if q_type == '七分组':
                    rlgv_pe_monthly_1 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_2 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_3 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_4 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_5 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_6 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_7 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_1[style + 'MARK'] = rlgv_pe_monthly_1.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '0%-10%' else 0, axis=1)
                    rlgv_pe_monthly_2[style + 'MARK'] = rlgv_pe_monthly_2.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '10%-20%' else 0, axis=1)
                    rlgv_pe_monthly_3[style + 'MARK'] = rlgv_pe_monthly_3.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '20%-40%' else 0, axis=1)
                    rlgv_pe_monthly_4[style + 'MARK'] = rlgv_pe_monthly_4.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '40%-60%' else 0, axis=1)
                    rlgv_pe_monthly_5[style + 'MARK'] = rlgv_pe_monthly_5.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '60%-80%' else 0, axis=1)
                    rlgv_pe_monthly_6[style + 'MARK'] = rlgv_pe_monthly_6.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '80%-90%' else 0, axis=1)
                    rlgv_pe_monthly_7[style + 'MARK'] = rlgv_pe_monthly_7.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '90%-100%' else 0, axis=1)
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax_r = ax.twinx()
                    ax.bar(rlgv_pe_monthly_1.index, rlgv_pe_monthly_1[style + 'MARK'].values, color=line_color_list[0], alpha=0.8, label='0%-10%')
                    ax.bar(rlgv_pe_monthly_2.index, rlgv_pe_monthly_2[style + 'MARK'].values, color=line_color_list[0], alpha=0.5, label='10%-20%')
                    ax.bar(rlgv_pe_monthly_3.index, rlgv_pe_monthly_3[style + 'MARK'].values, color=line_color_list[4], alpha=0.5, label='20%-40%')
                    ax.bar(rlgv_pe_monthly_4.index, rlgv_pe_monthly_4[style + 'MARK'].values, color=line_color_list[2], alpha=0.5, label='40%-60%')
                    ax.bar(rlgv_pe_monthly_5.index, rlgv_pe_monthly_5[style + 'MARK'].values, color=line_color_list[1], alpha=0.5, label='60%-80%')
                    ax.bar(rlgv_pe_monthly_6.index, rlgv_pe_monthly_6[style + 'MARK'].values, color=line_color_list[3], alpha=0.5, label='80%-90%')
                    ax.bar(rlgv_pe_monthly_7.index, rlgv_pe_monthly_7[style + 'MARK'].values, color=line_color_list[3], alpha=0.8, label='90%-100%')
                    ax_r.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
                    ax.set_xticks(np.arange(len(rlgv_pe_monthly))[::18])
                    ax.set_xticklabels(labels=rlgv_pe_monthly.index.tolist()[::18])
                    h1, l1 = ax.get_legend_handles_labels()
                    h2, l2 = ax_r.get_legend_handles_labels()
                    plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=8, frameon=False)
                    plt.title('罗素1000{0}过去{1}年估值分位对应区间'.format(style, n), fontdict={'weight': 'bold', 'size': 16})
                    plt.tight_layout()
                    sns.despine(top=True, right=False, left=False, bottom=False)
                    plt.savefig('{0}/美股成长价值/pe/{1}/罗素1000{2}过去{3}年估值分位对应区间.png'.format(self.data_path, q_type, style, n))

                if q_type == '五分组':
                    rlgv_pe_monthly_1 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_2 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_3 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_4 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_5 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_1[style + 'MARK'] = rlgv_pe_monthly_1.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '0%-20%' else 0, axis=1)
                    rlgv_pe_monthly_2[style + 'MARK'] = rlgv_pe_monthly_2.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '20%-40%' else 0, axis=1)
                    rlgv_pe_monthly_3[style + 'MARK'] = rlgv_pe_monthly_3.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '40%-60%' else 0, axis=1)
                    rlgv_pe_monthly_4[style + 'MARK'] = rlgv_pe_monthly_4.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '60%-80%' else 0, axis=1)
                    rlgv_pe_monthly_5[style + 'MARK'] = rlgv_pe_monthly_5.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '80%-100%' else 0, axis=1)
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax_r = ax.twinx()
                    ax.bar(rlgv_pe_monthly_1.index, rlgv_pe_monthly_1[style + 'MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
                    ax.bar(rlgv_pe_monthly_2.index, rlgv_pe_monthly_2[style + 'MARK'].values, color=line_color_list[4], alpha=0.5, label='20%-40%')
                    ax.bar(rlgv_pe_monthly_3.index, rlgv_pe_monthly_3[style + 'MARK'].values, color=line_color_list[2], alpha=0.5, label='40%-60%')
                    ax.bar(rlgv_pe_monthly_4.index, rlgv_pe_monthly_4[style + 'MARK'].values, color=line_color_list[1], alpha=0.5, label='60%-80%')
                    ax.bar(rlgv_pe_monthly_5.index, rlgv_pe_monthly_5[style + 'MARK'].values, color=line_color_list[3], alpha=0.5, label='80%-100%')
                    ax_r.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
                    ax.set_xticks(np.arange(len(rlgv_pe_monthly))[::18])
                    ax.set_xticklabels(labels=rlgv_pe_monthly.index.tolist()[::18])
                    h1, l1 = ax.get_legend_handles_labels()
                    h2, l2 = ax_r.get_legend_handles_labels()
                    plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7, frameon=False)
                    plt.title('罗素1000{0}过去{1}年估值分位对应区间'.format(style, n), fontdict={'weight': 'bold', 'size': 16})
                    plt.tight_layout()
                    sns.despine(top=True, right=False, left=False, bottom=False)
                    plt.savefig('{0}/美股成长价值/pe/{1}/罗素1000{2}过去{3}年估值分位对应区间.png'.format(self.data_path, q_type, style, n))

                if q_type == '三分组':
                    rlgv_pe_monthly_1 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_2 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_3 = rlgv_pe_monthly.copy(deep=True)
                    rlgv_pe_monthly_1[style + 'MARK'] = rlgv_pe_monthly_1.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '0%-20%' else 0, axis=1)
                    rlgv_pe_monthly_2[style + 'MARK'] = rlgv_pe_monthly_2.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '20%-80%' else 0, axis=1)
                    rlgv_pe_monthly_3[style + 'MARK'] = rlgv_pe_monthly_3.apply(lambda x: max(rlgv_pe_monthly['罗素1000价值/成长PE']) if x['罗素1000' + style + 'PE分位档位'] == '80%-100%' else 0, axis=1)
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax_r = ax.twinx()
                    ax.bar(rlgv_pe_monthly_1.index, rlgv_pe_monthly_1[style + 'MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
                    ax.bar(rlgv_pe_monthly_2.index, rlgv_pe_monthly_2[style + 'MARK'].values, color=line_color_list[2], alpha=0.5, label='20%-80%')
                    ax.bar(rlgv_pe_monthly_3.index, rlgv_pe_monthly_3[style + 'MARK'].values, color=line_color_list[1], alpha=0.5, label='80%-100%')
                    ax_r.plot(np.arange(len(rlgv_pe_monthly)), rlgv_pe_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
                    ax.set_xticks(np.arange(len(rlgv_pe_monthly))[::18])
                    ax.set_xticklabels(labels=rlgv_pe_monthly.index.tolist()[::18])
                    h1, l1 = ax.get_legend_handles_labels()
                    h2, l2 = ax_r.get_legend_handles_labels()
                    plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
                    plt.title('罗素1000{0}过去{1}年估值分位对应区间'.format(style, n), fontdict={'weight': 'bold', 'size': 16})
                    plt.tight_layout()
                    sns.despine(top=True, right=False, left=False, bottom=False)
                    plt.savefig('{0}/美股成长价值/pe/{1}/罗素1000{2}过去{3}年估值分位对应区间.png'.format(self.data_path, q_type, style, n))


        # 罗素1000成长价值EPS走势
        eps_type = 'best_eps_rolling'
        rlg_eps = pd.read_excel('{0}美股成长价值/RLG Index EPS 2.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlg_eps = rlg_eps.iloc[rlg_eps[rlg_eps[0] == 'Date'].index[0] + 1:, [0, 2]]
        rlg_eps.columns = ['TRADE_DATE', 'EPS']
        rlg_eps['TICKER_SYMBOL'] = 'RLG'
        rlg_eps['TRADE_DATE'] = rlg_eps['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlg_eps = rlg_eps.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='EPS').sort_index()
        rlv_eps = pd.read_excel('{0}美股成长价值/RLV Index EPS 2.xlsx'.format(data_path), header=None).reset_index(drop=True)
        rlv_eps = rlv_eps.iloc[rlv_eps[rlv_eps[0] == 'Date'].index[0] + 1:, [0, 2]]
        rlv_eps.columns = ['TRADE_DATE', 'EPS']
        rlv_eps['TICKER_SYMBOL'] = 'RLV'
        rlv_eps['TRADE_DATE'] = rlv_eps['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        rlv_eps = rlv_eps.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='EPS').sort_index()
        rlgv_eps = rlg_eps.merge(rlv_eps, left_index=True, right_index=True, how='outer').dropna().sort_index()
        rlgv_eps = rlgv_eps.rename(columns={'RLG': '罗素1000成长EPS', 'RLV': '罗素1000价值EPS'})
        rlgv_eps = rlgv_eps.reset_index()
        rlgv_eps['YEAR_MONTH'] = rlgv_eps['TRADE_DATE'].apply(lambda x: str(x)[:6])
        rlgv_eps_monthly = rlgv_eps.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        rlgv_eps_monthly = rlgv_eps_monthly.set_index('YEAR_MONTH').drop('TRADE_DATE', axis=1)
        rlgv_eps_monthly = rlgv_eps_monthly[(rlgv_eps_monthly.index >= self.start_date[:6]) & (rlgv_eps_monthly.index <= self.end_date[:6])]
        rlgv_eps_monthly = rlgv_eps_monthly.merge(rlgv_monthly, left_index=True, right_index=True, how='left')
        rlgv_eps_monthly['罗素1000价值EPS'] = rlgv_eps_monthly['罗素1000价值EPS'].rolling(12).mean()
        rlgv_eps_monthly['罗素1000成长EPS'] = rlgv_eps_monthly['罗素1000成长EPS'].rolling(12).mean()
        rlgv_eps_monthly['罗素1000价值EPS同比'] = rlgv_eps_monthly['罗素1000价值EPS'].pct_change(12)
        rlgv_eps_monthly['罗素1000成长EPS同比'] = rlgv_eps_monthly['罗素1000成长EPS'].pct_change(12)
        rlgv_eps_monthly['罗素1000价值EPS同比'] = filter_extreme_mad(rlgv_eps_monthly['罗素1000价值EPS同比'])
        rlgv_eps_monthly['罗素1000成长EPS同比'] = filter_extreme_mad(rlgv_eps_monthly['罗素1000成长EPS同比'])
        rlgv_eps_monthly = rlgv_eps_monthly.dropna()
        rlgv_eps_monthly_ori = rlgv_eps_monthly.copy(deep=True)

        rlgv_eps_monthly = rlgv_eps_monthly_ori.copy(deep=True)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['罗素1000价值EPS同比'].values, color=line_color_list[0], label='罗素1000价值EPS同比', linewidth=2)
        ax.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['罗素1000成长EPS同比'].values, color=line_color_list[1], label='罗素1000成长EPS同比', linewidth=2)
        ax_r.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
        ax.set_xticks(np.arange(len(rlgv_eps_monthly))[::18])
        ax.set_xticklabels(labels=rlgv_eps_monthly.index.tolist()[::18])
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('EPS同比与罗素1000价值/成长表现', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}/美股成长价值/{1}/EPS同比.png'.format(self.data_path, eps_type))

        rlgv_eps_monthly = rlgv_eps_monthly_ori.copy(deep=True)
        rlgv_eps_monthly['FORMARD_RET'] = rlgv_eps_monthly['罗素1000价值/成长'].pct_change(1).shift(-1)
        rlgv_eps_monthly['ACTUAL_MARK'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['FORMARD_RET'] >= 0 else 0, axis=1)
        rlgv_eps_monthly['SIGNAL_MARK'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['罗素1000价值EPS同比'] >= x['罗素1000成长EPS同比'] else 0, axis=1)
        print('EPS同比高低区间：', len(rlgv_eps_monthly[rlgv_eps_monthly['SIGNAL_MARK'] == rlgv_eps_monthly['ACTUAL_MARK']]) / float(len(rlgv_eps_monthly.dropna())))
        rlgv_eps_monthly_1 = rlgv_eps_monthly.copy(deep=True)
        rlgv_eps_monthly_2 = rlgv_eps_monthly.copy(deep=True)
        rlgv_eps_monthly_1['MARK'] = rlgv_eps_monthly_1.apply(lambda x: 1.0 if x['罗素1000价值EPS同比'] >= x['罗素1000成长EPS同比'] else 0, axis=1)
        rlgv_eps_monthly_2['MARK'] = rlgv_eps_monthly_2.apply(lambda x: 1.0 if x['罗素1000价值EPS同比'] < x['罗素1000成长EPS同比'] else 0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.bar(rlgv_eps_monthly_1.index, rlgv_eps_monthly_1['MARK'].values, color=line_color_list[0], alpha=0.5, label='罗素1000价值EPS同比高')
        ax.bar(rlgv_eps_monthly_2.index, rlgv_eps_monthly_2['MARK'].values, color=line_color_list[1], alpha=0.5, label='罗素1000成长EPS同比高')
        ax_r.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
        ax.set_xticks(np.arange(len(rlgv_eps_monthly))[::18])
        ax.set_xticklabels(labels=rlgv_eps_monthly.index.tolist()[::18])
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('EPS同比高低区间与罗素1000价值/成长表现', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}/美股成长价值/{1}/EPS同比高低区间.png'.format(self.data_path, eps_type))

        rlgv_eps_monthly = rlgv_eps_monthly_ori.copy(deep=True)
        rlgv_eps_monthly['价值仓位'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['罗素1000价值EPS同比'] >= x['罗素1000成长EPS同比'] else 0, axis=1)
        rlgv_eps_monthly['成长仓位'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['罗素1000价值EPS同比'] < x['罗素1000成长EPS同比'] else 0, axis=1)
        rlgv_eps_monthly['价值月度收益率'] = rlgv_eps_monthly['罗素1000价值'].pct_change(1).shift(-1)
        rlgv_eps_monthly['成长月度收益率'] = rlgv_eps_monthly['罗素1000成长'].pct_change(1).shift(-1)
        rlgv_eps_monthly['价值月度收益率'].iloc[0] = 0.0
        rlgv_eps_monthly['成长月度收益率'].iloc[0] = 0.0
        rlgv_eps_monthly['平均月度收益率'] = 0.5 * rlgv_eps_monthly['成长月度收益率'] + 0.5 * rlgv_eps_monthly['价值月度收益率']
        rlgv_eps_monthly['策略月度收益率'] = rlgv_eps_monthly['价值仓位'] * rlgv_eps_monthly['价值月度收益率'] + rlgv_eps_monthly['成长仓位'] * rlgv_eps_monthly['成长月度收益率']
        rlgv_eps_monthly['基准组合净值'] = (1 + rlgv_eps_monthly['平均月度收益率']).cumprod()
        rlgv_eps_monthly['策略组合净值'] = (1 + rlgv_eps_monthly['策略月度收益率']).cumprod()
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['策略组合净值'].values, color=line_color_list[0], label='策略组合净值', linewidth=2, linestyle='-')
        ax.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['基准组合净值'].values, color=line_color_list[2], label='基准组合净值', linewidth=2, linestyle='-')
        ax.set_xticks(np.arange(len(rlgv_eps_monthly))[::18])
        ax.set_xticklabels(labels=rlgv_eps_monthly.index.tolist()[::18])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('EPS同比高低区间择时策略', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}/美股成长价值/{1}/EPS同比高低区间择时策略.png'.format(self.data_path, eps_type))
        performance = get_performance(rlgv_eps_monthly[['策略组合净值', '基准组合净值']], 12)
        performance.to_excel('{0}/美股成长价值/{1}/EPS同比高低区间择时策略表现.xlsx'.format(self.data_path, eps_type))

        for n in [1, 3, 6, 12]:
            rlgv_eps_monthly = rlgv_eps_monthly_ori.copy(deep=True)
            rlgv_eps_monthly['罗素1000价值EPS同比差分'] = rlgv_eps_monthly['罗素1000价值EPS同比'].diff(n)
            rlgv_eps_monthly['罗素1000成长EPS同比差分'] = rlgv_eps_monthly['罗素1000成长EPS同比'].diff(n)
            rlgv_eps_monthly = rlgv_eps_monthly.dropna()
            fig, ax = plt.subplots(figsize=(12, 6))
            ax_r = ax.twinx()
            width = 0.5
            ax.bar(np.arange(len(rlgv_eps_monthly)) - 0.5 * width, rlgv_eps_monthly['罗素1000价值EPS同比差分'].values, color=line_color_list[0], label='罗素1000价值EPS同比差分', linewidth=2)
            ax.bar(np.arange(len(rlgv_eps_monthly)) + 0.5 * width, rlgv_eps_monthly['罗素1000成长EPS同比差分'].values, color=line_color_list[1], label='罗素1000成长EPS同比差分', linewidth=2)
            ax_r.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
            ax.set_xticks(np.arange(len(rlgv_eps_monthly))[::18])
            ax.set_xticklabels(labels=rlgv_eps_monthly.index.tolist()[::18])
            ax_r.set_xticks(np.arange(len(rlgv_eps_monthly))[::18])
            ax_r.set_xticklabels(labels=rlgv_eps_monthly.index.tolist()[::18])
            ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax_r.get_legend_handles_labels()
            plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
            plt.title('EPS同比{0}期差分与罗素1000价值/成长表现'.format(n), fontdict={'weight': 'bold', 'size': 16})
            plt.tight_layout()
            sns.despine(top=True, right=False, left=False, bottom=False)
            plt.savefig('{0}/美股成长价值/{1}EPS同比{2}期差分.png'.format(self.data_path, eps_type, n))

            rlgv_eps_monthly['FORMARD_RET'] = rlgv_eps_monthly['罗素1000价值/成长'].pct_change(1).shift(-1)
            rlgv_eps_monthly['ACTUAL_MARK'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['FORMARD_RET'] >= 0 else 0, axis=1)
            rlgv_eps_monthly['价值_MARK'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['罗素1000价值EPS同比差分'] > 0 else 0, axis=1)
            rlgv_eps_monthly['成长_MARK'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['罗素1000成长EPS同比差分'] > 0 else 0, axis=1)
            print('价值EPS同比{0}期差分：'.format(n), len(rlgv_eps_monthly[rlgv_eps_monthly['价值_MARK'] == rlgv_eps_monthly['ACTUAL_MARK']]) / float(len(rlgv_eps_monthly.dropna())))
            print('成长EPS同比{0}期差分：'.format(n), len(rlgv_eps_monthly[rlgv_eps_monthly['成长_MARK'] == rlgv_eps_monthly['ACTUAL_MARK']]) / float(len(rlgv_eps_monthly.dropna())))
            rlgv_eps_monthly['价值仓位'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['罗素1000价值EPS同比差分'] > 0 else 0.5, axis=1)
            rlgv_eps_monthly['成长仓位'] = rlgv_eps_monthly.apply(lambda x: 1.0 if x['罗素1000成长EPS同比差分'] > 0 else 0.5, axis=1)
            rlgv_eps_monthly['价值月度收益率'] = rlgv_eps_monthly['罗素1000价值'].pct_change(1).shift(-1)
            rlgv_eps_monthly['成长月度收益率'] = rlgv_eps_monthly['罗素1000成长'].pct_change(1).shift(-1)
            rlgv_eps_monthly['价值月度收益率'].iloc[0] = 0.0
            rlgv_eps_monthly['成长月度收益率'].iloc[0] = 0.0
            for style in ['价值', '成长']:
                rlgv_eps_monthly_1 = rlgv_eps_monthly.copy(deep=True)
                rlgv_eps_monthly_2 = rlgv_eps_monthly.copy(deep=True)
                rlgv_eps_monthly_1['MARK'] = rlgv_eps_monthly_1.apply(lambda x: 1.0 if x['罗素1000' + style + 'EPS同比差分'] > 0 else 0, axis=1)
                rlgv_eps_monthly_2['MARK'] = rlgv_eps_monthly_2.apply(lambda x: 1.0 if x['罗素1000' + style + 'EPS同比差分'] <= 0 else 0, axis=1)
                fig, ax = plt.subplots(figsize=(12, 6))
                ax_r = ax.twinx()
                ax.bar(rlgv_eps_monthly_1.index, rlgv_eps_monthly_1['MARK'].values, color=line_color_list[0], alpha=0.5, label='罗素1000' + style + 'EPS同比差分>0')
                ax.bar(rlgv_eps_monthly_2.index, rlgv_eps_monthly_2['MARK'].values, color=line_color_list[1], alpha=0.5, label='罗素1000' + style + 'EPS同比差分<=0')
                ax_r.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['罗素1000价值/成长'].values, color=line_color_list[2], label='罗素1000价值/成长（右轴）', linewidth=2)
                ax.set_xticks(np.arange(len(rlgv_eps_monthly))[::18])
                ax.set_xticklabels(labels=rlgv_eps_monthly.index.tolist()[::18])
                h1, l1 = ax.get_legend_handles_labels()
                h2, l2 = ax_r.get_legend_handles_labels()
                plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
                plt.title('{0}EPS同比{1}期差分高低区间与罗素1000价值/成长表现'.format(style, n), fontdict={'weight': 'bold', 'size': 16})
                plt.tight_layout()
                sns.despine(top=True, right=False, left=False, bottom=False)
                plt.savefig('{0}/美股成长价值/{1}/{2}EPS同比{3}期差分高低区间.png'.format(self.data_path, eps_type, style, n))

                rlgv_eps_monthly['平均月度收益率'] = 0.5 * rlgv_eps_monthly['成长月度收益率'] + 0.5 * rlgv_eps_monthly['价值月度收益率']
                if style == '价值':
                    rlgv_eps_monthly['策略月度收益率'] = rlgv_eps_monthly.apply(lambda x: x['价值仓位'] * x['价值月度收益率'] + (1 - x['价值仓位']) * x['成长月度收益率'], axis=1)
                else:
                    rlgv_eps_monthly['策略月度收益率'] = rlgv_eps_monthly.apply(lambda x: x['成长仓位'] * x['成长月度收益率'] + (1 - x['成长仓位']) * x['价值月度收益率'], axis=1)
                rlgv_eps_monthly['基准组合净值'] = (1 + rlgv_eps_monthly['平均月度收益率']).cumprod()
                rlgv_eps_monthly['策略组合净值'] = (1 + rlgv_eps_monthly['策略月度收益率']).cumprod()
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['策略组合净值'].values, color=line_color_list[0], label='策略组合净值', linewidth=2, linestyle='-')
                ax.plot(np.arange(len(rlgv_eps_monthly)), rlgv_eps_monthly['基准组合净值'].values, color=line_color_list[2], label='基准组合净值', linewidth=2, linestyle='-')
                ax.set_xticks(np.arange(len(rlgv_eps_monthly))[::18])
                ax.set_xticklabels(labels=rlgv_eps_monthly.index.tolist()[::18])
                plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
                plt.title('{0}EPS同比{1}期差分高低区间择时策略'.format(style, n), fontdict={'weight': 'bold', 'size': 16})
                plt.tight_layout()
                sns.despine(top=True, right=False, left=False, bottom=False)
                plt.savefig('{0}/美股成长价值/{1}/{2}EPS同比{3}期差分高低区间择时策略.png'.format(self.data_path, eps_type, style, n))
                performance = get_performance(rlgv_eps_monthly[['策略组合净值', '基准组合净值']], 12)
                performance.to_excel('{0}/美股成长价值/{1}/{2}EPS同比{3}期差分高低区间择时策略表现.xlsx'.format(self.data_path, eps_type, style, n))


        factor = pd.read_excel('{0}/美股成长价值/factor.xlsx'.format(self.data_path))
        factor['YEAR_MONTH'] = factor['YEAR_MONTH'].astype(str)
        factor = factor.set_index('YEAR_MONTH')
        factor = factor.dropna()
        factor['罗素1000价值/成长PE仓位'] = factor['罗素1000价值/成长PE分位'].apply(lambda x: 1.0 if x < 0.2 else 0.0 if x > 0.8 else 0.5)
        factor['罗素1000价值PE仓位'] = factor['罗素1000价值PE分位'].apply(lambda x: 1.0 if x >= 0.0 and x < 0.2 else 0.75 if x >= 0.2 and x < 0.4 else 0.5 if x >= 0.4 and x < 0.6 else 0.25 if x >= 0.6 and x < 0.8 else 0.0)
        factor['罗素1000成长PE仓位'] = factor['罗素1000成长PE分位'].apply(lambda x: 1.0 if x >= 0.0 and x < 0.2 else 0.75 if x >= 0.2 and x < 0.4 else 0.5 if x >= 0.4 and x < 0.6 else 0.25 if x >= 0.6 and x < 0.8 else 0.0)
        factor['罗素1000价值/成长EPS同比仓位'] = factor.apply(lambda x: 1.0 if x['罗素1000价值EPS同比'] >= x['罗素1000成长EPS同比'] else 0.0, axis=1)
        factor['价值仓位'] = (factor['罗素1000价值/成长PE仓位'] + factor['罗素1000价值PE仓位'] + factor['罗素1000价值/成长EPS同比仓位']) / 3.0
        factor['成长仓位'] = factor['价值仓位'].apply(lambda x: 1 - x)
        factor = factor.merge(rlgv_monthly, left_index=True, right_index=True, how='left')
        factor['价值月度收益率'] = factor['罗素1000价值'].pct_change(1).shift(-1)
        factor['成长月度收益率'] = factor['罗素1000成长'].pct_change(1).shift(-1)
        factor['价值月度收益率'].iloc[0] = 0.0
        factor['成长月度收益率'].iloc[0] = 0.0
        factor['平均月度收益率'] = 0.5 * factor['成长月度收益率'] + 0.5 * factor['价值月度收益率']
        factor['策略月度收益率'] = factor['价值仓位'] * factor['价值月度收益率'] + factor['成长仓位'] * factor['成长月度收益率']
        factor['基准组合净值'] = (1 + factor['平均月度收益率']).cumprod()
        factor['策略组合净值'] = (1 + factor['策略月度收益率']).cumprod()
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(np.arange(len(factor)), factor['策略组合净值'].values, color=line_color_list[0], label='策略组合净值', linewidth=2, linestyle='-')
        ax.plot(np.arange(len(factor)), factor['基准组合净值'].values, color=line_color_list[2], label='基准组合净值', linewidth=2, linestyle='-')
        ax.set_xticks(np.arange(len(factor))[::18])
        ax.set_xticklabels(labels=factor.index.tolist()[::18])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
        plt.title('多指标择时策略', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}/美股成长价值/多指标择时策略.png'.format(self.data_path))
        performance = get_performance(factor[['策略组合净值', '基准组合净值']])
        performance.to_excel('{0}/美股成长价值/多指标择时策略表现.xlsx'.format(self.data_path))
        return

def get_performance(df, q):
    df = df.dropna()
    df.columns = ['P_NAV', 'B_NAV']
    df['P_RET'] = df['P_NAV'].pct_change()
    df['B_RET'] = df['B_NAV'].pct_change()
    df['E_RET'] = df['P_RET'] - df['B_RET']
    df['E_NAV'] = (df['E_RET'].fillna(0.0) + 1).cumprod()
    performance = pd.DataFrame(index=['年化收益率', '年化波动率', '最大回撤', '夏普比率', '卡玛比率', '投资胜率', '投资损益比'], columns=['指标值', '基准指标值', '超额指标值'])

    performance.loc['年化收益率', '指标值'] = (df['P_NAV'].iloc[-1] / df['P_NAV'].iloc[0]) ** (q / float(len(df))) - 1.0
    performance.loc['年化波动率', '指标值'] = np.std(df['P_RET'].dropna(), ddof=1) * np.sqrt(q)
    performance.loc['最大回撤', '指标值'] = max([(min(df['P_NAV'].iloc[i:]) / df['P_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['P_NAV']))])
    performance.loc['夏普比率', '指标值'] = (performance.loc['年化收益率', '指标值'] - 0.015) / performance.loc['年化波动率', '指标值']
    performance.loc['卡玛比率', '指标值'] = performance.loc['年化收益率', '指标值'] / performance.loc['最大回撤', '指标值']
    performance.loc['投资胜率', '指标值'] = len(df[df['P_RET'] >= 0]) / float(len(df.dropna()))
    performance.loc['投资损益比', '指标值'] = df[df['P_RET'] >= 0]['P_RET'].mean() / df[df['P_RET'] < 0]['P_RET'].mean() * (-1.0)

    performance.loc['年化收益率', '基准指标值'] = (df['B_NAV'].iloc[-1] / df['B_NAV'].iloc[0]) ** (q / float(len(df))) - 1.0
    performance.loc['年化波动率', '基准指标值'] = np.std(df['B_RET'].dropna(), ddof=1) * np.sqrt(q)
    performance.loc['最大回撤', '基准指标值'] = max([(min(df['B_NAV'].iloc[i:]) / df['B_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['B_NAV']))])
    performance.loc['夏普比率', '基准指标值'] = (performance.loc['年化收益率', '基准指标值'] - 0.015) / performance.loc['年化波动率', '基准指标值']
    performance.loc['卡玛比率', '基准指标值'] = performance.loc['年化收益率', '基准指标值'] / performance.loc['最大回撤', '基准指标值']
    performance.loc['投资胜率', '基准指标值'] = len(df[df['B_RET'] >= 0]) / float(len(df.dropna()))
    performance.loc['投资损益比', '基准指标值'] = df[df['B_RET'] >= 0]['B_RET'].mean() / df[df['B_RET'] < 0]['B_RET'].mean() * (-1.0)

    performance.loc['年化收益率', '超额指标值'] = (df['E_NAV'].iloc[-1] / df['E_NAV'].iloc[0]) ** (q / float(len(df))) - 1.0
    performance.loc['年化波动率', '超额指标值'] = np.std(df['E_RET'].dropna(), ddof=1) * np.sqrt(q)
    performance.loc['最大回撤', '超额指标值'] = max([(min(df['E_NAV'].iloc[i:]) / df['E_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['E_NAV']))])
    performance.loc['夏普比率', '超额指标值'] = (performance.loc['年化收益率', '超额指标值'] - 0.015) / performance.loc['年化波动率', '超额指标值']
    performance.loc['卡玛比率', '超额指标值'] = performance.loc['年化收益率', '超额指标值'] / performance.loc['最大回撤', '超额指标值']
    performance.loc['投资胜率', '超额指标值'] = len(df[df['E_RET'] >= 0]) / float(len(df.dropna()))
    performance.loc['投资损益比', '超额指标值'] = df[df['E_RET'] >= 0]['E_RET'].mean() / df[df['E_RET'] < 0]['E_RET'].mean() * (-1.0)
    return performance

class StyleConstruction:
    def __init__(self, start_date, end_date, report_date, tracking_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_hyphen = datetime.strptime(self.start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(self.end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.report_date = report_date
        self.tracking_date = tracking_date
        self.data_path = data_path
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date(self.start_date, self.tracking_date)
        self.load()

    def load(self):
        # 个股相关
        self.stock_info = get_stock_info(180)

        # 股票收盘价、涨跌幅、成交金额、换手率、流通市值、总市值
        stock_daily_k_path = '{0}style_construction/stock_daily_k.hdf'.format(self.data_path)
        if os.path.isfile(stock_daily_k_path):
            existed_stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
            max_date = max(existed_stock_daily_k['TDATE'])
            start_date = max(str(max_date), '20051231')
        else:
            existed_stock_daily_k = pd.DataFrame()
            start_date = '20051231'
        trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.tracking_date)]
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
        self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
        self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]

        # 股票估值数据
        stock_valuation_path = '{0}style_construction/stock_valuation.hdf'.format(self.data_path)
        if os.path.isfile(stock_valuation_path):
            existed_stock_valuation = pd.read_hdf(stock_valuation_path, key='table')
            max_date = max(existed_stock_valuation['TRADE_DATE'])
            start_date = max(str(max_date), '20051231')
        else:
            existed_stock_valuation = pd.DataFrame()
            start_date = '20051231'
        trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.tracking_date)]
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
        self.stock_valuation = pd.read_hdf(stock_valuation_path, key='table')
        self.stock_valuation['TRADE_DATE'] = self.stock_valuation['TRADE_DATE'].astype(str)
        self.stock_valuation = self.stock_valuation.loc[self.stock_valuation['TICKER_SYMBOL'].str.len() == 6]
        self.stock_valuation = self.stock_valuation.loc[self.stock_valuation['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]

        # 股票财务数据
        stock_finance_path = '{0}style_construction/stock_finance.hdf'.format(self.data_path)
        if os.path.isfile(stock_finance_path):
            existed_stock_finance = pd.read_hdf(stock_finance_path, key='table')
            max_date = max(existed_stock_finance['END_DATE'])
            start_date = max(str(max_date), '20051231')
        else:
            existed_stock_finance = pd.DataFrame()
            start_date = '20051231'
        report_df = self.report_df[(self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.report_date)]
        stock_finance_list = []
        for date in report_df['REPORT_DATE'].unique().tolist():
            stock_finance_date = HBDB().read_stock_finance_jy(date)
            stock_finance_date = stock_finance_date[['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM']] if len(stock_finance_date) > 0 else pd.DataFrame(columns=['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM'])
            star_stock_finance_date = HBDB().read_star_stock_finance_jy(date)
            star_stock_finance_date = star_stock_finance_date[['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM']] if len(star_stock_finance_date) > 0 else pd.DataFrame(columns=['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM'])
            stock_finance_date = pd.concat([stock_finance_date, star_stock_finance_date])
            stock_finance_list.append(stock_finance_date)
            print(date)
        self.stock_finance = pd.concat([existed_stock_finance] + stock_finance_list, ignore_index=True)
        self.stock_finance.to_hdf(stock_finance_path, key='table', mode='w')
        self.stock_finance = pd.read_hdf(stock_finance_path, key='table')
        self.stock_finance['END_DATE'] = self.stock_finance['END_DATE'].astype(str)
        self.stock_finance['PUBLISH_DATE'] = self.stock_finance['PUBLISH_DATE'].astype(str)
        self.stock_finance = self.stock_finance.loc[self.stock_finance['TICKER_SYMBOL'].str.len() == 6]
        self.stock_finance = self.stock_finance.loc[self.stock_finance['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        self.stock_finance = self.stock_finance.sort_values(['TICKER_SYMBOL', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')

        # 股票一致预期数据
        type = 'FY1'
        stock_consensus_path = '{0}style_construction/stock_consensus_{1}.hdf'.format(self.data_path, type)
        if os.path.isfile(stock_consensus_path):
            existed_stock_consensus = pd.read_hdf(stock_consensus_path, key='table')
            max_date = max(existed_stock_consensus['EST_DT'])
            start_date = max(str(max_date), '20051231')
        else:
            existed_stock_consensus = pd.DataFrame()
            start_date = '20051231'
        calendar_df = self.calendar_df[(self.calendar_df['CALENDAR_DATE'] > start_date) & (self.calendar_df['CALENDAR_DATE'] <= self.tracking_date)]
        stock_consensus_list = []
        for date in calendar_df['CALENDAR_DATE'].unique().tolist():
            stock_consensus_date = HBDB().read_consensus_given_date(date, type)
            stock_consensus_list.append(stock_consensus_date)
            print(date)
        self.stock_consensus = pd.concat([existed_stock_consensus] + stock_consensus_list, ignore_index=True)
        self.stock_consensus = self.stock_consensus.sort_values(['EST_DT', 'TICKER_SYMBOL'])
        self.stock_consensus = self.stock_consensus.reset_index().drop('index', axis=1)
        self.stock_consensus.to_hdf(stock_consensus_path, key='table', mode='w')
        self.stock_consensus = pd.read_hdf(stock_consensus_path, key='table')
        self.stock_consensus = self.stock_consensus.rename(columns={'EST_DT': 'TRADE_DATE', 'EST_EPS': 'CON_EPS'})
        self.stock_consensus['TRADE_DATE'] = self.stock_consensus['TRADE_DATE'].astype(str)
        self.stock_consensus['TICKER_SYMBOL'] = self.stock_consensus['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
        self.stock_consensus = self.stock_consensus.loc[self.stock_consensus['TICKER_SYMBOL'].str.len() == 6]
        self.stock_consensus = self.stock_consensus.loc[self.stock_consensus['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
        self.stock_consensus = self.stock_consensus[self.stock_consensus['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        return

    def analysis(self):
        # 指数走势
        style_index = w.wsd("399370.SZ,399371.SZ,399006.SZ,000016.SH,801821.SI,801823.SI", "close", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        style_index.to_hdf('{0}style_construction/style_index_wind.hdf'.format(self.data_path), key='table', mode='w')
        style_index = pd.read_hdf('{0}style_construction/style_index_wind.hdf'.format(self.data_path), key='table')
        style_index.columns = ['TRADE_DATE', '国证成长', '国证价值', '创业板指', '上证50', '高市盈率指数', '低市盈率指数']
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        style_index = style_index[style_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style_index = style_index.dropna().set_index('TRADE_DATE').sort_index()
        style_index = style_index / style_index.iloc[0]
        style_index['国证成长/国证价值'] = style_index['国证成长'] / style_index['国证价值']
        style_index['创业板指/上证50'] = style_index['创业板指'] / style_index['上证50']
        style_index['高市盈率指数/低市盈率指数'] = style_index['高市盈率指数'] / style_index['低市盈率指数']

        style_index_disp = style_index.copy(deep=True)
        style_index_disp = style_index_disp[(style_index_disp.index > self.start_date) & (style_index_disp.index <= self.end_date)]
        style_index_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index_disp.index)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax_r = ax.twinx()
        ax.plot(style_index_disp.index, style_index_disp['国证成长'].values, color=line_color_list[0], label='国证成长', linewidth=2)
        ax.plot(style_index_disp.index, style_index_disp['国证价值'].values, color=line_color_list[1], label='国证价值', linewidth=2)
        ax_r.plot(style_index_disp.index, style_index_disp['国证成长/国证价值'].values, color=line_color_list[2], label='国证成长/国证价值（右轴）', linewidth=2)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.20), ncol=3, frameon=False)
        plt.title('国证成长与国证价值', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}style_construction/国证成长与国证价值.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(8, 4))
        ax_r = ax.twinx()
        ax.plot(style_index_disp.index, style_index_disp['创业板指'].values, color=line_color_list[0], label='创业板指', linewidth=2)
        ax.plot(style_index_disp.index, style_index_disp['上证50'].values, color=line_color_list[1], label='上证50', linewidth=2)
        ax_r.plot(style_index_disp.index, style_index_disp['创业板指/上证50'].values, color=line_color_list[2], label='创业板指/上证50（右轴）', linewidth=2)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.20), ncol=3, frameon=False)
        plt.title('创业板指与上证50', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}style_construction/创业板指与上证50.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(8, 4))
        ax_r = ax.twinx()
        ax.plot(style_index_disp.index, style_index_disp['高市盈率指数'].values, color=line_color_list[0], label='高市盈率指数', linewidth=2)
        ax.plot(style_index_disp.index, style_index_disp['低市盈率指数'].values, color=line_color_list[1], label='低市盈率指数', linewidth=2)
        ax_r.plot(style_index_disp.index, style_index_disp['高市盈率指数/低市盈率指数'].values, color=line_color_list[2], label='高市盈率指数/低市盈率指数（右轴）', linewidth=2)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.20), ncol=3, frameon=False)
        plt.title('高市盈率指数与低市盈率指数', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}style_construction/高市盈率指数与低市盈率指数.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(style_index_disp.index, style_index_disp['国证成长/国证价值'].values, color=line_color_list[0], label='国证成长/国证价值', linewidth=2)
        ax.plot(style_index_disp.index, style_index_disp['创业板指/上证50'].values, color=line_color_list[1], label='创业板指/上证50', linewidth=2)
        ax.plot(style_index_disp.index, style_index_disp['高市盈率指数/低市盈率指数'].values, color=line_color_list[2], label='高市盈率指数/低市盈率指数', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.20), ncol=3, frameon=False)
        plt.title('成长与价值', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/成长与价值.png'.format(self.data_path))

        # 行业相关
        self.industry_info = get_industry_info('申万')
        self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == 1]
        self.industry_info = self.industry_info[self.industry_info['IS_NEW'] == 1]
        self.industry_info = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.industry_list = self.industry_info['INDUSTRY_ID'].unique().tolist()
        self.industry_symbol = get_industry_symbol('申万')
        self.industry_symbol = self.industry_symbol[self.industry_symbol['INDUSTRY_TYPE'] == 1]
        self.industry_symbol = self.industry_symbol[self.industry_symbol['IS_NEW'] == 1]
        self.industry_symbol = self.industry_symbol[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.stock_industry = get_stock_industry('申万')
        self.stock_industry = self.stock_industry[self.stock_industry['INDUSTRY_TYPE'] == 1]
        self.stock_industry = self.stock_industry[self.stock_industry['IS_NEW'] == 1]
        self.stock_industry = self.stock_industry.drop('INDUSTRY_NAME', axis=1).merge(self.industry_symbol, on=['INDUSTRY_ID'], how='left')
        self.stock_industry = self.stock_industry.drop('INDUSTRY_ID', axis=1).merge(self.industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID']], on=['INDUSTRY_NAME'], how='left')
        self.stock_industry = self.stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME', 'TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE']]
        self.sw_stock_industry = self.stock_industry.copy(deep=True)

        self.industry_info = get_industry_info('中信')
        self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == 1]
        self.industry_info = self.industry_info[self.industry_info['IS_NEW'] == 1]
        self.industry_info = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.industry_info['INDUSTRY_NAME'] = self.industry_info['INDUSTRY_NAME'].replace({'电力设备': '电力设备及新能源', '餐饮旅游': '消费者服务', '电子元器件': '电子'})
        self.industry_list = self.industry_info['INDUSTRY_ID'].unique().tolist()
        self.industry_symbol = get_industry_symbol('中信')
        self.industry_symbol = self.industry_symbol[self.industry_symbol['INDUSTRY_TYPE'] == 1]
        self.industry_symbol = self.industry_symbol[self.industry_symbol['IS_NEW'] == 1]
        self.industry_symbol = self.industry_symbol[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.industry_symbol['INDUSTRY_NAME'] = self.industry_symbol['INDUSTRY_NAME'].replace({'电力设备': '电力设备及新能源', '餐饮旅游': '消费者服务', '电子元器件': '电子'})
        self.stock_industry = get_stock_industry('中信')
        self.stock_industry = self.stock_industry[self.stock_industry['INDUSTRY_TYPE'] == 1]
        self.stock_industry = self.stock_industry[self.stock_industry['IS_NEW'] == 1]
        self.stock_industry = self.stock_industry.drop('INDUSTRY_NAME', axis=1).merge(self.industry_symbol, on=['INDUSTRY_ID'], how='left')
        self.stock_industry = self.stock_industry.drop('INDUSTRY_ID', axis=1).merge(self.industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID']], on=['INDUSTRY_NAME'], how='left')
        self.stock_industry = self.stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME', 'TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE']]
        self.stock_industry['INDUSTRY_NAME'] = self.stock_industry['INDUSTRY_NAME'].replace({'电力设备': '电力设备及新能源', '餐饮旅游': '消费者服务', '电子元器件': '电子'})
        self.zx_stock_industry = self.stock_industry.copy(deep=True)

        # 指数成分股
        semi_year = self.report_trade_df[self.report_trade_df['MONTH'].isin(['06', '12'])]
        semi_year = semi_year[(semi_year['TRADE_DATE'] >= '20100101') & (semi_year['TRADE_DATE'] <= '20221231')]
        style_index_cons_list = []
        for date in semi_year['TRADE_DATE'].unique().tolist():
            date_hyphen = datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d')
            g1 = w.wset("indexconstituent","date={0};windcode=399370.SZ".format(date_hyphen), usedf=True)[1].reset_index()
            g1['index'] = '399370.SZ'
            style_index_cons_list.append(g1)
            v1 = w.wset("indexconstituent", "date={0};windcode=399371.SZ".format(date_hyphen), usedf=True)[1].reset_index()
            v1['index'] = '399371.SZ'
            style_index_cons_list.append(v1)
            g2 = w.wset("indexconstituent", "date={0};windcode=399006.SZ".format(date_hyphen), usedf=True)[1].reset_index()
            g2['index'] = '399006.SZ'
            style_index_cons_list.append(g2)
            v2 = w.wset("indexconstituent", "date={0};windcode=000016.SH".format(date_hyphen), usedf=True)[1].reset_index()
            v2['index'] = '000016.SH'
            style_index_cons_list.append(v2)
            g3 = w.wset("indexconstituent", "date={0};windcode=801821.SI".format(date_hyphen), usedf=True)[1].reset_index()
            g3['index'] = '801821.SI'
            style_index_cons_list.append(g3)
            v3 = w.wset("indexconstituent", "date={0};windcode=801823.SI".format(date_hyphen), usedf=True)[1].reset_index()
            v3['index'] = '801823.SI'
            style_index_cons_list.append(v3)
            print(date)
        style_index_cons = pd.concat(style_index_cons_list)
        style_index_cons.to_hdf('{0}style_construction/style_index_cons_wind.hdf'.format(self.data_path), key='table', mode='w')
        style_index_cons = pd.read_hdf('{0}style_construction/style_index_cons_wind.hdf'.format(self.data_path), key='table')
        style_index_cons.columns = ['INDEX_NAME', 'TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'WEIGHT', 'INDUSTRY_NAME']
        style_index_cons['INDEX_NAME'] = style_index_cons['INDEX_NAME'].replace({'399370.SZ': '国证成长', '399371.SZ': '国证价值', '399006.SZ': '创业板指', '000016.SH': '上证50', '801821.SI': '高市盈率指数', '801823.SI': '低市盈率指数'})
        style_index_cons['TRADE_DATE'] = style_index_cons['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        style_index_cons['TICKER_SYMBOL'] = style_index_cons['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
        style_index_cons['END_DATE'] = style_index_cons['TRADE_DATE'].apply(lambda x: x[:6] + '30' if x[4:6] == '06' else x[:6] + '31')
        self.total_market_value = self.stock_daily_k[['TRADE_DATE', 'MARKET_VALUE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum().reset_index().rename(columns={'MARKET_VALUE': 'TOTAL_MARKET_VALUE', 'NEG_MARKET_VALUE': 'TOTAL_NEG_MARKET_VALUE'})
        style_index_cons = style_index_cons.merge(self.stock_daily_k[['TICKER_SYMBOL', 'TRADE_DATE', 'MARKET_VALUE', 'NEG_MARKET_VALUE']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left').merge(self.total_market_value, on=['TRADE_DATE'], how='left')
        style_index_cons['MARKET_VALUE_RATIO'] = style_index_cons['MARKET_VALUE'] / style_index_cons['TOTAL_MARKET_VALUE']
        style_index_cons['NEG_MARKET_VALUE_RATIO'] = style_index_cons['NEG_MARKET_VALUE'] / style_index_cons['TOTAL_NEG_MARKET_VALUE']
        style_index_cons = style_index_cons.merge(self.stock_valuation[['TICKER_SYMBOL', 'TRADE_DATE', 'PE_TTM']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left').merge(self.stock_finance[['TICKER_SYMBOL', 'END_DATE', 'ROE_TTM']], on=['TICKER_SYMBOL', 'END_DATE'], how='left')
        style_index_cons = style_index_cons.merge(self.sw_stock_industry[['TICKER_SYMBOL', 'INDUSTRY_NAME']].rename(columns={'INDUSTRY_NAME': 'SW_INDUSTRY_NAME'}), on=['TICKER_SYMBOL'], how='left').merge(self.zx_stock_industry[['TICKER_SYMBOL', 'INDUSTRY_NAME']].rename(columns={'INDUSTRY_NAME': 'ZX_INDUSTRY_NAME'}), on=['TICKER_SYMBOL'], how='left')
        style_index_cons.to_hdf('{0}style_construction/style_index_cons.hdf'.format(self.data_path), key='table', mode='w')
        style_index_cons = pd.read_hdf('{0}style_construction/style_index_cons.hdf'.format(self.data_path), key='table')
        style_index_cons = style_index_cons[style_index_cons['TRADE_DATE'].str.slice(4, 6).isin(['06', '12'])]
        style_index_cons = style_index_cons.dropna()

        # 总市值占比
        mv = style_index_cons[['INDEX_NAME', 'END_DATE', 'MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE']).sum()
        total_mv = style_index_cons[['INDEX_NAME', 'END_DATE', 'TOTAL_MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE']).mean()
        mv = mv.merge(total_mv, left_index=True, right_index=True, how='left').reset_index()
        mv['MARKET_VALUE_RATIO'] = mv['MARKET_VALUE'] / mv['TOTAL_MARKET_VALUE']
        mv = mv.pivot(index='END_DATE', columns='INDEX_NAME', values='MARKET_VALUE_RATIO').sort_index()
        mv_disp = mv.copy(deep=True)
        mv_disp = mv_disp[(mv_disp.index > self.start_date) & (mv_disp.index <= self.end_date)]
        mv_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), mv_disp.index)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(mv_disp.index, mv_disp['国证成长'].values, color=line_color_list[0], label='国证成长', linewidth=2)
        ax.plot(mv_disp.index, mv_disp['国证价值'].values, color=line_color_list[0], alpha=0.5, label='国证价值', linewidth=2)
        ax.plot(mv_disp.index, mv_disp['创业板指'].values, color=line_color_list[1], label='创业板指', linewidth=2)
        ax.plot(mv_disp.index, mv_disp['上证50'].values, color=line_color_list[1], alpha=0.5, label='上证50', linewidth=2)
        ax.plot(mv_disp.index, mv_disp['高市盈率指数'].values, color=line_color_list[2], label='高市盈率指数', linewidth=2)
        ax.plot(mv_disp.index, mv_disp['低市盈率指数'].values, color=line_color_list[2], alpha=0.5, label='低市盈率指数', linewidth=2)
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=3, frameon=False)
        plt.title('总市值占比', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/总市值占比.png'.format(self.data_path))

        # 流通市值占比
        neg_mv = style_index_cons[['INDEX_NAME', 'END_DATE', 'NEG_MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE']).sum()
        total_neg_mv = style_index_cons[['INDEX_NAME', 'END_DATE', 'TOTAL_NEG_MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE']).mean()
        neg_mv = neg_mv.merge(total_neg_mv, left_index=True, right_index=True, how='left').reset_index()
        neg_mv['NEG_MARKET_VALUE_RATIO'] = neg_mv['NEG_MARKET_VALUE'] / neg_mv['TOTAL_NEG_MARKET_VALUE']
        neg_mv = neg_mv.pivot(index='END_DATE', columns='INDEX_NAME', values='NEG_MARKET_VALUE_RATIO').sort_index()
        neg_mv_disp = neg_mv.copy(deep=True)
        neg_mv_disp = neg_mv_disp[(neg_mv_disp.index > self.start_date) & (neg_mv_disp.index <= self.end_date)]
        neg_mv_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), neg_mv_disp.index)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(neg_mv_disp.index, neg_mv_disp['国证成长'].values, color=line_color_list[0], label='国证成长', linewidth=2)
        ax.plot(neg_mv_disp.index, neg_mv_disp['国证价值'].values, color=line_color_list[0], alpha=0.5, label='国证价值', linewidth=2)
        ax.plot(neg_mv_disp.index, neg_mv_disp['创业板指'].values, color=line_color_list[1], label='创业板指', linewidth=2)
        ax.plot(neg_mv_disp.index, neg_mv_disp['上证50'].values, color=line_color_list[1], alpha=0.5, label='上证50', linewidth=2)
        ax.plot(neg_mv_disp.index, neg_mv_disp['高市盈率指数'].values, color=line_color_list[2], label='高市盈率指数', linewidth=2)
        ax.plot(neg_mv_disp.index, neg_mv_disp['低市盈率指数'].values, color=line_color_list[2], alpha=0.5, label='低市盈率指数', linewidth=2)
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=3, frameon=False)
        plt.title('流通市值占比', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/流通市值占比.png'.format(self.data_path))

        # PE_TTM中位数
        pe = style_index_cons[['INDEX_NAME', 'END_DATE', 'PE_TTM']].groupby(['INDEX_NAME', 'END_DATE']).median().reset_index()
        pe = pe.pivot(index='END_DATE', columns='INDEX_NAME', values='PE_TTM').sort_index()
        pe_disp = pe.copy(deep=True)
        pe_disp = pe_disp[(pe_disp.index > self.start_date) & (pe_disp.index <= self.end_date)]
        pe_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), pe_disp.index)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(pe_disp.index, pe_disp['国证成长'].values, color=line_color_list[0], label='国证成长', linewidth=2)
        ax.plot(pe_disp.index, pe_disp['国证价值'].values, color=line_color_list[0], alpha=0.5, label='国证价值', linewidth=2)
        ax.plot(pe_disp.index, pe_disp['创业板指'].values, color=line_color_list[1], label='创业板指', linewidth=2)
        ax.plot(pe_disp.index, pe_disp['上证50'].values, color=line_color_list[1], alpha=0.5, label='上证50', linewidth=2)
        ax.plot(pe_disp.index, pe_disp['高市盈率指数'].values, color=line_color_list[2], label='高市盈率指数', linewidth=2)
        ax.plot(pe_disp.index, pe_disp['低市盈率指数'].values, color=line_color_list[2], alpha=0.5, label='低市盈率指数', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=3, frameon=False)
        plt.title('PE_TTM中位数', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/PE_TTM中位数.png'.format(self.data_path))

        # ROE_TTM
        roe = style_index_cons[['INDEX_NAME', 'END_DATE', 'ROE_TTM']].groupby(['INDEX_NAME', 'END_DATE']).median().reset_index()
        roe = roe.pivot(index='END_DATE', columns='INDEX_NAME', values='ROE_TTM').sort_index()
        roe_disp = roe.copy(deep=True)
        roe_disp = roe_disp[(roe_disp.index > self.start_date) & (roe_disp.index <= self.end_date)]
        roe_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), roe_disp.index)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(roe_disp.index, roe_disp['国证成长'].values, color=line_color_list[0], label='国证成长', linewidth=2)
        ax.plot(roe_disp.index, roe_disp['国证价值'].values, color=line_color_list[0], alpha=0.5, label='国证价值', linewidth=2)
        ax.plot(roe_disp.index, roe_disp['创业板指'].values, color=line_color_list[1], label='创业板指', linewidth=2)
        ax.plot(roe_disp.index, roe_disp['上证50'].values, color=line_color_list[1], alpha=0.5, label='上证50', linewidth=2)
        ax.plot(roe_disp.index, roe_disp['高市盈率指数'].values, color=line_color_list[2], label='高市盈率指数', linewidth=2)
        ax.plot(roe_disp.index, roe_disp['低市盈率指数'].values, color=line_color_list[2], alpha=0.5, label='低市盈率指数', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=3, frameon=False)
        plt.title('ROE_TTM中位数', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/ROE_TTM中位数.png'.format(self.data_path))

        # 行业分布
        sw_industry = style_index_cons[['INDEX_NAME', 'END_DATE', 'SW_INDUSTRY_NAME', 'NEG_MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE', 'SW_INDUSTRY_NAME']).sum().reset_index()
        sw_industry = sw_industry.pivot(index=['INDEX_NAME', 'END_DATE'], columns='SW_INDUSTRY_NAME', values='NEG_MARKET_VALUE').sort_index()
        sw_industry.to_excel('{0}style_construction/sw_industry.xlsx'.format(self.data_path))
        zx_industry = style_index_cons[['INDEX_NAME', 'END_DATE', 'ZX_INDUSTRY_NAME', 'NEG_MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE', 'ZX_INDUSTRY_NAME']).sum().reset_index()
        zx_industry = zx_industry.pivot(index=['INDEX_NAME', 'END_DATE'], columns='ZX_INDUSTRY_NAME', values='NEG_MARKET_VALUE').sort_index()
        zx_industry.to_excel('{0}style_construction/zx_industry.xlsx'.format(self.data_path))

        # 因子分析
        growth = pd.read_hdf('{0}style_construction/growth.hdf'.format(self.data_path), key='table')
        growth = growth[growth['TRADE_DATE'].isin(self.report_trade_df['TRADE_DATE'].unique().tolist())]
        growth = growth[growth['TRADE_DATE'].str.slice(4, 6).isin(['06', '12'])]
        growth['END_DATE'] = growth['TRADE_DATE'].apply(lambda x: x[:6] + '30' if x[4:6] == '06' else x[:6] + '31')
        growth = growth[(growth['END_DATE'] > self.start_date) & (growth['END_DATE'] <= self.end_date)]
        growth = growth.dropna()
        growth = growth.merge(self.sw_stock_industry[['TICKER_SYMBOL', 'INDUSTRY_NAME']].rename(columns={'INDUSTRY_NAME': 'SW_INDUSTRY_NAME'}), on=['TICKER_SYMBOL'], how='left')
        growth = growth.merge(self.zx_stock_industry[['TICKER_SYMBOL', 'INDUSTRY_NAME']].rename(columns={'INDUSTRY_NAME': 'ZX_INDUSTRY_NAME'}), on=['TICKER_SYMBOL'], how='left')
        sw_industry_growth = growth[['END_DATE', 'SW_INDUSTRY_NAME', 'GROWTH']].groupby(['END_DATE', 'SW_INDUSTRY_NAME']).median().reset_index()
        sw_industry_growth = sw_industry_growth.pivot(index='END_DATE', columns='SW_INDUSTRY_NAME', values='GROWTH').sort_index()
        sw_industry_growth.to_excel('{0}style_construction/sw_industry_growth.xlsx'.format(self.data_path))
        zx_industry_growth = growth[['END_DATE', 'ZX_INDUSTRY_NAME', 'GROWTH']].groupby(['END_DATE', 'ZX_INDUSTRY_NAME']).median().reset_index()
        zx_industry_growth = zx_industry_growth.pivot(index='END_DATE', columns='ZX_INDUSTRY_NAME', values='GROWTH').sort_index()
        zx_industry_growth.to_excel('{0}style_construction/zx_industry_growth.xlsx'.format(self.data_path))
        return

    def construction(self):
        for industry_type in ['申万', '中信']:
            for industry_level in [1, 2]:
                self.industry_info = get_industry_info(industry_type)
                self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == industry_level]
                self.industry_info = self.industry_info[self.industry_info['IS_NEW'] == 1]
                self.industry_info = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
                if industry_type == '中信' and industry_level == 1:
                    self.industry_info['INDUSTRY_NAME'] = self.industry_info['INDUSTRY_NAME'].replace({'电力设备': '电力设备及新能源', '餐饮旅游': '消费者服务', '电子元器件': '电子'})
                self.industry_list = self.industry_info['INDUSTRY_ID'].unique().tolist()
                self.industry_symbol = get_industry_symbol(industry_type)
                self.industry_symbol = self.industry_symbol[self.industry_symbol['INDUSTRY_TYPE'] == industry_level]
                self.industry_symbol = self.industry_symbol[self.industry_symbol['IS_NEW'] == 1]
                self.industry_symbol = self.industry_symbol[['INDUSTRY_ID', 'INDUSTRY_NAME']]
                if industry_type == '中信' and industry_level == 1:
                    self.industry_symbol['INDUSTRY_NAME'] = self.industry_symbol['INDUSTRY_NAME'].replace({'电力设备': '电力设备及新能源', '餐饮旅游': '消费者服务', '电子元器件': '电子'})
                self.stock_industry = get_stock_industry(industry_type)
                self.stock_industry = self.stock_industry[self.stock_industry['INDUSTRY_TYPE'] == industry_level]
                self.stock_industry = self.stock_industry[self.stock_industry['IS_NEW'] == 1]
                self.stock_industry = self.stock_industry.drop('INDUSTRY_NAME', axis=1).merge(self.industry_symbol, on=['INDUSTRY_ID'], how='left')
                self.stock_industry = self.stock_industry.drop('INDUSTRY_ID', axis=1).merge(self.industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID']], on=['INDUSTRY_NAME'], how='left')
                self.stock_industry = self.stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME', 'TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE']]
                if industry_type == '中信' and industry_level == 1:
                    self.stock_industry['INDUSTRY_NAME'] = self.stock_industry['INDUSTRY_NAME'].replace({'电力设备': '电力设备及新能源', '餐饮旅游': '消费者服务', '电子元器件': '电子'})
                self.id_name_dic = self.stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME']].drop_duplicates().set_index('INDUSTRY_ID')['INDUSTRY_NAME'].to_dict()

                stock_daily_k = self.stock_daily_k.copy(deep=True)
                stock_daily_k = stock_daily_k.merge(self.stock_valuation[['TICKER_SYMBOL', 'TRADE_DATE', 'PE_TTM']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left')
                stock_daily_k = stock_daily_k.merge(self.stock_consensus[['TICKER_SYMBOL', 'TRADE_DATE', 'CON_EPS']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left')
                stock_daily_k = stock_daily_k.merge(self.stock_industry[['TICKER_SYMBOL', 'INDUSTRY_ID']], on=['TICKER_SYMBOL'], how='left')
                stock_daily_k = stock_daily_k.merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='left')
                stock_daily_k = stock_daily_k[stock_daily_k['TRADE_DATE'] >= stock_daily_k['SAMPLE_DATE']]
                stock_daily_k['PCT_CHANGE'] = stock_daily_k['PCT_CHANGE'] / 100.0
                industry_nmv_list, industry_ret_list, industry_pettm_list, industry_coneps_list = [], [], [], []
                for idx, industry_id in enumerate(self.industry_list):
                    stock_daily_k_ind = stock_daily_k[stock_daily_k['INDUSTRY_ID'] == industry_id]
                    stock_daily_k_ind = stock_daily_k_ind[['TRADE_DATE', 'TICKER_SYMBOL', 'PCT_CHANGE', 'PE_TTM', 'CON_EPS', 'NEG_MARKET_VALUE']].dropna(subset=['TRADE_DATE', 'TICKER_SYMBOL', 'NEG_MARKET_VALUE'])
                    stock_daily_ret = stock_daily_k_ind.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PCT_CHANGE').sort_index()
                    stock_daily_pettm = stock_daily_k_ind.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PE_TTM').sort_index()
                    stock_daily_pettm = stock_daily_pettm.apply(lambda x: filter_extreme_mad(x), axis=1)
                    stock_daily_coneps = stock_daily_k_ind.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CON_EPS').sort_index()
                    stock_daily_coneps = stock_daily_coneps.apply(lambda x: filter_extreme_mad(x), axis=1)
                    stock_daily_nmv = stock_daily_k_ind.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NEG_MARKET_VALUE').sort_index()
                    stock_daily_weight = stock_daily_nmv.apply(lambda x: x / x.sum(), axis=1)
                    industry_nmv = pd.DataFrame(stock_daily_nmv.sum(axis=1), columns=[industry_id])
                    industry_ret = pd.DataFrame((stock_daily_ret * stock_daily_weight).sum(axis=1), columns=[industry_id])
                    industry_pettm = pd.DataFrame((stock_daily_pettm * stock_daily_weight).sum(axis=1), columns=[industry_id])
                    industry_coneps = pd.DataFrame((stock_daily_coneps * stock_daily_weight).sum(axis=1), columns=[industry_id])
                    industry_nmv_list.append(industry_nmv)
                    industry_ret_list.append(industry_ret)
                    industry_pettm_list.append(industry_pettm)
                    industry_coneps_list.append(industry_coneps)
                    print(idx, len(self.industry_list))
                industry_nmv = pd.concat(industry_nmv_list, axis=1)
                industry_ret = pd.concat(industry_ret_list, axis=1)
                industry_pettm = pd.concat(industry_pettm_list, axis=1)
                industry_coneps = pd.concat(industry_coneps_list, axis=1)
                industry_nmv.to_hdf('{0}style_construction/{1}_{2}/industry_nmv.hdf'.format(self.data_path, industry_type, industry_level), key='table', mode='w')
                industry_ret.to_hdf('{0}style_construction/{1}_{2}/industry_ret.hdf'.format(self.data_path, industry_type, industry_level), key='table', mode='w')
                industry_pettm.to_hdf('{0}style_construction/{1}_{2}/industry_pettm.hdf'.format(self.data_path, industry_type, industry_level), key='table', mode='w')
                industry_coneps.to_hdf('{0}style_construction/{1}_{2}/industry_coneps.hdf'.format(self.data_path, industry_type, industry_level), key='table', mode='w')

                stock_finance = self.stock_finance.sort_values(['TICKER_SYMBOL', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')
                stock_finance = stock_finance.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'END_DATE'}), on=['END_DATE'], how='left')
                stock_finance = stock_finance.merge(self.stock_daily_k[['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE', 'MARKET_VALUE', 'NEG_MARKET_VALUE']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left')
                stock_finance['CLOSE_PRICE'] = stock_finance['CLOSE_PRICE'].replace(0.0, np.nan)
                stock_finance['MARKET_VALUE'] = stock_finance['MARKET_VALUE'].replace(0.0, np.nan)
                stock_finance = stock_finance[(stock_finance['OPER_REVENUE_YOY'] >= -300) & (stock_finance['OPER_REVENUE_YOY'] <= 300)]
                stock_finance = stock_finance[(stock_finance['NET_PROFIT_YOY'] >= -300) & (stock_finance['NET_PROFIT_YOY'] <= 300)]
                or_yoy = stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='OPER_REVENUE_YOY').sort_index()
                or_yoy = or_yoy.rolling(4).mean()
                or_yoy = or_yoy.unstack().reset_index()
                or_yoy.columns = ['TICKER_SYMBOL', 'END_DATE', 'OPER_REVENUE_YOY_MEAN']
                np_yoy = stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='NET_PROFIT_YOY').sort_index()
                np_yoy = np_yoy.rolling(4).mean()
                np_yoy = np_yoy.unstack().reset_index()
                np_yoy.columns = ['TICKER_SYMBOL', 'END_DATE', 'NET_PROFIT_YOY_MEAN']
                stock_finance = stock_finance.merge(or_yoy, on=['TICKER_SYMBOL', 'END_DATE'], how='left').merge(np_yoy, on=['TICKER_SYMBOL', 'END_DATE'], how='left')
                stock_finance['EP_TTM'] = stock_finance['EPS_TTM'] / stock_finance['CLOSE_PRICE']
                stock_finance['BP'] = stock_finance['NAPS'] / stock_finance['CLOSE_PRICE']
                stock_finance['CFP_TTM'] = stock_finance['OCF_TTM'] / stock_finance['CLOSE_PRICE']
                stock_finance['DP_TTM'] = stock_finance['DIVIDEND_TTM'] / stock_finance['MARKET_VALUE']
                stock_finance = stock_finance[['TICKER_SYMBOL', 'END_DATE', 'NEG_MARKET_VALUE', 'OPER_REVENUE_YOY_MEAN', 'NET_PROFIT_YOY_MEAN', 'ROE_TTM', 'EP_TTM', 'BP', 'CFP_TTM', 'DP_TTM']]
                stock_finance = stock_finance.merge(self.stock_industry[['TICKER_SYMBOL', 'INDUSTRY_ID']], on=['TICKER_SYMBOL'], how='left')
                date_list = sorted([date for date in stock_finance['END_DATE'].unique().tolist() if date >= self.start_date and date <= self.end_date and (date[4:6] == '06' or date[4:6] == '12')])
                industry_finance_list = []
                industry_finance_date = pd.DataFrame()
                for date in date_list:
                    stock_finance_date = stock_finance[stock_finance['END_DATE'] == date]
                    total_neg_mv_date = stock_finance_date[['INDUSTRY_ID', 'NEG_MARKET_VALUE']].groupby('INDUSTRY_ID').sum().reset_index().rename(columns={'NEG_MARKET_VALUE': 'TOTAL_NEG_MARKET_VALUE'})
                    stock_finance_date = stock_finance_date.merge(total_neg_mv_date, on=['INDUSTRY_ID'], how='left')
                    for col in ['OPER_REVENUE_YOY_MEAN', 'NET_PROFIT_YOY_MEAN', 'ROE_TTM', 'EP_TTM', 'BP', 'CFP_TTM', 'DP_TTM']:
                        stock_finance_date[col] = filter_extreme_mad(stock_finance_date[col])
                        industry_mean_date = stock_finance_date[['INDUSTRY_ID', col]].groupby('INDUSTRY_ID').mean().rename(columns={col: col + '_INDU'})
                        stock_finance_date = stock_finance_date.merge(industry_mean_date, on=['INDUSTRY_ID'], how='left')
                        stock_finance_date[col] = stock_finance_date.apply(lambda x: x[col + '_INDU'] if np.isnan(x[col]) else x[col], axis=1)
                        stock_finance_date[col] = stock_finance_date[col] * stock_finance_date['NEG_MARKET_VALUE'] / stock_finance_date['TOTAL_NEG_MARKET_VALUE']
                        industry_finance_singal_date = stock_finance_date[['END_DATE', 'INDUSTRY_ID', col]].groupby(['END_DATE', 'INDUSTRY_ID']).sum().reset_index()
                        industry_finance_singal_date[col] = (industry_finance_singal_date[col] - industry_finance_singal_date[col].mean()) / industry_finance_singal_date[col].std(ddof=1)
                        if col == 'OPER_REVENUE_YOY_MEAN':
                            industry_finance_date = industry_finance_singal_date
                        else:
                            industry_finance_date = industry_finance_date.merge(industry_finance_singal_date, on=['END_DATE', 'INDUSTRY_ID'], how='left')
                    industry_finance_list.append(industry_finance_date)
                    print(date)
                industry_finance = pd.concat(industry_finance_list)
                industry_finance = industry_finance[['END_DATE', 'INDUSTRY_ID', 'OPER_REVENUE_YOY_MEAN', 'NET_PROFIT_YOY_MEAN', 'ROE_TTM', 'EP_TTM', 'BP', 'CFP_TTM', 'DP_TTM']]
                industry_finance['GROWTH'] = (industry_finance['OPER_REVENUE_YOY_MEAN'] + industry_finance['NET_PROFIT_YOY_MEAN'] + industry_finance['ROE_TTM']) / 3.0
                industry_finance['VALUE'] = (industry_finance['EP_TTM'] + industry_finance['BP'] + industry_finance['CFP_TTM'] + industry_finance['DP_TTM']) / 4.0
                # 成长因子
                growth = industry_finance.pivot(index='END_DATE', columns='INDUSTRY_ID', values='GROWTH').sort_index()
                growth.loc[self.end_date] = np.nan
                growth = growth.shift().iloc[1:]
                growth.to_hdf('{0}style_construction/{1}_{2}/growth.hdf'.format(self.data_path, industry_type, industry_level), key='table', mode='w')
                # 价值因子
                value = industry_finance.pivot(index='END_DATE', columns='INDUSTRY_ID', values='VALUE').sort_index()
                value.loc[self.end_date] = np.nan
                value = value.shift().iloc[1:]
                value.to_hdf('{0}style_construction/{1}_{2}/value.hdf'.format(self.data_path, industry_type, industry_level), key='table', mode='w')

                industry_nmv = pd.read_hdf('{0}style_construction/{1}_{2}/industry_nmv.hdf'.format(self.data_path, industry_type, industry_level), key='table')
                industry_nmv = industry_nmv.unstack().reset_index()
                industry_nmv.columns = ['INDUSTRY_ID', 'TRADE_DATE', 'NEG_NARKET_VALUE']
                growth = pd.read_hdf('{0}style_construction/{1}_{2}/growth.hdf'.format(self.data_path, industry_type, industry_level), key='table')
                growth = growth.unstack().reset_index().rename(columns={0: 'GROWTH'})
                growth['INDUSTRY_NAME'] = growth['INDUSTRY_ID'].apply(lambda x: self.id_name_dic[x])
                value = pd.read_hdf('{0}style_construction/{1}_{2}/value.hdf'.format(self.data_path, industry_type, industry_level), key='table')
                value = value.unstack().reset_index().rename(columns={0: 'VALUE'})
                value['INDUSTRY_NAME'] = value['INDUSTRY_ID'].apply(lambda x: self.id_name_dic[x])
                date_list = sorted(growth['END_DATE'].unique().tolist())
                growth_industry = pd.DataFrame(index=date_list, columns=range(len(self.industry_list)))
                value_industry = pd.DataFrame(index=date_list, columns=range(len(self.industry_list)))
                for date in date_list:
                    trade_date = self.trade_df[self.trade_df['TRADE_DATE'] <= date]['TRADE_DATE'].iloc[-1]
                    industry_nmv_date = industry_nmv[industry_nmv['TRADE_DATE'] == trade_date]
                    industry_nmv_tail_date = industry_nmv_date.sort_values('NEG_NARKET_VALUE', ascending=False).tail(int(round(len(self.industry_list) / 10.0, 0)))
                    growth_date = growth[growth['END_DATE'] == date]
                    value_date = value[value['END_DATE'] == date]
                    growth_date = growth_date[~growth_date['INDUSTRY_ID'].isin(industry_nmv_tail_date['INDUSTRY_ID'].unique().tolist())]
                    value_date = value_date[~value_date['INDUSTRY_ID'].isin(industry_nmv_tail_date['INDUSTRY_ID'].unique().tolist())]
                    ################## v1 ##################
                    # growth_industry_date = growth_date.sort_values('GROWTH', ascending=False).head(int(len(self.industry_list) / 3))
                    # value_industry_date = value_date.sort_values('VALUE', ascending=False).head(int(len(self.industry_list) / 3))
                    ################## v2 ##################
                    # growth_top_date = growth_date.sort_values('GROWTH', ascending=False).head(int(len(self.industry_list) / 3))
                    # value_top_date = value_date.sort_values('VALUE', ascending=False).head(int(len(self.industry_list) / 3))
                    # growth_industry_date = growth_date[~growth_date['INDUSTRY_ID'].isin(value_top_date['INDUSTRY_ID'].unique().tolist())].sort_values('GROWTH', ascending=False).head(int(len(self.industry_list) / 3))
                    # value_industry_date = value_date[~value_date['INDUSTRY_ID'].isin(growth_top_date['INDUSTRY_ID'].unique().tolist())].sort_values('VALUE', ascending=False).head(int(len(self.industry_list) / 3))
                    ################## v3 ##################
                    # growth_top_date = growth_date.sort_values('GROWTH', ascending=False).head(int(len(self.industry_list) / 3))
                    # value_top_date = value_date.sort_values('VALUE', ascending=False).head(int(len(self.industry_list) / 3))
                    # intersection = set(growth_top_date['INDUSTRY_ID'].unique().tolist()).intersection(set(value_top_date['INDUSTRY_ID'].unique().tolist()))
                    # growth_industry_date = growth_date.sort_values('GROWTH', ascending=False).head(int(len(self.industry_list) / 3) + len(intersection))
                    # value_industry_date = value_date.sort_values('VALUE', ascending=False).head(int(len(self.industry_list) / 3) + len(intersection))
                    ########################################
                    value_industry_date = value_date.sort_values('VALUE', ascending=False).head(int(round(len(self.industry_list) / 3.0, 0)))
                    growth_industry_date = growth_date[~growth_date['INDUSTRY_ID'].isin(value_industry_date['INDUSTRY_ID'].unique().tolist())].sort_values('GROWTH', ascending=False).head(int(round(len(self.industry_list) / 3.0, 0)))
                    ########################################
                    growth_industry.loc[date].iloc[:len(growth_industry_date)] = growth_industry_date['INDUSTRY_ID'].values
                    value_industry.loc[date].iloc[:len(value_industry_date)] = value_industry_date['INDUSTRY_ID'].values
                growth_industry.replace(self.id_name_dic).to_excel('{0}style_construction/{1}_{2}/growth_industry.xlsx'.format(self.data_path, industry_type, industry_level))
                value_industry.replace(self.id_name_dic).to_excel('{0}style_construction/{1}_{2}/value_industry.xlsx'.format(self.data_path, industry_type, industry_level))

                industry_nmv = pd.read_hdf('{0}style_construction/{1}_{2}/industry_nmv.hdf'.format(self.data_path, industry_type, industry_level), key='table')
                industry_ret = pd.read_hdf('{0}style_construction/{1}_{2}/industry_ret.hdf'.format(self.data_path, industry_type, industry_level), key='table')
                industry_pettm = pd.read_hdf('{0}style_construction/{1}_{2}/industry_pettm.hdf'.format(self.data_path, industry_type, industry_level), key='table')
                industry_coneps = pd.read_hdf('{0}style_construction/{1}_{2}/industry_coneps.hdf'.format(self.data_path, industry_type, industry_level), key='table')
                date_list = sorted(list(set(growth_industry.index.unique().tolist() + [self.tracking_date])))
                style_ret_list, style_pettm_list, style_coneps_list = [], [], []
                for i in range(len(date_list) - 1):
                    start = self.trade_df[self.trade_df['TRADE_DATE'] <= date_list[i]]['TRADE_DATE'].iloc[-1]
                    end = self.trade_df[self.trade_df['TRADE_DATE'] <= date_list[i + 1]]['TRADE_DATE'].iloc[-1]
                    growth_indu_list = growth_industry.loc[date_list[i]].dropna().unique().tolist()
                    growth_nmv = industry_nmv[growth_indu_list].loc[start: end]
                    growth_weight = growth_nmv.apply(lambda x: x / x.sum(), axis=1)
                    growth_ret = (industry_ret[growth_indu_list].loc[start: end]) * growth_weight
                    growth_ret = pd.DataFrame(growth_ret.sum(axis=1), columns=['GROWTH'])
                    growth_pettm = (industry_pettm[growth_indu_list].loc[start: end]) * growth_weight
                    growth_pettm = pd.DataFrame(growth_pettm.sum(axis=1), columns=['GROWTH_PETTM'])
                    growth_coneps = (industry_coneps[growth_indu_list].loc[start: end]) * growth_weight
                    growth_coneps = pd.DataFrame(growth_coneps.sum(axis=1), columns=['GROWTH_CONEPS'])
                    value_indu_list = value_industry.loc[date_list[i]].dropna().unique().tolist()
                    value_nmv = industry_nmv[value_indu_list].loc[start: end]
                    value_weight = value_nmv.apply(lambda x: x / x.sum(), axis=1)
                    value_ret = (industry_ret[value_indu_list].loc[start: end]) * value_weight
                    value_ret = pd.DataFrame(value_ret.sum(axis=1), columns=['VALUE'])
                    value_pettm = (industry_pettm[value_indu_list].loc[start: end]) * value_weight
                    value_pettm = pd.DataFrame(value_pettm.sum(axis=1), columns=['VALUE_PETTM'])
                    value_coneps = (industry_coneps[value_indu_list].loc[start: end]) * value_weight
                    value_coneps = pd.DataFrame(value_coneps.sum(axis=1), columns=['VALUE_CONEPS'])
                    style_ret = pd.concat([growth_ret, value_ret], axis=1)
                    style_pettm = pd.concat([growth_pettm, value_pettm], axis=1)
                    style_coneps = pd.concat([growth_coneps, value_coneps], axis=1)
                    if i != 0:
                        style_ret = style_ret.iloc[1:]
                        style_pettm = style_pettm.iloc[1:]
                        style_coneps = style_coneps.iloc[1:]
                    style_ret_list.append(style_ret)
                    style_pettm_list.append(style_pettm)
                    style_coneps_list.append(style_coneps)
                    print(start, end)
                style_ret = pd.concat(style_ret_list)
                style_ret.iloc[0] = 0.0
                style_nav = (style_ret + 1).cumprod()
                style_pettm = pd.concat(style_pettm_list)
                style_coneps = pd.concat(style_coneps_list)
                style = pd.concat([style_nav, style_pettm, style_coneps], axis=1)
                style.to_excel('{0}style_construction/{1}_{2}/style.xlsx'.format(self.data_path, industry_type, industry_level))

                # stock_daily_k = self.stock_daily_k.merge(self.stock_industry[['TICKER_SYMBOL', 'INDUSTRY_ID']], on=['TICKER_SYMBOL'], how='left')
                # stock_daily_k = stock_daily_k.merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='left')
                # stock_daily_k = stock_daily_k[stock_daily_k['TRADE_DATE'] >= stock_daily_k['SAMPLE_DATE']]
                # stock_daily_k['PCT_CHANGE'] = stock_daily_k['PCT_CHANGE'] / 100.0
                # date_list = growth_industry.index.unique().tolist()
                # style_ret_list = []
                # for i in range(len(date_list) - 1):
                #     start = self.trade_df[self.trade_df['TRADE_DATE'] <= date_list[i]]['TRADE_DATE'].iloc[-1]
                #     end = self.trade_df[self.trade_df['TRADE_DATE'] <= date_list[i + 1]]['TRADE_DATE'].iloc[-1]
                #     growth_indu_list = growth_industry.loc[date_list[i]].dropna().unique().tolist()
                #     growth_stock = stock_daily_k[stock_daily_k['INDUSTRY_ID'].isin(growth_indu_list)]
                #     growth_stock = growth_stock[['TRADE_DATE', 'TICKER_SYMBOL', 'PCT_CHANGE', 'NEG_MARKET_VALUE']].dropna()
                #     growth_nmv = growth_stock.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NEG_MARKET_VALUE').loc[start: end]
                #     growth_weight = growth_nmv.apply(lambda x: x / x.sum(), axis=1)
                #     growth_ret = growth_stock.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PCT_CHANGE').loc[start: end]
                #     growth_ret = growth_ret * growth_weight
                #     growth_ret = pd.DataFrame(growth_ret.sum(axis=1), columns=['GROWTH'])
                #     value_indu_list = value_industry.loc[date_list[i]].dropna().unique().tolist()
                #     value_stock = stock_daily_k[stock_daily_k['INDUSTRY_ID'].isin(value_indu_list)]
                #     value_stock = value_stock[['TRADE_DATE', 'TICKER_SYMBOL', 'PCT_CHANGE', 'NEG_MARKET_VALUE']].dropna()
                #     value_nmv = value_stock.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='NEG_MARKET_VALUE').loc[start: end]
                #     value_weight = value_nmv.apply(lambda x: x / x.sum(), axis=1)
                #     value_ret = value_stock.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='PCT_CHANGE').loc[start: end]
                #     value_ret = value_ret * value_weight
                #     value_ret = pd.DataFrame(value_ret.sum(axis=1), columns=['VALUE'])
                #     style_ret = pd.concat([growth_ret, value_ret], axis=1)
                #     if i != 0:
                #         style_ret = style_ret.iloc[1:]
                #     style_ret_list.append(style_ret)
                #     print(start, end)
                # style_ret = pd.concat(style_ret_list)
                # style_ret.iloc[0] = 0.0
                # style_nav = (style_ret + 1).cumprod()
                # style_nav.to_excel('{0}style_construction/{1}_{2}/style_nav_整体.xlsx'.format(self.data_path, industry_type, industry_level))
                #
                # stock_daily_k = self.stock_daily_k.merge(self.stock_industry[['TICKER_SYMBOL', 'INDUSTRY_ID']], on=['TICKER_SYMBOL'], how='left')
                # date_list = growth_industry.index.unique().tolist()
                # style_index_cons_list = []
                # for date in date_list:
                #     trade_date = self.trade_df[self.trade_df['TRADE_DATE'] <= date]['TRADE_DATE'].iloc[-1]
                #     stock_daily_k_date = stock_daily_k[stock_daily_k['TRADE_DATE'] == trade_date]
                #     growth_indu_list = growth_industry.loc[date].dropna().unique().tolist()
                #     growth_index_cons = stock_daily_k_date[stock_daily_k_date['INDUSTRY_ID'].isin(growth_indu_list)]
                #     growth_index_cons['INDEX_NAME'] = '成长'
                #     growth_index_cons['END_DATE'] = date
                #     value_indu_list = value_industry.loc[date].dropna().unique().tolist()
                #     value_index_cons = stock_daily_k_date[stock_daily_k_date['INDUSTRY_ID'].isin(value_indu_list)]
                #     value_index_cons['INDEX_NAME'] = '价值'
                #     value_index_cons['END_DATE'] = date
                #     style_index_cons = pd.concat([growth_index_cons, value_index_cons])
                #     style_index_cons_list.append(style_index_cons)
                # style_index_cons = pd.concat(style_index_cons_list)
                # style_index_cons['INDUSTRY_NAME'] = style_index_cons['INDUSTRY_ID'].apply(lambda x: self.id_name_dic[x])
                # style_index_cons['WEIGHT'] = np.nan
                # style_index_cons = style_index_cons[['INDEX_NAME', 'TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'WEIGHT', 'INDUSTRY_NAME', 'END_DATE']]
                # self.total_market_value = self.stock_daily_k[['TRADE_DATE', 'MARKET_VALUE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum().reset_index().rename(columns={'MARKET_VALUE': 'TOTAL_MARKET_VALUE', 'NEG_MARKET_VALUE': 'TOTAL_NEG_MARKET_VALUE'})
                # style_index_cons = style_index_cons.merge(self.stock_daily_k[['TICKER_SYMBOL', 'TRADE_DATE', 'MARKET_VALUE', 'NEG_MARKET_VALUE']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left').merge(self.total_market_value, on=['TRADE_DATE'], how='left')
                # style_index_cons['MARKET_VALUE_RATIO'] = style_index_cons['MARKET_VALUE'] / style_index_cons['TOTAL_MARKET_VALUE']
                # style_index_cons['NEG_MARKET_VALUE_RATIO'] = style_index_cons['NEG_MARKET_VALUE'] / style_index_cons['TOTAL_NEG_MARKET_VALUE']
                # style_index_cons = style_index_cons.merge(self.stock_valuation[['TICKER_SYMBOL', 'TRADE_DATE', 'PE_TTM']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left').merge(self.stock_finance[['TICKER_SYMBOL', 'END_DATE', 'ROE_TTM']], on=['TICKER_SYMBOL', 'END_DATE'], how='left')
                # style_index_cons.to_hdf('{0}style_construction/{1}_{2}/style_index_cons.hdf'.format(self.data_path, industry_type, industry_level), key='table', mode='w')
                #
                # style_index_cons = pd.read_hdf('{0}style_construction/{1}_{2}/style_index_cons.hdf'.format(self.data_path, industry_type, industry_level), key='table')
                # style_index_cons_ori = pd.read_hdf('{0}style_construction/style_index_cons.hdf'.format(self.data_path), key='table')
                # style_index_cons_ori = style_index_cons_ori[style_index_cons_ori['TRADE_DATE'].str.slice(4, 6).isin(['06', '12'])]
                # style_index_cons_ori = style_index_cons_ori.dropna()
                # style_index_cons = pd.concat([style_index_cons, style_index_cons_ori])
                #
                # # 总市值占比
                # mv = style_index_cons[['INDEX_NAME', 'END_DATE', 'MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE']).sum()
                # total_mv = style_index_cons[['INDEX_NAME', 'END_DATE', 'TOTAL_MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE']).mean()
                # mv = mv.merge(total_mv, left_index=True, right_index=True, how='left').reset_index()
                # mv['MARKET_VALUE_RATIO'] = mv['MARKET_VALUE'] / mv['TOTAL_MARKET_VALUE']
                # mv = mv.pivot(index='END_DATE', columns='INDEX_NAME', values='MARKET_VALUE_RATIO').sort_index()
                # mv_disp = mv.copy(deep=True)
                # mv_disp = mv_disp[(mv_disp.index > self.start_date) & (mv_disp.index <= self.end_date)]
                # mv_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), mv_disp.index)
                # fig, ax = plt.subplots(figsize=(8, 4))
                # ax.plot(mv_disp.index, mv_disp['成长'].values, color=line_color_list[0], label='成长', linewidth=2)
                # ax.plot(mv_disp.index, mv_disp['价值'].values, color=line_color_list[0], alpha=0.5, label='价值', linewidth=2)
                # ax.plot(mv_disp.index, mv_disp['国证成长'].values, color=line_color_list[1], label='国证成长', linewidth=2)
                # ax.plot(mv_disp.index, mv_disp['国证价值'].values, color=line_color_list[1], alpha=0.5, label='国证价值', linewidth=2)
                # ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
                # plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=4, frameon=False)
                # plt.title('总市值占比', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
                # plt.tight_layout()
                # sns.despine(top=True, right=True, left=False, bottom=False)
                # plt.savefig('{0}style_construction/{1}_{2}/总市值占比.png'.format(self.data_path, industry_type, industry_level))
                #
                # # 流通市值占比
                # neg_mv = style_index_cons[['INDEX_NAME', 'END_DATE', 'NEG_MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE']).sum()
                # total_neg_mv = style_index_cons[['INDEX_NAME', 'END_DATE', 'TOTAL_NEG_MARKET_VALUE']].groupby(['INDEX_NAME', 'END_DATE']).mean()
                # neg_mv = neg_mv.merge(total_neg_mv, left_index=True, right_index=True, how='left').reset_index()
                # neg_mv['NEG_MARKET_VALUE_RATIO'] = neg_mv['NEG_MARKET_VALUE'] / neg_mv['TOTAL_NEG_MARKET_VALUE']
                # neg_mv = neg_mv.pivot(index='END_DATE', columns='INDEX_NAME', values='NEG_MARKET_VALUE_RATIO').sort_index()
                # neg_mv_disp = neg_mv.copy(deep=True)
                # neg_mv_disp = neg_mv_disp[(neg_mv_disp.index > self.start_date) & (neg_mv_disp.index <= self.end_date)]
                # neg_mv_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), neg_mv_disp.index)
                # fig, ax = plt.subplots(figsize=(8, 4))
                # ax.plot(neg_mv_disp.index, neg_mv_disp['成长'].values, color=line_color_list[0], label='成长', linewidth=2)
                # ax.plot(neg_mv_disp.index, neg_mv_disp['价值'].values, color=line_color_list[0], alpha=0.5, label='价值', linewidth=2)
                # ax.plot(neg_mv_disp.index, neg_mv_disp['国证成长'].values, color=line_color_list[1], label='国证成长', linewidth=2)
                # ax.plot(neg_mv_disp.index, neg_mv_disp['国证价值'].values, color=line_color_list[1], alpha=0.5, label='国证价值', linewidth=2)
                # ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
                # plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=4, frameon=False)
                # plt.title('流通市值占比', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
                # plt.tight_layout()
                # sns.despine(top=True, right=True, left=False, bottom=False)
                # plt.savefig('{0}style_construction/{1}_{2}/流通市值占比.png'.format(self.data_path, industry_type, industry_level))
                #
                # # PE_TTM中位数
                # pe = style_index_cons[['INDEX_NAME', 'END_DATE', 'PE_TTM']].groupby(['INDEX_NAME', 'END_DATE']).median().reset_index()
                # pe = pe.pivot(index='END_DATE', columns='INDEX_NAME', values='PE_TTM').sort_index()
                # pe_disp = pe.copy(deep=True)
                # pe_disp = pe_disp[(pe_disp.index > self.start_date) & (pe_disp.index <= self.end_date)]
                # pe_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), pe_disp.index)
                # fig, ax = plt.subplots(figsize=(8, 4))
                # ax.plot(pe_disp.index, pe_disp['成长'].values, color=line_color_list[0], label='成长', linewidth=2)
                # ax.plot(pe_disp.index, pe_disp['价值'].values, color=line_color_list[0], alpha=0.5, label='价值', linewidth=2)
                # ax.plot(pe_disp.index, pe_disp['国证成长'].values, color=line_color_list[1], label='国证成长', linewidth=2)
                # ax.plot(pe_disp.index, pe_disp['国证价值'].values, color=line_color_list[1], alpha=0.5, label='国证价值', linewidth=2)
                # plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=4, frameon=False)
                # plt.title('PE_TTM中位数', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
                # plt.tight_layout()
                # sns.despine(top=True, right=True, left=False, bottom=False)
                # plt.savefig('{0}style_construction/{1}_{2}/PE_TTM中位数.png'.format(self.data_path, industry_type, industry_level))
                #
                # # ROE_TTM
                # roe = style_index_cons[['INDEX_NAME', 'END_DATE', 'ROE_TTM']].groupby(['INDEX_NAME', 'END_DATE']).median().reset_index()
                # roe = roe.pivot(index='END_DATE', columns='INDEX_NAME', values='ROE_TTM').sort_index()
                # roe_disp = roe.copy(deep=True)
                # roe_disp = roe_disp[(roe_disp.index > self.start_date) & (roe_disp.index <= self.end_date)]
                # roe_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), roe_disp.index)
                # fig, ax = plt.subplots(figsize=(8, 4))
                # ax.plot(roe_disp.index, roe_disp['成长'].values, color=line_color_list[0], label='成长', linewidth=2)
                # ax.plot(roe_disp.index, roe_disp['价值'].values, color=line_color_list[0], alpha=0.5, label='价值', linewidth=2)
                # ax.plot(roe_disp.index, roe_disp['国证成长'].values, color=line_color_list[1], label='国证成长', linewidth=2)
                # ax.plot(roe_disp.index, roe_disp['国证价值'].values, color=line_color_list[1], alpha=0.5, label='国证价值', linewidth=2)
                # plt.legend(loc=8, bbox_to_anchor=(0.5, -0.27), ncol=4, frameon=False)
                # plt.title('ROE_TTM中位数', fontdict={'font': 'SimHei', 'weight': 'bold', 'size': 12})
                # plt.tight_layout()
                # sns.despine(top=True, right=True, left=False, bottom=False)
                # plt.savefig('{0}style_construction/{1}_{2}/ROE_TTM中位数.png'.format(self.data_path, industry_type, industry_level))
                #
                # # 行业分布
                # growth_index_cons = style_index_cons[style_index_cons['INDEX_NAME'] == '成长']
                # value_index_cons = style_index_cons[style_index_cons['INDEX_NAME'] == '价值']
                # growth_index_cons = growth_index_cons[['END_DATE', 'INDUSTRY_NAME', 'NEG_MARKET_VALUE']].groupby(['END_DATE', 'INDUSTRY_NAME']).sum().reset_index()
                # value_index_cons = value_index_cons[['END_DATE', 'INDUSTRY_NAME', 'NEG_MARKET_VALUE']].groupby(['END_DATE', 'INDUSTRY_NAME']).sum().reset_index()
                # growth_cons_industry = growth_index_cons.pivot(index='END_DATE', columns='INDUSTRY_NAME', values='NEG_MARKET_VALUE').sort_index()
                # value_cons_industry = value_index_cons.pivot(index='END_DATE', columns='INDUSTRY_NAME', values='NEG_MARKET_VALUE').sort_index()
                # growth_cons_industry.to_excel('{0}style_construction/{1}_{2}/growth_cons_industry.xlsx'.format(self.data_path, industry_type, industry_level))
                # value_cons_industry.to_excel('{0}style_construction/{1}_{2}/value_cons_industry.xlsx'.format(self.data_path, industry_type, industry_level))
        return

    def strategy(self):
        style_timing = pd.read_hdf('{0}style_construction/strategy/style_timing.hdf'.format(self.data_path), key='table')
        style_timing['成长仓位'] = style_timing['成长_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        style_timing['价值仓位'] = style_timing['价值_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        style_timing = style_timing[['成长仓位', '价值仓位']]
        new_style_index = pd.read_excel('{0}style_construction/strategy/style_nav.xlsx'.format(self.data_path))
        new_style_index = new_style_index.rename(columns={'GROWTH': '成长', 'VALUE': '价值'})
        new_style_index['TRADE_DATE'] = new_style_index['TRADE_DATE'].astype(str)
        new_style_index = new_style_index[['TRADE_DATE', '成长', '价值']].set_index('TRADE_DATE')
        industry_index = ['801010', '801030', '801040', '801050', '801080', '801110', '801120', '801130', '801140', '801150',
                          '801160', '801170', '801180', '801200', '801210', '801230', '801710', '801720', '801730', '801740',
                          '801750', '801760', '801770', '801780', '801790', '801880', '801890', '801950', '801960', '801970', '801980']
        style_index = HBDB().read_index_daily_k_given_date_and_indexs('20100630', ['399370', '399371', '881001'] + industry_index)
        style_index.to_hdf('{0}style_construction/strategy/style_index_all.xlsx'.format(self.data_path), key='table', mode='w')
        style_index = pd.read_hdf('{0}style_construction/strategy/style_index_all.xlsx'.format(self.data_path), key='table')
        style_index = style_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].astype(str)
        style_index = style_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX')
        style_index = style_index.rename(columns={'399370': '国证成长', '399371': '国证价值', '881001': '万得全A'})
        style_index = style_timing.merge(new_style_index, left_index=True, right_index=True, how='right').merge(style_index, left_index=True, right_index=True, how='left')
        style_index[['成长仓位', '价值仓位']] = style_index[['成长仓位', '价值仓位']].fillna(method='ffill')
        style_index = style_index.dropna()
        style_index_ret = style_index.copy(deep=True)
        style_index_ret.iloc[:, 2:] = style_index_ret.iloc[:, 2:].pct_change().fillna(0.0)
        style_index_ret.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index_ret.index)

        style_index_ret['成长价值择时收益'] = style_index_ret['成长仓位'] * style_index_ret['成长'] + style_index_ret['价值仓位'] * style_index_ret['价值']
        style_index_ret['成长价值等权收益'] = 0.5 * style_index_ret['成长'] + 0.5 * style_index_ret['价值']
        style_index_ret['成长价值择时相对风格等权超额收益'] = style_index_ret['成长价值择时收益'] - style_index_ret['成长价值等权收益']
        style_index_ret['成长价值择时净值'] = (style_index_ret['成长价值择时收益'] + 1.0).cumprod()
        style_index_ret['成长价值等权净值'] = (style_index_ret['成长价值等权收益'] + 1.0).cumprod()
        style_index_ret['成长价值择时相对风格等权超额净值'] = (style_index_ret['成长价值择时相对风格等权超额收益'] + 1.0).cumprod()

        style_index_ret['国证成长价值择时收益'] = style_index_ret['成长仓位'] * style_index_ret['国证成长'] + style_index_ret['价值仓位'] * style_index_ret['国证价值']
        style_index_ret['国证成长价值等权收益'] = 0.5 * style_index_ret['国证成长'] + 0.5 * style_index_ret['国证价值']
        style_index_ret['国证成长价值择时相对国证风格等权超额收益'] = style_index_ret['国证成长价值择时收益'] - style_index_ret['国证成长价值等权收益']
        style_index_ret['国证成长价值择时净值'] = (style_index_ret['国证成长价值择时收益'] + 1.0).cumprod()
        style_index_ret['国证成长价值等权净值'] = (style_index_ret['国证成长价值等权收益'] + 1.0).cumprod()
        style_index_ret['国证成长价值择时相对国证风格等权超额净值'] = (style_index_ret['国证成长价值择时相对国证风格等权超额收益'] + 1.0).cumprod()

        style_index_ret['全行业等权收益'] = style_index_ret[industry_index].mean(axis=1)
        style_index_ret['成长价值择时相对全行业等权超额收益'] = style_index_ret['成长价值择时收益'] - style_index_ret['全行业等权收益']
        style_index_ret['国证成长价值择时相对全行业等权超额收益'] = style_index_ret['国证成长价值择时收益'] - style_index_ret['全行业等权收益']
        style_index_ret['全行业等权净值'] = (style_index_ret['全行业等权收益'] + 1.0).cumprod()
        style_index_ret['成长价值择时相对全行业等权超额净值'] = (style_index_ret['成长价值择时相对全行业等权超额收益'] + 1.0).cumprod()
        style_index_ret['国证成长价值择时相对全行业等权超额净值'] = (style_index_ret['国证成长价值择时相对全行业等权超额收益'] + 1.0).cumprod()

        style_index_ret['成长价值择时相对万得全A超额收益'] = style_index_ret['成长价值择时收益'] - style_index_ret['万得全A']
        style_index_ret['国证成长价值择时相对万得全A超额收益'] = style_index_ret['国证成长价值择时收益'] - style_index_ret['万得全A']
        style_index_ret['万得全A净值'] = (style_index_ret['万得全A'] + 1.0).cumprod()
        style_index_ret['成长价值择时相对万得全A超额净值'] = (style_index_ret['成长价值择时相对万得全A超额收益'] + 1.0).cumprod()
        style_index_ret['国证成长价值择时相对万得全A超额净值'] = (style_index_ret['国证成长价值择时相对万得全A超额收益'] + 1.0).cumprod()

        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        ax[0].plot(style_index_ret.index, style_index_ret['成长价值择时净值'].values, color=line_color_list[0], label='成长价值择时', linewidth=2)
        ax[0].plot(style_index_ret.index, style_index_ret['成长价值等权净值'].values, color=line_color_list[0], alpha=0.5, label='成长价值等权', linewidth=2)
        ax[0].plot(style_index_ret.index, style_index_ret['国证成长价值择时净值'].values, color=line_color_list[1], label='国证成长价值择时', linewidth=2)
        ax[0].plot(style_index_ret.index, style_index_ret['国证成长价值等权净值'].values, color=line_color_list[1], alpha=0.5, label='国证成长价值等权', linewidth=2)
        ax[0].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False)
        ax[0].set_title('净值', fontdict={'weight': 'bold', 'size': 12})
        ax[1].plot(style_index_ret.index, style_index_ret['成长价值择时相对风格等权超额净值'].values, color=line_color_list[0], label='成长价值择时相对风格等权', linewidth=2)
        ax[1].plot(style_index_ret.index, style_index_ret['国证成长价值择时相对国证风格等权超额净值'].values, color=line_color_list[1], label='国证成长价值择时相对国证风格等权', linewidth=2)
        ax[1].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
        ax[1].set_title('超额净值', fontdict={'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/strategy/择时策略_相对风格等权.png'.format(data_path))
        result = get_performance(style_index_ret[['成长价值择时净值', '成长价值等权净值']], 250)
        gz_result = get_performance(style_index_ret[['国证成长价值择时净值', '国证成长价值等权净值']], 250)
        result = pd.concat([result, gz_result])
        result.to_excel('{0}style_construction/strategy/择时策略_相对风格等权.xlsx'.format(data_path))

        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        ax[0].plot(style_index_ret.index, style_index_ret['成长价值择时净值'].values, color=line_color_list[0], label='成长价值择时', linewidth=2)
        ax[0].plot(style_index_ret.index, style_index_ret['国证成长价值择时净值'].values, color=line_color_list[1], label='国证成长价值择时', linewidth=2)
        ax[0].plot(style_index_ret.index, style_index_ret['全行业等权净值'].values, color=line_color_list[2], label='全行业等权', linewidth=2)
        ax[0].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
        ax[0].set_title('净值', fontdict={'weight': 'bold', 'size': 12})
        ax[1].plot(style_index_ret.index, style_index_ret['成长价值择时相对全行业等权超额净值'].values, color=line_color_list[0], label='成长价值择时相对全行业等权', linewidth=2)
        ax[1].plot(style_index_ret.index, style_index_ret['国证成长价值择时相对全行业等权超额净值'].values, color=line_color_list[1], label='国证成长价值择时相对全行业等权', linewidth=2)
        ax[1].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
        ax[1].set_title('超额净值', fontdict={'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/strategy/择时策略_相对全行业等权.png'.format(data_path))
        result = get_performance(style_index_ret[['成长价值择时净值', '全行业等权净值']], 250)
        gz_result = get_performance(style_index_ret[['国证成长价值择时净值', '全行业等权净值']], 250)
        result = pd.concat([result, gz_result])
        result.to_excel('{0}style_construction/strategy/择时策略_相对全行业等权.xlsx'.format(data_path))

        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        ax[0].plot(style_index_ret.index, style_index_ret['成长价值择时净值'].values, color=line_color_list[0], label='成长价值择时', linewidth=2)
        ax[0].plot(style_index_ret.index, style_index_ret['国证成长价值择时净值'].values, color=line_color_list[1], label='国证成长价值择时', linewidth=2)
        ax[0].plot(style_index_ret.index, style_index_ret['万得全A净值'].values, color=line_color_list[2], label='万得全A', linewidth=2)
        ax[0].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
        ax[0].set_title('净值', fontdict={'weight': 'bold', 'size': 12})
        ax[1].plot(style_index_ret.index, style_index_ret['成长价值择时相对万得全A超额净值'].values, color=line_color_list[0], label='成长价值择时相对万得全A', linewidth=2)
        ax[1].plot(style_index_ret.index, style_index_ret['国证成长价值择时相对万得全A超额净值'].values, color=line_color_list[1], label='国证成长价值择时相对万得全A', linewidth=2)
        ax[1].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
        ax[1].set_title('超额净值', fontdict={'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/strategy/择时策略_相对万得全A.png'.format(data_path))
        result = get_performance(style_index_ret[['成长价值择时净值', '万得全A净值']], 250)
        gz_result = get_performance(style_index_ret[['国证成长价值择时净值', '万得全A净值']], 250)
        result = pd.concat([result, gz_result])
        result.to_excel('{0}style_construction/strategy/择时策略_相对万得全A.xlsx'.format(data_path))

        size_timing = pd.read_hdf('{0}style_construction/strategy/size_timing.hdf'.format(self.data_path), key='table')
        size_timing['大盘仓位'] = size_timing['大盘_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        size_timing['中小盘仓位'] = size_timing['中小盘_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        size_timing = size_timing[['大盘仓位', '中小盘仓位']]
        size_index = HBDB().read_index_daily_k_given_date_and_indexs('20100630', ['000300', '000852', '399314', '399401', '881001'])
        size_index.to_hdf('{0}style_construction/strategy/size_index_all.xlsx'.format(self.data_path), key='table', mode='w')
        size_index = pd.read_hdf('{0}style_construction/strategy/size_index_all.xlsx'.format(self.data_path), key='table')
        size_index = size_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_index['TRADE_DATE'] = size_index['TRADE_DATE'].astype(str)
        size_index = size_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX')
        size_index = size_index.rename(columns={'000300': '沪深300', '000852': '中证1000', '399314': '巨潮大盘', '399401': '巨潮中小盘', '881001': '万得全A'})
        size_index = size_timing.merge(size_index, left_index=True, right_index=True, how='right')
        size_index[['大盘仓位', '中小盘仓位']] = size_index[['大盘仓位', '中小盘仓位']].fillna(method='ffill')
        size_index = size_index.dropna()
        size_index_ret = size_index.copy(deep=True)
        size_index_ret.iloc[:, 2:] = size_index_ret.iloc[:, 2:].pct_change().fillna(0.0)
        size_index_ret.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_index_ret.index)

        size_index_ret['大中小盘择时收益'] = size_index_ret['大盘仓位'] * size_index_ret['沪深300'] + size_index_ret['中小盘仓位'] * size_index_ret['中证1000']
        size_index_ret['大中小盘等权收益'] = 0.5 * size_index_ret['沪深300'] + 0.5 * size_index_ret['中证1000']
        size_index_ret['大中小盘择时相对风格等权超额收益'] = size_index_ret['大中小盘择时收益'] - size_index_ret['大中小盘等权收益']
        size_index_ret['大中小盘择时净值'] = (size_index_ret['大中小盘择时收益'] + 1.0).cumprod()
        size_index_ret['大中小盘等权净值'] = (size_index_ret['大中小盘等权收益'] + 1.0).cumprod()
        size_index_ret['大中小盘择时相对风格等权超额净值'] = (size_index_ret['大中小盘择时相对风格等权超额收益'] + 1.0).cumprod()

        size_index_ret['巨潮大中小盘择时收益'] = size_index_ret['大盘仓位'] * size_index_ret['巨潮大盘'] + size_index_ret['中小盘仓位'] * size_index_ret['巨潮中小盘']
        size_index_ret['巨潮大中小盘等权收益'] = 0.5 * size_index_ret['巨潮大盘'] + 0.5 * size_index_ret['巨潮中小盘']
        size_index_ret['巨潮大中小盘择时相对巨潮风格等权超额收益'] = size_index_ret['巨潮大中小盘择时收益'] - size_index_ret['巨潮大中小盘等权收益']
        size_index_ret['巨潮大中小盘择时净值'] = (size_index_ret['巨潮大中小盘择时收益'] + 1.0).cumprod()
        size_index_ret['巨潮大中小盘等权净值'] = (size_index_ret['巨潮大中小盘等权收益'] + 1.0).cumprod()
        size_index_ret['巨潮大中小盘择时相对巨潮风格等权超额净值'] = (size_index_ret['巨潮大中小盘择时相对巨潮风格等权超额收益'] + 1.0).cumprod()

        size_index_ret['大中小盘择时相对万得全A超额收益'] = size_index_ret['大中小盘择时收益'] - size_index_ret['万得全A']
        size_index_ret['巨潮大中小盘择时相对万得全A超额收益'] = size_index_ret['巨潮大中小盘择时收益'] - size_index_ret['万得全A']
        size_index_ret['万得全A净值'] = (size_index_ret['万得全A'] + 1.0).cumprod()
        size_index_ret['大中小盘择时相对万得全A超额净值'] = (size_index_ret['大中小盘择时相对万得全A超额收益'] + 1.0).cumprod()
        size_index_ret['巨潮大中小盘择时相对万得全A超额净值'] = (size_index_ret['巨潮大中小盘择时相对万得全A超额收益'] + 1.0).cumprod()

        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        ax[0].plot(size_index_ret.index, size_index_ret['大中小盘择时净值'].values, color=line_color_list[0], label='沪深300/中证1000择时', linewidth=2)
        ax[0].plot(size_index_ret.index, size_index_ret['大中小盘等权净值'].values, color=line_color_list[0], alpha=0.5, label='沪深300/中证1000等权', linewidth=2)
        ax[0].plot(size_index_ret.index, size_index_ret['巨潮大中小盘择时净值'].values, color=line_color_list[1], label='巨潮大盘/巨潮中小盘择时', linewidth=2)
        ax[0].plot(size_index_ret.index, size_index_ret['巨潮大中小盘等权净值'].values, color=line_color_list[1], alpha=0.5, label='巨潮大盘/巨潮中小盘等权', linewidth=2)
        ax[0].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False)
        ax[0].set_title('净值', fontdict={'weight': 'bold', 'size': 12})
        ax[1].plot(size_index_ret.index, size_index_ret['大中小盘择时相对风格等权超额净值'].values, color=line_color_list[0], label='沪深300/中证1000择时相对风格等权', linewidth=2)
        ax[1].plot(size_index_ret.index, size_index_ret['巨潮大中小盘择时相对巨潮风格等权超额净值'].values, color=line_color_list[1], label='巨潮大盘/巨潮中小盘择时相对巨潮风格等权', linewidth=2)
        ax[1].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
        ax[1].set_title('超额净值', fontdict={'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/strategy/择时策略_相对风格等权.png'.format(data_path))
        result = get_performance(size_index_ret[['大中小盘择时净值', '大中小盘等权净值']], 250)
        gz_result = get_performance(size_index_ret[['巨潮大中小盘择时净值', '巨潮大中小盘等权净值']], 250)
        result = pd.concat([result, gz_result])
        result.to_excel('{0}style_construction/strategy/择时策略_相对风格等权.xlsx'.format(data_path))

        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        ax[0].plot(size_index_ret.index, size_index_ret['大中小盘择时净值'].values, color=line_color_list[0], label='沪深300/中证1000择时', linewidth=2)
        ax[0].plot(size_index_ret.index, size_index_ret['巨潮大中小盘择时净值'].values, color=line_color_list[1], label='巨潮大盘/巨潮中小盘择时', linewidth=2)
        ax[0].plot(size_index_ret.index, size_index_ret['万得全A净值'].values, color=line_color_list[2], label='万得全A', linewidth=2)
        ax[0].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
        ax[0].set_title('净值', fontdict={'weight': 'bold', 'size': 12})
        ax[1].plot(size_index_ret.index, size_index_ret['大中小盘择时相对万得全A超额净值'].values, color=line_color_list[0], label='沪深300/中证1000择时相对万得全A', linewidth=2)
        ax[1].plot(size_index_ret.index, size_index_ret['巨潮大中小盘择时相对万得全A超额净值'].values, color=line_color_list[1], label='巨潮大盘/巨潮中小盘择时相对万得全A', linewidth=2)
        ax[1].legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
        ax[1].set_title('超额净值', fontdict={'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}style_construction/strategy/择时策略_相对万得全A.png'.format(data_path))
        result = get_performance(size_index_ret[['大中小盘择时净值', '万得全A净值']], 250)
        gz_result = get_performance(size_index_ret[['巨潮大中小盘择时净值', '万得全A净值']], 250)
        result = pd.concat([result, gz_result])
        result.to_excel('{0}style_construction/strategy/择时策略_相对万得全A.xlsx'.format(data_path))
        return

def get_industry_info(type):
    if type == '中信':
        type_code = 1
    if type == '申万':
        type_code = 3
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
    industry_info = industry_info[industry_info['INDUSTRY_VERSION'] == type_code]
    return industry_info

def get_industry_symbol(type):
    if type == '中信':
        type_code = 1
    if type == '申万':
        type_code = 3
    industry_symbol = HBDB().read_industry_symbol()
    industry_symbol = industry_symbol.rename(columns={'hyhfbz': 'INDUSTRY_VERSION', 'fldm': 'INDUSTRY_ID', 'flmc': 'INDUSTRY_NAME', 'zsdm': 'INDEX_SYMBOL', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    industry_symbol = industry_symbol.dropna(subset=['BEGIN_DATE'])
    industry_symbol['END_DATE'] = industry_symbol['END_DATE'].replace('', np.nan).fillna('20990101')
    industry_symbol['BEGIN_DATE'] = industry_symbol['BEGIN_DATE'].astype(int).astype(str)
    industry_symbol['END_DATE'] = industry_symbol['END_DATE'].astype(int).astype(str)
    industry_symbol['INDUSTRY_VERSION'] = industry_symbol['INDUSTRY_VERSION'].astype(int)
    industry_symbol['INDUSTRY_TYPE'] = industry_symbol['INDUSTRY_TYPE'].astype(int)
    industry_symbol['IS_NEW'] = industry_symbol['IS_NEW'].astype(int)
    industry_symbol = industry_symbol[industry_symbol['INDUSTRY_VERSION'] == type_code]
    return industry_symbol

def get_stock_industry(type):
    if type == '中信':
        type_code = 1
    if type == '申万':
        type_code = 2
    stock_industry = HBDB().read_stock_industry()
    stock_industry.to_hdf('{0}style_construction/stock_industry.hdf'.format(data_path), key='table', mode='w')
    stock_industry = pd.read_hdf('{0}style_construction/stock_industry.hdf'.format(data_path), key='table')
    stock_industry = stock_industry.rename(columns={'zqdm': 'TICKER_SYMBOL', 'flmc': 'INDUSTRY_NAME', 'fldm': 'INDUSTRY_ID', 'hyhfbz': 'INDUSTRY_VERSION', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    stock_industry = stock_industry.dropna(subset=['BEGIN_DATE'])
    stock_industry['END_DATE'] = stock_industry['END_DATE'].fillna('20990101')
    stock_industry['BEGIN_DATE'] = stock_industry['BEGIN_DATE'].astype(int).astype(str)
    stock_industry['END_DATE'] = stock_industry['END_DATE'].astype(int).astype(str)
    stock_industry['INDUSTRY_VERSION'] = stock_industry['INDUSTRY_VERSION'].astype(int)
    stock_industry['INDUSTRY_TYPE'] = stock_industry['INDUSTRY_TYPE'].astype(int)
    stock_industry['IS_NEW'] = stock_industry['IS_NEW'].astype(int)
    stock_industry = stock_industry[stock_industry['INDUSTRY_VERSION'] == type_code]
    stock_industry = stock_industry.loc[stock_industry['TICKER_SYMBOL'].str.len() == 6]
    stock_industry = stock_industry.loc[stock_industry['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
    return stock_industry

def get_stock_info(days=180):
    stock_info = HBDB().read_stock_info()
    stock_info = stock_info.rename(columns={'zqdm': 'TICKER_SYMBOL', 'zqjc': 'SEC_SHORT_NAME', 'ssrq': 'ESTABLISH_DATE'})
    stock_info['ESTABLISH_DATE'] = stock_info['ESTABLISH_DATE'].dropna()
    stock_info['ESTABLISH_DATE'] = stock_info['ESTABLISH_DATE'].astype(int).astype(str)
    stock_info = stock_info.loc[stock_info['TICKER_SYMBOL'].str.len() == 6]
    stock_info = stock_info.loc[stock_info['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
    stock_info['SAMPLE_DATE'] = stock_info['ESTABLISH_DATE'].apply(lambda x: (datetime.strptime(x, '%Y%m%d') + timedelta(days)).strftime('%Y%m%d'))
    return stock_info

def insert_ytm(data_path, start_date, end_date):
    ytm_co = pd.read_excel('{0}利差数据跟踪.xlsx'.format(data_path), sheet_name='企业债', header=1)
    ytm_co = ytm_co.rename(columns={'指标名称': 'TRADE_DATE'})
    ytm_co['TRADE_DATE'] = ytm_co['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
    ytm_co = ytm_co[(ytm_co['TRADE_DATE'] > start_date) & (ytm_co['TRADE_DATE'] <= end_date)]
    ytm_co = ytm_co.set_index('TRADE_DATE').sort_index()

    ytm_gk = pd.read_excel('{0}利差数据跟踪.xlsx'.format(data_path), sheet_name='国开', header=1)
    ytm_gk = ytm_gk.rename(columns={'指标名称': 'TRADE_DATE'})
    ytm_gk['TRADE_DATE'] = ytm_gk['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
    ytm_gk = ytm_gk[(ytm_gk['TRADE_DATE'] > start_date) & (ytm_gk['TRADE_DATE'] <= end_date)]
    ytm_gk = ytm_gk.set_index('TRADE_DATE').sort_index()

    ytm = pd.concat([ytm_co, ytm_gk], axis=1).reset_index()
    ytm.to_sql('ytm_zhongzhai', engine, index=False, if_exists='append')
    return

class TAA:
    def __init__(self, data_path, start_date, end_date):
        self.data_path = data_path + 'new/'
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)
        self.month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']

    def get_test(self, type):
        self.data_path = self.data_path + 'pe_eps/{0}/'.format(type)

        # 成长价值走势
        style = pd.read_excel('{0}{1}.xlsx'.format(self.data_path, type)).reset_index(drop=True)
        if type == 'style' or type == '国证_style':
            style = style.rename(columns={'GROWTH': '成长', 'VALUE': '价值'})
        if type == 'size':
            style = style.rename(columns={'LARGE': '成长', 'SMALL': '价值'})
        style['TRADE_DATE'] = style['TRADE_DATE'].astype(str)
        style = style[['TRADE_DATE', '成长', '价值']]
        style['成长/价值'] = style['成长'] / style['价值']
        style['YEAR_MONTH'] = style['TRADE_DATE'].apply(lambda x: str(x)[:6])
        style_monthly = style.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        style_monthly = style_monthly.set_index('YEAR_MONTH').drop('TRADE_DATE', axis=1)
        style_monthly = style_monthly[(style_monthly.index >= self.start_date[:6]) & (style_monthly.index <= self.end_date[:6])]

        # 成长价值PE走势
        style_pe = pd.read_excel('{0}{1}.xlsx'.format(self.data_path, type)).reset_index(drop=True)
        if type == 'style' or type == '国证_style':
            style_pe = style_pe.rename(columns={'GROWTH_PETTM': '成长PE', 'VALUE_PETTM': '价值PE'})
        if type == 'size':
            style_pe = style_pe.rename(columns={'LARGE_PETTM': '成长PE', 'SMALL_PETTM': '价值PE'})
        style_pe['TRADE_DATE'] = style_pe['TRADE_DATE'].astype(str)
        style_pe = style_pe[['TRADE_DATE', '成长PE', '价值PE']]
        style_pe['成长/价值PE'] = style_pe['成长PE'] / style_pe['价值PE']
        style_pe['YEAR_MONTH'] = style_pe['TRADE_DATE'].apply(lambda x: str(x)[:6])
        style_pe_monthly = style_pe.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
        style_pe_monthly = style_pe_monthly.set_index('YEAR_MONTH').drop('TRADE_DATE', axis=1)
        style_pe_monthly = style_pe_monthly[(style_pe_monthly.index >= self.start_date[:6]) & (style_pe_monthly.index <= self.end_date[:6])]
        style_pe_monthly = style_pe_monthly.merge(style_monthly, left_index=True, right_index=True, how='left')
        style_pe_monthly = style_pe_monthly.dropna()
        style_pe_monthly_ori = style_pe_monthly.copy(deep=True)

        for q_type in ['三分组', '五分组', '七分组']:
            for n in [1, 3, 5, 10]:
                style_pe_monthly = style_pe_monthly_ori.copy(deep=True)
                style_pe_monthly['IDX'] = range(len(style_pe_monthly))
                style_pe_monthly['成长PE分位'] = style_pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, '成长PE', style_pe_monthly))
                style_pe_monthly['价值PE分位'] = style_pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, '价值PE', style_pe_monthly))
                style_pe_monthly['成长/价值PE分位'] = style_pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, '成长/价值PE', style_pe_monthly))
                style_pe_monthly = style_pe_monthly.dropna()

                if q_type == '七分组':
                    style_pe_monthly['成长PE分位档位'] = style_pe_monthly['成长PE分位'].apply(lambda x: '0%-10%' if x >= 0.0 and x < 0.1 else '10%-20%' if x >= 0.1 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-90%' if x >= 0.8 and x < 0.9 else '90%-100%')
                    style_pe_monthly['价值PE分位档位'] = style_pe_monthly['价值PE分位'].apply(lambda x: '0%-10%' if x >= 0.0 and x < 0.1 else '10%-20%' if x >= 0.1 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-90%' if x >= 0.8 and x < 0.9 else '90%-100%')
                    style_pe_monthly['成长/价值PE分位档位'] = style_pe_monthly['成长/价值PE分位'].apply(lambda x: '0%-10%' if x >= 0.0 and x < 0.1 else '10%-20%' if x >= 0.1 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-90%' if x >= 0.8 and x < 0.9 else '90%-100%')
                    style_pe_monthly['成长仓位'] = style_pe_monthly['成长PE分位档位'].apply(lambda x: 1.0 if x == '0%-10%' else 0.8 if x == '10%-20%' else 0.6 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.4 if x == '60%-80%' else 0.2 if x == '80%-90%' else 0.0)
                    style_pe_monthly['价值仓位'] = style_pe_monthly['价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-10%' else 0.8 if x == '10%-20%' else 0.6 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.4 if x == '60%-80%' else 0.2 if x == '80%-90%' else 0.0)
                    style_pe_monthly['成长/价值仓位'] = style_pe_monthly['成长/价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-10%' else 0.8 if x == '10%-20%' else 0.6 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.4 if x == '60%-80%' else 0.2 if x == '80%-90%' else 0.0)
                if q_type == '五分组':
                    style_pe_monthly['成长PE分位档位'] = style_pe_monthly['成长PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-100%')
                    style_pe_monthly['价值PE分位档位'] = style_pe_monthly['价值PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-100%')
                    style_pe_monthly['成长/价值PE分位档位'] = style_pe_monthly['成长/价值PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-40%' if x >= 0.2 and x < 0.4 else '40%-60%' if x >= 0.4 and x < 0.6 else '60%-80%' if x >= 0.6 and x < 0.8 else '80%-100%')
                    style_pe_monthly['成长仓位'] = style_pe_monthly['成长PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.75 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.25 if x == '60%-80%' else 0.0)
                    style_pe_monthly['价值仓位'] = style_pe_monthly['价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.75 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.25 if x == '60%-80%' else 0.0)
                    style_pe_monthly['成长/价值仓位'] = style_pe_monthly['成长/价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.75 if x == '20%-40%' else 0.5 if x == '40%-60%' else 0.25 if x == '60%-80%' else 0.0)
                if q_type == '三分组':
                    style_pe_monthly['成长PE分位档位'] = style_pe_monthly['成长PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-80%' if x >= 0.2 and x <= 0.8 else '80%-100%')
                    style_pe_monthly['价值PE分位档位'] = style_pe_monthly['价值PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-80%' if x >= 0.2 and x <= 0.8 else '80%-100%')
                    style_pe_monthly['成长/价值PE分位档位'] = style_pe_monthly['成长/价值PE分位'].apply(lambda x: '0%-20%' if x >= 0.0 and x < 0.2 else '20%-80%' if x >= 0.2 and x <= 0.8 else '80%-100%')
                    style_pe_monthly['成长仓位'] = style_pe_monthly['成长PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.5 if x == '20%-80%' else 0.0)
                    style_pe_monthly['价值仓位'] = style_pe_monthly['价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.5 if x == '20%-80%' else 0.0)
                    style_pe_monthly['成长/价值仓位'] = style_pe_monthly['成长/价值PE分位档位'].apply(lambda x: 1.0 if x == '0%-20%' else 0.5 if x == '20%-80%' else 0.0)
                for style in ['成长', '价值', '成长/价值']:
                    style_pe_monthly[style + '未来1月收益率'] = style_pe_monthly[style].pct_change(1).shift(-1)
                    style_pe_monthly[style + '未来3月收益率'] = style_pe_monthly[style].pct_change(3).shift(-3)
                    style_pe_monthly[style + '未来6月收益率'] = style_pe_monthly[style].pct_change(6).shift(-6)
                    style_pe_monthly[style + '未来1年收益率'] = style_pe_monthly[style].pct_change(12).shift(-12)
                    style_pe_monthly[style + '未来2年收益率'] = style_pe_monthly[style].pct_change(24).shift(-24)
                    style_pe_monthly[style + '未来3年收益率'] = style_pe_monthly[style].pct_change(36).shift(-36)
                    style_pe_ret_1m = style_pe_monthly[[style + 'PE分位档位', style + '未来1月收益率']].dropna().groupby(style + 'PE分位档位').mean()
                    style_pe_ret_3m = style_pe_monthly[[style + 'PE分位档位', style + '未来3月收益率']].dropna().groupby(style + 'PE分位档位').mean()
                    style_pe_ret_6m = style_pe_monthly[[style + 'PE分位档位', style + '未来6月收益率']].dropna().groupby(style + 'PE分位档位').mean()
                    style_pe_ret_1y = style_pe_monthly[[style + 'PE分位档位', style + '未来1年收益率']].dropna().groupby(style + 'PE分位档位').mean()
                    style_pe_ret_2y = style_pe_monthly[[style + 'PE分位档位', style + '未来2年收益率']].dropna().groupby(style + 'PE分位档位').mean()
                    style_pe_ret_3y = style_pe_monthly[[style + 'PE分位档位', style + '未来3年收益率']].dropna().groupby(style + 'PE分位档位').mean()
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(np.arange(len(style_pe_ret_1m)), style_pe_ret_1m[style + '未来1月收益率'].values, color=line_color_list[0], label='未来1月收益率', linewidth=2, linestyle='-')
                    ax.plot(np.arange(len(style_pe_ret_3m)), style_pe_ret_3m[style + '未来3月收益率'].values, color=line_color_list[1], label='未来3月收益率', linewidth=2, linestyle='-')
                    ax.plot(np.arange(len(style_pe_ret_6m)), style_pe_ret_6m[style + '未来6月收益率'].values, color=line_color_list[2], label='未来6月收益率', linewidth=2, linestyle='-')
                    ax.plot(np.arange(len(style_pe_ret_1y)), style_pe_ret_1y[style + '未来1年收益率'].values, color=line_color_list[3], label='未来1年收益率', linewidth=2, linestyle='-')
                    # ax.plot(np.arange(len(style_pe_ret_2y)), style_pe_ret_2y[style + '未来2年收益率'].values, color=line_color_list[1], label='未来2年收益率', linewidth=2, linestyle='--')
                    # ax.plot(np.arange(len(style_pe_ret_3y)), style_pe_ret_3y[style + '未来3年收益率'].values, color=line_color_list[2], label='未来3年收益率', linewidth=2, linestyle='--')
                    ax.set_xticks(np.arange(len(style_pe_ret_1m)))
                    ax.set_xticklabels(labels=style_pe_ret_1m.index.tolist())
                    ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
                    plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6, frameon=False)
                    plt.xlabel('{0}估值分位区间'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘')))
                    plt.ylabel('{0}持有期收益率'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘')))
                    plt.title('{0}不同估值分位区间的平均持有期收益率统计'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘')), fontdict={'weight': 'bold', 'size': 16})
                    plt.tight_layout()
                    sns.despine(top=True, right=False, left=False, bottom=False)
                    plt.savefig('{0}{1}/{2}过去{3}年估值分位区间的平均持有期收益率统计.png'.format(self.data_path, q_type, style.replace('/', 'to') if type != 'size' else style.replace('/', 'to').replace('成长', '大盘').replace('价值', '小盘'), n))

                    if q_type == '七分组':
                        style_pe_monthly_1 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_2 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_3 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_4 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_5 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_6 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_7 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_1[style + 'MARK'] = style_pe_monthly_1.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '0%-10%' else 0.0, axis=1)
                        style_pe_monthly_2[style + 'MARK'] = style_pe_monthly_2.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '10%-20%' else 0.0, axis=1)
                        style_pe_monthly_3[style + 'MARK'] = style_pe_monthly_3.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '20%-40%' else 0.0, axis=1)
                        style_pe_monthly_4[style + 'MARK'] = style_pe_monthly_4.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '40%-60%' else 0.0, axis=1)
                        style_pe_monthly_5[style + 'MARK'] = style_pe_monthly_5.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '60%-80%' else 0.0, axis=1)
                        style_pe_monthly_6[style + 'MARK'] = style_pe_monthly_6.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '80%-90%' else 0.0, axis=1)
                        style_pe_monthly_7[style + 'MARK'] = style_pe_monthly_7.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '90%-100%' else 0.0, axis=1)
                        fig, ax = plt.subplots(figsize=(12, 6))
                        ax_r = ax.twinx()
                        ax.bar(style_pe_monthly_1.index, style_pe_monthly_1[style + 'MARK'].values, color=line_color_list[0], alpha=0.8, label='0%-10%')
                        ax.bar(style_pe_monthly_2.index, style_pe_monthly_2[style + 'MARK'].values, color=line_color_list[0], alpha=0.5, label='10%-20%')
                        ax.bar(style_pe_monthly_3.index, style_pe_monthly_3[style + 'MARK'].values, color=line_color_list[4], alpha=0.5, label='20%-40%')
                        ax.bar(style_pe_monthly_4.index, style_pe_monthly_4[style + 'MARK'].values, color=line_color_list[2], alpha=0.5, label='40%-60%')
                        ax.bar(style_pe_monthly_5.index, style_pe_monthly_5[style + 'MARK'].values, color=line_color_list[1], alpha=0.5, label='60%-80%')
                        ax.bar(style_pe_monthly_6.index, style_pe_monthly_6[style + 'MARK'].values, color=line_color_list[3], alpha=0.5, label='80%-90%')
                        ax.bar(style_pe_monthly_7.index, style_pe_monthly_7[style + 'MARK'].values, color=line_color_list[3], alpha=0.8, label='90%-100%')
                        ax_r.plot(np.arange(len(style_pe_monthly)), style_pe_monthly['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）' if type != 'size' else '大盘/小盘（右轴）', linewidth=2)
                        # ax_r.plot(np.arange(len(style_pe_monthly)), style_pe_monthly['成长/价值PE'].values, color=line_color_list[3], label='成长/价值PE（右轴）' if type != 'size' else '大盘/小盘PE（右轴）', linewidth=2)
                        ax.set_xticks(np.arange(len(style_pe_monthly))[::18])
                        ax.set_xticklabels(labels=style_pe_monthly.index.tolist()[::18])
                        h1, l1 = ax.get_legend_handles_labels()
                        h2, l2 = ax_r.get_legend_handles_labels()
                        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=9, frameon=False)
                        plt.title('{0}过去{1}年估值分位对应区间'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n), fontdict={'weight': 'bold', 'size': 16})
                        plt.tight_layout()
                        sns.despine(top=True, right=False, left=False, bottom=False)
                        plt.savefig('{0}{1}/{2}过去{3}年估值分位对应区间.png'.format(self.data_path, q_type, style.replace('/', 'to') if type != 'size' else style.replace('/', 'to').replace('成长', '大盘').replace('价值', '小盘'), n))

                    if q_type == '五分组':
                        style_pe_monthly_1 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_2 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_3 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_4 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_5 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_1[style + 'MARK'] = style_pe_monthly_1.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '0%-20%' else 0.0, axis=1)
                        style_pe_monthly_2[style + 'MARK'] = style_pe_monthly_2.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '20%-40%' else 0.0, axis=1)
                        style_pe_monthly_3[style + 'MARK'] = style_pe_monthly_3.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '40%-60%' else 0.0, axis=1)
                        style_pe_monthly_4[style + 'MARK'] = style_pe_monthly_4.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '60%-80%' else 0.0, axis=1)
                        style_pe_monthly_5[style + 'MARK'] = style_pe_monthly_5.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '80%-100%' else 0.0, axis=1)
                        fig, ax = plt.subplots(figsize=(12, 6))
                        ax_r = ax.twinx()
                        ax.bar(style_pe_monthly_1.index, style_pe_monthly_1[style + 'MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
                        ax.bar(style_pe_monthly_2.index, style_pe_monthly_2[style + 'MARK'].values, color=line_color_list[4], alpha=0.5, label='20%-40%')
                        ax.bar(style_pe_monthly_3.index, style_pe_monthly_3[style + 'MARK'].values, color=line_color_list[2], alpha=0.5, label='40%-60%')
                        ax.bar(style_pe_monthly_4.index, style_pe_monthly_4[style + 'MARK'].values, color=line_color_list[1], alpha=0.5, label='60%-80%')
                        ax.bar(style_pe_monthly_5.index, style_pe_monthly_5[style + 'MARK'].values, color=line_color_list[3], alpha=0.5, label='80%-100%')
                        ax_r.plot(np.arange(len(style_pe_monthly)), style_pe_monthly['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）' if type != 'size' else '大盘/小盘（右轴）', linewidth=2)
                        # ax_r.plot(np.arange(len(style_pe_monthly)), style_pe_monthly['成长/价值PE'].values, color=line_color_list[3], label='成长/价值PE（右轴）' if type != 'size' else '大盘/小盘PE（右轴）', linewidth=2)
                        ax.set_xticks(np.arange(len(style_pe_monthly))[::18])
                        ax.set_xticklabels(labels=style_pe_monthly.index.tolist()[::18])
                        h1, l1 = ax.get_legend_handles_labels()
                        h2, l2 = ax_r.get_legend_handles_labels()
                        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7, frameon=False)
                        plt.title('{0}过去{1}年估值分位对应区间'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n), fontdict={'weight': 'bold', 'size': 16})
                        plt.tight_layout()
                        sns.despine(top=True, right=False, left=False, bottom=False)
                        plt.savefig('{0}{1}/{2}过去{3}年估值分位对应区间.png'.format(self.data_path, q_type, style.replace('/', 'to') if type != 'size' else style.replace('/', 'to').replace('成长', '大盘').replace('价值', '小盘'), n))

                    if q_type == '三分组':
                        style_pe_monthly_1 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_2 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_3 = style_pe_monthly.copy(deep=True)
                        style_pe_monthly_1[style + 'MARK'] = style_pe_monthly_1.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '0%-20%' else 0.0, axis=1)
                        style_pe_monthly_2[style + 'MARK'] = style_pe_monthly_2.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '20%-80%' else 0.0, axis=1)
                        style_pe_monthly_3[style + 'MARK'] = style_pe_monthly_3.apply(lambda x: 1.0 if x[style + 'PE分位档位'] == '80%-100%' else 0.0, axis=1)
                        fig, ax = plt.subplots(figsize=(12, 6))
                        ax_r = ax.twinx()
                        ax.bar(style_pe_monthly_1.index, style_pe_monthly_1[style + 'MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
                        ax.bar(style_pe_monthly_2.index, style_pe_monthly_2[style + 'MARK'].values, color=line_color_list[2], alpha=0.5, label='20%-80%')
                        ax.bar(style_pe_monthly_3.index, style_pe_monthly_3[style + 'MARK'].values, color=line_color_list[1], alpha=0.5, label='80%-100%')
                        ax_r.plot(np.arange(len(style_pe_monthly)), style_pe_monthly['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）' if type != 'size' else '大盘/小盘（右轴）', linewidth=2)
                        # ax_r.plot(np.arange(len(style_pe_monthly)), style_pe_monthly['成长/价值PE'].values, color=line_color_list[3], label='成长/价值PE（右轴）' if type != 'size' else '大盘/小盘PE（右轴）', linewidth=2)
                        ax.set_xticks(np.arange(len(style_pe_monthly))[::18])
                        ax.set_xticklabels(labels=style_pe_monthly.index.tolist()[::18])
                        h1, l1 = ax.get_legend_handles_labels()
                        h2, l2 = ax_r.get_legend_handles_labels()
                        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5, frameon=False)
                        plt.title('{0}过去{1}年估值分位对应区间'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n), fontdict={'weight': 'bold', 'size': 16})
                        plt.tight_layout()
                        sns.despine(top=True, right=False, left=False, bottom=False)
                        plt.savefig('{0}{1}/{2}过去{3}年估值分位对应区间.png'.format(self.data_path, q_type, style.replace('/', 'to') if type != 'size' else style.replace('/', 'to').replace('成长', '大盘').replace('价值', '小盘'), n))

                    style_pe_monthly['成长月度收益率'] = style_pe_monthly['成长'].pct_change(1).shift(-1)
                    style_pe_monthly['价值月度收益率'] = style_pe_monthly['价值'].pct_change(1).shift(-1)
                    style_pe_monthly['成长月度收益率'].iloc[0] = 0.0
                    style_pe_monthly['价值月度收益率'].iloc[0] = 0.0
                    style_pe_monthly['平均月度收益率'] = 0.5 * style_pe_monthly['成长月度收益率'] + 0.5 * style_pe_monthly['价值月度收益率']
                    if style == '成长':
                        style_pe_monthly['策略月度收益率'] = style_pe_monthly.apply(lambda x: x['成长仓位'] * x['成长月度收益率'] + (1 - x['成长仓位']) * x['价值月度收益率'], axis=1)
                    elif style == '价值':
                        style_pe_monthly['策略月度收益率'] = style_pe_monthly.apply(lambda x: x['价值仓位'] * x['价值月度收益率'] + (1 - x['价值仓位']) * x['成长月度收益率'], axis=1)
                    else:
                        style_pe_monthly['策略月度收益率'] = style_pe_monthly.apply(lambda x: x['成长/价值仓位'] * x['成长月度收益率'] + (1 - x['成长/价值仓位']) * x['价值月度收益率'], axis=1)
                    style_pe_monthly['基准组合净值'] = (1 + style_pe_monthly['平均月度收益率']).cumprod()
                    style_pe_monthly['策略组合净值'] = (1 + style_pe_monthly['策略月度收益率']).cumprod()
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(np.arange(len(style_pe_monthly)), style_pe_monthly['策略组合净值'].values, color=line_color_list[0], label='策略组合净值', linewidth=2, linestyle='-')
                    ax.plot(np.arange(len(style_pe_monthly)), style_pe_monthly['基准组合净值'].values, color=line_color_list[2], label='基准组合净值', linewidth=2, linestyle='-')
                    ax.set_xticks(np.arange(len(style_pe_monthly))[::18])
                    ax.set_xticklabels(labels=style_pe_monthly.index.tolist()[::18])
                    plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
                    plt.title('{0}过去{1}年估值分位择时策略'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n), fontdict={'weight': 'bold', 'size': 16})
                    plt.tight_layout()
                    sns.despine(top=True, right=False, left=False, bottom=False)
                    plt.savefig('{0}{1}/{2}过去{3}年估值分位择时策略.png'.format(self.data_path, q_type, style.replace('/', 'to') if type != 'size' else style.replace('/', 'to').replace('成长', '大盘').replace('价值', '小盘'), n))
                    performance = get_performance(style_pe_monthly[['策略组合净值', '基准组合净值']], 12)
                    performance.to_excel('{0}{1}/{2}过去{3}年估值分位择时策略表现.xlsx'.format(self.data_path, q_type, style.replace('/', 'to') if type != 'size' else style.replace('/', 'to').replace('成长', '大盘').replace('价值', '小盘'), n))

        # 成长价值EPS走势
        for eps_type in ['eps', 'eps_rolling']:
            style_eps = pd.read_excel('{0}{1}.xlsx'.format(self.data_path, type)).reset_index(drop=True)
            if type == 'style' or type == '国证_style':
                style_eps = style_eps.rename(columns={'GROWTH_CONEPS': '成长EPS', 'VALUE_CONEPS': '价值EPS'})
            if type == 'size':
                style_eps = style_eps.rename(columns={'LARGE_CONEPS': '成长EPS', 'SMALL_CONEPS': '价值EPS'})
            style_eps['TRADE_DATE'] = style_eps['TRADE_DATE'].astype(str)
            style_eps = style_eps[['TRADE_DATE', '成长EPS', '价值EPS']]
            style_eps['成长/价值EPS'] = style_eps['成长EPS'] / style_eps['价值EPS']
            style_eps['YEAR_MONTH'] = style_eps['TRADE_DATE'].apply(lambda x: str(x)[:6])
            style_eps_monthly = style_eps.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
            style_eps_monthly = style_eps_monthly.set_index('YEAR_MONTH').drop('TRADE_DATE', axis=1)
            style_eps_monthly = style_eps_monthly[(style_eps_monthly.index >= self.start_date[:6]) & (style_eps_monthly.index <= self.end_date[:6])]
            style_eps_monthly = style_eps_monthly.merge(style_monthly, left_index=True, right_index=True, how='left')
            if eps_type == 'eps_rolling':
                style_eps_monthly['成长EPS'] = style_eps_monthly['成长EPS'].rolling(12).mean()
                style_eps_monthly['价值EPS'] = style_eps_monthly['价值EPS'].rolling(12).mean()
            style_eps_monthly['成长EPS同比'] = style_eps_monthly['成长EPS'].pct_change(12)
            style_eps_monthly['价值EPS同比'] = style_eps_monthly['价值EPS'].pct_change(12)
            style_eps_monthly['成长EPS同比'] = filter_extreme_mad(style_eps_monthly['成长EPS同比'])
            style_eps_monthly['价值EPS同比'] = filter_extreme_mad(style_eps_monthly['价值EPS同比'])
            style_eps_monthly = style_eps_monthly.dropna()
            style_eps_monthly_ori = style_eps_monthly.copy(deep=True)

            style_eps_monthly = style_eps_monthly_ori.copy(deep=True)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax_r = ax.twinx()
            ax.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['成长EPS同比'].values, color=line_color_list[0], label='成长EPS同比' if type != 'size' else '大盘EPS同比', linewidth=2)
            ax.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['价值EPS同比'].values, color=line_color_list[1], label='价值EPS同比' if type != 'size' else '小盘EPS同比', linewidth=2)
            ax_r.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）' if type != 'size' else '大盘/小盘（右轴）', linewidth=2)
            ax.set_xticks(np.arange(len(style_eps_monthly))[::18])
            ax.set_xticklabels(labels=style_eps_monthly.index.tolist()[::18])
            ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax_r.get_legend_handles_labels()
            plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
            plt.title('EPS同比与成长/价值表现' if type != 'size' else 'EPS同比与大盘/小盘表现', fontdict={'weight': 'bold', 'size': 16})
            plt.tight_layout()
            sns.despine(top=True, right=False, left=False, bottom=False)
            plt.savefig('{0}{1}/EPS同比.png'.format(self.data_path, eps_type))

            style_eps_monthly_1 = style_eps_monthly.copy(deep=True)
            style_eps_monthly_2 = style_eps_monthly.copy(deep=True)
            style_eps_monthly_1['MARK'] = style_eps_monthly_1.apply(lambda x: 1.0 if x['成长EPS同比'] > x['价值EPS同比'] else 0, axis=1)
            style_eps_monthly_2['MARK'] = style_eps_monthly_2.apply(lambda x: 1.0 if x['成长EPS同比'] < x['价值EPS同比'] else 0, axis=1)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax_r = ax.twinx()
            ax.bar(style_eps_monthly_1.index, style_eps_monthly_1['MARK'].values, color=line_color_list[0], alpha=0.5, label='成长EPS同比高' if type != 'size' else '大盘EPS同比高')
            ax.bar(style_eps_monthly_2.index, style_eps_monthly_2['MARK'].values, color=line_color_list[1], alpha=0.5, label='价值EPS同比高' if type != 'size' else '小盘EPS同比高')
            ax_r.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）' if type != 'size' else '大盘/小盘（右轴）', linewidth=2)
            ax.set_xticks(np.arange(len(style_eps_monthly))[::18])
            ax.set_xticklabels(labels=style_eps_monthly.index.tolist()[::18])
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax_r.get_legend_handles_labels()
            plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
            plt.title('EPS同比高低区间与成长/价值表现' if type != 'size' else 'EPS同比高低区间与大盘/小盘值表现', fontdict={'weight': 'bold', 'size': 16})
            plt.tight_layout()
            sns.despine(top=True, right=False, left=False, bottom=False)
            plt.savefig('{0}{1}/EPS同比高低区间.png'.format(self.data_path, eps_type))

            style_eps_monthly['成长仓位'] = style_eps_monthly.apply(lambda x: 1.0 if x['成长EPS同比'] > x['价值EPS同比'] else 0, axis=1)
            style_eps_monthly['价值仓位'] = style_eps_monthly.apply(lambda x: 1.0 if x['成长EPS同比'] < x['价值EPS同比'] else 0, axis=1)
            style_eps_monthly['成长月度收益率'] = style_eps_monthly['成长'].pct_change(1).shift(-1)
            style_eps_monthly['价值月度收益率'] = style_eps_monthly['价值'].pct_change(1).shift(-1)
            style_eps_monthly['成长月度收益率'].iloc[0] = 0.0
            style_eps_monthly['价值月度收益率'].iloc[0] = 0.0
            style_eps_monthly['平均月度收益率'] = 0.5 * style_eps_monthly['成长月度收益率'] + 0.5 * style_eps_monthly['价值月度收益率']
            style_eps_monthly['策略月度收益率'] = style_eps_monthly['价值仓位'] * style_eps_monthly['价值月度收益率'] + style_eps_monthly['成长仓位'] * style_eps_monthly['成长月度收益率']
            style_eps_monthly['基准组合净值'] = (1 + style_eps_monthly['平均月度收益率']).cumprod()
            style_eps_monthly['策略组合净值'] = (1 + style_eps_monthly['策略月度收益率']).cumprod()
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['策略组合净值'].values, color=line_color_list[0], label='策略组合净值', linewidth=2, linestyle='-')
            ax.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['基准组合净值'].values, color=line_color_list[2], label='基准组合净值', linewidth=2, linestyle='-')
            ax.set_xticks(np.arange(len(style_eps_monthly))[::18])
            ax.set_xticklabels(labels=style_eps_monthly.index.tolist()[::18])
            plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
            plt.title('EPS同比高低区间择时策略', fontdict={'weight': 'bold', 'size': 16})
            plt.tight_layout()
            sns.despine(top=True, right=False, left=False, bottom=False)
            plt.savefig('{0}{1}/EPS同比高低区间择时策略.png'.format(self.data_path, eps_type))
            performance = get_performance(style_eps_monthly[['策略组合净值', '基准组合净值']], 12)
            performance.to_excel('{0}{1}/EPS同比高低区间择时策略表现.xlsx'.format(self.data_path, eps_type))

            for n in [1, 3, 6, 12]:
                style_eps_monthly = style_eps_monthly_ori.copy(deep=True)
                style_eps_monthly['成长EPS同比差分'] = style_eps_monthly['成长EPS同比'].diff(n)
                style_eps_monthly['价值EPS同比差分'] = style_eps_monthly['价值EPS同比'].diff(n)
                style_eps_monthly = style_eps_monthly.dropna()
                fig, ax = plt.subplots(figsize=(12, 6))
                ax_r = ax.twinx()
                width = 0.5
                ax.bar(np.arange(len(style_eps_monthly)) + 0.5 * width, style_eps_monthly['成长EPS同比差分'].values, color=line_color_list[0], label='成长EPS同比差分' if type != 'size' else '大盘EPS同比差分', linewidth=2)
                ax.bar(np.arange(len(style_eps_monthly)) - 0.5 * width, style_eps_monthly['价值EPS同比差分'].values, color=line_color_list[1], label='价值EPS同比差分' if type != 'size' else '小盘EPS同比差分', linewidth=2)
                ax_r.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）' if type != 'size' else '大盘/小盘（右轴）', linewidth=2)
                ax.set_xticks(np.arange(len(style_eps_monthly))[::18])
                ax.set_xticklabels(labels=style_eps_monthly.index.tolist()[::18])
                ax_r.set_xticks(np.arange(len(style_eps_monthly))[::18])
                ax_r.set_xticklabels(labels=style_eps_monthly.index.tolist()[::18])
                ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
                h1, l1 = ax.get_legend_handles_labels()
                h2, l2 = ax_r.get_legend_handles_labels()
                plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
                plt.title('EPS同比{0}期差分与成长/价值表现'.format(n) if type != 'size' else 'EPS同比{0}期差分与大盘/小盘表现'.format(n), fontdict={'weight': 'bold', 'size': 16})
                plt.tight_layout()
                sns.despine(top=True, right=False, left=False, bottom=False)
                plt.savefig('{0}{1}/EPS同比{2}期差分.png'.format(self.data_path, eps_type, n))

                style_eps_monthly['成长仓位'] = style_eps_monthly.apply(lambda x: 1.0 if x['成长EPS同比差分'] > 0 else 0.5, axis=1)
                style_eps_monthly['价值仓位'] = style_eps_monthly.apply(lambda x: 1.0 if x['价值EPS同比差分'] > 0 else 0.5, axis=1)
                style_eps_monthly['成长月度收益率'] = style_eps_monthly['成长'].pct_change(1).shift(-1)
                style_eps_monthly['价值月度收益率'] = style_eps_monthly['价值'].pct_change(1).shift(-1)
                style_eps_monthly['成长月度收益率'].iloc[0] = 0.0
                style_eps_monthly['价值月度收益率'].iloc[0] = 0.0
                for style in ['成长', '价值']:
                    style_eps_monthly_1 = style_eps_monthly.copy(deep=True)
                    style_eps_monthly_2 = style_eps_monthly.copy(deep=True)
                    style_eps_monthly_1['MARK'] = style_eps_monthly_1.apply(lambda x: 1.0 if x[style + 'EPS同比差分'] > 0 else 0, axis=1)
                    style_eps_monthly_2['MARK'] = style_eps_monthly_2.apply(lambda x: 1.0 if x[style + 'EPS同比差分'] <= 0 else 0, axis=1)
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax_r = ax.twinx()
                    ax.bar(style_eps_monthly_1.index, style_eps_monthly_1['MARK'].values, color=line_color_list[0], alpha=0.5, label=style + 'EPS同比差分>0' if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘') + 'EPS同比差分>0')
                    ax.bar(style_eps_monthly_2.index, style_eps_monthly_2['MARK'].values, color=line_color_list[1], alpha=0.5, label=style + 'EPS同比差分<=0' if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘') + 'EPS同比差分>0')
                    ax_r.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）' if type != 'size' else '大盘/小盘（右轴）', linewidth=2)
                    ax.set_xticks(np.arange(len(style_eps_monthly))[::18])
                    ax.set_xticklabels(labels=style_eps_monthly.index.tolist()[::18])
                    h1, l1 = ax.get_legend_handles_labels()
                    h2, l2 = ax_r.get_legend_handles_labels()
                    plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
                    plt.title('{0}EPS同比{1}期差分高低区间与成长/价值表现'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n), fontdict={'weight': 'bold', 'size': 16})
                    plt.tight_layout()
                    sns.despine(top=True, right=False, left=False, bottom=False)
                    plt.savefig('{0}{1}/{2}EPS同比{3}期差分高低区间.png'.format(self.data_path, eps_type, style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n))

                    style_eps_monthly['平均月度收益率'] = 0.5 * style_eps_monthly['成长月度收益率'] + 0.5 * style_eps_monthly['价值月度收益率']
                    if style == '成长':
                        style_eps_monthly['策略月度收益率'] = style_eps_monthly.apply(lambda x: x['成长仓位'] * x['成长月度收益率'] + (1 - x['成长仓位']) * x['价值月度收益率'], axis=1)
                    else:
                        style_eps_monthly['策略月度收益率'] = style_eps_monthly.apply(lambda x: x['价值仓位'] * x['价值月度收益率'] + (1 - x['价值仓位']) * x['成长月度收益率'], axis=1)
                    style_eps_monthly['基准组合净值'] = (1 + style_eps_monthly['平均月度收益率']).cumprod()
                    style_eps_monthly['策略组合净值'] = (1 + style_eps_monthly['策略月度收益率']).cumprod()
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['策略组合净值'].values, color=line_color_list[0], label='策略组合净值', linewidth=2, linestyle='-')
                    ax.plot(np.arange(len(style_eps_monthly)), style_eps_monthly['基准组合净值'].values, color=line_color_list[2], label='基准组合净值', linewidth=2, linestyle='-')
                    ax.set_xticks(np.arange(len(style_eps_monthly))[::18])
                    ax.set_xticklabels(labels=style_eps_monthly.index.tolist()[::18])
                    plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
                    plt.title('{0}EPS同比{1}期差分高低区间择时策略'.format(style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n), fontdict={'weight': 'bold', 'size': 16})
                    plt.tight_layout()
                    sns.despine(top=True, right=False, left=False, bottom=False)
                    plt.savefig('{0}{1}/{2}EPS同比{3}期差分高低区间择时策略.png'.format(self.data_path, eps_type, style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n))
                    performance = get_performance(style_eps_monthly[['策略组合净值', '基准组合净值']], 12)
                    performance.to_excel('{0}{1}/{2}EPS同比{3}期差分高低区间择时策略表现.xlsx'.format(self.data_path, eps_type, style if type != 'size' else style.replace('成长', '大盘').replace('价值', '小盘'), n))
        return

    def get_signal(self):
        industry_info = get_industry_info('申万')
        industry_info = industry_info[industry_info['INDUSTRY_TYPE'] == 1]
        industry_info = industry_info[industry_info['IS_NEW'] == 1]
        industry_info = industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        industry_list = industry_info['INDUSTRY_ID'].unique().tolist()
        industry_symbol = get_industry_symbol('申万')
        industry_symbol = industry_symbol[industry_symbol['INDUSTRY_TYPE'] == 1]
        industry_symbol = industry_symbol[industry_symbol['IS_NEW'] == 1]
        industry_symbol = industry_symbol[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        stock_industry = get_stock_industry('申万')
        stock_industry = stock_industry[stock_industry['INDUSTRY_TYPE'] == 1]
        stock_industry = stock_industry[stock_industry['IS_NEW'] == 1]
        stock_industry = stock_industry.drop('INDUSTRY_NAME', axis=1).merge(industry_symbol, on=['INDUSTRY_ID'], how='left')
        stock_industry = stock_industry.drop('INDUSTRY_ID', axis=1).merge(industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID']], on=['INDUSTRY_NAME'], how='left')
        stock_industry = stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME', 'TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE']]
        id_name_dic = stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME']].drop_duplicates().set_index('INDUSTRY_ID')['INDUSTRY_NAME'].to_dict()

        index = pd.read_excel('{0}data.xlsx'.format(self.data_path), sheet_name='净值', header=1)
        index = index[['TRADE_DATE', 'LARGE', 'SMALL', 'VALUE', 'GROWTH']]
        index['TRADE_DATE'] = index['TRADE_DATE'].astype(str)
        index = index.set_index('TRADE_DATE').sort_index()
        index['LARGE/SMALL'] = index['LARGE'] / index['SMALL']
        index['VALUE/GROWTH'] = index['VALUE'] / index['GROWTH']
        index = index[(index.index > self.start_date) & (index.index <= self.end_date)]

        eps = pd.read_excel('{0}data.xlsx'.format(self.data_path), sheet_name='一致预测每股收益（NTM）', header=1)
        eps['TRADE_DATE'] = eps['TRADE_DATE'].astype(str)
        eps = eps.drop('TRADE_DATE.1', axis=1).set_index('TRADE_DATE').sort_index()
        eps.columns = [col.split('.')[0] for col in list(eps.columns)]
        eps = eps[eps.index >= '20170101']
        eps = eps.rename(columns={'000300': 'LARGE_EPS', '000852': 'SMALL_EPS'})
        eps = eps.rename(columns=id_name_dic)

        np = pd.read_excel('{0}data.xlsx'.format(self.data_path), sheet_name='一致预测净利润（NTM）', header=1)
        np['TRADE_DATE'] = np['TRADE_DATE'].astype(str)
        np = np.drop('TRADE_DATE.1', axis=1).set_index('TRADE_DATE').sort_index()
        np.columns = [col.split('.')[0] for col in list(np.columns)]
        np = np[np.index >= '20170101']
        np = np.rename(columns=id_name_dic)

        mv = pd.read_excel('{0}data.xlsx'.format(self.data_path), sheet_name='总市值', header=1)
        mv['TRADE_DATE'] = mv['TRADE_DATE'].astype(str)
        mv = mv.drop('TRADE_DATE.1', axis=1).set_index('TRADE_DATE').sort_index()
        mv.columns = [col.split('.')[0] for col in list(mv.columns)]
        mv = mv[mv.index >= '20170101']
        mv = mv.rename(columns=id_name_dic)

        pe = mv / np
        pe = pe.rename(columns={'000300': 'LARGE_PE', '000852': 'SMALL_PE'})

        # 价值成长行业
        value_industry = pd.read_excel('{0}value_industry.xlsx'.format(self.data_path), index_col=0)
        value_industry.index = map(lambda x: str(x), value_industry.index)
        growth_industry = pd.read_excel('{0}growth_industry.xlsx'.format(self.data_path), index_col=0)
        growth_industry.index = map(lambda x: str(x), growth_industry.index)

        date_list = [date for date in value_industry.index.unique().tolist() if date >= '20170101']
        date_list = sorted(list(set(['20161231'] + date_list + [self.end_date])))
        style_pe_list, style_eps_list = [], []
        for i in range(len(date_list) - 1):
            start = self.trade_df[self.trade_df['TRADE_DATE'] <= date_list[i]]['TRADE_DATE'].iloc[-1]
            end = self.trade_df[self.trade_df['TRADE_DATE'] <= date_list[i + 1]]['TRADE_DATE'].iloc[-1]
            value_indu_list = value_industry.loc[date_list[i]].dropna().unique().tolist()
            value_mv = mv[value_indu_list].loc[start: end]
            value_weight = value_mv.apply(lambda x: x / x.sum(), axis=1)
            value_pe = (pe[value_indu_list].loc[start: end]) * value_weight
            value_pe = pd.DataFrame(value_pe.sum(axis=1), columns=['VALUE_PE'])
            value_eps = (eps[value_indu_list].loc[start: end]) * value_weight
            value_eps = pd.DataFrame(value_eps.sum(axis=1), columns=['VALUE_EPS'])
            growth_indu_list = growth_industry.loc[date_list[i]].dropna().unique().tolist()
            growth_mv = mv[growth_indu_list].loc[start: end]
            growth_weight = growth_mv.apply(lambda x: x / x.sum(), axis=1)
            growth_pe = (pe[growth_indu_list].loc[start: end]) * growth_weight
            growth_pe = pd.DataFrame(growth_pe.sum(axis=1), columns=['GROWTH_PE'])
            growth_eps = (eps[growth_indu_list].loc[start: end]) * growth_weight
            growth_eps = pd.DataFrame(growth_eps.sum(axis=1), columns=['GROWTH_EPS'])
            style_pe = pd.concat([value_pe, growth_pe], axis=1)
            style_eps = pd.concat([value_eps, growth_eps], axis=1)
            if i != 0:
                style_pe = style_pe.iloc[1:]
                style_eps = style_eps.iloc[1:]
            style_pe_list.append(style_pe)
            style_eps_list.append(style_eps)
            print(start, end)
        style_pe = pd.concat(style_pe_list)
        style_eps = pd.concat(style_eps_list)

        pe = pe[['LARGE_PE', 'SMALL_PE']].merge(style_pe[['VALUE_PE', 'GROWTH_PE']], left_index=True, right_index=True)
        eps = eps[['LARGE_EPS', 'SMALL_EPS']].merge(style_eps[['VALUE_EPS', 'GROWTH_EPS']], left_index=True, right_index=True)

        ##### PE分位水平 #####
        pe_monthly = pe[pe.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        pe_monthly['LARGE/SMALL_PE'] = pe_monthly['LARGE_PE'] / pe_monthly['SMALL_PE']
        pe_monthly['VALUE/GROWTH_PE'] = pe_monthly['VALUE_PE'] / pe_monthly['GROWTH_PE']
        pe_monthly['IDX'] = range(len(pe_monthly))
        pe_monthly['大盘/小盘过去三年PE分位'] = pe_monthly['IDX'].rolling(12 * 3).apply(lambda x: quantile_definition(x, 'LARGE/SMALL_PE', pe_monthly))
        pe_monthly['价值/成长过去三年PE分位'] = pe_monthly['IDX'].rolling(12 * 3).apply(lambda x: quantile_definition(x, 'VALUE/GROWTH_PE', pe_monthly))
        pe_monthly = index.merge(pe_monthly, left_index=True, right_index=True, how='right').sort_index()
        pe_monthly_xls = pe_monthly.copy(deep=True)
        pe_monthly_xls.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), pe_monthly_xls.index)
        pe_monthly_xls.to_excel('{0}PE.xlsx'.format(self.data_path))
        # pe_monthly_ori = pe_monthly.copy(deep=True)
        # for n in [1, 2, 3, 5]:
        #     pe_monthly = pe_monthly_ori.copy(deep=True)
        #     pe_monthly['LARGE/SMALL_PE分位'] = pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, 'LARGE/SMALL_PE', pe_monthly))
        #     pe_monthly['LARGE/SMALL_PE分位档位'] = pe_monthly['LARGE/SMALL_PE分位'].apply(lambda x: '0%-20%' if x < 0.2 else '80%-100%' if x > 0.8 else '20%-80%')
        #     pe_monthly['LARGE_PE分位'] = pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, 'LARGE_PE', pe_monthly))
        #     pe_monthly['LARGE_PE分位档位'] = pe_monthly['LARGE_PE分位'].apply(lambda x: '0%-20%' if x < 0.2 else '80%-100%' if x > 0.8 else '20%-80%')
        #     pe_monthly['SMALL_PE分位'] = pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, 'SMALL_PE', pe_monthly))
        #     pe_monthly['SMALL_PE分位档位'] = pe_monthly['SMALL_PE分位'].apply(lambda x: '0%-20%' if x < 0.2 else '80%-100%' if x > 0.8 else '20%-80%')
        #     pe_monthly['VALUE/GROWTH_PE分位'] = pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, 'VALUE/GROWTH_PE', pe_monthly))
        #     pe_monthly['VALUE/GROWTH_PE分位档位'] = pe_monthly['VALUE/GROWTH_PE分位'].apply(lambda x: '0%-20%' if x < 0.2 else '80%-100%' if x > 0.8 else '20%-80%')
        #     pe_monthly['VALUE_PE分位'] = pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, 'VALUE_PE', pe_monthly))
        #     pe_monthly['VALUE_PE分位档位'] = pe_monthly['VALUE_PE分位'].apply(lambda x: '0%-20%' if x < 0.2 else '80%-100%' if x > 0.8 else '20%-80%')
        #     pe_monthly['GROWTH_PE分位'] = pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, 'GROWTH_PE', pe_monthly))
        #     pe_monthly['GROWTH_PE分位档位'] = pe_monthly['GROWTH_PE分位'].apply(lambda x: '0%-20%' if x < 0.2 else '80%-100%' if x > 0.8 else '20%-80%')
        #     pe_monthly = pe_monthly.dropna()
        #
        #     pe_monthly['LARGE/SMALL未来1月收益率'] = pe_monthly['LARGE/SMALL'].pct_change(1).shift(-1)
        #     pe_monthly['LARGE/SMALL未来3月收益率'] = pe_monthly['LARGE/SMALL'].pct_change(3).shift(-3)
        #     pe_monthly['LARGE/SMALL未来6月收益率'] = pe_monthly['LARGE/SMALL'].pct_change(6).shift(-6)
        #     pe_monthly['LARGE/SMALL未来12月收益率'] = pe_monthly['LARGE/SMALL'].pct_change(12).shift(-12)
        #     pe_monthly['LARGE未来1月收益率'] = pe_monthly['LARGE'].pct_change(1).shift(-1)
        #     pe_monthly['LARGE未来3月收益率'] = pe_monthly['LARGE'].pct_change(3).shift(-3)
        #     pe_monthly['LARGE未来6月收益率'] = pe_monthly['LARGE'].pct_change(6).shift(-6)
        #     pe_monthly['LARGE未来12月收益率'] = pe_monthly['LARGE'].pct_change(12).shift(-12)
        #     pe_monthly['SMALL未来1月收益率'] = pe_monthly['SMALL'].pct_change(1).shift(-1)
        #     pe_monthly['SMALL未来3月收益率'] = pe_monthly['SMALL'].pct_change(3).shift(-3)
        #     pe_monthly['SMALL未来6月收益率'] = pe_monthly['SMALL'].pct_change(6).shift(-6)
        #     pe_monthly['SMALL未来12月收益率'] = pe_monthly['SMALL'].pct_change(12).shift(-12)
        #     pe_monthly['VALUE/GROWTH未来1月收益率'] = pe_monthly['VALUE/GROWTH'].pct_change(1).shift(-1)
        #     pe_monthly['VALUE/GROWTH未来3月收益率'] = pe_monthly['VALUE/GROWTH'].pct_change(3).shift(-3)
        #     pe_monthly['VALUE/GROWTH未来6月收益率'] = pe_monthly['VALUE/GROWTH'].pct_change(6).shift(-6)
        #     pe_monthly['VALUE/GROWTH未来12月收益率'] = pe_monthly['VALUE/GROWTH'].pct_change(12).shift(-12)
        #     pe_monthly['VALUE未来1月收益率'] = pe_monthly['VALUE'].pct_change(1).shift(-1)
        #     pe_monthly['VALUE未来3月收益率'] = pe_monthly['VALUE'].pct_change(3).shift(-3)
        #     pe_monthly['VALUE未来6月收益率'] = pe_monthly['VALUE'].pct_change(6).shift(-6)
        #     pe_monthly['VALUE未来12月收益率'] = pe_monthly['VALUE'].pct_change(12).shift(-12)
        #     pe_monthly['GROWTH未来1月收益率'] = pe_monthly['GROWTH'].pct_change(1).shift(-1)
        #     pe_monthly['GROWTH未来3月收益率'] = pe_monthly['GROWTH'].pct_change(3).shift(-3)
        #     pe_monthly['GROWTH未来6月收益率'] = pe_monthly['GROWTH'].pct_change(6).shift(-6)
        #     pe_monthly['GROWTH未来12月收益率'] = pe_monthly['GROWTH'].pct_change(12).shift(-12)
        #
        #     pe_monthly_1m_ls = pe_monthly[['LARGE/SMALL_PE分位档位', 'LARGE/SMALL未来1月收益率']].dropna().groupby('LARGE/SMALL_PE分位档位').median()
        #     pe_monthly_3m_ls = pe_monthly[['LARGE/SMALL_PE分位档位', 'LARGE/SMALL未来3月收益率']].dropna().groupby('LARGE/SMALL_PE分位档位').median()
        #     pe_monthly_6m_ls = pe_monthly[['LARGE/SMALL_PE分位档位', 'LARGE/SMALL未来6月收益率']].dropna().groupby('LARGE/SMALL_PE分位档位').median()
        #     pe_monthly_12m_ls = pe_monthly[['LARGE/SMALL_PE分位档位', 'LARGE/SMALL未来12月收益率']].dropna().groupby('LARGE/SMALL_PE分位档位').median()
        #     pe_monthly_1m_l = pe_monthly[['LARGE_PE分位档位', 'LARGE未来1月收益率']].dropna().groupby('LARGE_PE分位档位').median()
        #     pe_monthly_3m_l = pe_monthly[['LARGE_PE分位档位', 'LARGE未来3月收益率']].dropna().groupby('LARGE_PE分位档位').median()
        #     pe_monthly_6m_l = pe_monthly[['LARGE_PE分位档位', 'LARGE未来6月收益率']].dropna().groupby('LARGE_PE分位档位').median()
        #     pe_monthly_12m_l = pe_monthly[['LARGE_PE分位档位', 'LARGE未来12月收益率']].dropna().groupby('LARGE_PE分位档位').median()
        #     pe_monthly_1m_s = pe_monthly[['SMALL_PE分位档位', 'SMALL未来1月收益率']].dropna().groupby('SMALL_PE分位档位').median()
        #     pe_monthly_3m_s = pe_monthly[['SMALL_PE分位档位', 'SMALL未来3月收益率']].dropna().groupby('SMALL_PE分位档位').median()
        #     pe_monthly_6m_s = pe_monthly[['SMALL_PE分位档位', 'SMALL未来6月收益率']].dropna().groupby('SMALL_PE分位档位').median()
        #     pe_monthly_12m_s = pe_monthly[['SMALL_PE分位档位', 'SMALL未来12月收益率']].dropna().groupby('SMALL_PE分位档位').median()
        #     pe_monthly_1m_vg = pe_monthly[['VALUE/GROWTH_PE分位档位', 'VALUE/GROWTH未来1月收益率']].dropna().groupby('VALUE/GROWTH_PE分位档位').median()
        #     pe_monthly_3m_vg = pe_monthly[['VALUE/GROWTH_PE分位档位', 'VALUE/GROWTH未来3月收益率']].dropna().groupby('VALUE/GROWTH_PE分位档位').median()
        #     pe_monthly_6m_vg = pe_monthly[['VALUE/GROWTH_PE分位档位', 'VALUE/GROWTH未来6月收益率']].dropna().groupby('VALUE/GROWTH_PE分位档位').median()
        #     pe_monthly_12m_vg = pe_monthly[['VALUE/GROWTH_PE分位档位', 'VALUE/GROWTH未来12月收益率']].dropna().groupby('VALUE/GROWTH_PE分位档位').median()
        #     pe_monthly_1m_v = pe_monthly[['VALUE_PE分位档位', 'VALUE未来1月收益率']].dropna().groupby('VALUE_PE分位档位').median()
        #     pe_monthly_3m_v = pe_monthly[['VALUE_PE分位档位', 'VALUE未来3月收益率']].dropna().groupby('VALUE_PE分位档位').median()
        #     pe_monthly_6m_v = pe_monthly[['VALUE_PE分位档位', 'VALUE未来6月收益率']].dropna().groupby('VALUE_PE分位档位').median()
        #     pe_monthly_12m_v = pe_monthly[['VALUE_PE分位档位', 'VALUE未来12月收益率']].dropna().groupby('VALUE_PE分位档位').median()
        #     pe_monthly_1m_g = pe_monthly[['GROWTH_PE分位档位', 'GROWTH未来1月收益率']].dropna().groupby('GROWTH_PE分位档位').median()
        #     pe_monthly_3m_g = pe_monthly[['GROWTH_PE分位档位', 'GROWTH未来3月收益率']].dropna().groupby('GROWTH_PE分位档位').median()
        #     pe_monthly_6m_g = pe_monthly[['GROWTH_PE分位档位', 'GROWTH未来6月收益率']].dropna().groupby('GROWTH_PE分位档位').median()
        #     pe_monthly_12m_g = pe_monthly[['GROWTH_PE分位档位', 'GROWTH未来12月收益率']].dropna().groupby('GROWTH_PE分位档位').median()
        #
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax.plot(range(len(pe_monthly_1m_ls)), pe_monthly_1m_ls['LARGE/SMALL未来1月收益率'].values, color=line_color_list[0], label='未来1月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_3m_ls)), pe_monthly_3m_ls['LARGE/SMALL未来3月收益率'].values, color=line_color_list[1], label='未来3月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_6m_ls)), pe_monthly_6m_ls['LARGE/SMALL未来6月收益率'].values, color=line_color_list[2], label='未来6月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_12m_ls)), pe_monthly_12m_ls['LARGE/SMALL未来12月收益率'].values, color=line_color_list[3], label='未来12月收益率', linewidth=2, linestyle='-')
        #     ax.set_xticks(range(len(pe_monthly_1m_ls)))
        #     ax.set_xticklabels(labels=pe_monthly_1m_ls.index.tolist())
        #     ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        #     plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('大盘/小盘过去{0}年估值分位区间平均持有期收益率统计'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/大盘小盘过去{1}年估值分位区间的平均持有期收益率统计.png'.format(self.data_path, n))
        #
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax.plot(range(len(pe_monthly_1m_l)), pe_monthly_1m_l['LARGE未来1月收益率'].values, color=line_color_list[0], label='未来1月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_3m_l)), pe_monthly_3m_l['LARGE未来3月收益率'].values, color=line_color_list[1], label='未来3月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_6m_l)), pe_monthly_6m_l['LARGE未来6月收益率'].values, color=line_color_list[2], label='未来6月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_12m_l)), pe_monthly_12m_l['LARGE未来12月收益率'].values, color=line_color_list[3], label='未来12月收益率', linewidth=2, linestyle='-')
        #     ax.set_xticks(range(len(pe_monthly_1m_l)))
        #     ax.set_xticklabels(labels=pe_monthly_1m_l.index.tolist())
        #     ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        #     plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('大盘过去{0}年估值分位区间平均持有期收益率统计'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/大盘过去{1}年估值分位区间的平均持有期收益率统计.png'.format(self.data_path, n))
        #
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax.plot(range(len(pe_monthly_1m_s)), pe_monthly_1m_s['SMALL未来1月收益率'].values, color=line_color_list[0], label='未来1月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_3m_s)), pe_monthly_3m_s['SMALL未来3月收益率'].values, color=line_color_list[1], label='未来3月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_6m_s)), pe_monthly_6m_s['SMALL未来6月收益率'].values, color=line_color_list[2], label='未来6月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_12m_s)), pe_monthly_12m_s['SMALL未来12月收益率'].values, color=line_color_list[3], label='未来12月收益率', linewidth=2, linestyle='-')
        #     ax.set_xticks(range(len(pe_monthly_1m_s)))
        #     ax.set_xticklabels(labels=pe_monthly_1m_s.index.tolist())
        #     ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        #     plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('小盘过去{0}年估值分位区间平均持有期收益率统计'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/小盘过去{1}年估值分位区间的平均持有期收益率统计.png'.format(self.data_path, n))
        #
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax.plot(range(len(pe_monthly_1m_vg)), pe_monthly_1m_vg['VALUE/GROWTH未来1月收益率'].values, color=line_color_list[0], label='未来1月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_3m_vg)), pe_monthly_3m_vg['VALUE/GROWTH未来3月收益率'].values, color=line_color_list[1], label='未来3月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_6m_vg)), pe_monthly_6m_vg['VALUE/GROWTH未来6月收益率'].values, color=line_color_list[2], label='未来6月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_12m_vg)), pe_monthly_12m_vg['VALUE/GROWTH未来12月收益率'].values, color=line_color_list[3], label='未来12月收益率', linewidth=2, linestyle='-')
        #     ax.set_xticks(range(len(pe_monthly_1m_vg)))
        #     ax.set_xticklabels(labels=pe_monthly_1m_vg.index.tolist())
        #     ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        #     plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('价值/成长过去{0}年估值分位区间平均持有期收益率统计'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/价值成长过去{1}年估值分位区间的平均持有期收益率统计.png'.format(self.data_path, n))
        #
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax.plot(range(len(pe_monthly_1m_v)), pe_monthly_1m_v['VALUE未来1月收益率'].values, color=line_color_list[0], label='未来1月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_3m_v)), pe_monthly_3m_v['VALUE未来3月收益率'].values, color=line_color_list[1], label='未来3月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_6m_v)), pe_monthly_6m_v['VALUE未来6月收益率'].values, color=line_color_list[2], label='未来6月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_12m_v)), pe_monthly_12m_v['VALUE未来12月收益率'].values, color=line_color_list[3], label='未来12月收益率', linewidth=2, linestyle='-')
        #     ax.set_xticks(range(len(pe_monthly_1m_v)))
        #     ax.set_xticklabels(labels=pe_monthly_1m_v.index.tolist())
        #     ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        #     plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('价值过去{0}年估值分位区间平均持有期收益率统计'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/价值过去{1}年估值分位区间的平均持有期收益率统计.png'.format(self.data_path, n))
        #
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax.plot(range(len(pe_monthly_1m_g)), pe_monthly_1m_g['GROWTH未来1月收益率'].values, color=line_color_list[0], label='未来1月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_3m_g)), pe_monthly_3m_g['GROWTH未来3月收益率'].values, color=line_color_list[1], label='未来3月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_6m_g)), pe_monthly_6m_g['GROWTH未来6月收益率'].values, color=line_color_list[2], label='未来6月收益率', linewidth=2, linestyle='-')
        #     ax.plot(range(len(pe_monthly_12m_g)), pe_monthly_12m_g['GROWTH未来12月收益率'].values, color=line_color_list[3], label='未来12月收益率', linewidth=2, linestyle='-')
        #     ax.set_xticks(range(len(pe_monthly_1m_g)))
        #     ax.set_xticklabels(labels=pe_monthly_1m_g.index.tolist())
        #     ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        #     plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('成长过去{0}年估值分位区间平均持有期收益率统计'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/成长过去{1}年估值分位区间的平均持有期收益率统计.png'.format(self.data_path, n))
        #
        #     pe_monthly_1_ls = pe_monthly.copy(deep=True)
        #     pe_monthly_2_ls = pe_monthly.copy(deep=True)
        #     pe_monthly_3_ls = pe_monthly.copy(deep=True)
        #     pe_monthly_1_ls['MARK'] = pe_monthly_1_ls.apply(lambda x: 1.0 if x['LARGE/SMALL_PE分位档位'] == '0%-20%' else 0.0, axis=1)
        #     pe_monthly_2_ls['MARK'] = pe_monthly_2_ls.apply(lambda x: 1.0 if x['LARGE/SMALL_PE分位档位'] == '20%-80%' else 0.0, axis=1)
        #     pe_monthly_3_ls['MARK'] = pe_monthly_3_ls.apply(lambda x: 1.0 if x['LARGE/SMALL_PE分位档位'] == '80%-100%' else 0.0, axis=1)
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax_r = ax.twinx()
        #     ax.bar(pe_monthly_1_ls.index, pe_monthly_1_ls['MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
        #     ax.bar(pe_monthly_2_ls.index, pe_monthly_2_ls['MARK'].values, color=line_color_list[2], alpha=0.5, label='20%-80%')
        #     ax.bar(pe_monthly_3_ls.index, pe_monthly_3_ls['MARK'].values, color=line_color_list[1], alpha=0.5, label='80%-100%')
        #     ax_r.plot(range(len(pe_monthly)), pe_monthly['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=2)
        #     ax.set_xticks(range(len(pe_monthly))[::12])
        #     ax.set_xticklabels(labels=pe_monthly.index.tolist()[::12])
        #     h1, l1 = ax.get_legend_handles_labels()
        #     h2, l2 = ax_r.get_legend_handles_labels()
        #     plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('大盘/小盘过去{0}年估值分位对应区间'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/大盘小盘过去{1}年估值分位对应区间.png'.format(self.data_path, n))
        #
        #     pe_monthly_1_l = pe_monthly.copy(deep=True)
        #     pe_monthly_2_l = pe_monthly.copy(deep=True)
        #     pe_monthly_3_l = pe_monthly.copy(deep=True)
        #     pe_monthly_1_l['MARK'] = pe_monthly_1_l.apply(lambda x: 1.0 if x['LARGE_PE分位档位'] == '0%-20%' else 0.0, axis=1)
        #     pe_monthly_2_l['MARK'] = pe_monthly_2_l.apply(lambda x: 1.0 if x['LARGE_PE分位档位'] == '20%-80%' else 0.0, axis=1)
        #     pe_monthly_3_l['MARK'] = pe_monthly_3_l.apply(lambda x: 1.0 if x['LARGE_PE分位档位'] == '80%-100%' else 0.0, axis=1)
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax_r = ax.twinx()
        #     ax.bar(pe_monthly_1_l.index, pe_monthly_1_l['MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
        #     ax.bar(pe_monthly_2_l.index, pe_monthly_2_l['MARK'].values, color=line_color_list[2], alpha=0.5, label='20%-80%')
        #     ax.bar(pe_monthly_3_l.index, pe_monthly_3_l['MARK'].values, color=line_color_list[1], alpha=0.5, label='80%-100%')
        #     ax_r.plot(range(len(pe_monthly)), pe_monthly['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=2)
        #     ax.set_xticks(range(len(pe_monthly))[::12])
        #     ax.set_xticklabels(labels=pe_monthly.index.tolist()[::12])
        #     h1, l1 = ax.get_legend_handles_labels()
        #     h2, l2 = ax_r.get_legend_handles_labels()
        #     plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('大盘过去{0}年估值分位对应区间'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/大盘过去{1}年估值分位对应区间.png'.format(self.data_path, n))
        #
        #     pe_monthly_1_s = pe_monthly.copy(deep=True)
        #     pe_monthly_2_s = pe_monthly.copy(deep=True)
        #     pe_monthly_3_s = pe_monthly.copy(deep=True)
        #     pe_monthly_1_s['MARK'] = pe_monthly_1_s.apply(lambda x: 1.0 if x['SMALL_PE分位档位'] == '0%-20%' else 0.0, axis=1)
        #     pe_monthly_2_s['MARK'] = pe_monthly_2_s.apply(lambda x: 1.0 if x['SMALL_PE分位档位'] == '20%-80%' else 0.0, axis=1)
        #     pe_monthly_3_s['MARK'] = pe_monthly_3_s.apply(lambda x: 1.0 if x['SMALL_PE分位档位'] == '80%-100%' else 0.0, axis=1)
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax_r = ax.twinx()
        #     ax.bar(pe_monthly_1_s.index, pe_monthly_1_s['MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
        #     ax.bar(pe_monthly_2_s.index, pe_monthly_2_s['MARK'].values, color=line_color_list[2], alpha=0.5, label='20%-80%')
        #     ax.bar(pe_monthly_3_s.index, pe_monthly_3_s['MARK'].values, color=line_color_list[1], alpha=0.5, label='80%-100%')
        #     ax_r.plot(range(len(pe_monthly)), pe_monthly['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=2)
        #     ax.set_xticks(range(len(pe_monthly))[::12])
        #     ax.set_xticklabels(labels=pe_monthly.index.tolist()[::12])
        #     h1, l1 = ax.get_legend_handles_labels()
        #     h2, l2 = ax_r.get_legend_handles_labels()
        #     plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('小盘过去{0}年估值分位对应区间'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/小盘过去{1}年估值分位对应区间.png'.format(self.data_path, n))
        #
        #     pe_monthly_1_vg = pe_monthly.copy(deep=True)
        #     pe_monthly_2_vg = pe_monthly.copy(deep=True)
        #     pe_monthly_3_vg = pe_monthly.copy(deep=True)
        #     pe_monthly_1_vg['MARK'] = pe_monthly_1_vg.apply(lambda x: 1.0 if x['VALUE/GROWTH_PE分位档位'] == '0%-20%' else 0.0, axis=1)
        #     pe_monthly_2_vg['MARK'] = pe_monthly_2_vg.apply(lambda x: 1.0 if x['VALUE/GROWTH_PE分位档位'] == '20%-80%' else 0.0, axis=1)
        #     pe_monthly_3_vg['MARK'] = pe_monthly_3_vg.apply(lambda x: 1.0 if x['VALUE/GROWTH_PE分位档位'] == '80%-100%' else 0.0, axis=1)
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax_r = ax.twinx()
        #     ax.bar(pe_monthly_1_vg.index, pe_monthly_1_vg['MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
        #     ax.bar(pe_monthly_2_vg.index, pe_monthly_2_vg['MARK'].values, color=line_color_list[2], alpha=0.5, label='20%-80%')
        #     ax.bar(pe_monthly_3_vg.index, pe_monthly_3_vg['MARK'].values, color=line_color_list[1], alpha=0.5, label='80%-100%')
        #     ax_r.plot(range(len(pe_monthly)), pe_monthly['VALUE/GROWTH'].values, color=line_color_list[2], label='价值/成长（右轴）', linewidth=2)
        #     ax.set_xticks(range(len(pe_monthly))[::12])
        #     ax.set_xticklabels(labels=pe_monthly.index.tolist()[::12])
        #     h1, l1 = ax.get_legend_handles_labels()
        #     h2, l2 = ax_r.get_legend_handles_labels()
        #     plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('价值/成长过去{0}年估值分位对应区间'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/价值成长过去{1}年估值分位对应区间.png'.format(self.data_path, n))
        #
        #     pe_monthly_1_v = pe_monthly.copy(deep=True)
        #     pe_monthly_2_v = pe_monthly.copy(deep=True)
        #     pe_monthly_3_v = pe_monthly.copy(deep=True)
        #     pe_monthly_1_v['MARK'] = pe_monthly_1_v.apply(lambda x: 1.0 if x['VALUE_PE分位档位'] == '0%-20%' else 0.0, axis=1)
        #     pe_monthly_2_v['MARK'] = pe_monthly_2_v.apply(lambda x: 1.0 if x['VALUE_PE分位档位'] == '20%-80%' else 0.0, axis=1)
        #     pe_monthly_3_v['MARK'] = pe_monthly_3_v.apply(lambda x: 1.0 if x['VALUE_PE分位档位'] == '80%-100%' else 0.0, axis=1)
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax_r = ax.twinx()
        #     ax.bar(pe_monthly_1_v.index, pe_monthly_1_v['MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
        #     ax.bar(pe_monthly_2_v.index, pe_monthly_2_v['MARK'].values, color=line_color_list[2], alpha=0.5, label='20%-80%')
        #     ax.bar(pe_monthly_3_v.index, pe_monthly_3_v['MARK'].values, color=line_color_list[1], alpha=0.5, label='80%-100%')
        #     ax_r.plot(range(len(pe_monthly)), pe_monthly['VALUE/GROWTH'].values, color=line_color_list[2], label='价值/成长（右轴）', linewidth=2)
        #     ax.set_xticks(range(len(pe_monthly))[::12])
        #     ax.set_xticklabels(labels=pe_monthly.index.tolist()[::12])
        #     h1, l1 = ax.get_legend_handles_labels()
        #     h2, l2 = ax_r.get_legend_handles_labels()
        #     plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('价值过去{0}年估值分位对应区间'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/价值过去{1}年估值分位对应区间.png'.format(self.data_path, n))
        #
        #     pe_monthly_1_g = pe_monthly.copy(deep=True)
        #     pe_monthly_2_g = pe_monthly.copy(deep=True)
        #     pe_monthly_3_g = pe_monthly.copy(deep=True)
        #     pe_monthly_1_g['MARK'] = pe_monthly_1_g.apply(lambda x: 1.0 if x['GROWTH_PE分位档位'] == '0%-20%' else 0.0, axis=1)
        #     pe_monthly_2_g['MARK'] = pe_monthly_2_g.apply(lambda x: 1.0 if x['GROWTH_PE分位档位'] == '20%-80%' else 0.0, axis=1)
        #     pe_monthly_3_g['MARK'] = pe_monthly_3_g.apply(lambda x: 1.0 if x['GROWTH_PE分位档位'] == '80%-100%' else 0.0, axis=1)
        #     fig, ax = plt.subplots(figsize=(12, 6))
        #     ax_r = ax.twinx()
        #     ax.bar(pe_monthly_1_g.index, pe_monthly_1_g['MARK'].values, color=line_color_list[0], alpha=0.5, label='0%-20%')
        #     ax.bar(pe_monthly_2_g.index, pe_monthly_2_g['MARK'].values, color=line_color_list[2], alpha=0.5, label='20%-80%')
        #     ax.bar(pe_monthly_3_g.index, pe_monthly_3_g['MARK'].values, color=line_color_list[1], alpha=0.5, label='80%-100%')
        #     ax_r.plot(range(len(pe_monthly)), pe_monthly['VALUE/GROWTH'].values, color=line_color_list[2], label='价值/成长（右轴）', linewidth=2)
        #     ax.set_xticks(range(len(pe_monthly))[::12])
        #     ax.set_xticklabels(labels=pe_monthly.index.tolist()[::12])
        #     h1, l1 = ax.get_legend_handles_labels()
        #     h2, l2 = ax_r.get_legend_handles_labels()
        #     plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        #     plt.title('成长过去{0}年估值分位对应区间'.format(n), fontdict={'weight': 'bold', 'size': 16})
        #     plt.tight_layout()
        #     sns.despine(top=True, right=False, left=False, bottom=False)
        #     plt.savefig('{0}pe/成长过去{1}年估值分位对应区间.png'.format(self.data_path, n))

        # ##### EPS同比一阶差分 #####
        # eps_monthly = eps[eps.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        # eps_monthly = eps_monthly.rolling(12).mean()
        # eps_monthly['大盘EPS同比一阶差分'] = eps_monthly['LARGE_EPS'].pct_change(12).diff()
        # eps_monthly['小盘EPS同比一阶差分'] = eps_monthly['SMALL_EPS'].pct_change(12).diff()
        # eps_monthly['价值EPS同比一阶差分'] = eps_monthly['VALUE_EPS'].pct_change(12).diff()
        # eps_monthly['成长EPS同比一阶差分'] = eps_monthly['GROWTH_EPS'].pct_change(12).diff()
        # eps_monthly = index.merge(eps_monthly, left_index=True, right_index=True, how='right').sort_index()
        # eps_monthly.to_excel('{0}EPS.xlsx'.format(self.data_path))
        # ##########
        # eps_monthly_disp = eps_monthly.dropna()
        # eps_monthly_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), eps_monthly_disp.index)
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.plot(eps_monthly_disp.index, eps_monthly_disp['大盘EPS同比一阶差分'].values, color=line_color_list[0], label='大盘EPS同比一阶差分', linewidth=3)
        # ax.plot(eps_monthly_disp.index, eps_monthly_disp['小盘EPS同比一阶差分'].values, color=line_color_list[1], label='小盘EPS同比一阶差分', linewidth=3)
        # ax_r.plot(eps_monthly_disp.index, eps_monthly_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        # plt.title('大小盘EPS同比一阶差分比较', fontdict={'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}eps/大小盘EPS同比一阶差分比较.png'.format(self.data_path))
        # ##########
        # eps_monthly_disp = eps_monthly.dropna()
        # eps_monthly_1, eps_monthly_2 = eps_monthly_disp.copy(deep=True), eps_monthly_disp.copy(deep=True)
        # eps_monthly_1['大盘盈利状况相对较好'] = eps_monthly_1.apply(lambda x: 1.0 if x['大盘EPS同比一阶差分'] > x['小盘EPS同比一阶差分'] else 0.0, axis=1)
        # eps_monthly_2['小盘盈利状况相对较好'] = eps_monthly_2.apply(lambda x: 1.0 if x['大盘EPS同比一阶差分'] < x['小盘EPS同比一阶差分'] else 0.0, axis=1)
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.bar(range(len(eps_monthly_1)), eps_monthly_1['大盘盈利状况相对较好'].values, color=line_color_list[0], alpha=0.5, label='大盘盈利状况相对较好', linewidth=3)
        # ax.bar(range(len(eps_monthly_2)), eps_monthly_2['小盘盈利状况相对较好'].values, color=line_color_list[1], alpha=0.5, label='小盘盈利状况相对较好', linewidth=3)
        # ax_r.plot(range(len(eps_monthly_disp)), eps_monthly_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        # ax.set_xticks(range(len(eps_monthly_disp))[::12])
        # ax.set_xticklabels(labels=eps_monthly_disp.index.tolist()[::12])
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        # plt.title('大小盘EPS同比一阶差分比较分区', fontdict={'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}eps/大小盘EPS同比一阶差分比较分区.png'.format(self.data_path))
        # ##########
        # eps_monthly_disp = eps_monthly.dropna()
        # eps_monthly_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), eps_monthly_disp.index)
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.plot(eps_monthly_disp.index, eps_monthly_disp['价值EPS同比一阶差分'].values, color=line_color_list[0], label='价值EPS同比一阶差分', linewidth=3)
        # ax.plot(eps_monthly_disp.index, eps_monthly_disp['成长EPS同比一阶差分'].values, color=line_color_list[1], label='成长EPS同比一阶差分', linewidth=3)
        # ax_r.plot(eps_monthly_disp.index, eps_monthly_disp['LARGE/SMALL'].values, color=line_color_list[2], label='价值/成长（右轴）', linewidth=3)
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        # plt.title('价值成长EPS同比一阶差分比较', fontdict={'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}eps/价值成长EPS同比一阶差分比较.png'.format(self.data_path))
        # ##########
        # eps_monthly_disp = eps_monthly.dropna()
        # eps_monthly_1, eps_monthly_2 = eps_monthly_disp.copy(deep=True), eps_monthly_disp.copy(deep=True)
        # eps_monthly_1['价值盈利状况相对较好'] = eps_monthly_1.apply(lambda x: 1.0 if x['价值EPS同比一阶差分'] > x['成长EPS同比一阶差分'] else 0.0, axis=1)
        # eps_monthly_2['成长盈利状况相对较好'] = eps_monthly_2.apply(lambda x: 1.0 if x['价值EPS同比一阶差分'] < x['成长EPS同比一阶差分'] else 0.0, axis=1)
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.bar(range(len(eps_monthly_1)), eps_monthly_1['价值盈利状况相对较好'].values, color=line_color_list[0], alpha=0.5, label='价值盈利状况相对较好', linewidth=3)
        # ax.bar(range(len(eps_monthly_2)), eps_monthly_2['成长盈利状况相对较好'].values, color=line_color_list[1], alpha=0.5, label='成长盈利状况相对较好', linewidth=3)
        # ax_r.plot(range(len(eps_monthly_disp)), eps_monthly_disp['LARGE/SMALL'].values, color=line_color_list[2], label='价值/成长（右轴）', linewidth=3)
        # ax.set_xticks(range(len(eps_monthly_disp))[::12])
        # ax.set_xticklabels(labels=eps_monthly_disp.index.tolist()[::12])
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        # plt.title('价值成长EPS同比一阶差分比较分区', fontdict={'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}eps/价值成长EPS同比一阶差分比较分区.png'.format(self.data_path))

        ##### EPS同比 #####
        eps_monthly = eps[eps.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        eps_monthly = eps_monthly.rolling(12).mean()
        eps_monthly['大盘EPS同比'] = eps_monthly['LARGE_EPS'].pct_change(12)
        eps_monthly['小盘EPS同比'] = eps_monthly['SMALL_EPS'].pct_change(12)
        eps_monthly['价值EPS同比'] = eps_monthly['VALUE_EPS'].pct_change(12)
        eps_monthly['成长EPS同比'] = eps_monthly['GROWTH_EPS'].pct_change(12)
        eps_monthly = index.merge(eps_monthly, left_index=True, right_index=True, how='right').sort_index()
        eps_monthly_xls = eps_monthly.copy(deep=True)
        eps_monthly_xls.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), eps_monthly_xls.index)
        eps_monthly_xls.to_excel('{0}EPS.xlsx'.format(self.data_path))
        # ##########
        # eps_monthly_disp = eps_monthly.dropna()
        # eps_monthly_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), eps_monthly_disp.index)
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.plot(eps_monthly_disp.index, eps_monthly_disp['大盘EPS同比'].values, color=line_color_list[0], label='大盘EPS同比', linewidth=3)
        # ax.plot(eps_monthly_disp.index, eps_monthly_disp['小盘EPS同比'].values, color=line_color_list[1], label='小盘EPS同比', linewidth=3)
        # ax_r.plot(eps_monthly_disp.index, eps_monthly_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        # plt.title('大小盘EPS同比比较', fontdict={'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}eps/大小盘EPS同比比较.png'.format(self.data_path))
        # ##########
        # eps_monthly_disp = eps_monthly.dropna()
        # eps_monthly_1, eps_monthly_2 = eps_monthly_disp.copy(deep=True), eps_monthly_disp.copy(deep=True)
        # eps_monthly_1['大盘EPS同比相对较高'] = eps_monthly_1.apply(lambda x: 1.0 if x['大盘EPS同比'] > x['小盘EPS同比'] else 0.0, axis=1)
        # eps_monthly_2['小盘EPS同比相对较高'] = eps_monthly_2.apply(lambda x: 1.0 if x['大盘EPS同比'] < x['小盘EPS同比'] else 0.0, axis=1)
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.bar(range(len(eps_monthly_1)), eps_monthly_1['大盘EPS同比相对较高'].values, color=line_color_list[0], alpha=0.5, label='大盘EPS同比相对较高', linewidth=3)
        # ax.bar(range(len(eps_monthly_2)), eps_monthly_2['小盘EPS同比相对较高'].values, color=line_color_list[1], alpha=0.5, label='小盘EPS同比相对较高', linewidth=3)
        # ax_r.plot(range(len(eps_monthly_disp)), eps_monthly_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        # ax.set_xticks(range(len(eps_monthly_disp))[::12])
        # ax.set_xticklabels(labels=eps_monthly_disp.index.tolist()[::12])
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        # plt.title('大小盘EPS同比比较分区', fontdict={'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}eps/大小盘EPS同比比较分区.png'.format(self.data_path))
        # ##########
        # eps_monthly_disp = eps_monthly.dropna()
        # eps_monthly_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), eps_monthly_disp.index)
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.plot(eps_monthly_disp.index, eps_monthly_disp['价值EPS同比'].values, color=line_color_list[0], label='价值EPS同比', linewidth=3)
        # ax.plot(eps_monthly_disp.index, eps_monthly_disp['成长EPS同比'].values, color=line_color_list[1], label='成长EPS同比', linewidth=3)
        # ax_r.plot(eps_monthly_disp.index, eps_monthly_disp['LARGE/SMALL'].values, color=line_color_list[2], label='价值/成长（右轴）', linewidth=3)
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        # plt.title('价值成长EPS同比比较', fontdict={'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}eps/价值成长EPS同比比较.png'.format(self.data_path))
        # ##########
        # eps_monthly_disp = eps_monthly.dropna()
        # eps_monthly_1, eps_monthly_2 = eps_monthly_disp.copy(deep=True), eps_monthly_disp.copy(deep=True)
        # eps_monthly_1['价值EPS同比相对较高'] = eps_monthly_1.apply(lambda x: 1.0 if x['价值EPS同比'] > x['成长EPS同比'] else 0.0, axis=1)
        # eps_monthly_2['成长EPS同比相对较高'] = eps_monthly_2.apply(lambda x: 1.0 if x['价值EPS同比'] < x['成长EPS同比'] else 0.0, axis=1)
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.bar(range(len(eps_monthly_1)), eps_monthly_1['价值EPS同比相对较高'].values, color=line_color_list[0], alpha=0.5, label='价值EPS同比相对较高', linewidth=3)
        # ax.bar(range(len(eps_monthly_2)), eps_monthly_2['成长EPS同比相对较高'].values, color=line_color_list[1], alpha=0.5, label='成长EPS同比相对较高', linewidth=3)
        # ax_r.plot(range(len(eps_monthly_disp)), eps_monthly_disp['LARGE/SMALL'].values, color=line_color_list[2], label='价值/成长（右轴）', linewidth=3)
        # ax.set_xticks(range(len(eps_monthly_disp))[::12])
        # ax.set_xticklabels(labels=eps_monthly_disp.index.tolist()[::12])
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        # plt.title('价值成长EPS同比比较分区', fontdict={'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}eps/价值成长EPS同比比较分区.png'.format(self.data_path))

        ##### CPI-PPI剪刀差 #####
        cpi_ppi = w.edb("M0000612,M0001227", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        cpi_ppi.to_hdf('{0}cpi_ppi.hdf'.format(self.data_path), key='table', mode='w')
        cpi_ppi = pd.read_hdf('{0}cpi_ppi.hdf'.format(self.data_path), key='table')
        cpi_ppi.columns = ['CALENDAR_DATE', 'CPI_当月同比', 'PPI_当月同比']
        cpi_ppi['CALENDAR_DATE'] = cpi_ppi['CALENDAR_DATE'].shift(-1).fillna(self.end_date_hyphen)
        cpi_ppi['CALENDAR_DATE'] = cpi_ppi['CALENDAR_DATE'].apply(lambda x: str(x).replace('-', ''))
        cpi_ppi = cpi_ppi.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        cpi_ppi = cpi_ppi.drop('CALENDAR_DATE', axis=1).set_index('TRADE_DATE').sort_index()
        cpi_ppi = cpi_ppi[(cpi_ppi.index > self.start_date) & (cpi_ppi.index <= self.end_date)]
        cpi_ppi_monthly = cpi_ppi.loc[cpi_ppi.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        cpi_ppi_monthly['CPI_当月同比'] = cpi_ppi_monthly['CPI_当月同比'] / 100.0
        cpi_ppi_monthly['PPI_当月同比'] = cpi_ppi_monthly['PPI_当月同比'] / 100.0
        cpi_ppi_monthly['CPI-PPI'] = cpi_ppi_monthly['CPI_当月同比'] - cpi_ppi_monthly['PPI_当月同比']
        cpi_ppi_monthly['CPI-PPI短（3个月）均值'] = cpi_ppi_monthly['CPI-PPI'].rolling(3).mean()
        cpi_ppi_monthly['CPI-PPI长（12个月）均值'] = cpi_ppi_monthly['CPI-PPI'].rolling(12).mean()
        cpi_ppi_monthly['CPI-PPI剪刀差'] = cpi_ppi_monthly['CPI-PPI短（3个月）均值'] - cpi_ppi_monthly['CPI-PPI长（12个月）均值']
        cpi_ppi_monthly = index.merge(cpi_ppi_monthly, left_index=True, right_index=True, how='right').sort_index()
        cpi_ppi_monthly_xls = cpi_ppi_monthly.copy(deep=True)
        cpi_ppi_monthly_xls.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), cpi_ppi_monthly_xls.index)
        cpi_ppi_monthly_xls.to_excel('{0}CPI-PPI剪刀差.xlsx'.format(self.data_path))
        ##########
        cpi_ppi_disp = cpi_ppi_monthly.dropna()
        cpi_ppi_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), cpi_ppi_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(cpi_ppi_disp.index, cpi_ppi_disp['CPI-PPI短（3个月）均值'].values, color=line_color_list[0], label='CPI-PPI短（3个月）均值', linewidth=3)
        ax.plot(cpi_ppi_disp.index, cpi_ppi_disp['CPI-PPI长（12个月）均值'].values, color=line_color_list[1], label='CPI-PPI长（12个月）均值', linewidth=3)
        ax.plot(cpi_ppi_disp.index, cpi_ppi_disp['CPI-PPI剪刀差'].values, color=line_color_list[4], label='CPI-PPI剪刀差', linewidth=3)
        ax_r.plot(cpi_ppi_disp.index, cpi_ppi_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(cpi_ppi_disp.index, cpi_ppi_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('CPI-PPI剪刀差', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}CPI-PPI剪刀差.png'.format(self.data_path))
        ##########
        cpi_ppi_disp = cpi_ppi_monthly.dropna()
        cpi_ppi_1, cpi_ppi_2 = cpi_ppi_disp.copy(deep=True), cpi_ppi_disp.copy(deep=True)
        cpi_ppi_1['扩大'] = cpi_ppi_1.apply(lambda x: 1.0 if x['CPI-PPI短（3个月）均值'] > x['CPI-PPI长（12个月）均值'] else 0.0, axis=1)
        cpi_ppi_2['缩小'] = cpi_ppi_2.apply(lambda x: 1.0 if x['CPI-PPI短（3个月）均值'] < x['CPI-PPI长（12个月）均值'] else 0.0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.bar(range(len(cpi_ppi_1)), cpi_ppi_1['扩大'].values, color=line_color_list[0], alpha=0.5, label='扩大', linewidth=3)
        ax.bar(range(len(cpi_ppi_2)), cpi_ppi_2['缩小'].values, color=line_color_list[1], alpha=0.5, label='缩小', linewidth=3)
        ax_r.plot(range(len(cpi_ppi_disp)), cpi_ppi_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(range(len(cpi_ppi_disp)), cpi_ppi_disp['VALUE/GROWTH'].values, color=line_color_list[4], label='价值/成长（右轴）', linewidth=3)
        ax.set_xticks(range(len(cpi_ppi_disp))[::12])
        ax.set_xticklabels(labels=cpi_ppi_disp.index.tolist()[::12])
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('CPI-PPI剪刀差分区', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}CPI-PPI剪刀差分区.png'.format(self.data_path))

        ##### 十年期国债收益率与年度平均比较 #####
        bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期国债收益率', '1年期国债收益率']
        bond_yield = bond_yield[['TRADE_DATE', '10年期国债收益率']]
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().fillna(method='ffill').dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield = bond_yield[(bond_yield.index > self.start_date) & (bond_yield.index <= self.end_date)].dropna()
        bond_yield_monthly = bond_yield.loc[bond_yield.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_monthly['10年期国债收益率'] = bond_yield_monthly['10年期国债收益率'] / 100.0
        bond_yield_monthly['10年期国债收益率_年度平均'] = bond_yield_monthly['10年期国债收益率'].rolling(12).mean()
        bond_yield_monthly = index.merge(bond_yield_monthly, left_index=True, right_index=True, how='right').sort_index()
        bond_yield_monthly_xls = bond_yield_monthly.copy(deep=True)
        bond_yield_monthly_xls.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_monthly_xls.index)
        bond_yield_monthly_xls.to_excel('{0}十年期国债收益率与年度平均比较.xlsx'.format(self.data_path))
        ##########
        bond_yield_disp = bond_yield_monthly.dropna()
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['10年期国债收益率'].values, color=line_color_list[0], label='10年期国债收益率', linewidth=3)
        ax.plot(bond_yield_disp.index, bond_yield_disp['10年期国债收益率_年度平均'].values, color=line_color_list[1], label='10年期国债收益率_年度平均', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('十年期国债收益率与年度平均比较', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}十年期国债收益率与年度平均比较.png'.format(self.data_path))
        ##########
        bond_yield_disp = bond_yield_monthly.dropna()
        bond_yield_1, bond_yield_2 = bond_yield_disp.copy(deep=True), bond_yield_disp.copy(deep=True)
        bond_yield_1['宽松'] = bond_yield_1.apply(lambda x: 1.0 if x['10年期国债收益率'] < x['10年期国债收益率_年度平均'] else 0.0, axis=1)
        bond_yield_2['收紧'] = bond_yield_2.apply(lambda x: 1.0 if x['10年期国债收益率'] > x['10年期国债收益率_年度平均'] else 0.0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.bar(range(len(bond_yield_1)), bond_yield_1['宽松'].values, color=line_color_list[0], alpha=0.5, label='宽松', linewidth=3)
        ax.bar(range(len(bond_yield_2)), bond_yield_2['收紧'].values, color=line_color_list[1], alpha=0.5, label='收紧', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        ax.set_xticks(range(len(bond_yield_disp))[::12])
        ax.set_xticklabels(labels=bond_yield_disp.index.tolist()[::12])
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('十年期国债收益率与年度平均比较分区', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}十年期国债收益率与年度平均比较分区.png'.format(self.data_path))

        ##### 长期贷款余额同比与前期均值比较 #####
        long_loan = w.edb("M0043418", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        long_loan.to_hdf('{0}long_loan.hdf'.format(self.data_path), key='table', mode='w')
        long_loan = pd.read_hdf('{0}long_loan.hdf'.format(self.data_path), key='table')
        long_loan.columns = ['CALENDAR_DATE', '中长期贷款余额']
        long_loan['CALENDAR_DATE'] = long_loan['CALENDAR_DATE'].shift(-1).fillna(self.end_date_hyphen)
        long_loan['CALENDAR_DATE'] = long_loan['CALENDAR_DATE'].apply(lambda x: str(x).replace('-', ''))
        long_loan = long_loan.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        long_loan = long_loan.drop('CALENDAR_DATE', axis=1).set_index('TRADE_DATE').sort_index()
        long_loan = long_loan[(long_loan.index > self.start_date) & (long_loan.index <= self.end_date)].dropna()
        long_loan_monthly = long_loan.loc[long_loan.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        long_loan_monthly['中长期贷款余额同比'] = long_loan_monthly['中长期贷款余额'].pct_change(12)
        long_loan_monthly['前期均值'] = long_loan_monthly['中长期贷款余额同比'].rolling(2).mean()
        long_loan_monthly['前期均值'] = long_loan_monthly['前期均值'].shift()
        long_loan_monthly = index.merge(long_loan_monthly, left_index=True, right_index=True, how='right').sort_index()
        long_loan_monthly_xls = long_loan_monthly.copy(deep=True)
        long_loan_monthly_xls.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), long_loan_monthly_xls.index)
        long_loan_monthly_xls.to_excel('{0}长期贷款余额同比与前期比较.xlsx'.format(self.data_path))
        ##########
        long_loan_disp = long_loan_monthly.dropna()
        long_loan_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), long_loan_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(long_loan_disp.index, long_loan_disp['中长期贷款余额同比'].values, color=line_color_list[0], label='中长期贷款余额同比', linewidth=3)
        ax.plot(long_loan_disp.index, long_loan_disp['前期均值'].values, color=line_color_list[1], label='前期均值', linewidth=3)
        ax_r.plot(long_loan_disp.index, long_loan_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(long_loan_disp.index, long_loan_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('长期贷款余额同比与前期均值比较', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}长期贷款余额同比与前期均值比较.png'.format(self.data_path))
        ##########
        long_loan_disp = long_loan_monthly.dropna()
        long_loan_1, long_loan_2 = long_loan_disp.copy(deep=True), long_loan_disp.copy(deep=True)
        long_loan_1['宽松'] = long_loan_1.apply(lambda x: 1.0 if x['中长期贷款余额同比'] > x['前期均值'] else 0.0, axis=1)
        long_loan_2['收紧'] = long_loan_2.apply(lambda x: 1.0 if x['中长期贷款余额同比'] < x['前期均值'] else 0.0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.bar(range(len(long_loan_1)), long_loan_1['宽松'].values, color=line_color_list[0], alpha=0.5, label='宽松', linewidth=3)
        ax.bar(range(len(long_loan_2)), long_loan_2['收紧'].values, color=line_color_list[1], alpha=0.5, label='收紧', linewidth=3)
        ax_r.plot(long_loan_disp.index, long_loan_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(long_loan_disp.index, long_loan_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        ax.set_xticks(range(len(long_loan_disp))[::12])
        ax.set_xticklabels(labels=long_loan_disp.index.tolist()[::12])
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('长期贷款余额同比与前期均值比较分区', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}长期贷款余额同比与前期均值比较分区.png'.format(self.data_path))

        ##### 期限利差 #####
        bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期长端国债利率', '1年期短端国债利率']
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield = bond_yield[(bond_yield.index > self.start_date) & (bond_yield.index <= self.end_date)].dropna()
        bond_yield['10年期长端国债利率'] = bond_yield['10年期长端国债利率'] / 100.0
        bond_yield['1年期短端国债利率'] = bond_yield['1年期短端国债利率'] / 100.0
        bond_yield['期限利差'] = bond_yield['10年期长端国债利率'] - bond_yield['1年期短端国债利率']
        bond_yield['期限利差_平滑'] = bond_yield['期限利差'].rolling(20).mean()
        bond_yield_monthly = bond_yield.loc[bond_yield.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_monthly['IDX'] = range(len(bond_yield_monthly))
        bond_yield_monthly['期限利差近一年分位水平'] = bond_yield_monthly['IDX'].rolling(12).apply(lambda x: quantile_definition(x, '期限利差_平滑', bond_yield_monthly))
        bond_yield_monthly = bond_yield_monthly.drop('IDX', axis=1)
        bond_yield_monthly = index.merge(bond_yield_monthly, left_index=True, right_index=True, how='right').sort_index()
        bond_yield_monthly_xls = bond_yield_monthly.copy(deep=True)
        bond_yield_monthly_xls.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_monthly_xls.index)
        bond_yield_monthly_xls.to_excel('{0}期限利差.xlsx'.format(self.data_path))
        ##########
        bond_yield_disp = bond_yield_monthly.dropna()
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['期限利差近一年分位水平'].values, color=line_color_list[0], label='期限利差近一年分位水平', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('期限利差', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差.png'.format(self.data_path))
        ##########
        bond_yield_disp = bond_yield_monthly.dropna()
        bond_yield_1, bond_yield_2 = bond_yield_disp.copy(deep=True), bond_yield_disp.copy(deep=True)
        bond_yield_1['上行'] = bond_yield_1.apply(lambda x: 1.0 if x['期限利差近一年分位水平'] > 0.5 else 0.0, axis=1)
        bond_yield_2['下行'] = bond_yield_2.apply(lambda x: 1.0 if x['期限利差近一年分位水平'] < 0.5 else 0.0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.bar(range(len(bond_yield_1)), bond_yield_1['上行'].values, color=line_color_list[0], alpha=0.5, label='上行', linewidth=3)
        ax.bar(range(len(bond_yield_2)), bond_yield_2['下行'].values, color=line_color_list[1], alpha=0.5, label='下行', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        ax.set_xticks(range(len(bond_yield_disp))[::12])
        ax.set_xticklabels(labels=bond_yield_disp.index.tolist()[::12])
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('期限利差分区', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差分区.png'.format(self.data_path))

        ##### 信用利差 #####
        bond_spread = FEDB().read_ytm_zhongzhai()
        bond_spread['TRADE_DATE'] = bond_spread['TRADE_DATE'].astype(str)
        bond_spread = bond_spread.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_spread = bond_spread[bond_spread.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_spread = bond_spread[(bond_spread.index > self.start_date) & (bond_spread.index <= self.end_date)].dropna()
        bond_spread['中债企业债到期收益率(AA+):5年'] = bond_spread['中债企业债到期收益率(AA+):5年'] / 100.0
        bond_spread['中债国开债到期收益率:5年'] = bond_spread['中债国开债到期收益率:5年'] / 100.0
        bond_spread['信用利差'] = bond_spread['中债企业债到期收益率(AA+):5年'] - bond_spread['中债国开债到期收益率:5年']
        bond_spread['信用利差_平滑'] = bond_spread['信用利差'].rolling(20).mean()
        bond_spread_monthly = bond_spread.loc[bond_spread.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        bond_spread_monthly['IDX'] = range(len(bond_spread_monthly))
        bond_spread_monthly['信用利差近一年分位水平'] = bond_spread_monthly['IDX'].rolling(12).apply(lambda x: quantile_definition(x, '信用利差_平滑', bond_spread_monthly))
        bond_spread_monthly = bond_spread_monthly.drop('IDX', axis=1)
        bond_spread_monthly = index.merge(bond_spread_monthly, left_index=True, right_index=True, how='right').sort_index()
        bond_spread_monthly_xls = bond_spread_monthly.copy(deep=True)
        bond_spread_monthly_xls.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread_monthly_xls.index)
        bond_spread_monthly_xls.to_excel('{0}信用利差.xlsx'.format(self.data_path))
        ##########
        bond_spread_disp = bond_spread_monthly.dropna()
        bond_spread_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_spread_disp.index, bond_spread_disp['信用利差近一年分位水平'].values, color=line_color_list[0], label='信用利差近一年分位水平', linewidth=3)
        ax_r.plot(bond_spread_disp.index, bond_spread_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(bond_spread_disp.index, bond_spread_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)
        plt.title('信用利差', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}信用利差.png'.format(self.data_path))
        ##########
        bond_spread_disp = bond_spread_monthly.dropna()
        bond_spread_1, bond_spread_2 = bond_spread_disp.copy(deep=True), bond_spread_disp.copy(deep=True)
        bond_spread_1['上行'] = bond_spread_1.apply(lambda x: 1.0 if x['信用利差近一年分位水平'] > 0.5 else 0.0, axis=1)
        bond_spread_2['下行'] = bond_spread_2.apply(lambda x: 1.0 if x['信用利差近一年分位水平'] < 0.5 else 0.0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.bar(range(len(bond_spread_1)), bond_spread_1['上行'].values, color=line_color_list[0], alpha=0.5, label='上行', linewidth=3)
        ax.bar(range(len(bond_spread_2)), bond_spread_2['下行'].values, color=line_color_list[1], alpha=0.5, label='下行', linewidth=3)
        ax_r.plot(bond_spread_disp.index, bond_spread_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(bond_spread_disp.index, bond_spread_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        ax.set_xticks(range(len(bond_spread_disp))[::12])
        ax.set_xticklabels(labels=bond_spread_disp.index.tolist()[::12])
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('信用利差分区', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}信用利差分区.png'.format(self.data_path))

        ##### PMI #####
        pmi = w.edb("M0017126", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        pmi.to_hdf('{0}pmi.hdf'.format(self.data_path), key='table', mode='w')
        pmi = pd.read_hdf('{0}pmi.hdf'.format(self.data_path), key='table')
        pmi.columns = ['CALENDAR_DATE', '中国制造业PMI']
        # pmi['CALENDAR_DATE'] = pmi['CALENDAR_DATE'].shift(-1).fillna(self.end_date_hyphen)
        pmi['CALENDAR_DATE'] = pmi['CALENDAR_DATE'].apply(lambda x: str(x).replace('-', ''))
        pmi = pmi.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']], on=['CALENDAR_DATE'], how='left')
        pmi = pmi.drop('CALENDAR_DATE', axis=1).set_index('TRADE_DATE').sort_index()
        pmi = pmi[(pmi.index > self.start_date) & (pmi.index <= self.end_date)].dropna()
        pmi_monthly = pmi.loc[pmi.index.isin(self.month_df['TRADE_DATE'].unique().tolist())]
        pmi_monthly['中国制造业PMI'] = pmi_monthly['中国制造业PMI'] / 100.0
        pmi_monthly['短期均值'] = pmi_monthly['中国制造业PMI'].rolling(3).mean()
        pmi_monthly['长期均值'] = pmi_monthly['中国制造业PMI'].rolling(12).mean()
        pmi_monthly = index.merge(pmi_monthly, left_index=True, right_index=True, how='right').sort_index()
        pmi_monthly_xls = pmi_monthly.copy(deep=True)
        pmi_monthly_xls.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), pmi_monthly_xls.index)
        pmi_monthly_xls.to_excel('{0}中国制造业PMI.xlsx'.format(self.data_path))
        ##########
        pmi_disp = pmi_monthly.dropna()
        pmi_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), pmi_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(pmi_disp.index, pmi_disp['短期均值'].values, color=line_color_list[0], label='短期均值', linewidth=3)
        ax.plot(pmi_disp.index, pmi_disp['长期均值'].values, color=line_color_list[1], label='长期均值', linewidth=3)
        ax_r.plot(pmi_disp.index, pmi_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(pmi_disp.index, pmi_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('中国制造业PMI', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}中国制造业PMI.png'.format(self.data_path))
        ##########
        pmi_disp = pmi_monthly.dropna()
        pmi_1, pmi_2 = pmi_disp.copy(deep=True), pmi_disp.copy(deep=True)
        pmi_1['上行'] = pmi_1.apply(lambda x: 1.0 if x['短期均值'] > x['长期均值'] else 0.0, axis=1)
        pmi_2['下行'] = pmi_2.apply(lambda x: 1.0 if x['短期均值'] < x['长期均值'] else 0.0, axis=1)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.bar(range(len(pmi_1)), pmi_1['上行'].values, color=line_color_list[0], alpha=0.5, label='上行', linewidth=3)
        ax.bar(range(len(pmi_2)), pmi_2['下行'].values, color=line_color_list[1], alpha=0.5, label='下行', linewidth=3)
        ax_r.plot(pmi_disp.index, pmi_disp['LARGE/SMALL'].values, color=line_color_list[2], label='大盘/小盘（右轴）', linewidth=3)
        ax_r.plot(pmi_disp.index, pmi_disp['VALUE/GROWTH'].values, color=line_color_list[3], label='价值/成长（右轴）', linewidth=3)
        ax.set_xticks(range(len(pmi_disp))[::12])
        ax.set_xticklabels(labels=pmi_disp.index.tolist()[::12])
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
        plt.title('中国制造业PMI分区', fontdict={'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}中国制造业PMI分区.png'.format(self.data_path))
        return


if __name__ == '__main__':
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/taa/'
    start_date = '20100630'
    end_date = '20240131'
    tracking_end_date = '20240131'
    # StyleTest(data_path, start_date, end_date).test()
    # SizeTest(data_path, start_date, end_date).test()
    # SizeTest(data_path, start_date, end_date).test_2()
    # IndustryTest(data_path, start_date, end_date).test('801180', '房地产')

    # insert_ytm(data_path, '20231231', '20240131')
    # SizeTAA(data_path, start_date, end_date, tracking_end_date).get_signal()
    # StyleTAA(data_path, start_date, end_date, tracking_end_date).get_signal()
    # StyleTAA(data_path, start_date, end_date, tracking_end_date).get_signal_new()
    # OverseasTAA(data_path, start_date, end_date, tracking_end_date).get_signal()
    # OverseasTAA(data_path, start_date, end_date, tracking_end_date).get_test()
    # StyleConstruction('20091231', '20231231', '20230930', '20240131', data_path).construction()
    # TAA(data_path, start_date, end_date).get_signal()