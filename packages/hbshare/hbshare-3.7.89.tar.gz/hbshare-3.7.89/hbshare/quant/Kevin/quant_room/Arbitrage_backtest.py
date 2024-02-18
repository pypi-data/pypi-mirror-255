"""
套利FOF回测模块
"""
import numpy as np
from MyUtil.data_loader import get_trading_day_list, get_fund_nav_from_sql
from MyUtil.util_func import cal_annual_return, cal_annual_volatility, cal_max_drawdown, cal_sharpe_ratio
import pandas as pd
import datetime


def arb_port_simulation(start_date, end_date):
    fund_dict = {
        "杉阳云杉量化1号": "SLB530",
        "百奕传家一号": "SJS027",
        "百奕传家二号": "SNZ338",
        "安值福慧量化1号": "SCP765",
        "展弘稳进1号1期": "SE8723",
        "悬铃C号": "SEK201",
        "悬铃C号6期": "SNY736",
        "御澜伏尔加元创5号": "SGT788",
        "稳博中睿6号": "SJB143",
        "茂源巴舍里耶2期": "SCV226",
        "蒙玺竞起6号": "SSM855",
        "宽德踏远11号": "SSQ331",
        "稳博对冲18号": "SNW150",
        "泓倍商品相对价值1号": "SCU913",
        "塑造者1号": "SCA422",
        "磐松多空对冲1号": "SXZ248"
    }
    trading_day_list = get_trading_day_list(start_date, end_date, frequency='week')
    nav_df = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(trading_day_list)
    inc1 = ["杉阳云杉量化1号", "百奕传家一号", "安值福慧量化1号", "展弘稳进1号1期",
            "悬铃C号", "御澜伏尔加元创5号", "稳博中睿6号", "茂源巴舍里耶2期"]
    inc2 = inc1 + ['蒙玺竞起6号', '茂源巴舍里耶2期']
    inc3 = ["杉阳云杉量化1号", "百奕传家二号", "安值福慧量化1号", "御澜伏尔加元创5号", "稳博对冲18号", "茂源巴舍里耶2期",
            "蒙玺竞起6号", "宽德踏远11号", "泓倍商品相对价值1号", "塑造者1号", "磐松多空对冲1号"]
    # p1
    p_data = nav_df.loc[start_date: "20210930", inc1]
    assert p_data.isnull().sum().sum() == 0
    p_data /= p_data.iloc[0]
    port_ret_p1 = p_data.mean(axis=1).pct_change().fillna(0.)
    # p2
    p_data = nav_df.loc["20210930": "20230120", inc2]
    assert p_data.isnull().sum().sum() == 0
    p_data /= p_data.iloc[0]
    port_ret_p2 = p_data.mean(axis=1).pct_change().dropna()
    # p3
    p_data = nav_df.loc["20230120": end_date, inc3].fillna(1.)
    assert p_data.isnull().sum().sum() == 0
    p_data /= p_data.iloc[0]
    port_ret_p3 = p_data.mean(axis=1).pct_change().dropna()

    return_df = pd.concat([port_ret_p1, port_ret_p2, port_ret_p3], axis=0).to_frame('模拟套利组合').sort_index()
    nav_df = (1 + return_df).cumprod()

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
    # 格式处理
    performance_df['累计收益'] = performance_df['累计收益'].apply(lambda x: format(x, '.2%'))
    performance_df['年化收益率'] = performance_df['年化收益率'].apply(lambda x: format(x, '.2%'))
    performance_df['年化波动率'] = performance_df['年化波动率'].apply(lambda x: format(x, '.2%'))
    performance_df['最大回撤'] = performance_df['最大回撤'].apply(lambda x: format(x, '.2%'))
    performance_df['Sharpe比率'] = performance_df['Sharpe比率'].round(2)
    performance_df['Calmar比率'] = performance_df['Calmar比率'].round(2)
    performance_df['投资胜率'] = performance_df['投资胜率'].apply(lambda x: format(x, '.2%'))
    performance_df['平均损益比'] = performance_df['平均损益比'].round(2)

    nav_df['最大回撤'] = nav_df['模拟套利组合'] / nav_df['模拟套利组合'].cummax() - 1



    return performance_df


