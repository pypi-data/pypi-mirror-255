"""
FOF相关的代码模块
"""
import datetime
# coding=utf-8
import os
import pandas as pd
import numpy as np
import hbshare as hbs
import random
from tqdm import tqdm
from prettytable import PrettyTable
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, \
    get_trading_day_list, get_index_return_from_sql
from Arbitrage_backtest import cal_annual_return, cal_annual_volatility, cal_sharpe_ratio, cal_max_drawdown
from WindPy import w

w.start()


class FofGapAnalysis:
    def __init__(self, start_date, end_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path

    def run(self):
        # 持仓数据-start_date
        path = os.path.join(self.data_path,
                            "估值表文件\\SSL554_新方程量化中小盘精选二号_{}.xlsx".format(self.start_date))
        holding_df = pd.read_excel(path, header=3)
        init_cash = holding_df.loc[holding_df['科目代码'] == '实收资本', '市值'].values[0]
        init_asset = holding_df.loc[holding_df['科目代码'] == '基金资产净值:', '市值'].values[0]
        holding_df = holding_df[holding_df['科目代码'].str.startswith('11090601')].dropna(subset=['单位成本'])
        holding_df.rename(columns={"科目名称": "fund_name", "市值": self.start_date}, inplace=True)
        holding_df = holding_df.set_index('fund_name')[[self.start_date]]
        # 交易流水
        path = os.path.join(self.data_path, "资金流水\\产品资金流水.xls")
        trading_df = pd.read_excel(path, header=2)
        trading_df['交易时点'] = trading_df['交易时点'].apply(lambda x: x.split(' ')[0].replace('-', ''))
        include_list = ['交易时点', '收付方向', '发生金额', '账户余额', '摘要']
        trading_df = trading_df[include_list]
        trading_df = trading_df[trading_df['交易时点'] <= self.end_date].sort_values(by='交易时点')

        buy_df = trading_df[trading_df['摘要'].str.contains('申购款')]
        sell_df = trading_df[(trading_df['摘要'].str.contains('赎回款')) & (trading_df['收付方向'] == '付款')]
        trading_day_list = get_trading_day_list(self.start_date, self.end_date)
        init_df = pd.DataFrame({"trade_date": trading_day_list, "t_asset": init_cash})
        init_df = init_df.merge(sell_df.rename(columns={"交易时点": "trade_date", "发生金额": "赎回金额"})[
                                    ['trade_date', '赎回金额']], on='trade_date', how='left')
        init_df = init_df.merge(buy_df.rename(columns={"交易时点": "trade_date", "发生金额": "申购金额"})[
                                    ['trade_date', '申购金额']], on='trade_date', how='left')
        init_df['申购金额'] = init_df['申购金额'].fillna(0.).cumsum()
        init_df['赎回金额'] = init_df['赎回金额'].fillna(0.).cumsum()
        init_df['t_asset_adj'] = init_df['t_asset'] + init_df['申购金额'] - init_df['赎回金额']

        select_df = trading_df[~trading_df['摘要'].str.contains('申购款')]
        select_df = select_df[(~select_df['摘要'].str.contains('赎回款')) | (select_df['收付方向'] != '付款')]
        select_df = select_df[~select_df['摘要'].str.contains('支付')]
        select_df = select_df[~select_df['摘要'].str.contains('业绩报酬')]
        # 虚拟净值
        nav_list = []
        for s_name in ['500指数增强', '1000指数增强', '量化多头']:
            df = pd.read_excel(os.path.join(
                self.data_path, '虚拟净值文件\\量化产品日净值收益统计_20230310.xlsx'), sheet_name=s_name, index_col=0)
            cols = [x for x in df.columns if 'Unnamed' not in x]
            df = df.dropna(how='all')[cols][1:]
            nav_list.append(df)
        nav_df = pd.concat(nav_list, axis=1)
        nav_df['trade_date'] = nav_df.index
        nav_df['trade_date'] = nav_df['trade_date'].apply(lambda x: x.replace('-', ''))
        nav_df = nav_df.set_index('trade_date').sort_index().loc[self.start_date:]
        nav_df.rename(columns={"乾象股票进取6号": "乾象股票进取6号私募证券投资基金",
                               "诚奇睿盈500指数增强A": "诚奇睿盈500指数增强私募证券投资基金",
                               "宽德中证1000指数增强8号": "宽德中证1000指数增强8号私募证券投资基金",
                               "星阔山海6号股票优选": "星阔山海6号股票优选私募证券投资基金",
                               "珠海宽德九臻": "珠海宽德九臻私募投资基金",
                               "黑翼中证500指数增强8号B类": "黑翼中证500指数增强8号私募证券投资基金B类",
                               "明汯量化中小盘增强1号": "明汯量化中小盘增强1号私募证券投资基金",
                               "伯兄熙宁中证500指数增强": "伯兄熙宁中证500指数增强私募证券投资基金",
                               "伯兄至道中证500指数增强": "伯兄至道中证500指数增强私募证券投资基金",
                               "顽岩中证500指数增强5号": "顽岩中证500指数增强3号私募证券投资基金",
                               "稳博1000指数增强1号A": "稳博1000指数增强1号私募证券投资基金",
                               "概率500指增2号": "概率500指增2号私募证券投资基金",
                               "白鹭精选量化鲲鹏十号B类": "白鹭精选量化鲲鹏十号私募证券投资基金B",
                               "概率1000指增1号": "概率1000指增1号私募证券投资基金"
                               }, inplace=True)

        holding_df = holding_df.T.reindex(trading_day_list).T
        add_fund_list = ['衍复指增三号', '千衍六和3号B类']
        all_fund_list = list(set(holding_df.index.tolist()).union(set(add_fund_list)))
        holding_df = holding_df.reindex(all_fund_list)
        nav_df = nav_df.loc[self.start_date: self.end_date, all_fund_list]

        mkv_list = []
        # 概率500：1.18赎回
        name = '概率500指增2号私募证券投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp.loc["20230119":] = np.NaN
        tmp = tmp.to_frame(name)
        mkv_list.append(tmp[[name]])
        # 黑翼500增强8号
        name = '黑翼中证500指数增强8号私募证券投资基金B类'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp.loc["20230222":] = np.NaN
        tmp = tmp.to_frame(name)
        mkv_list.append(tmp[[name]])
        # 稳博1000指数增强1号
        name = '稳博1000指数增强1号私募证券投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name)
        tmp.loc["20230302":, 'change'] = 1400000
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230303":, "change"] = (1 + tmp.loc["20230303":, 'return']).cumprod() * tmp['change']
        tmp['change'] = tmp['change'].fillna(0.)
        tmp[name] += tmp['change']
        mkv_list.append(tmp[[name]])
        # 伯兄熙宁
        name = '伯兄熙宁中证500指数增强私募证券投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name)
        tmp.loc["20230221":, 'change'] = -5156301.4
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230222":, "change"] = (1 + tmp.loc["20230222":, 'return']).cumprod() * tmp['change']
        tmp['change'] = tmp['change'].fillna(0.)
        tmp[name] += tmp['change']
        mkv_list.append(tmp[[name]])
        # 白鹭
        name = '白鹭精选量化鲲鹏十号私募证券投资基金B'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name)
        tmp.loc["20230104":, 'change1'] = -4351050
        tmp.loc["20230118":, 'change2'] = -4524300
        tmp.loc["20230201":, 'change3'] = -5468865.14
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230105":, "change1"] = (1 + tmp.loc["20230105":, 'return']).cumprod() * tmp['change1']
        tmp.loc["20230119":, "change2"] = (1 + tmp.loc["20230119":, 'return']).cumprod() * tmp['change2']
        tmp.loc["20230202":, "change3"] = (1 + tmp.loc["20230202":, 'return']).cumprod() * tmp['change3']
        tmp['change1'] = tmp['change1'].fillna(0.)
        tmp['change2'] = tmp['change2'].fillna(0.)
        tmp['change3'] = tmp['change3'].fillna(0.)
        tmp[name] = tmp[name] + tmp['change1'] + tmp['change2'] + tmp['change3']
        tmp.loc["20230201":] = np.NaN
        mkv_list.append(tmp[[name]])
        # 千衍六和3号B类
        name = '千衍六和3号B类'
        tmp = nav_df[name]
        tmp = tmp.to_frame(name)
        tmp.loc["20230302":] = 7000000
        mkv_list.append(tmp[[name]])
        # 衍复
        name = '衍复指增三号'
        tmp = nav_df[name]
        tmp = tmp.to_frame(name)
        tmp.loc["20230119":, 'change1'] = 8900000
        tmp.loc["20230202":, 'change2'] = 6000000
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230120":, "change1"] = (1 + tmp.loc["20230120":, 'return']).cumprod() * tmp['change1']
        tmp.loc["20230203":, "change2"] = (1 + tmp.loc["20230203":, 'return']).cumprod() * tmp['change2']
        tmp['change1'] = tmp['change1'].fillna(0.)
        tmp['change2'] = tmp['change2'].fillna(0.)
        tmp[name] = tmp['change1'] + tmp['change2']
        tmp.loc[:"20230118", name] = np.NaN
        mkv_list.append(tmp[[name]])
        # 诚奇
        name = '诚奇睿盈500指数增强私募证券投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name).fillna(method='ffill')
        tmp.loc["20230202":, 'change'] = -4889734
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230203":, "change"] = (1 + tmp.loc["20230203":, 'return']).cumprod() * tmp['change']
        tmp['change'] = tmp['change'].fillna(0.)
        tmp[name] += tmp['change']
        tmp.loc["20230202":, name] = np.NaN
        mkv_list.append(tmp[[name]])
        # 宽德
        name = '珠海宽德九臻私募投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name)
        tmp.loc["20230301":, 'change'] = -7139000
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230302":, "change"] = (1 + tmp.loc["20230302":, 'return']).cumprod() * tmp['change']
        tmp['change'] = tmp['change'].fillna(0.)
        tmp[name] += tmp['change']
        mkv_list.append(tmp[[name]])
        # 剩余
        include_list = ['明汯量化中小盘增强1号私募证券投资基金', '顽岩中证500指数增强3号私募证券投资基金',
                        '伯兄至道中证500指数增强私募证券投资基金', '星阔山海6号股票优选私募证券投资基金',
                        '乾象股票进取6号私募证券投资基金', '宽德中证1000指数增强8号私募证券投资基金',
                        '概率1000指增1号私募证券投资基金']
        sub_nav = nav_df[include_list].fillna(method='ffill')
        sub_nav /= sub_nav.iloc[0]
        sub_mkv = sub_nav.multiply(holding_df.reindex(include_list)[self.start_date])
        mkv_list.append(sub_mkv)

        mkv_df = pd.concat(mkv_list, axis=1)
        compare_df = mkv_df.sum(axis=1).to_frame('asset').merge(
            init_df.set_index('trade_date')[['t_asset_adj']], left_index=True, right_index=True)
        compare_df['nav'] = compare_df['asset'] / compare_df['t_asset_adj']


