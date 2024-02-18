"""
量化中小盘精选代码模块
"""
import os

import numpy as np
import pandas as pd
import riskfolio as rp
from MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list
from MyUtil.data_config import fund_dict_compare
from datetime import datetime, timedelta
import statsmodels.api as sm
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params, style_names
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
from WindPy import w

w.start()


def customer_analysis():
    """
    存量客户数据分析函数
    """
    store_path = "D:\\研究基地\\Y-量化中小盘精选\\数据基地\\"
    data = pd.read_excel(os.path.join(store_path, "量化中小盘精选-存量客户数据-202311.xlsx"), sheet_name=0)
    include_cols = ['手机号归属省', '投顾客户号', '一级组织名称', '二级组织名称', '三级组织名称', '存量市值']
    data = data[include_cols]
    data['手机号归属省'] = data['手机号归属省'].fillna('其他')
    # 区域分布
    region_df = data.groupby('手机号归属省')['存量市值'].sum().sort_values().reset_index()
    # 组织分布
    level_1 = ((data.groupby('一级组织名称')['存量市值'].sum().sort_values() / 1e+4).round()).reset_index()
    level_2 = ((data.groupby('二级组织名称')['存量市值'].sum().sort_values() / 1e+4).round()).reset_index()
    level_3 = ((data.groupby('三级组织名称')['存量市值'].sum().sort_values() / 1e+4).round()).reset_index()

    data_param = {
        "region": region_df,
        "level_1": level_1,
        "level_2": level_2,
        "level_3": level_3
    }

    return data_param


def character_filter(str_x, characters_to_remove):
    for char in characters_to_remove:
        str_x = str_x.replace(char, '')

    return str_x

def HoldingExtractor_SMS(trade_date):
    """
    估值表解析函数
    """
    store_path = "D:\\研究基地\\Y-量化中小盘精选\\估值表"
    data = pd.read_excel(os.path.join(store_path, "SGG703_新方程量化中小盘精选_{}.xlsx".format(trade_date)),
                         sheet_name=0, header=3).dropna(subset=['科目代码'])
    hd_data = data[data['科目代码'].str.startswith('11090601')].dropna(how='all', axis=1)
    hd_data.dropna(inplace=True)
    hd_data = hd_data[['科目名称', '市值', '市值占净值%']].rename(
        columns={"科目名称": "fund_name", "市值": "MarketValue", "市值占净值%": "weight"})
    characters_to_remove = ['私募', '证券', '投资', '基金']
    hd_data['fund_name'] = hd_data['fund_name'].apply(lambda x: character_filter(x, characters_to_remove))
    # Link
    parent_path = os.path.dirname(store_path)
    link_df = pd.read_excel(os.path.join(parent_path, "My-底表.xlsx"), sheet_name="基金映射表")
    fund_dict = link_df.set_index('AMS映射标的')['Fund_id'].to_dict()
    trade_dt = datetime.strptime(trade_date, "%Y%m%d")
    pre_date = (trade_dt - timedelta(days=365)).strftime("%Y%m%d")
    week_list = get_trading_day_list(pre_date, trade_date, frequency="week")
    fund_nav = get_fund_nav_from_sql(pre_date, trade_date, fund_dict).reindex(week_list)
    return_df = fund_nav.pct_change(periods=1).iloc[-1].to_frame('最近一周').merge(
        fund_nav.pct_change(periods=2).iloc[-1].to_frame('最近二周'), left_index=True, right_index=True).merge(
        fund_nav.pct_change(periods=4).iloc[-1].to_frame('最近四周'), left_index=True, right_index=True).merge(
        fund_nav.pct_change(periods=8).iloc[-1].to_frame('最近八周'), left_index=True, right_index=True)
    print("===================================净值缺失===================================")
    na_counts = fund_nav.isnull().sum(axis=1)
    na_dates = na_counts[na_counts > 0].index.tolist()
    for date in na_dates:
        na_names = fund_nav.loc[date][fund_nav.loc[date].isna()].index.to_list()
        true_na = []
        for name in na_names:
            true_na.append(name)
        if len(true_na) >= 1:
            print("{}期: 缺失{}".format(date, true_na))
    # merge
    cf = link_df.merge(hd_data.set_index('fund_name'), left_on='投资标的名', right_index=True)
    holding_df = cf.groupby('AMS映射标的')[['MarketValue', 'weight']].sum()
    pf = holding_df.merge(
        cf.drop_duplicates(subset=['AMS映射标的']).set_index('AMS映射标的')[['池属性', '二级策略']],
        left_index=True, right_index=True).merge(return_df, left_index=True, right_index=True)
    pf['weight'] /= 100.
    pf.rename(columns={"MarketValue": "持仓市值", "weight": "权重"}, inplace=True)
    pf.sort_index(inplace=True)

    return pf


