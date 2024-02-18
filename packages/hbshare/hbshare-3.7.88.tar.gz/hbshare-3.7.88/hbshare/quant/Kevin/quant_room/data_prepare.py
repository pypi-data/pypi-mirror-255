"""
数据准备模块, 新方程FOF历史业绩拟合
"""
import pandas as pd
import hbshare as hbs
import numpy as np
import os
from datetime import datetime
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import (get_fund_nav_from_sql,
                                                               get_trading_day_list, get_index_return_from_sql)
from Arbitrage_backtest import cal_annual_return, cal_annual_volatility, cal_sharpe_ratio, cal_max_drawdown
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from tqdm import tqdm
from WindPy import w
import matplotlib.pyplot as plt

plt.style.use('seaborn')

w.start()


def load_benchmark_components(date):
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                 "SecuCode in ('000300', '000905', '000852', '399303')"
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

    weight = []
    for benchmark_id in ['000300', '000905', '000852', '399303']:
        inner_code = inner_code_series.loc[benchmark_id]
        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
        weight_df['benchmark_id'] = benchmark_id
        weight.append(weight_df[['ticker', 'benchmark_id']])
    # 000852优先于399303
    weight = pd.concat(weight).sort_values(by=['ticker', 'benchmark_id']).drop_duplicates(
        subset=['ticker'], keep='first')

    return weight


def load_benchmark_components_new(date):
    """
    带有中证2000的成分股数据
    """
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                 "SecuCode in ('000300', '000905', '000852', '932000')"
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

    weight = []
    for benchmark_id in ['000300', '000905', '000852', '932000']:
        inner_code = inner_code_series.loc[benchmark_id]
        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
        weight_df['benchmark_id'] = benchmark_id
        weight.append(weight_df[['ticker', 'benchmark_id']])
    weight = pd.concat(weight).sort_values(by=['ticker', 'benchmark_id'])

    return weight



def data_preparation(start_date, end_date):
    # db
    benchmark_id_list = ['000300', '000905', '000852', '000001', 'CBA00201']
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    benchmark_list = []
    for benchmark_id in benchmark_id_list:
        benchmark_series = get_index_return_from_sql(start_date, end_date, benchmark_id).reindex(
            trading_day_list).to_frame(benchmark_id)
        benchmark_list.append(benchmark_series)
    benchmark_df = pd.concat(benchmark_list, axis=1)
    # 好买策略指数
    sql_script = "SELECT zsdm, spjg, jyrq FROM st_hedge.t_st_sm_zhmzs WHERE " \
                 "zsdm in ('HB1002','HB0018','HB0015','HB0017') and jyrq <= '20221230'"
    res = hbs.db_data_query('highuser', sql_script, page_size=5000)
    data = pd.DataFrame(res['data'])
    hb_index = pd.pivot_table(
        data, index='jyrq', columns='zsdm', values='spjg').reindex(trading_day_list).dropna(how='all').loc["20151231":]
    # strategy
    res = w.wsd(
        "NH0100.NHF,885001.WI,885306.WI,885309.WI,885308.WI,885312.WI", "close", start_date, end_date, "Period=W")
    d_list = [datetime.strftime(x, '%Y%m%d') for x in res.Times]
    data = pd.DataFrame(res.Data, index=res.Codes, columns=d_list).T.reindex(trading_day_list)
    benchmark_df = benchmark_df.merge(data[['NH0100.NHF']], left_index=True, right_index=True)
    strategy_index = data[data.columns[1:]].dropna()

    # 计算
    benchmark_df.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
    strategy_index.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)

    return hb_index


