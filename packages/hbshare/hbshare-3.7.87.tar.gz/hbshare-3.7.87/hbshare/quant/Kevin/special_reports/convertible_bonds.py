"""
可转债策略研究专题报告
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import hbshare as hbs
import seaborn as sns
from datetime import datetime, timedelta
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_trading_day_list, load_industry_sw3
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import fetch_data_batch_hbs
from WindPy import w

w.start()


def cb_summary(date):
    """
    转债市场概览
    """
    tday = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
    res = w.wset("cbissue", "startdate=2015-01-01;enddate={}".format(tday))
    cb_info = pd.DataFrame(index=res.Fields, data=res.Data).T
    # 筛选
    cb_info.dropna(subset=['listing_date'], inplace=True)
    cb_info = cb_info[cb_info['issue_type'].str.contains('优先配售')]
    cb_info = cb_info[cb_info['bond_code'].str.startswith('1')]
    # 列处理
    include_cols = ['_companycode', 'name', 'bond_code', 'bond_name', 'listing_date', 'interest_end_date',
                    'conversion_start_date', 'credit_rating', 'issue_size']
    cb_info = cb_info[include_cols]
    # 时间处理
    for col in ['listing_date', 'interest_end_date', 'conversion_start_date']:
        cb_info[col] = cb_info[col].apply(lambda x: x.strftime("%Y%m%d"))
    # 最新截面概览
    t_df = cb_info[(cb_info['listing_date'] < date) & (cb_info['interest_end_date'] > date)]
    t_df = t_df[~t_df['bond_name'].str.contains('退市')]
    # 行业
    industry_df = load_industry_sw3(date).to_frame('industry')
    t_df['ticker'] = t_df['_companycode'].apply(lambda x: x.split('.')[0])
    t_df = t_df.merge(industry_df, left_on='ticker', right_index=True, how='left')
    # 转债全价
    cb_price = w.wss(','.join(t_df['bond_code'].tolist()),
                     "outstandingbalance,dirtyprice,strbvalue,convprice", "tradeDate={}".format(date))
    cb_price = pd.DataFrame(columns=cb_price.Codes, index=cb_price.Fields, data=cb_price.Data).T
    t_df = t_df.merge(cb_price, left_on='bond_code', right_index=True)
    # 正股价
    stock_price = w.wss(','.join(t_df['_companycode'].unique()), "close",
                        "tradeDate={};priceAdj=U;cycle=D".format(date))
    stock_price = pd.DataFrame(columns=stock_price.Codes, data=stock_price.Data).T
    stock_price.columns = ['stock_price']
    t_df = t_df.merge(stock_price, left_on='_companycode', right_index=True)
    # premium
    t_df['conv_value'] = 100 * t_df['stock_price'] / t_df['CONVPRICE']
    t_df['conv_premium'] = t_df['DIRTYPRICE'] / (t_df['conv_value']) - 1
    t_df['bond_premium'] = t_df['conv_value'] / t_df['STRBVALUE'] - 1
    # 正股的性质
    mkt_info = pd.read_csv("D:\\MarketInfoSaver\\market_info_{}.csv".format(date), dtype={"ticker": str})
    t_df = t_df.merge(mkt_info[['ticker', 'marketValue']], on='ticker')
    t_df['weight'] = t_df['marketValue'] / t_df['marketValue'].sum()

    return t_df


def cb_mkv_converter(start_date, end_date, path):
    """
    转债市场概览
    """
    tday = datetime.strptime(end_date, "%Y%m%d").strftime("%Y-%m-%d")
    res = w.wset("cbissue", "startdate=2015-01-01;enddate={}".format(tday))
    cb_info = pd.DataFrame(index=res.Fields, data=res.Data).T
    # 筛选
    cb_info.dropna(subset=['listing_date'], inplace=True)
    cb_info = cb_info[cb_info['issue_type'].str.contains('优先配售')]
    cb_info = cb_info[cb_info['bond_code'].str.startswith('1')]
    # 列处理
    include_cols = ['_companycode', 'name', 'bond_code', 'bond_name', 'listing_date', 'interest_end_date',
                    'conversion_start_date', 'credit_rating', 'issue_size']
    cb_info = cb_info[include_cols]
    # 时间处理
    for col in ['listing_date', 'interest_end_date', 'conversion_start_date']:
        cb_info[col] = cb_info[col].apply(lambda x: x.strftime("%Y%m%d"))

    month_list = get_trading_day_list(start_date, end_date, "month")

    for date in month_list:
        t_df = cb_info[(cb_info['listing_date'] < date) & (cb_info['interest_end_date'] > date)]
        t_df = t_df[~t_df['bond_name'].str.contains('退市')]
        # 转债全价
        cb_price = w.wss(','.join(t_df['bond_code'].tolist()),
                         "outstandingbalance,dirtyprice,strbvalue,convprice", "tradeDate={}".format(date))
        cb_price = pd.DataFrame(columns=cb_price.Codes, index=cb_price.Fields, data=cb_price.Data).T
        t_df = t_df.merge(cb_price, left_on='bond_code', right_index=True)
        # 正股价
        stock_price = w.wss(','.join(t_df['_companycode'].unique()), "close",
                            "tradeDate={};priceAdj=U;cycle=D".format(date))
        stock_price = pd.DataFrame(columns=stock_price.Codes, data=stock_price.Data).T
        stock_price.columns = ['stock_price']
        t_df = t_df.merge(stock_price, left_on='_companycode', right_index=True)
        # premium
        t_df['conv_value'] = 100 * t_df['stock_price'] / t_df['CONVPRICE']
        t_df['conv_premium'] = t_df['DIRTYPRICE'] / (t_df['conv_value']) - 1
        t_df['bond_premium'] = t_df['conv_value'] / t_df['STRBVALUE'] - 1

        t_df[['_companycode', 'bond_code', 'conv_premium', 'bond_premium']].to_csv(
            os.path.join(path, "{}.csv".format(date)), index=False)


def calc_iv_spread(start_date, end_date, path):
    # 计算隐波差因子
    month_list = get_trading_day_list(start_date, end_date, "month")
    for date in month_list:
        universe_df = pd.read_csv(os.path.join(path, "{}.csv".format(date))).rename(columns={"_companycode": "ticker"})
        cb_code_list = universe_df['bond_code'].unique()
        # iv
        res = w.wss(','.join(cb_code_list), "impliedvol", "tradeDate={};rfIndex=7".format(date))
        data = pd.DataFrame(res.Data[0], index=res.Codes, columns=res.Times)
        data.columns = ['iv']
        data.index.name = 'bond_code'
        data = data.reset_index().dropna()
        universe_df = universe_df.merge(data, on='bond_code')
        # hv
        trade_dt = datetime.strptime(date, "%Y%m%d")
        pre_date = (trade_dt - timedelta(days=100)).strftime("%Y%m%d")
        mkt_path = "D:\\MarketInfoSaver"
        listdir = os.listdir(mkt_path)
        listdir = [x for x in listdir if pre_date < x.split('_')[-1].split('.')[0] <= date]
        data = []
        for filename in listdir:
            trade_date = filename.split('.')[0].split('_')[-1]
            date_t_data = pd.read_csv(os.path.join(mkt_path, filename))
            date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
            date_t_data['trade_date'] = trade_date
            data.append(date_t_data)
        data = pd.concat(data)
        data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
        data = pd.pivot_table(data, index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index() / 100.
        ticker_list = [x.split('.')[0] for x in universe_df['ticker'].unique()]
        period_data = data.loc[:date][-60:][ticker_list]
        universe_df['ticker'] = universe_df['ticker'].apply(lambda x: x.split('.')[0])
        universe_df = universe_df.merge(period_data.std().to_frame('hv'), left_on='ticker', right_index=True)
        universe_df['hv'] *= np.sqrt(252)
        universe_df['iv'] /= 100.
        universe_df.eval("iv_spread = iv - hv", inplace=True)
        # 正股收益率
        stock_return = ((1 + period_data[-20:]).prod() - 1).to_frame('ret20').merge(
            ((1 + period_data).prod() - 1).to_frame('ret60'), left_index=True, right_index=True)
        universe_df = universe_df.merge(stock_return, left_on='ticker', right_index=True)
        # 转债收益率
        trading_day_list = get_trading_day_list(pre_date, date, "day")
        res = w.wss(','.join(cb_code_list), "pq_pctchange",
                    "startDate={};endDate={};bondPriceType=2".format(trading_day_list[-20], date))
        period_return = pd.DataFrame(index=res.Fields, columns=res.Codes, data=res.Data).T
        period_return.columns = ['cb_ret20']
        period_return /= 100.
        universe_df = universe_df.merge(period_return, left_on='bond_code', right_index=True)
        # PETTM
        sql_script = "SELECT a.SecuCode, b.TradingDay, b.DividendRatio, b.PE FROM " \
                     "hsjy_gg.LC_DIndicesForValuation b join hsjy_gg.SecuMain a on " \
                     "a.InnerCode = b.InnerCode where a.SecuCategory = 1 and " \
                     "a.SecuMarket in (83, 90) and to_char(b.TradingDay,'yyyymmdd') = '{}'".format(date)
        fin_data_main = fetch_data_batch_hbs(sql_script)
        sql_script = "SELECT a.SecuCode, b.TradingDay, b.DividendRatioTTM, b.PETTM FROM " \
                     "hsjy_gg.LC_STIBDIndiForValue b join hsjy_gg.SecuMain a on " \
                     "a.InnerCode = b.InnerCode where a.SecuCategory = 1 and " \
                     "a.SecuMarket in (83, 90) and to_char(b.TradingDay,'yyyymmdd') = '{}'".format(date)
        res = hbs.db_data_query("readonly", sql_script, page_size=500)
        fin_data_stib = pd.DataFrame(res['data'])
        fin_data_stib.rename(columns={"DIVIDENDRATIOTTM": "DIVIDENDRATIO", "PETTM": "PE"}, inplace=True)
        fin_data = pd.concat([fin_data_main, fin_data_stib])
        fin_data.rename(columns={"SECUCODE": "ticker"}, inplace=True)

        universe_df = universe_df.merge(fin_data[['ticker', 'PE']], on='ticker')
        print("{}: 有效数据{}条".format(date, universe_df.shape[0]))

        universe_df.to_csv("D:\\研究基地\\G-专题报告\\【2023.10】可转债策略探究\\可转债因子\\{}.csv".format(date), index=False)


def cb_backtest(start_date, end_date):
    month_end = get_trading_day_list(start_date, end_date, "month")
    month_end.append(end_date)
    factor_list = ['iv_spread', 'conv_premium', 'ret20', 'ret60', 'cb_ret20', 'PE']
    factor_list1 = ['iv_spread', 'conv_premium', 'ret20', 'ret60', 'cb_ret20', 'PE', 'combine']
    res_list = []
    for i in range(1, len(month_end)):
        p_date, t_date = month_end[i - 1], month_end[i]
        d_list = get_trading_day_list(p_date, t_date, 'day')
        p_date_next = d_list[1]
        factor_df = pd.read_csv(
            "D:\\研究基地\\G-专题报告\\【2023.10】可转债策略探究\\可转债因子\\{}.csv".format(p_date), dtype={"ticker": str})
        factor_df = factor_df.dropna()
        factor_df = factor_df[factor_df['iv'] > 1e-8]
        factor_df.loc[factor_df['bond_premium'] < -0.2, "type"] = 'bond'
        factor_df.loc[factor_df['bond_premium'] > 0.2, "type"] = "stock"
        factor_df['type'].fillna('balance', inplace=True)
        # future_ret
        cb_code_list = factor_df['bond_code'].unique()
        res = w.wss(','.join(cb_code_list), "pq_pctchange",
                    "startDate={};endDate={};bondPriceType=2".format(p_date_next, t_date))
        period_return = pd.DataFrame(index=res.Fields, columns=res.Codes, data=res.Data).T / 100.
        period_return.columns = ['period_ret']
        factor_df = factor_df.merge(period_return, left_on='bond_code', right_index=True)
        # 预处理
        for factor_name in factor_list:
            factor_df[factor_name] = (
                    (factor_df[factor_name] - factor_df[factor_name].mean()) / factor_df[factor_name].std())
        factor_df.eval("combine = conv_premium + PE", inplace=True)
        # 根据因子构建分层组合
        for factor_name in factor_list1:
            all_df = []
            for cb_type in ['bond', 'balance', 'stock']:
                df = factor_df[factor_df['type'] == cb_type].copy()
                df['group'] = pd.qcut(df[factor_name], q=5, labels=False) + 1
                all_df.append(df)
            all_df = pd.concat(all_df)
            group_ret = all_df.groupby('group')['period_ret'].mean().reset_index()
            group_ret['factor_name'] = factor_name
            group_ret['trade_date'] = t_date
            res_list.append(group_ret)

    res_df = pd.concat(res_list)
    res_dict = dict()
    for factor_name in factor_list1:
        sub_df = res_df[res_df['factor_name'] == factor_name]
        sub_df = sub_df.pivot_table(index='trade_date', columns='group', values='period_ret').sort_index()
        sub_df.loc[start_date] = 0.
        sub_df.sort_index(inplace=True)
        sub_df.columns = ['Group_' + str(x) for x in sub_df.columns]
        sub_df = (1 + sub_df).cumprod()
        res_dict[factor_name] = sub_df

    return res_dict


def pricing_compare():
    valuation_df = pd.read_csv("C:\\Users\\kai.zhang\\Desktop\\可转债\\可转债估值结果_新.csv")
    include_cols = ['B-S', 'tree', 'mc']
    # filter
    valuation_df = valuation_df[valuation_df['close'] <= 200].dropna().set_index('cb_id')
    # deviation
    dev_df = valuation_df.copy()
    for col in include_cols:
        dev_df[col] = (dev_df['close'] - dev_df[col]) / dev_df[col]
    # abs_deviation
    abs_dev = valuation_df.copy()
    for col in include_cols:
        abs_dev[col] = (abs_dev['close'] - abs_dev[col]).abs() / abs_dev[col]

    sns.kdeplot(dev_df['B-S'], shade=True, color='g', label="B-S")
    sns.kdeplot(dev_df['tree'], shade=True, color='b', label="tree")
    sns.kdeplot(dev_df['mc'], shade=True, color='r', label="Monte-Carlo")
    plt.legend()


def portfolio_compare():
    valuation_df = pd.read_csv("C:\\Users\\kai.zhang\\Desktop\\可转债\\可转债估值结果.csv")
    valuation_df['spread'] = (valuation_df['close'] - valuation_df['mc']) / valuation_df['mc']
    valuation_df['group'] = pd.qcut(valuation_df['spread'], q=5, labels=False)
    valuation_df['group'] += 1
    valuation_df['group'] = valuation_df['group'].apply(lambda x: 'G' + str(x))
    cb_id_list = valuation_df['cb_id'].tolist()
    # 转债收益
    res = w.wsd(','.join(cb_id_list), "close", "2021-06-01", "2021-07-01", "")
    data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times)
    data.columns = [datetime.strftime(x, "%Y%m%d") for x in data.columns]
    data = data.T.sort_index()
    data /= data.iloc[0]

    valuation_df = valuation_df.merge(data.iloc[5].to_frame('ret5'), left_on='cb_id', right_index=True)
    valuation_df = valuation_df.merge(data.iloc[10].to_frame('ret10'), left_on='cb_id', right_index=True)
    valuation_df = valuation_df.merge(data.iloc[20].to_frame('ret20'), left_on='cb_id', right_index=True)

    group_ret = valuation_df.groupby('group')[['ret5', 'ret10', 'ret20']].mean() - 1

    return group_ret

if __name__ == '__main__':
    data_path = "D:\\研究基地\\G-专题报告\\【2023.10】可转债策略探究\\可转债月度universe"
    # cb_summary("20230331")
    # cb_mkv_converter("20201231", "20230831", data_path)
    # calc_iv_spread("20201231", "20230831", data_path)
    # cb_backtest("20201231", "20230922")
    # pricing_compare()
    portfolio_compare()