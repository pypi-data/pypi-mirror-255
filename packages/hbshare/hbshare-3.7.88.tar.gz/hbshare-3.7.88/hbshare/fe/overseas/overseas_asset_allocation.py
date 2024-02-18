# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
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


def quantile_definition(idxs, col, daily_df):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    q = (1.0 - np.count_nonzero(part_df[col].iloc[-1] < part_df[col]) / len(part_df)) if len(part_df[col].dropna()) != 0 else np.nan
    return q


class OverseasAssetAllocation:
    def __init__(self, start_date, end_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.index_list = ['SPX Index', 'CCMP Index', 'TPX Index', 'VN30 Index', 'SENSEX Index', 'DAX Index']
        self.index_name_dict = {
            'SPX Index': '标普500指数', 'CCMP Index': '纳斯达克综合指数', 'TPX Index': '日本东证指数',
            'VN30 Index': '越南VN30指数', 'SENSEX Index': '印度孟买30指数', 'DAX Index': '德国DAX30指数'
        }
        self.index_weight_dict = {
            'SPX Index': 0.25, 'CCMP Index': 0.25, 'TPX Index': 0.125,
            'VN30 Index': 0.125, 'SENSEX Index': 0.125, 'DAX Index': 0.125
        }
        self.index_weight_dict_2 = {
            'SPX Index': 0.251733, 'CCMP Index': 0.277008, 'TPX Index': 0.120829,
            'VN30 Index': 0.124195, 'SENSEX Index': 0.116720, 'DAX Index': 0.109514
        }
        self.index_weight_dict_3 = {
            'SPX Index': 0.377567, 'CCMP Index': 0.377567, 'TPX Index': 0.091469,
            'VN30 Index': 0.003476, 'SENSEX Index': 0.118483, 'DAX Index': 0.031438
        }
        self.load()

    def load(self):
        # 交易日历
        self.cal = HBDB().read_overseas_cal('76')
        self.cal['rq'] = self.cal['rq'].astype(str)
        self.trade_cal = self.cal[self.cal['sfjy'] == '1']
        self.monthly_cal = self.cal[self.cal['sfym'] == '1']

        # 指数数据
        # self.overseas_index_daily_k = HBDB().read_overseas_index_daily_k_given_indexs(self.index_list)
        # self.overseas_index_daily_k.to_hdf('{0}overseas_index_daily_k.hdf'.format(self.data_path), key='table', mode='w')
        self.overseas_index_daily_k = pd.read_hdf('{0}overseas_index_daily_k.hdf'.format(self.data_path), key='table')
        self.overseas_index_daily_k['jyrq'] = self.overseas_index_daily_k['jyrq'].astype(str)
        self.overseas_index_daily_k = self.overseas_index_daily_k[(self.overseas_index_daily_k['jyrq'] >= self.start_date) & (self.overseas_index_daily_k['jyrq'] <= self.end_date)]

        # self.overseas_index_finance = HBDB().read_overseas_index_finance_given_indexs(self.index_list)
        # self.overseas_index_finance.to_hdf('{0}overseas_index_finance.hdf'.format(self.data_path), key='table', mode='w')
        self.overseas_index_finance = pd.read_hdf('{0}overseas_index_finance.hdf'.format(self.data_path), key='table')
        self.overseas_index_finance['jyrq'] = self.overseas_index_finance['jyrq'].astype(str)
        self.overseas_index_finance = self.overseas_index_finance[(self.overseas_index_finance['jyrq'] >= self.start_date) & (self.overseas_index_finance['jyrq'] <= self.end_date)]

        # self.overseas_index_best = HBDB().read_overseas_index_best_given_indexs(self.index_list)
        # self.overseas_index_best.to_hdf('{0}overseas_index_best.hdf'.format(self.data_path), key='table', mode='w')
        self.overseas_index_best = pd.read_hdf('{0}overseas_index_best.hdf'.format(self.data_path), key='table')
        self.overseas_index_best['jyrq'] = self.overseas_index_best['jyrq'].astype(str)
        self.overseas_index_best = self.overseas_index_best[(self.overseas_index_best['jyrq'] >= self.start_date) & (self.overseas_index_best['jyrq'] <= self.end_date)]
        return

    def strategy(self, w_p, w_b, ret, q, strategy_name):
        ret_p = (w_p.shift() * ret).dropna().sum(axis=1)
        ret_b = (w_b.shift() * ret).dropna().sum(axis=1)
        df = pd.concat([ret_p, ret_b], axis=1)
        df.columns = ['P_RET', 'B_RET']
        df['E_RET'] = df['P_RET'] - df['B_RET']
        df.iloc[0] = 0.0
        df['P_NAV'] = (df['P_RET'] + 1.0).cumprod()
        df['B_NAV'] = (df['B_RET'] + 1.0).cumprod()
        df['E_NAV'] = (df['E_RET'] + 1.0).cumprod()
        df.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), df.index)

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(df.index, df['P_NAV'].values, color=line_color_list[0], label='组合', linewidth=2)
        ax.plot(df.index, df['B_NAV'].values, color=line_color_list[2], label='基准', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.25), ncol=3, frameon=False)
        plt.title(strategy_name)
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}{1}.png'.format(self.data_path, strategy_name))

        performance = pd.DataFrame(index=['年化收益率', '年化波动率', '最大回撤', '夏普比率', '卡玛比率', '投资胜率', '投资损益比'], columns=['指标值', '基准指标值', '超额指标值'])
        performance.loc['年化收益率', '指标值'] = (df['P_NAV'].iloc[-1] / df['P_NAV'].iloc[0]) ** (q / float(len(df) - 1)) - 1.0
        performance.loc['年化波动率', '指标值'] = np.std(df['P_RET'].dropna(), ddof=1) * np.sqrt(q)
        performance.loc['最大回撤', '指标值'] = max([(min(df['P_NAV'].iloc[i:]) / df['P_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['P_NAV']))])
        performance.loc['夏普比率', '指标值'] = (performance.loc['年化收益率', '指标值'] - 0.015) / performance.loc['年化波动率', '指标值']
        performance.loc['卡玛比率', '指标值'] = performance.loc['年化收益率', '指标值'] / performance.loc['最大回撤', '指标值']
        performance.loc['投资胜率', '指标值'] = len(df[df['P_RET'] > 0]) / float(len(df.dropna()))
        performance.loc['投资损益比', '指标值'] = df[df['P_RET'] > 0]['P_RET'].mean() / df[df['P_RET'] < 0]['P_RET'].mean() * (-1.0)
        performance.loc['年化收益率', '基准指标值'] = (df['B_NAV'].iloc[-1] / df['B_NAV'].iloc[0]) ** (q / float(len(df) - 1)) - 1.0
        performance.loc['年化波动率', '基准指标值'] = np.std(df['B_RET'].dropna(), ddof=1) * np.sqrt(q)
        performance.loc['最大回撤', '基准指标值'] = max([(min(df['B_NAV'].iloc[i:]) / df['B_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['B_NAV']))])
        performance.loc['夏普比率', '基准指标值'] = (performance.loc['年化收益率', '基准指标值'] - 0.015) / performance.loc['年化波动率', '基准指标值']
        performance.loc['卡玛比率', '基准指标值'] = performance.loc['年化收益率', '基准指标值'] / performance.loc['最大回撤', '基准指标值']
        performance.loc['投资胜率', '基准指标值'] = len(df[df['B_RET'] > 0]) / float(len(df.dropna()))
        performance.loc['投资损益比', '基准指标值'] = df[df['B_RET'] > 0]['B_RET'].mean() / df[df['B_RET'] < 0]['B_RET'].mean() * (-1.0)
        performance.loc['年化收益率', '超额指标值'] = (df['E_NAV'].iloc[-1] / df['E_NAV'].iloc[0]) ** (q / float(len(df) - 1)) - 1.0
        performance.loc['年化波动率', '超额指标值'] = np.std(df['E_RET'].dropna(), ddof=1) * np.sqrt(q)
        performance.loc['最大回撤', '超额指标值'] = max([(min(df['E_NAV'].iloc[i:]) / df['E_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(df['E_NAV']))])
        performance.loc['夏普比率', '超额指标值'] = (performance.loc['年化收益率', '超额指标值'] - 0.015) / performance.loc['年化波动率', '超额指标值']
        performance.loc['卡玛比率', '超额指标值'] = performance.loc['年化收益率', '超额指标值'] / performance.loc['最大回撤', '超额指标值']
        performance.loc['投资胜率', '超额指标值'] = len(df[df['E_RET'] > 0]) / float(len(df.dropna()))
        performance.loc['投资损益比', '超额指标值'] = df[df['E_RET'] > 0]['E_RET'].mean() / df[df['E_RET'] < 0]['E_RET'].mean() * (-1.0)
        performance.to_excel('{0}{1}.xlsx'.format(self.data_path, strategy_name))
        return

    def test(self):
        # 月度收益率
        nav = self.overseas_index_daily_k.pivot(index='jyrq', columns='bzzsdm', values='px_last').sort_index()
        nav = nav[self.index_list].rename(columns=self.index_name_dict)
        nav = nav.dropna()
        nav_monthly = nav[nav.index.isin(self.monthly_cal['rq'].unique().tolist())].sort_index()
        ret_monthly = nav_monthly.pct_change().dropna()

        # 总市值
        mv = self.overseas_index_daily_k.pivot(index='jyrq', columns='bzzsdm', values='cur_mkt_cap').sort_index()
        mv = mv[self.index_list].rename(columns=self.index_name_dict)
        mv = mv.dropna()
        mv_monthly = mv[mv.index.isin(self.monthly_cal['rq'].unique().tolist())].sort_index()
        mv_monthly['日本东证指数'] = mv_monthly['日本东证指数'] / 144.52
        mv_monthly['越南VN30指数'] = mv_monthly['越南VN30指数'] / 23900
        mv_monthly['印度孟买30指数'] = mv_monthly['印度孟买30指数'] / 83.33
        mv_monthly['德国DAX30指数'] = mv_monthly['德国DAX30指数'] / 0.91
        for col in list(mv_monthly.columns):
            mv_monthly[col] = mv_monthly[col].apply(lambda x: np.log(x))

        # # EPS/BEST_EPS增长率排序策略
        # eps = self.overseas_index_best.pivot(index='jyrq', columns='bzzsdm', values='best_eps').sort_index()
        # # eps = self.overseas_index_finance.pivot(index='jyrq', columns='bzzsdm', values='trail_12m_eps_bef_xo_item').sort_index()
        # eps = eps[self.index_list].rename(columns=self.index_name_dict)
        # eps = eps.dropna()
        # eps_monthly = eps[eps.index.isin(self.monthly_cal['rq'].unique().tolist())].sort_index()
        # weight_p = eps_monthly.rolling(12).mean().pct_change(12).dropna()
        # weight_p = weight_p.rank(axis=1)
        # weight_p = weight_p.replace({6: 0.5, 5: 0.3, 4: 0.1, 3: -0.1, 2: -0.3, 1: -0.5})
        # weight_p = 1.0 / weight_p.shape[1] * (1 + weight_p)
        # weight_b = 1.0 / weight_p.shape[1] * pd.DataFrame(np.ones(weight_p.shape), index=weight_p.index.tolist(), columns=self.index_list)
        # weight_b = weight_b[self.index_list].rename(columns=self.index_name_dict)
        # self.strategy(weight_p, weight_b, ret_monthly, 12, 'BEST_EPS增长率排序策略')
        # # self.strategy(weight_p, weight_b, ret_monthly, 12, 'EPS增长率排序策略')

        # # PE/BEST_PE分位区间排序策略
        # pe = self.overseas_index_best.pivot(index='jyrq', columns='bzzsdm', values='best_pe_ratio').sort_index()
        # # pe = self.overseas_index_daily_k.pivot(index='jyrq', columns='bzzsdm', values='pe_ratio').sort_index()
        # pe = pe[self.index_list].rename(columns=self.index_name_dict)
        # pe = pe.dropna()
        # pe_monthly = pe[pe.index.isin(self.monthly_cal['rq'].unique().tolist())].sort_index()
        # pe_monthly_ori = pe_monthly.copy(deep=True)
        # for n in [1, 3, 5, 10]:
        #     pe_monthly = pe_monthly_ori.copy(deep=True)
        #     pe_monthly['IDX'] = range(len(pe_monthly))
        #     for col in list(pe_monthly.columns):
        #         pe_monthly[col] = pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, col, pe_monthly))
        #     weight_p = pe_monthly.drop('IDX', axis=1).dropna()
        #     weight_p = weight_p.rolling(12).mean().dropna()
        #     weight_p = weight_p.rank(axis=1)
        #     weight_p = weight_p.replace({1: 0.5, 2: 0.3, 3: 0.1, 4: -0.1, 5: -0.3, 6: -0.5})
        #     weight_p = 1.0 / weight_p.shape[1] * (1 + weight_p)
        #     weight_b = 1.0 / weight_p.shape[1] * pd.DataFrame(np.ones(weight_p.shape), index=weight_p.index.tolist(), columns=self.index_list)
        #     weight_b = weight_b[self.index_list].rename(columns=self.index_name_dict)
        #     self.strategy(weight_p, weight_b, ret_monthly, 12, '近{0}年BEST_PE分位排序策略'.format(n))
        #     # self.strategy(weight_p, weight_b, ret_monthly, 12, '近{0}年PE分位排序策略'.format(n))

        # # PE/BEST_PE分位区间策略
        # pe = self.overseas_index_best.pivot(index='jyrq', columns='bzzsdm', values='best_pe_ratio').sort_index()
        # # pe = self.overseas_index_daily_k.pivot(index='jyrq', columns='bzzsdm', values='pe_ratio').sort_index()
        # pe = pe[self.index_list].rename(columns=self.index_name_dict)
        # pe = pe.dropna()
        # pe_monthly = pe[pe.index.isin(self.monthly_cal['rq'].unique().tolist())].sort_index()
        # pe_monthly_ori = pe_monthly.copy(deep=True)
        # for n in [1, 3, 5, 10]:
        #     pe_monthly = pe_monthly_ori.copy(deep=True)
        #     pe_monthly['IDX'] = range(len(pe_monthly))
        #     for col in list(pe_monthly.columns):
        #         pe_monthly[col] = pe_monthly['IDX'].rolling(12 * n).apply(lambda x: quantile_definition(x, col, pe_monthly))
        #         pe_monthly[col] = pe_monthly[col].apply(lambda x: 1 if x <= 0.2 else 0 if x >= 0.8 else 0.5)
        #     weight_p = pe_monthly.drop('IDX', axis=1).dropna()
        #     weight_p = weight_p.apply(lambda x: x / x.sum() if x.sum() != 0 else 1.0 / weight_p.shape[1], axis=1)
        #     weight_b = 1.0 / weight_p.shape[1] * pd.DataFrame(np.ones(weight_p.shape), index=weight_p.index.tolist(), columns=self.index_list)
        #     weight_b = weight_b[self.index_list].rename(columns=self.index_name_dict)
        #     self.strategy(weight_p, weight_b, ret_monthly, 12, '近{0}年BEST_PE分位区间策略'.format(n))
        #     # self.strategy(weight_p, weight_b, ret_monthly, 12, '近{0}年PE分位区间策略'.format(n))

        # EPS/BEST_EPS增长率排序策略
        eps = self.overseas_index_best.pivot(index='jyrq', columns='bzzsdm', values='best_eps').sort_index()
        # eps = self.overseas_index_finance.pivot(index='jyrq', columns='bzzsdm', values='trail_12m_eps_bef_xo_item').sort_index()
        eps = eps[self.index_list].rename(columns=self.index_name_dict)
        eps = eps.dropna()
        eps_monthly = eps[eps.index.isin(self.monthly_cal['rq'].unique().tolist())].sort_index()
        weight_adj = eps_monthly.rolling(12).mean().pct_change(12).dropna()
        weight_adj = weight_adj.rank(axis=1)
        weight_adj = weight_adj.replace({6: 0.5, 5: 0.3, 4: 0.1, 3: -0.1, 2: -0.3, 1: -0.5})

        weight_b1 = pd.DataFrame(np.ones(weight_adj.shape), index=weight_adj.index.tolist(), columns=self.index_list)
        weight_b1 = weight_b1 * 1.0 / weight_adj.shape[1]
        weight_b1 = weight_b1[self.index_list].rename(columns=self.index_name_dict)
        weight_p1 = weight_b1 * (1 + weight_adj)
        weight_p1 = weight_p1.apply(lambda x: x / x.sum() if x.sum() != 0 else 1.0 / weight_adj.shape[1], axis=1)
        self.strategy(weight_p1, weight_b1, ret_monthly, 12, 'BEST_EPS增长率排序策略（等权基准）')
        # self.strategy(weight_p1, weight_b1, ret_monthly, 12, 'EPS增长率排序策略（等权基准）')

        weight_b2 = pd.DataFrame(np.ones(weight_adj.shape), index=weight_adj.index.tolist(), columns=self.index_list)
        for col in self.index_list:
            weight_b2[col] = weight_b2[col] * self.index_weight_dict[col]
        weight_b2 = weight_b2[self.index_list].rename(columns=self.index_name_dict)
        weight_p2 = weight_b2 * (1 + weight_adj)
        weight_p2 = weight_p2.apply(lambda x: x / x.sum() if x.sum() != 0 else 1.0 / weight_adj.shape[1], axis=1)
        self.strategy(weight_p2, weight_b2, ret_monthly, 12, 'BEST_EPS增长率排序策略（固定比例基准）')
        # self.strategy(weight_p2, weight_b2, ret_monthly, 12, 'EPS增长率排序策略（固定比例基准）')

        weight_b3 = pd.DataFrame(np.ones(weight_adj.shape), index=weight_adj.index.tolist(), columns=self.index_list)
        for col in self.index_list:
            weight_b3[col] = weight_b3[col] * self.index_weight_dict[col]
        weight_b3 = weight_b3[self.index_list].rename(columns=self.index_name_dict)
        weight_p3 = weight_b3 * (1 + weight_adj)
        weight_p3 = weight_p3.apply(lambda x: x / x.sum() if x.sum() != 0 else 1.0 / weight_adj.shape[1], axis=1)
        weight_p3['TEMP'] = weight_p3.iloc[:, :2].sum(axis=1)
        weight_p3_noadj = weight_p3[weight_p3['TEMP'] >= 0.5]
        weight_p3_adj = weight_p3[weight_p3['TEMP'] < 0.5]
        weight_p3_noadj = weight_p3_noadj.drop('TEMP', axis=1)
        weight_p3_adj = weight_p3_adj.drop('TEMP', axis=1)
        weight_p3_adj.iloc[:, :2] = weight_p3_adj.iloc[:, :2].apply(lambda x: x / x.sum() * 0.5 if x.sum() != 0 else 1.0 / 2.0 * 0.5, axis=1)
        weight_p3_adj.iloc[:, 2:] = weight_p3_adj.iloc[:, 2:].apply(lambda x: x / x.sum() * 0.5 if x.sum() != 0 else 1.0 / 4.0 * 0.5, axis=1)
        weight_p3 = pd.concat([weight_p3_noadj, weight_p3_adj]).sort_index()
        self.strategy(weight_p3, weight_b3, ret_monthly, 12, 'BEST_EPS增长率排序策略（固定比例基同时限定国家比例基准）')
        # self.strategy(weight_p3, weight_b3, ret_monthly, 12, 'EPS增长率排序策略（固定比例基同时限定国家比例基准）')

        # weight_pxlast = weight_p3.merge(nav_monthly, left_index=True, right_index=True, how='left')
        # weight_pxlast.to_excel('{0}weight_p3.xlsx'.format(self.data_path))

        weight_b4 = pd.DataFrame(np.ones(weight_adj.shape), index=weight_adj.index.tolist(), columns=self.index_list)
        for col in self.index_list:
            weight_b4[col] = weight_b4[col] * self.index_weight_dict_2[col]
        weight_b4 = weight_b4[self.index_list].rename(columns=self.index_name_dict)

        weight_b4 = pd.DataFrame(np.ones(weight_adj.shape), index=weight_adj.index.tolist(), columns=self.index_list)
        for col in self.index_list:
            weight_b4[col] = weight_b4[col] * self.index_weight_dict[col]
        weight_b4 = weight_b4[self.index_list].rename(columns=self.index_name_dict)
        weight_p4 = weight_b4 * (1 + weight_adj)
        weight_p4 = weight_p4.apply(lambda x: x / x.sum() if x.sum() != 0 else 1.0 / weight_adj.shape[1], axis=1)
        # weight_p4['TEMP'] = weight_p4.iloc[:, :2].sum(axis=1)
        # weight_p4_noadj = weight_p4[weight_p4['TEMP'] >= 0.5]
        # weight_p4_adj = weight_p4[weight_p4['TEMP'] < 0.5]
        # weight_p4_noadj = weight_p4_noadj.drop('TEMP', axis=1)
        # weight_p4_adj = weight_p4_adj.drop('TEMP', axis=1)
        # weight_p4_adj.iloc[:, :2] = weight_p4_adj.iloc[:, :2].apply(lambda x: x / x.sum() * 0.5 if x.sum() != 0 else 1.0 / 2.0 * 0.5, axis=1)
        # weight_p4_adj.iloc[:, 2:] = weight_p4_adj.iloc[:, 2:].apply(lambda x: x / x.sum() * 0.5 if x.sum() != 0 else 1.0 / 4.0 * 0.5, axis=1)
        # weight_p4 = pd.concat([weight_p4_noadj, weight_p4_adj]).sort_index()
        # weight_p4['TEMP'] = weight_p4.iloc[:, [2,4]].sum(axis=1)
        # weight_p4_noadj = weight_p4[weight_p4['TEMP'] <= 0.3]
        # weight_p4_adj = weight_p4[weight_p4['TEMP'] > 0.3]
        # weight_p4_noadj = weight_p4_noadj.drop('TEMP', axis=1)
        # weight_p4_adj = weight_p4_adj.drop('TEMP', axis=1)
        weight_p4.iloc[:, [2, 4]] = weight_p4.iloc[:, [2, 4]].apply(lambda x: x / x.sum() * 0.25 if x.sum() > 0.25 else x, axis=1)
        weight_p4.iloc[:, [3, 5]] = weight_p4.iloc[:, [3, 5]].apply(lambda x: x / x.sum() * 0.15 if x.sum() > 0.15 else x, axis=1)
        # weight_p4_adj.iloc[:, [3,5]] = weight_p4_adj.iloc[:, [3,5]].apply(lambda x: x / x.sum() * 0.2 if x.sum() != 0 else 1.0 / 2.0 * 0.2, axis=1)
        # weight_p4 = pd.concat([weight_p4_noadj, weight_p4_adj]).sort_index()
        # self.strategy(weight_p3, weight_b3, ret_monthly, 12, 'BEST_EPS增长率排序策略（固定比例基同时限定国家比例基准）')
        # self.strategy(weight_p3, weight_b3, ret_monthly, 12, 'EPS增长率排序策略（固定比例基同时限定国家比例基准）')

        ret_p1 = (weight_p1.shift() * ret_monthly).dropna().sum(axis=1)
        ret_b1 = (weight_b1.shift() * ret_monthly).dropna().sum(axis=1)
        ret_p2 = (weight_p2.shift() * ret_monthly).dropna().sum(axis=1)
        ret_b2 = (weight_b2.shift() * ret_monthly).dropna().sum(axis=1)
        ret_p3 = (weight_p3.shift() * ret_monthly).dropna().sum(axis=1)
        ret_b3 = (weight_b3.shift() * ret_monthly).dropna().sum(axis=1)
        ret_b4 = (weight_b4.shift() * ret_monthly).dropna().sum(axis=1)
        df = pd.concat([ret_p1, ret_b1, ret_p2, ret_b2, ret_p3, ret_b3,  ret_b4], axis=1)
        df.columns = ['P1_RET', 'B1_RET', 'P2_RET', 'B2_RET', 'P3_RET', 'B3_RET', 'B4_RET']
        df['E1_RET'] = df['P1_RET'] - df['B1_RET']
        df['E2_RET'] = df['P2_RET'] - df['B2_RET']
        df['E3_RET'] = df['P3_RET'] - df['B3_RET']
        df.iloc[0] = 0.0
        df['P1_NAV'] = (df['P1_RET'] + 1.0).cumprod()
        df['B1_NAV'] = (df['B1_RET'] + 1.0).cumprod()
        df['E1_NAV'] = (df['E1_RET'] + 1.0).cumprod()
        df['P2_NAV'] = (df['P2_RET'] + 1.0).cumprod()
        df['B2_NAV'] = (df['B2_RET'] + 1.0).cumprod()
        df['E2_NAV'] = (df['E2_RET'] + 1.0).cumprod()
        df['P3_NAV'] = (df['P3_RET'] + 1.0).cumprod()
        df['B3_NAV'] = (df['B3_RET'] + 1.0).cumprod()
        df['E3_NAV'] = (df['E3_RET'] + 1.0).cumprod()
        df['B4_NAV'] = (df['B4_RET'] + 1.0).cumprod()
        df.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), df.index)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df.index, df['P1_NAV'].values, color=line_color_list[0], label='等权基准上调整', linewidth=2)
        ax.plot(df.index, df['B1_NAV'].values, color=line_color_list[0], label='等权基准', linewidth=2, linestyle='--')
        ax.plot(df.index, df['P2_NAV'].values, color=line_color_list[1], label='固定比例基准上调整', linewidth=2)
        ax.plot(df.index, df['B2_NAV'].values, color=line_color_list[1], label='固定比例基准', linewidth=2, linestyle='--')
        ax.plot(df.index, df['P3_NAV'].values, color=line_color_list[2], label='固定比例同时限定国家比例基准上调整', linewidth=2)
        ax.plot(df.index, df['B3_NAV'].values, color=line_color_list[2], label='固定比例同时限定国家比例基准', linewidth=2, linestyle='--')
        ax.plot(df.index, df['B4_NAV'].values, color=line_color_list[3], label='固定比例同时限定国家比例基准（后验）', linewidth=2, linestyle='--')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False)
        plt.title('BEST_EPS增长率排序策略')
        # plt.title('EPS增长率排序策略')
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}BEST_EPS增长率排序策略（多个）.png'.format(self.data_path))
        # plt.savefig('{0}EPS增长率排序策略（多个）.png'.format(self.data_path))

        # EPS/BEST_EPS增长率排序策略
        eps = self.overseas_index_best.pivot(index='jyrq', columns='bzzsdm', values='best_eps').sort_index()
        # eps = self.overseas_index_finance.pivot(index='jyrq', columns='bzzsdm', values='trail_12m_eps_bef_xo_item').sort_index()
        eps = eps[self.index_list].rename(columns=self.index_name_dict)
        eps = eps.dropna()
        eps_monthly = eps[eps.index.isin(self.monthly_cal['rq'].unique().tolist())].sort_index()
        weight_adj = eps_monthly.rolling(12).mean().pct_change(12).dropna()
        weight_adj = weight_adj.rank(axis=1)
        weight_adj = weight_adj.replace({6: 0.5, 5: 0.3, 4: 0.1, 3: -0.1, 2: -0.3, 1: -0.5})

        weight_b5 = pd.DataFrame(np.ones(weight_adj.shape), index=weight_adj.index.tolist(), columns=self.index_list)
        for col in self.index_list:
            weight_b5[col] = weight_b5[col] * self.index_weight_dict_3[col]
        weight_b5 = weight_b5[self.index_list].rename(columns=self.index_name_dict)
        weight_p5 = weight_b5 * (1 + weight_adj)
        weight_p5 = weight_p5.apply(lambda x: x / x.sum() if x.sum() != 0 else 1.0 / weight_adj.shape[1], axis=1)
        self.strategy(weight_p5, weight_b5, ret_monthly, 12, 'BEST_EPS增长率排序策略（市值加权）')
        # self.strategy(weight_p2, weight_b2, ret_monthly, 12, 'EPS增长率排序策略（市值加权）')
        return

if __name__ == '__main__':
    start_date = '19900101'
    end_date = '20231231'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/overseas_asset_allocation/'
    OverseasAssetAllocation(start_date, end_date, data_path).test()