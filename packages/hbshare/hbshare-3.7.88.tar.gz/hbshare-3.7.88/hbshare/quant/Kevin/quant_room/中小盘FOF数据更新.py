"""
中小盘数据更新程序
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hbshare as hbs
from hbshare.quant.Kevin.periodic_reports.tracker import get_track_config_from_db
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list, get_index_return_from_sql
from hbshare.quant.Kevin.quant_room.MyUtil.util_func import (
    cal_max_drawdown, cal_dd_recovery, cal_annual_return, cal_annual_volatility, cal_sharpe_ratio)


def period_nav_compare(start_date, end_date):
    """
    区间绝对收益对比
    """
    fund_dict = {
        "中小盘二号": "SSL554",
        "明汯价值成长1期3号": "SEE194",
        "衍复指增三号": "SJH866",
        "天演中证500指数增强": "P20830",
        "启林中证500指数增强1号": "SGY379",
        "诚奇中证500增强精选1期": "SLS817",
        "鸣石春天十三号": "SX2090",
        "九坤日享中证500指数增强1号": "ST9804",
        "九章幻方中证500量化多策略1号": "SR6089",
        "黑翼中证500指数增强1号": "SEM323",
        "灵均进取1号": "SW3470"
    }
    # fof 底层
    # fund_dict = {
    #     "宽德500": "SEJ470",
    #     "衍复小市值": "SZL824",
    #     "顽岩": "SSA143",
    #     "乾象": "P48470",
    #     "稳博1000": "SJZ127",
    #     "千衍": "SQL839",
    #     "信弘": "P50259",
    #     "半鞅": "SVB591",
    #     "铭量": "SLY644",
    #     "超量子": "SNT059",
    #     "凡二多头": "STH545",
    #     "托特1000": "SVK180",
    #     "仲阳500": "SGN254",
    #     "磐松500": "SXZ439"
    # }
    period_date = get_trading_day_list(start_date, end_date, frequency='week')
    nav_df = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(period_date)
    nav_df['trade_date'] = nav_df.index
    nav_df['trade_date'] = nav_df['trade_date'].apply(
        lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    nav_df.set_index('trade_date', inplace=True)

    return nav_df


def excess_correlation(start_date, end_date):
    """
    超额相关性
    """
    fund_dict = {
        "九坤": "ST9804",
        "明汯": "SEE194",
        "幻方": "SY0607",
        "诚奇": "SLS817",
        "天演": "P20830",
        "启林": "SGY379",
        "茂源": "SNM667",
        "因诺": "SGX346",
        "世纪前沿": "SGP682",
        "量锐": "P23195",
        "黑翼": "SEM323",
        "卓识": "SGA015",
        "星阔": "SNU706",
        "新方程": "SSL554"
    }
    period_date = get_trading_day_list(start_date, end_date, frequency='week')
    fund_nav = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(
        period_date)
    sql_script = ("SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE FROM st_market.t_st_zs_hq WHERE "
                  "ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}").format('000905', start_date, end_date)
    res = hbs.db_data_query('alluser', sql_script, page_size=5000)
    data = pd.DataFrame(res['data'])
    data['TRADEDATE'] = data['TRADEDATE'].map(str)
    benchmark_series = data.set_index('TRADEDATE')['TCLOSE'].reindex(
            period_date).pct_change().dropna()
    return_df = fund_nav.pct_change(fill_method=None).dropna(how='all').sub(benchmark_series, axis=0).sort_index()
    corr_df = return_df.corr('pearson').round(3)

    return corr_df


def excess_drawdown_and_recovery(start_date, end_date):
    """
    超额回撤及修复期数
    """
    fund_dict = {
        "诚奇": "SLS817",
        "伯兄": "SQT564",
        "乾象": "P48470",
        "新方程": "SSL554",
        "明汯": "SEE194",
        "衍复": "SJH866",
        "量锐": "P23195",
        "宽德": "SJF555",
        "星阔": "SNU706",
        "赫富": "SEP463",
        "因诺": "SGX346",
        "启林": "SGY379",
        "概率": "SQT076",
        "茂源": "SNM667",
        "世纪前沿": "SGP682",
        "黑翼": "SEM323",
        "幻方": "SY0607",
        "天演": "P20830",
        "九坤": "ST9804",
        "鸣石": "SX2090",
    }
    period_date = get_trading_day_list(start_date, end_date, frequency='week')
    fund_nav = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(
        period_date)
    sql_script = ("SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE FROM st_market.t_st_zs_hq WHERE "
                  "ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}").format('000905', start_date, end_date)
    res = hbs.db_data_query('alluser', sql_script, page_size=5000)
    data = pd.DataFrame(res['data'])
    data['TRADEDATE'] = data['TRADEDATE'].map(str)
    benchmark_series = data.set_index('TRADEDATE')['TCLOSE'].reindex(
            period_date).pct_change().dropna()
    return_df = fund_nav.pct_change(fill_method=None).dropna(how='all').sub(benchmark_series, axis=0).sort_index()
    return_df.loc[start_date] = 0.
    return_df.sort_index(inplace=True)
    nav_df = (1 + return_df).cumprod()

    max_drawdown = nav_df.apply(cal_max_drawdown)
    dd_recovery = nav_df.apply(cal_dd_recovery)
    drawdown_df = max_drawdown.to_frame('最大回撤').merge(
        dd_recovery.to_frame('最长回撤修复期数'), left_index=True, right_index=True)

    return drawdown_df


def calc_stock_diff(start_date, end_date):
    trade_dt = datetime.strptime(start_date, '%Y%m%d')
    range_start = (trade_dt - timedelta(days=100)).strftime('%Y%m%d')
    path = r'D:\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if range_start <= x.split('.')[0].split('_')[-1] <= end_date]
    date_list = []
    vol = []
    for filename in listdir:
        date = filename.split('.')[0].split('_')[-1]
        date_list.append(date)
        date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"tradeDate": str})
        date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_rate.loc[date_t_rate['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NAN
        date_t_rate = date_t_rate[date_t_rate['dailyReturnReinv'].abs() <= 20]
        vol.append(date_t_rate['dailyReturnReinv'].dropna().std() / 100.)

    vol_df = pd.Series(index=date_list, data=vol).to_frame('stock_diff').sort_index()
    vol_df['mean_10'] = vol_df['stock_diff'].rolling(10).mean()
    vol_df = vol_df.loc[start_date:].dropna()
    vol_df.rename(columns={"stock_diff": "截面波动率", "mean_10": "10日平均"}, inplace=True)

    vol_df['trade_date'] = vol_df.index
    vol_df['trade_date'] = vol_df['trade_date'].apply(
        lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    vol_df.set_index('trade_date', inplace=True)

    return vol_df['截面波动率']


def curve_fitting(start_date, end_date, tday):
    """
    新方程指增FOF历史业绩拟合
    """
    config_df = pd.read_excel(
        "D:\\研究基地\\私募量化基金池\\量化基金池202302.xlsx", sheet_name="量化池列表", header=1).dropna(subset=["基金管理人"])
    config_df = config_df[(config_df['二级策略'] == '500指数增强') & (config_df['三级策略'] != "T0")]
    config_df['入池时间'] = config_df['入池时间'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    # 微调
    config_df.loc[config_df['基金管理人'] == "幻方量化", ["代表产品", "基金代码"]] = ["九章幻方中证500量化进取1号", "SEC185"]
    config_df.loc[config_df['基金管理人'] == "诚奇资产", ["代表产品", "基金代码"]] = ["诚奇中证500增强精选1期", "SLS817"]
    config_df.loc[config_df['基金管理人'] == "天演资本", ["代表产品", "基金代码"]] = ["天演中证500指数增强", "P20830"]
    config_df.loc[config_df['基金管理人'] == "明汯投资", ["代表产品", "基金代码"]] = ["明汯价值成长1期", "SS5789"]
    fund_dict = config_df.set_index('代表产品')['基金代码'].to_dict()
    trading_day_list = get_trading_day_list(start_date, end_date, "week")
    fund_nav = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(
        trading_day_list)
    # 入池矩阵
    fund_list = []
    for trading_day in trading_day_list:
        universe_list = config_df[config_df['入池时间'] <= trading_day]['代表产品'].tolist()
        universe = pd.Series(index=universe_list, data=1.).to_frame(trading_day)
        fund_list.append(universe)
    fund_mat = pd.concat(fund_list, axis=1).T.sort_index()
    count_num = fund_mat.sum(axis=1)
    reb_list = count_num[count_num.shift(1) != count_num].index.tolist()
    reb_list.append(end_date)
    # 回测
    ret_list = []
    for i in range(1, len(reb_list)):
        pre_date, t_date = reb_list[i - 1], reb_list[i]
        universe = fund_mat.loc[pre_date].dropna().index.tolist()
        period_data = fund_nav.loc[pre_date: t_date, universe]
        period_data /= period_data.iloc[0]
        period_ret = period_data.mean(axis=1).pct_change().dropna()
        # print(period_data.shape)
        ret_list.append(period_ret)
    ret_df = pd.concat(ret_list).sort_index()
    # 拼接
    trading_day_list = get_trading_day_list(end_date, tday, "week")
    new_formula = get_fund_nav_from_sql(end_date, tday, {"新方程": "SSL554"}).reindex(
        trading_day_list).pct_change().dropna()

    ret_df = pd.concat([ret_df.to_frame('模拟'), new_formula]).sort_index()
    ret_df['拼接'] = np.where(ret_df['新方程'].isnull(), ret_df['模拟'], ret_df['新方程'])
    trading_day_list = get_trading_day_list(start_date, tday, "week")
    benchmark_series = get_index_return_from_sql(start_date, tday, '000905').reindex(
            trading_day_list).pct_change().dropna()

    return_df = ret_df[['拼接']].merge(benchmark_series, left_index=True, right_index=True)
    return_df.rename(columns={"拼接": "中小盘二号", "TCLOSE": "中证500"}, inplace=True)
    return_df['超额收益'] = return_df['中小盘二号'] - return_df['中证500']
    nav_df = (1 + return_df).cumprod()
    nav_df.loc[start_date] = 1.
    nav_df = nav_df.sort_index()

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

    nav_df.rename(columns={"中小盘二号": "中小盘二号（模拟）"}, inplace=True)
    nav_df['中小盘二号（实盘）'] = np.NaN
    nav_df.loc[end_date:, "中小盘二号（实盘）"] = nav_df.loc[end_date:, "中小盘二号（模拟）"]
    nav_df = nav_df[['中小盘二号（模拟）',	'中小盘二号（实盘）', '中证500', '超额收益']]
    nav_df['trade_date'] = nav_df.index
    nav_df['trade_date'] = nav_df['trade_date'].apply(
        lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    nav_df.set_index('trade_date', inplace=True)

    return nav_df, portfolio_index_df


def curve_fitting2(start_date, end_date):
    """
    40万指增模拟(用量化多头模拟)
    """
    # 用跟踪池选取数据
    config_df = get_track_config_from_db()
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    fund_dict = config_df[config_df['strategy_type'] == "量化多头"].set_index('abr')['fund_id'].to_dict()
    dt_df = config_df[(config_df['strategy_type'] == "量化多头") & (~config_df['start_date'].isnull())]
    dt_df['start_date'] = dt_df['start_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    dt_dict = dt_df.set_index('abr')['start_date'].to_dict()
    fund_nav = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(
        trading_day_list)
    # start_date
    for key, value in dt_dict.items():
        if key not in fund_nav.columns:
            continue
        if value in trading_day_list:
            t_index = trading_day_list.index(value)
            if t_index == 0:
                continue
            else:
                pre_value = trading_day_list[t_index - 1]
                fund_nav.loc[: pre_value, key] = np.NaN
        else:
            continue
    return_df = fund_nav.pct_change(limit=1).mean(axis=1).to_frame('模拟净值')
    nav_df = (1 + return_df.fillna(0.)).cumprod()
    # 计算指标
    performance_df = pd.DataFrame(
        index=nav_df.columns, columns=["累计收益", "年化收益率", "年化波动率", "最大回撤",
                                       "Sharpe比率", "Calmar比率", "投资胜率", "平均损益比"])
    performance_df.loc[:, "累计收益"] = nav_df.iloc[-1] - 1
    performance_df.loc[:, "年化收益率"] = return_df.apply(cal_annual_return, axis=0)
    performance_df.loc[:, '年化波动率'] = return_df.apply(cal_annual_volatility, axis=0)
    performance_df.loc[:, "最大回撤"] = nav_df.apply(cal_max_drawdown, axis=0)
    performance_df.loc[:, "Sharpe比率"] = return_df.apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
    performance_df['Calmar比率'] = performance_df['年化收益率'] / performance_df['最大回撤'].abs()
    performance_df.loc[:, "投资胜率"] = return_df.apply(lambda x: x.gt(0).sum() / len(x), axis=0)
    performance_df.loc[:, "平均损益比"] = return_df.apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)

    return nav_df, performance_df


if __name__ == '__main__':
    # period_nav_compare("20221230", "20230928")
    # excess_correlation("20171229", "20230728")
    # excess_drawdown_and_recovery("20210930", "20230728")
    # calc_stock_diff("20201231", "20230818")
    # curve_fitting("20181228", "20211008", "20231124")
    curve_fitting2("20181228", "20231124")