def nav_series_update(start_date, end_date):
    """
    中小盘二号模拟历史拼接净值更新
    """
    nv_series = pd.read_excel('D:\\研究基地\\Z-数据整理\\中小盘模拟+实盘.xlsx')
    nv_series = nv_series[nv_series.columns[:3]]
    nv_series['TRADEDATE'] = nv_series['TRADEDATE'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    nv_series['中小盘二号'] = np.where(
        nv_series['中小盘二号（实盘）'].isnull(), nv_series['中小盘二号（模拟）'], nv_series['中小盘二号（实盘）'])
    # 新增实盘净值
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    new_formula = get_fund_nav_from_sql(start_date, end_date, {"中小盘二号": "SSL554"}).reindex(
        trading_day_list)

    assert (nv_series['TRADEDATE'].tolist()[-1] == new_formula.index.tolist()[0])

    return_df = pd.concat([nv_series.set_index('TRADEDATE')[['中小盘二号']].pct_change(),
                           new_formula.pct_change().dropna()]).fillna(0.).sort_index()
    trading_day_list = get_trading_day_list(return_df.index[0], return_df.index[-1], frequency="week")
    benchmark_series = get_index_return_from_sql(return_df.index[0], return_df.index[-1], '000905').reindex(
        trading_day_list).pct_change().fillna(0.)
    assert (len(return_df) == len(benchmark_series))
    return_df = return_df.merge(benchmark_series.to_frame('中证500'), left_index=True, right_index=True)
    return_df.eval("超额收益 = 中小盘二号 - 中证500", inplace=True)
    nav_df = (1 + return_df).cumprod()

    portfolio_index_df = pd.DataFrame(
        index=nav_df.columns, columns=['年化收益', '年化波动', '最大回撤', 'Sharpe', '胜率', '平均损益比'])
    portfolio_index_df.loc[:, '年化收益'] = nav_df.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
    portfolio_index_df.loc[:, '年化波动'] = \
        nav_df.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
    portfolio_index_df.loc[:, '最大回撤'] = nav_df.apply(cal_max_drawdown, axis=0)
    portfolio_index_df.loc[:, 'Sharpe'] = \
        nav_df.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
    portfolio_index_df.loc[:, '胜率'] = \
        nav_df.pct_change().dropna(how='all').apply(lambda x: x.gt(0).sum() / len(x), axis=0)
    portfolio_index_df.loc[:, '平均损益比'] = \
        nav_df.pct_change().dropna(how='all').apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
    portfolio_index_df.index.name = '产品名称'
    portfolio_index_df.reset_index(inplace=True)
    # 格式处理
    portfolio_index_df['年化收益'] = portfolio_index_df['年化收益'].apply(lambda x: format(x, '.2%'))
    portfolio_index_df['年化波动'] = portfolio_index_df['年化波动'].apply(lambda x: format(x, '.2%'))
    portfolio_index_df['最大回撤'] = portfolio_index_df['最大回撤'].apply(lambda x: format(x, '.2%'))
    portfolio_index_df['Sharpe'] = portfolio_index_df['Sharpe'].round(2)
    portfolio_index_df['胜率'] = portfolio_index_df['胜率'].apply(lambda x: format(x, '.1%'))
    portfolio_index_df['平均损益比'] = portfolio_index_df['平均损益比'].round(2)

    return portfolio_index_df


def calc_fof_volatility(start_date, end_date, type="1002"):
    """
    :param start_date:
    :param end_date:
    :param type: 1002代表量化多头，1001代表主观多头
    :return:
    """
    year_list = [str(x) for x in range(2020, 2024)]
    month_list = [str(x).zfill(2) for x in range(1, 13)]
    data_list = []
    for year in year_list:
        if year == "2023":
            month_list = month_list[:11]
        for month in month_list:
            t_date = year + month
            sql_script = "SELECT * FROM st_hedge.t_st_sm_zsyb WHERE jjfl = '{}' and tjyf = {}".format(type, t_date)
            t_data = pd.DataFrame(hbs.db_data_query('highuser', sql_script, page_size=5000)['data'])
            t_data = t_data.rename(columns={"tjyf": "month", "jjdm": "fund_id"})[['month', "fund_id"]]
            data_list.append(t_data)
    df = pd.concat(data_list)
    count_df = df['fund_id'].value_counts()
    idx = count_df[count_df >= 5].index.tolist()
    # 基金信息
    sql_script = \
        ("SELECT clrq, jjdm, jjmc, jjjc FROM st_hedge.t_st_jjxx where cpfl = '4' and ejfl = '{}' and "
         "jjzt = '0'").format(type)
    fund_info = pd.DataFrame(hbs.db_data_query('highuser', sql_script, page_size=50000)['data'])
    fund_info.rename(columns={"jjdm": "fund_id"}, inplace=True)
    idx = list(set(idx).intersection(set(fund_info['fund_id'])))
    fund_info = fund_info[fund_info['fund_id'].isin(idx)]
    fund_dict = fund_info.set_index('jjmc')['fund_id'].to_dict()

    trading_day_list = get_trading_day_list(start_date, end_date, "week")
    fund_nav = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(
        trading_day_list)
    fund_nav = fund_nav.dropna(axis=1)

    # sql_script = ("SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE FROM st_market.t_st_zs_hq WHERE "
    #               "ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}").format("000905", start_date, end_date)
    # res = hbs.db_data_query('alluser', sql_script, page_size=5000)
    # data = pd.DataFrame(res['data'])
    # data['TRADEDATE'] = data['TRADEDATE'].map(str)
    # benchmark_series = data.set_index('TRADEDATE')['TCLOSE']
    # benchmark_series = benchmark_series.reindex(trading_day_list).pct_change().dropna()

    return_df = fund_nav.pct_change(fill_method=None).dropna(how='all').sort_index()
    # return_df = fund_nav.pct_change(fill_method=None).dropna(how='all').sub(benchmark_series, axis=0).sort_index()
    return_df.loc[start_date] = 0.
    return_df = return_df.sort_index()
    fund_nav = (1 + return_df).cumprod()

    fund_index_df = pd.DataFrame(
        index=fund_nav.columns, columns=['年化波动', '年化收益'])
    fund_index_df.loc[:, '年化收益'] = fund_nav.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
    fund_index_df.loc[:, '年化波动'] = \
        fund_nav.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
    # 剔除异常值
    median = fund_index_df.median()
    new_median = abs(fund_index_df - median).median()
    up = median + 3 * new_median
    down = median - 5 * new_median
    fund_index_df = fund_index_df[(fund_index_df['年化收益'] <= up.loc["年化收益"]) & (
            fund_index_df['年化收益'] >= down.loc["年化收益"])]
    fund_index_df = fund_index_df[(fund_index_df['年化波动'] <= up.loc["年化波动"]) & (
            fund_index_df['年化波动'] >= down.loc["年化波动"])]
    nav_sub = fund_nav[fund_index_df.index.tolist()]
    nav_sub /= nav_sub.iloc[0]
    # 剔除多策略
    cols = nav_sub.columns.tolist()
    cols_new = [x for x in cols if '多策略' not in x]
    nav_sub = nav_sub[cols_new]
    fund_index_df = fund_index_df.reindex(cols_new)
    # 模拟
    pick_num = 10
    epoch = 50
    sim_port = pd.DataFrame(index=nav_sub.index, columns=["port_{}".format(x) for x in range(epoch)])
    for i in range(epoch):
        num_list = random.sample(range(0, nav_sub.shape[1]), pick_num)
        sub_df = nav_sub.T.iloc[num_list]
        sim_port["port_{}".format(i)] = sub_df.mean()
    # 添加FOF对比
    fof_nav = get_fund_nav_from_sql(start_date, end_date, {"中小盘精选": "SGG703", "二号": "SSL554"}).reindex(
        trading_day_list)
    fof_ret = fof_nav.pct_change(limit=1)
    fof_ret['拟合'] = np.where(fof_ret['二号'].isnull(), fof_ret['中小盘精选'], fof_ret['二号'])
    fof_ret.loc[start_date] = 0.
    fof_nav = (1 + fof_ret).cumprod()
    sim_port = sim_port.merge(fof_nav[['拟合']], left_index=True, right_index=True)

    port_index_df = pd.DataFrame(
        index=sim_port.columns, columns=['年化波动', '年化收益'])
    port_index_df.loc[:, '年化收益'] = sim_port.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
    port_index_df.loc[:, '年化波动'] = \
        sim_port.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)

    return fund_index_df, port_index_df