def get_data_from_Wind():
    trading_day_list = get_trading_day_list('20150101', '20221231', frequency="day")
    # 主力资金数据
    date_list = trading_day_list[::40] + [trading_day_list[-1]]
    data_list = []
    for i in tqdm(range(1, len(date_list))):
        start_date, end_date = date_list[i - 1], date_list[i]
        res = w.wset("marketmoneyflows", "startdate={};enddate={};frequency=day;sector=sse_szse;securitytype=A股;field=date,maininmoney,mainoutmoney,maininflowmoney".format(start_date, end_date))
        data = pd.DataFrame(
            {"trade_date": res.Data[0], "M_in": res.Data[1], "M_out": res.Data[2], "Delta": res.Data[3]})
        data_list.append(data)
    all_data = pd.concat(data_list, axis=0)
    all_data['trade_date'] = all_data['trade_date'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    all_data = all_data.drop_duplicates(subset=['trade_date']).set_index('trade_date').sort_index()
    all_data['sum'] = all_data['M_in'] + all_data['M_out']
    all_data = all_data.reindex(trading_day_list).dropna()
    # 成交额数据
    sql_script = "SELECT * FROM mac_stock_trading"
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    amt_data = data[['trade_date', 'amt_sh', 'amt_sz', 'amt_300', 'amt_500', 'amt_1000', 'amt_other']]
    amt_data['amt_all'] = amt_data['amt_sh'] + amt_data['amt_sz']
    amt_data = amt_data[(amt_data['trade_date'] > '20141231') & (amt_data['trade_date'] <= '20221231')]
    amt_data = amt_data.set_index('trade_date')[['amt_all']]

    df = all_data[['sum']].merge(amt_data, left_index=True, right_index=True)
    df['sum'] /= 1e+4

    # 按月度分类
    month_end = get_trading_day_list('20141220', '20221231', frequency="month")[::3]
    a = []
    b = []
    for i in range(1, len(month_end)):
        start, end = month_end[i - 1], month_end[i]
        period_data = df.loc[start: end][1:]
        ratio = period_data['sum'].sum() / period_data['amt_all'].sum()
        # ratio = period_data['sum'].sum()
        a.append(end)
        b.append(ratio)

    count_df = pd.DataFrame({"date": a, "ratio": b}).sort_values(by='date')
    count_df.set_index('date').plot.bar()


def ret_vol_beta(start_date, end_date):
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    # 超额数据
    alpha_series = pd.read_excel('D:\\alpha_data.xlsx', sheet_name=0)
    alpha_series['TRADEDATE'] = alpha_series['TRADEDATE'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    alpha_series = alpha_series.set_index('TRADEDATE')[['高频量价']].reindex(trading_day_list).pct_change().dropna()
    # benchmark
    benchmark_series = get_index_return_from_sql(start_date, end_date, '000905').reindex(
        trading_day_list).pct_change().dropna()
    # 成交额数据
    sql_script = "SELECT * FROM mac_stock_trading"
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    amt_data = data[['trade_date', 'amt_300', 'amt_500', 'amt_1000', 'amt_other']]
    amt_data = amt_data[(amt_data['trade_date'] >= '20201231') & (amt_data['trade_date'] <= '20230217')]
    amt_data = amt_data.set_index('trade_date').sort_index()
    amt_data['amt_all'] = amt_data.sum(axis=1)
    amt_data.loc[trading_day_list, "sign"] = 1.
    amt_data['sign'] = amt_data['sign'].shift(1).fillna(0.).cumsum()
    mean_amt = amt_data.groupby('sign')['amt_all'].mean().to_frame('mean_amt')
    mean_amt['trade_date'] = trading_day_list
    mean_amt = mean_amt.set_index('trade_date')[['mean_amt']]

    df = mean_amt.merge(benchmark_series, left_index=True, right_index=True).merge(
        alpha_series, left_index=True, right_index=True)
    df['mean_amt'] /= 10000.
    df.rename(columns={"TCLOSE": "benchmark", "高频量价": "alpha"}, inplace=True)

    # df = pd.read_excel('D:\\高频数据.xlsx', sheet_name=0, index_col=0)
    # df.rename(columns={"all_std_1": "benchmark", "高频量价": "alpha"}, inplace=True)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(df[df['alpha'] >= 0]['mean_amt'],
               df[df['alpha'] >= 0]['benchmark'],
               df[df['alpha'] >= 0]['alpha'], c='r')
    ax.scatter(df[df['alpha'] < 0]['mean_amt'],
               df[df['alpha'] < 0]['benchmark'],
               df[df['alpha'] < 0]['alpha'], c='g')

    df.loc[df['mean_amt'] <= df['mean_amt'].quantile(0.33), 'sign_amt'] = 'L'
    df.loc[(df['mean_amt'] > df['mean_amt'].quantile(0.33)) & (df['mean_amt'] <= df['mean_amt'].quantile(0.66)), 'sign_amt'] = 'M'
    df.loc[df['mean_amt'] > df['mean_amt'].quantile(0.66), 'sign_amt'] = 'H'

    df.loc[df['benchmark'] <= df['benchmark'].quantile(0.33), 'sign_benchmark'] = 'L'
    df.loc[(df['benchmark'] > df['benchmark'].quantile(0.33)) & (df['benchmark'] <= df['benchmark'].quantile(0.66)), 'sign_benchmark'] = 'M'
    df.loc[df['benchmark'] > df['benchmark'].quantile(0.66), 'sign_benchmark'] = 'H'

    group_ret = df.groupby(['sign_amt', 'sign_benchmark'])['alpha'].mean().reset_index()
    group_ret = pd.pivot_table(
        group_ret, index='sign_amt', columns='sign_benchmark', values='alpha').loc[["L", "M", "H"]][["L", "M", "H"]]

    return group_ret


def calc_period_group_ret(start_date, end_date):
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if start_date < x.split('_')[-1].split('.')[0] <= end_date]
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    stock_return = data[['trade_date', 'ticker', 'dailyReturnReinv', 'negMarketValue', 'PB']].dropna()
    stock_return['negMarketValue'] /= 1e+9
    stock_return['dailyReturnReinv'] /= 100.
    stock_return = stock_return.pivot_table(
        index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index()

    style_factor = pd.read_csv(
        "D:\\kevin\\risk_model_jy\\RiskModel\\data\\zzqz_sw\\style_factor\\{}.csv".format(start_date))
    style_factor['ticker'] = style_factor['ticker'].apply(lambda x: str(x).zfill(6))
    style_factor = style_factor.set_index('ticker').applymap(float)
    group_df = pd.qcut(style_factor['size'], q=10, labels=False)
    idx = list(set(stock_return.columns).intersection(group_df.index))

    stock_return = (1 + stock_return[idx]).prod() - 1
    group_df = group_df.reindex(idx).to_frame('group').merge(
        stock_return.to_frame('return'), left_index=True, right_index=True)
    group_ret = group_df.groupby('group')['return'].mean().sort_index()

    return group_ret


def market_median_versus_benchmark(start_date, end_date):
    # 市场中位数
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if start_date < x.split('_')[-1].split('.')[0] <= end_date]
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    data = data[data['dailyReturnReinv'].abs() < 20.]
    stock_return = pd.pivot_table(
        data, index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index().fillna(0.)
    stock_return /= 100.
    median_df = (1 + stock_return).cumprod().median(axis=1)
    # 指数收益
    sql_script = ("SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE FROM st_market.t_st_zs_hq WHERE "
                  "ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}").format('000905', start_date, end_date)
    res = hbs.db_data_query('alluser', sql_script, page_size=5000)
    data = pd.DataFrame(res['data'])
    data['TRADEDATE'] = data['TRADEDATE'].map(str)
    data.sort_values(by='TRADEDATE', inplace=True)
    data['index_return'] = data['TCLOSE'].pct_change().dropna()
    index_df = data.set_index('TRADEDATE')['TCLOSE']

    compare_df = median_df.to_frame('median').merge(index_df.to_frame('benchmark'), left_index=True, right_index=True)
    compare_df = compare_df.dropna()
    compare_df /= compare_df.iloc[0]
    compare_df.eval("relative = median - benchmark", inplace=True)

    return compare_df


def calc_index_strength_matrix(start_date, end_date):
    # strategy
    index_list = ["000016.SH", "000300.SH", "000905.SH", "000852.SH", "932000.CSI", "8841425.WI", "8841431.WI"]
    res = w.wsd(','.join(index_list), "close", start_date, end_date, "")
    d_list = [datetime.strftime(x, '%Y%m%d') for x in res.Times]
    data = pd.DataFrame(res.Data, index=res.Codes, columns=d_list).T
    data /= data.iloc[0]
    data.rename(columns={"000016.SH": "上证50", "000300.SH": "沪深300", "000905.SH": "中证500", "000852.SH": "中证1000",
                         "932000.CSI": "中证2000", "8841425.WI": "小市值指数", "8841431.WI": "微盘股指数"}, inplace=True)
    period_return = data.iloc[-1] - 1
    matrix_df = pd.DataFrame(index=data.columns, columns=data.columns)
    for row_name in data.columns:
        for col_name in data.columns:
            matrix_df.loc[row_name, col_name] = period_return.loc[row_name] - period_return.loc[col_name]

    return matrix_df


if __name__ == '__main__':
    # data_preparation('20130101', '20221230')
    # get_data_from_Wind()
    # ret_vol_beta("20221230", "20230811")
    # calc_period_group_ret("20230703", "20230728")

    market_median_versus_benchmark("20221230", "20231229")
    # calc_index_strength_matrix("20221230", "20231229")