if __name__ == '__main__':
    # s_date = '20200103'
    # e_date = '20220909'
    #
    # f_dict = {
    #     "展弘稳进1号1期": "SE8723",
    #     "盛冠达股指套利3号": "SGS597",
    #     "稳博中睿6号": "SJB143"
    # }
    #
    # date_list = get_trading_day_list(s_date, e_date, frequency='week')
    #
    # nav_df = get_fund_nav_from_sql(s_date, e_date, f_dict).reindex(date_list).fillna(method='ffill')
    #
    # mx_df = pd.read_excel('D:\\蒙玺竞起6号净值.xlsx', sheet_name=0)
    # mx_df['trade_date'] = mx_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    # mx_df.rename(columns={"nav": "蒙玺竞起6号"}, inplace=True)
    # mx_df = mx_df.set_index('trade_date').reindex(date_list).dropna()
    #
    # nav_df = pd.concat([nav_df, mx_df], axis=1)
    # return_df = nav_df.pct_change().fillna(0.)
    #
    # # 等权
    # weight_df1 = pd.DataFrame(index=return_df.index, columns=return_df.columns)
    # weight_df1.loc['20200103', :] = [1/3, 1/3, 1/3, 0]
    #
    # rbl_list = ['20201120']
    #
    # for i in range(1, len(return_df)):
    #     date = return_df.index[i]
    #     weight_df1.iloc[i, :] = weight_df1.iloc[i - 1, :] * (1 + return_df.iloc[i, :])
    #     if date in rbl_list:
    #         weight_df1.loc[date] = weight_df1.loc[date].mean()
    #
    # port_nav1 = weight_df1.sum(axis=1)
    #
    # # 额度加权
    # weight_df2 = pd.DataFrame(index=return_df.index, columns=return_df.columns)
    # weight_df2.loc['20200103', :] = [4/9, 1/9, 4/9, 0]
    # weight_df2.loc['20201120', :] = [4/11, 1/11, 4/11, 2/11]
    #
    # rbl_list = ['20201120']
    #
    # for i in range(1, len(return_df)):
    #     date = return_df.index[i]
    #     weight_df2.iloc[i, :] = weight_df2.iloc[i - 1, :] * (1 + return_df.iloc[i, :])
    #     if date in rbl_list:
    #         weight_df2.loc[date] = [weight_df2.loc[date].sum() * x for x in [4/11, 1/11, 4/11, 2/11]]
    #
    # port_nav2 = weight_df2.sum(axis=1)
    #
    # # 净值
    # port_nav = pd.concat([port_nav1.to_frame('等权组合'), port_nav2.to_frame('最大额度组合')], axis=1)
    # # 累计收益率
    # cum_return = port_nav.iloc[-1] - 1
    # # 年化收益
    # an_return = port_nav.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
    # # 年化波动
    # an_vol = port_nav.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
    # # 最大回撤
    # max_draw = port_nav.apply(cal_max_drawdown, axis=0)
    # draw_series = port_nav.apply(lambda x: x / x.cummax() - 1)
    # # sharpe
    # sharpe = port_nav.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
    # # # sortino
    # down_std = port_nav.pct_change().dropna(how='all').apply(lambda x: x[x < 0].std() * np.sqrt(52), axis=0)
    # sortino = an_return / down_std
    # # calmar
    # calmar = an_return / max_draw.abs()
    # # 胜率
    # win_ratio = port_nav.pct_change().dropna(how='all').apply(lambda x: x.gt(0).sum() / len(x), axis=0)
    # # 平均损益比
    # win_lose = port_nav.pct_change().dropna(how='all').apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
    # # 年度累计
    # ret_20 = port_nav.loc['20201231'] - 1
    # ret_21 = port_nav.iloc[-1] / port_nav.loc['20201231'] - 1

    arb_port_simulation("20201231", "20231027")