def get_strategy_index_return(month):
    sql_script = "SELECT * FROM st_hedge.t_st_sm_zhmzsyhb WHERE tjyf = {}".format(month)
    t_data = pd.DataFrame(hbs.db_data_query('highuser', sql_script, page_size=5000)['data'])
    t_data = t_data[t_data['zsdm'].isin(["HB0011", "HB0018"])]

    return t_data[['tjyf', "zsdm", "hb1y"]]


def fof_rate_simulation(start_date, end_date, threshold, accrue_rate, frequency):
    """
    :param start_date: 起始日期
    :param end_date: 结束日期
    :param threshold: 年化计提的阈值
    :param accrue_rate: 计提的比例
    :param frequency: 计提的频率，semi or year
    :return:
    """
    # 以量化中小盘一号为例
    nav_df = get_fund_nav_from_sql(start_date, end_date, {"量化中小盘": "SGG703"}).sort_index()
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    nav_df = nav_df.reindex(trading_day_list).dropna()
    nav_df /= nav_df.iloc[0]
    # 前端费率还原
    nav_df['before_fee'] = nav_df['量化中小盘'] / (1 - 0.008 / 52)
    nav_df.loc[start_date, 'before_fee'] = 1.
    nav_df['actual_ret'] = nav_df['before_fee'] / (nav_df['量化中小盘'].shift(1).fillna(1.)) - 1
    nav_df['费前净值'] = (1 + nav_df['actual_ret']).cumprod()
    nav_df['累计管理费'] = (nav_df['before_fee'] - nav_df['量化中小盘']).cumsum()
    # 计提时间点
    week_list = get_trading_day_list(start_date, end_date, frequency="week")
    week_df = pd.Series(index=week_list, data=week_list).to_frame('trade_date')
    week_df['trade_dt'] = week_df['trade_date'].apply(lambda x: datetime.datetime.strptime(x, "%Y%m%d"))
    week_df['month'] = week_df['trade_dt'].apply(lambda x: x.month)
    month_end = week_df[week_df['month'].shift(-1) != week_df['month']]['trade_date'].tolist()
    # 老的计提方式所提业绩报酬
    # reb_dates = [x for x in month_end if x[4:6] == '12']
    # reb_dates.append(start_date)
    # reb_dates = sorted(reb_dates)
    # pay_series_old = pd.Series(index=reb_dates[1:], data=np.NaN)
    # for i in range(1, len(reb_dates)):
    #     p_date, t_date = reb_dates[i - 1], reb_dates[i]
    #     period_nav = nav_df.loc[p_date: t_date, '量化中小盘']
    #     current_nav = period_nav.loc[t_date]
    #     cum_return = period_nav.iloc[-1] / period_nav.iloc[0] - 1
    #     dt_0 = datetime.datetime.strptime(p_date, "%Y%m%d")
    #     dt_1 = datetime.datetime.strptime(t_date, "%Y%m%d")
    #     period_days = (dt_1 - dt_0).days
    #     annual_return = cum_return * (365 / period_days)
    #     if annual_return > 0.08:
    #         performance_pay = (annual_return - 0.08) * (period_days / 365) * 0.1 * current_nav
    #     else:
    #         performance_pay = 0.
    #
    #     pay_series_old.loc[t_date] = performance_pay
    #
    # nav_df = nav_df.merge(pay_series_old.to_frame('业绩报酬'), left_index=True, right_index=True, how='left')
    # nav_df['业绩报酬'] = nav_df['业绩报酬'].fillna(0.)
    # nav_df['multiplier'] = (nav_df['量化中小盘'] - nav_df['业绩报酬']) / nav_df['量化中小盘']
    # nav_df['客户实际净值'] = nav_df['量化中小盘'] * (nav_df['multiplier'].cumprod())
    # nav_df['累计业绩报酬'] = nav_df['业绩报酬'].cumsum()
    # nav_df.eval("总扣费 = 累计业绩报酬 + 累计管理费", inplace=True)
    # nav_df.rename(columns={"量化中小盘": "管理费后净值"}, inplace=True)
    # cols = ['费前净值', '管理费后净值', '客户实际净值', '累计管理费', '累计业绩报酬', '总扣费']
    # nav_df_former = nav_df[cols]
    # 新计提方式
    if frequency == "semi":
        reb_dates = [x for x in month_end if x[4:6] in ['06', '12']]
    else:
        reb_dates = [x for x in month_end if x[4:6] == '12']
    reb_dates.append(start_date)
    reb_dates = sorted(reb_dates)
    pay_series_new = pd.Series(index=reb_dates[1:], data=np.NaN)
    for i in range(1, len(reb_dates)):
        p_date, t_date = reb_dates[i - 1], reb_dates[i]
        period_nav = nav_df.loc[p_date: t_date, '费前净值']
        current_nav = period_nav.loc[t_date]
        cum_return = period_nav.iloc[-1] / period_nav.iloc[0] - 1
        dt_0 = datetime.datetime.strptime(p_date, "%Y%m%d")
        dt_1 = datetime.datetime.strptime(t_date, "%Y%m%d")
        period_days = (dt_1 - dt_0).days
        annual_return = cum_return * (365 / period_days)
        if annual_return > threshold:
            performance_pay = (annual_return - threshold) * (period_days / 365) * accrue_rate * current_nav
        else:
            performance_pay = 0.

        pay_series_new.loc[t_date] = performance_pay

    nav_df = nav_df[['费前净值']].merge(pay_series_new.to_frame('业绩报酬'), left_index=True, right_index=True, how='left')
    nav_df['业绩报酬'] = nav_df['业绩报酬'].fillna(0.)
    nav_df['multiplier'] = (nav_df['费前净值'] - nav_df['业绩报酬']) / nav_df['费前净值']
    nav_df['客户实际净值'] = nav_df['费前净值'] * (nav_df['multiplier'].cumprod())
    nav_df['累计业绩报酬'] = nav_df['业绩报酬'].cumsum()

    return nav_df, nav_df.loc[end_date, '客户实际净值'], nav_df.loc[end_date, '累计业绩报酬']