def fund_compare(start_date, end_date):
    trading_day_list = get_trading_day_list(start_date, end_date, "week")
    fund_nav = get_fund_nav_from_sql(start_date, end_date, fund_dict_compare).reindex(trading_day_list)
    fund_nav.loc[: "20230120", "倍漾1000指增"] = np.NaN
    fund_nav.loc[: "20230324", "博普量化多头"] = np.NaN
    return_df = fund_nav.pct_change(limit=1).dropna(how='all')
    # index
    index_list = ["000852.SH", "932000.CSI", "999004.SSI"]
    res = w.wsd(','.join(index_list), "close", start_date, end_date, "")
    d_list = [datetime.strftime(x, '%Y%m%d') for x in res.Times]
    index_df = pd.DataFrame(res.Data, index=res.Codes, columns=d_list).T
    index_df /= index_df.iloc[0]
    index_df.rename(columns={"000852.SH": "中证1000", "932000.CSI": "中证2000", "999004.SSI": "华证微盘"}, inplace=True)
    index_df = index_df.reindex(trading_day_list).pct_change().dropna()
    index_df.eval("中证2000_中证1000 = 中证2000 - 中证1000", inplace=True)
    index_df.eval("微盘_中证1000 = 华证微盘 - 中证1000", inplace=True)
    include_cols = ['中证2000_中证1000', '微盘_中证1000']

    assert (return_df.shape[0] == index_df.shape[0])

    excess_df = return_df.sub(index_df['中证1000'], axis=0)
    excess_df = excess_df.merge(index_df[include_cols], left_index=True, right_index=True)
    coef_df = pd.DataFrame(index=excess_df.columns[:-2], columns=excess_df.columns[-2:])
    alpha_df = pd.DataFrame(index=excess_df.columns[:-2], columns=excess_df.columns[-2:])
    for col1 in corr_df.index.tolist():
        for col2 in corr_df.columns.tolist():
            tmp = excess_df[[col1, col2]].dropna()
            results = sm.OLS(tmp[col1], sm.add_constant(tmp[col2])).fit()
            coef_df.loc[col1, col2] = results.params.loc[col2]
            alpha_df.loc[col1, col2] = results.params.loc["const"]

    return corr_df


def portfolio_optimization(start_date, reb_date):
    """
    :param start_date: 起始日期
    :param reb_date: 优化日期
    :return:
    """
    config_df = pd.read_excel("D:\\研究基地\\Y-量化中小盘精选\\量化多头标的分析.xlsx", sheet_name="备选配置标的",
                              dtype={"nav_start": str})
    fund_dict = config_df.set_index('基金')['fund_id'].to_dict()
    trading_day_list = get_trading_day_list(start_date, reb_date, "week")
    fund_nav = get_fund_nav_from_sql(start_date, reb_date, fund_dict).reindex(trading_day_list)
    Y = fund_nav.pct_change().dropna()
    # 风格收益
    sql_script = "SELECT * FROM factor_return where TRADE_DATE >= {} and TRADE_DATE <= {}".format(start_date, reb_date)
    engine = create_engine(engine_params)
    factor_return = pd.read_sql(sql_script, engine)
    factor_return['trade_date'] = factor_return['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    factor_return = pd.pivot_table(
        factor_return, index='trade_date', columns='factor_name', values='factor_ret').sort_index()
    factor_return = (1 + factor_return).cumprod().reindex(trading_day_list).pct_change().dropna()[style_names]
    factor_loading = (sm.OLS(Y, sm.add_constant(factor_return)).fit()).params
    factor_loading.columns = Y.columns
    factor_loading = factor_loading.T
    # 个基约束
    asset_classes = config_df.rename(
        columns={"基金": "Assets", "type": "Class1"})[['Assets', 'Class1']]
    constraints = pd.read_excel(
        "D:\\研究基地\\Y-量化中小盘精选\\量化多头标的分析.xlsx", sheet_name="优化约束条件")

    A, B = rp.assets_constraints(constraints, asset_classes)
    # 添加市值下限约束
    # A = np.vstack((A, factor_loading['size'].values))
    # B = np.vstack((B, [-1.3]))
    # 优化参数
    port = rp.Portfolio(returns=Y)
    method_mu = "hist"
    method_cov = "hist"
    port.assets_stats(method_mu=method_mu, method_cov=method_cov, d=0.94)

    port.ainequality = A
    port.binequality = B

    model = 'Classic'
    rm = 'MV'
    # obj = 'Utility'
    # obj = "Sharpe"
    obj = "MaxRet"
    hist = True
    rf = 0
    l = 0

    optimal_w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)

    # 饼图
    # ax = rp.plot_pie(w=optimal_w, title='Sharpe Mean Variance', others=0.01, nrow=25, cmap="tab20",
    #                  height=6, width=10, ax=None)

    # 柱状图
    # ax = rp.plot_bar(optimal_w,
    #                  title='Sharpe Mean Variance',
    #                  kind="v",
    #                  others=0.01,
    #                  nrow=25,
    #                  height=6,
    #                  width=10,
    #                  ax=None)
    print("市值敞口: {}".format(factor_loading.T.dot(optimal_w).loc['size']))
    # 有效前沿
    # points = 50  # Number of points of the frontier
    # frontier = port.efficient_frontier(model=model, rm=rm, points=points, rf=rf, hist=hist)
    # label = 'Max Risk Adjusted Return Portfolio'  # Title of point
    # mu = port.mu  # Expected returns
    # cov = port.cov  # Covariance matrix
    # returns = port.returns  # Returns of the assets
    # ax = rp.plot_frontier(w_frontier=frontier, mu=mu, cov=cov, returns=returns, rm=rm,
    #                       rf=rf, alpha=0.05, cmap='viridis', w=w, label=label,
    #                       marker='*', s=16, c='r', height=6, width=10, ax=None)

    # 回测曲线
    Y1 = Y.copy()
    Y1.loc[start_date] = 0.
    Y1.sort_index(inplace=True)
    Y1['trade_date'] = Y1.index
    Y1['trade_date'] = Y1['trade_date'].apply(lambda x: datetime.strptime(x, "%Y%m%d"))
    Y1.set_index('trade_date', inplace=True)
    # ax = rp.plot_series(returns=Y1, w=w, cmap='tab20', height=6, width=10, ax=None)

    nav_df = (1 + Y1).cumprod().dot(optimal_w).merge((1 + Y1).cumprod(), left_index=True, right_index=True)

    return optimal_w, nav_df, factor_loading


if __name__ == '__main__':
    # HoldingExtractor_SMS("20231222")
    # customer_analysis()
    # fund_compare("20221230", "20231222")
    portfolio_optimization("20230331", "20231215")