def fee_loop(freq):
    # threshold_list = np.linspace(0.06, 0.12, num=7)
    threshold_list = [0.]
    ratio_list = np.array([0.08, 0.10, 0.12, 0.15])
    results = []
    for threshold in tqdm(threshold_list):
        for ratio in ratio_list:
            _, after_fee_nav, bonus = fof_rate_simulation(
                start_date="20190531", end_date="20230721", threshold=threshold, accrue_rate=ratio, frequency=freq)
            pay_df = pd.Series(index=['客户实际净值', '累计业绩报酬'], data=[after_fee_nav, bonus]).to_frame('a').T
            pay_df['threshold'] = threshold
            pay_df['accrue_rate'] = ratio
            results.append(pay_df)

    results = pd.concat(results)
    results.reset_index(drop=True, inplace=True)

    return results


def get_daily_nav_from_mysql(start_date, end_date, token):
    period_dates = get_trading_day_list(start_date, end_date, frequency="week")
    data = hbs.commonQuery("FOF_ZJJLIST", startDate=start_date, endDate=end_date,
                           sorts=[{"field": "jzrq", "sort": "desc"}], access_token=token,
                           fields=['jjdm', 'jjmc', 'khdm', 'khmc', 'jzrq', 'jjjz', 'ljjz', 'xnjz'])
    data = data.dropna(subset=['jjmc'])
    fof_list = ['新方程对冲精选H1号基金', '新方程对冲精选N1号私募基金']
    data = data[data['khmc'].isin(fof_list)]
    "===================================================H1============================================================="
    h1_data = data[data['khmc'] == '新方程对冲精选H1号基金']
    data_na = h1_data[h1_data['jjdm'].isna()]
    data_na = data_na.pivot_table(index='jzrq', columns='jjmc', values='ljjz').sort_index()
    data_not_na = h1_data[~h1_data['jjdm'].isna()].sort_values(by=['jjdm', 'jjmc'])
    map_dict = data_not_na.drop_duplicates(subset=['jjdm', 'jjmc'], keep="first").set_index('jjdm')['jjmc'].to_dict()
    data_not_na = data_not_na[~data_not_na['ljjz'].isna()]
    data_not_na['ljjz'] = data_not_na['ljjz'].astype(float)
    trans_dict = {"TH545A": "P50163"}
    data_not_na['jjdm'] = data_not_na['jjdm'].replace(trans_dict)
    data_not_na = data_not_na.pivot_table(index='jzrq', columns='jjdm', values='ljjz').sort_index()
    data_not_na.columns = [map_dict[x] for x in data_not_na.columns]
    nav_data_h1 = pd.concat([data_na, data_not_na], axis=1).sort_index()
    nav_data_h1 = nav_data_h1.reindex(period_dates)
    h1_dict = {
        "市场中性": ['卓识利民二号私募证券投资基金A', '稳博对冲18号私募证券投资基金A',
                   '衍复中性三号私募证券投资基金', '乾象股票对冲3号私募证券投资基金B类'],
        "CTA": ['半夏宏观对冲好买专享3号私募证券投资基金', '明汯CTA白羊二号私募投资基金B', '黑翼CTA-S3私募证券投资基金',
                '均成CTA12号私募证券投资基金'],
        "股票多头": ['托特春晓中证1000指数增强2号私募证券投资基金', '衍复1000指增一号私募证券投资基金',
                   '凡二量化选股3号1期私募证券投资基金A类份额', '半鞅量化精选私募证券投资基金B类',
                   '仁桥鲲淼3期私募证券投资基金A', '勤辰森裕2号私募证券投资基金C类', '正松云睿全球私募证券投资基金A']
    }
    excel_writer = pd.ExcelWriter(
        'D:\\研究基地\\Y-H1&N1\\My底表\\A-H1底层净值.xlsx', engine='xlsxwriter')
    nav_data_h1['trade_date'] = nav_data_h1.index
    nav_data_h1['trade_date'] = nav_data_h1['trade_date'].apply(
        lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    nav_data_h1.set_index('trade_date', inplace=True)
    nav_data_h1.columns = [x.split('私募')[0] for x in nav_data_h1.columns]
    nav_data_h1.to_excel(excel_writer, sheet_name='汇总')
    nav_data_h1[[x.split('私募')[0] for x in h1_dict['市场中性']]].to_excel(excel_writer, sheet_name='市场中性')
    nav_data_h1[[x.split('私募')[0] for x in h1_dict['CTA']]].to_excel(excel_writer, sheet_name='CTA')
    nav_data_h1[[x.split('私募')[0] for x in h1_dict['股票多头']]].to_excel(excel_writer, sheet_name='股票多头')
    excel_writer.close()
    "===================================================N1============================================================="
    n1_data = data[data['khmc'] == '新方程对冲精选N1号私募基金']
    data_na = n1_data[n1_data['jjdm'].isna()]
    data_na = data_na.pivot_table(index='jzrq', columns='jjmc', values='ljjz').sort_index()
    data_not_na = n1_data[~n1_data['jjdm'].isna()].sort_values(by=['jjdm', 'jjmc'])
    map_dict = data_not_na.drop_duplicates(subset=['jjdm', 'jjmc'], keep="first").set_index('jjdm')['jjmc'].to_dict()
    data_not_na = data_not_na[~data_not_na['ljjz'].isna()]
    data_not_na['ljjz'] = data_not_na['ljjz'].astype(float)
    data_not_na = data_not_na.pivot_table(index='jzrq', columns='jjdm', values='ljjz').sort_index()
    data_not_na.columns = [map_dict[x] for x in data_not_na.columns]
    nav_data_n1 = pd.concat([data_na, data_not_na], axis=1).sort_index()
    nav_data_n1 = nav_data_n1.reindex(period_dates)
    n1_dict = {
        "市场中性": ['卓识利民二号私募证券投资基金A', '衍复中性三号私募证券投资基金',
                   '稳博对冲18号私募证券投资基金A', '托特市场中性2号私募证券投资基金', '磐松多空对冲1号私募证券投资基金'],
        "CTA": ['涵德盈冲量化CTA2号私募投资基金', '明汯CTA组合私募证券投资基金', '黑翼尊享CTA七号私募证券投资基金',
                '上国象专享3号私募证券投资基金'],
        "股票多头": ['衍复1000指增一号私募证券投资基金', '乾象股票进取6号私募证券投资基金',
                   '超量子好买专选中证500增强私募证券投资基金A', '慎知2号睿享D期私募证券投资基金',
                   '勤辰森裕2号私募证券投资基金C类', '文多专享私募证券投资基金A类']
    }
    excel_writer = pd.ExcelWriter(
        'D:\\研究基地\\Y-H1&N1\\My底表\\A-N1底层净值.xlsx', engine='xlsxwriter')
    nav_data_n1['trade_date'] = nav_data_n1.index
    nav_data_n1['trade_date'] = nav_data_n1['trade_date'].apply(
        lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    nav_data_n1.set_index('trade_date', inplace=True)
    nav_data_n1.columns = [x.split('私募')[0] for x in nav_data_n1.columns]
    nav_data_n1.to_excel(excel_writer, sheet_name='汇总')
    nav_data_n1[[x.split('私募')[0] for x in n1_dict['市场中性']]].to_excel(excel_writer, sheet_name='市场中性')
    nav_data_n1[[x.split('私募')[0] for x in n1_dict['CTA']]].to_excel(excel_writer, sheet_name='CTA')
    nav_data_n1[[x.split('私募')[0] for x in n1_dict['股票多头']]].to_excel(excel_writer, sheet_name='股票多头')
    excel_writer.close()


def calc_benchmark_h1_n1(start_date, end_date):
    """
    H1和N1的基准拟合代码
    """
    # 股票指数
    sql_script = "SELECT * FROM st_hedge.t_st_sm_zhmzs WHERE zsdm in ('HB0011', 'HB0018') and " \
                 "jyrq >= {} and jyrq <= {}".format(start_date, end_date)
    res = hbs.db_data_query('highuser', sql_script)
    data = pd.DataFrame(res['data'])
    hb_index = data.pivot_table(index='jyrq', columns='zsdm', values='spjg').sort_index()
    hb_index.rename(columns={"HB0011": "好买股票指数", "HB0018": "好买管理期货指数"}, inplace=True)
    # 5亿CTA指数
    cta_index = pd.read_excel("D:\\研究基地\\Y-H1&N1\\5亿CTA指数\\5亿CTA指数{}.xlsx".format(end_date), sheet_name=0)
    cta_index['t_date'] = cta_index['t_date'].apply(lambda x: x.strftime("%Y%m%d"))
    cta_index = cta_index.set_index('t_date')[['5亿CTA指数']]
    hb_index = hb_index.merge(cta_index, left_index=True, right_index=True, how='left')
    # 外部指数
    s_date = datetime.datetime.strptime(start_date, "%Y%m%d").strftime("%Y-%m-%d")
    e_date = datetime.datetime.strptime(end_date, "%Y%m%d").strftime("%Y-%m-%d")
    res = w.wsd("H11001.CSI,892400.MI", "close", s_date, e_date, "")
    w_data = pd.DataFrame(index=res.Codes, columns=res.Times, data=res.Data).T
    w_data['trade_date'] = w_data.index
    w_data['trade_date'] = w_data['trade_date'].apply(lambda x: x.strftime("%Y%m%d"))
    w_data.set_index("trade_date", inplace=True)
    w_data.rename(columns={"H11001.CSI": "中证全债指数", "892400.MI": "MSCI全球指数"}, inplace=True)

    hb_index = hb_index.merge(w_data, left_index=True, right_index=True)
    date_list = get_trading_day_list(start_date, end_date, "week")
    hb_index = hb_index.reindex(date_list)
    hb_return = hb_index.pct_change(limit=1)
    hb_return.loc[hb_return['5亿CTA指数'].isnull(), '5亿CTA指数'] = hb_return['好买管理期货指数']
    hb_return = hb_return.fillna(0.)
    # 基准构成
    n1_benchmark = {
        "好买股票指数": 1/3,
        "5亿CTA指数": 1/3,
        "中证全债指数": 1/3
    }
    # h1_benchmark = {
    #     "好买股票指数": 0.42,
    #     "MSCI全球指数": 0.18,
    #     "5亿CTA指数": 0.20,
    #     "中证全债指数": 0.20
    # }
    h1_benchmark = {
        "好买股票指数": 0.5,
        "5亿CTA指数": 0.25,
        "中证全债指数": 0.25
    }
    weight_n1 = pd.DataFrame.from_dict(n1_benchmark, orient="index").rename(columns={0: "N1_BenchMark"})
    weight_h1 = pd.DataFrame.from_dict(h1_benchmark, orient="index").rename(columns={0: "H1_BenchMark"})
    weight = weight_n1.merge(
        weight_h1, left_index=True, right_index=True, how='outer').reindex(hb_index.columns).fillna(0.)

    benchmark_return = hb_return.multiply(weight['N1_BenchMark']).sum(axis=1).to_frame('N1_BenchMark').merge(
        hb_return.multiply(weight['H1_BenchMark']).sum(axis=1).to_frame('H1_BenchMark'),
        left_index=True, right_index=True)
    benchmark_return.loc[:"20230224", "H1_BenchMark"] = benchmark_return.loc[:"20230224", "N1_BenchMark"]

    benchmark_nav = (1 + benchmark_return).cumprod()
    nav_df = get_fund_nav_from_sql(
        start_date, end_date, {"N1": "SCS026", "H1": "S21582", "AAA": "SSY770"})
    nav_df = nav_df.merge(benchmark_nav, left_index=True, right_index=True)

    period_return = nav_df.loc[end_date] / nav_df.loc[start_date] - 1
    period_return = period_return.apply(lambda x: format(x, ".2%"))

    table = PrettyTable(period_return.index.tolist())
    table.add_row(period_return.values)

    print(table)


def overseas_etf_compare(start_date, end_date):
    # 基金
    fund_id_list = ["000055.OF", "000834.OF", "040046.OF", "006075.OF", "161125.OF"]
    res = w.wsd(','.join(fund_id_list), "NAV_adj", start_date, end_date, "")
    fund_nav = pd.DataFrame(index=res.Codes, columns=res.Times, data=res.Data).T
    fund_nav['trade_date'] = fund_nav.index
    fund_nav['trade_date'] = fund_nav['trade_date'].apply(lambda x: x.strftime("%Y%m%d"))
    fund_nav = fund_nav.set_index('trade_date').dropna().sort_index()
    return_df = fund_nav.pct_change().fillna(0.)
    # 指数
    res = w.wsd("NDX.GI,SPX.GI", "close", start_date, end_date, "")
    benchmark_df = pd.DataFrame(index=res.Codes, columns=res.Times, data=res.Data).T
    benchmark_df['trade_date'] = benchmark_df.index
    benchmark_df['trade_date'] = benchmark_df['trade_date'].apply(lambda x: x.strftime("%Y%m%d"))
    benchmark_df = benchmark_df.set_index('trade_date').dropna().sort_index()
    benchmark_return = benchmark_df.pct_change().fillna(0.)

    ndx_df = return_df[return_df.columns[:3]].sub(benchmark_return['NDX.GI'], axis=0)
    sp_df = return_df[return_df.columns[3:]].sub(benchmark_return['SPX.GI'], axis=0)

    return ndx_df, sp_df



if __name__ == '__main__':
    # FofGapAnalysis("20221230", "20230303", "D:\\新方程量化FOF").run()
    # nav_series_update("20230210", "20230407")
    # calc_fof_volatility("20191227", "20231124", type="1001")
    # fof_rate_simulation(start_date="20190531", end_date="20230721", threshold=0.08, accrue_rate=0.12, frequency="semi")
    # res = fee_loop("year")

    get_daily_nav_from_mysql(
        "20231115", "20240102", "9169171606b64cc2a21626cda87b8c68")

    # calc_benchmark_h1_n1("20230928", "20231027")

    # overseas_etf_compare("2020-12-31", "2023-09-20")