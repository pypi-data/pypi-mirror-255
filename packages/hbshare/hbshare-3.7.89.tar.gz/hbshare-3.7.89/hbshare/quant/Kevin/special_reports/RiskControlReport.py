"""
风险控制专题报告-代码1，代码2在组合优化项目中
新增周度量价因子的代码
"""
import numpy as np
import pandas as pd
import hbshare as hbs
from tqdm import tqdm
import statsmodels.api as sm
import datetime
import os
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from hbshare.fe.common.util.config import style_name, industry_name
from hbshare.fe.common.util.data_loader import get_trading_day_list
from hbshare.quant.Kevin.rm_associated.config import style_names
from hbshare.quant.Kevin.special_reports.UMR_Structure import UMROperator, true_range_extractor
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import fetch_data_batch_hbs
from sklearn.preprocessing import MinMaxScaler
from WindPy import w

w.start()


def save_mkt_data_to_csv(start_date, end_date):
    trading_day_list = get_trading_day_list(start_date, end_date)

    for date in tqdm(trading_day_list):
        # MKT
        sql_script = "SELECT SYMBOL, TDATE, TCLOSE, VATURNOVER, PCHG, MCAP, TCAP FROM finchina.CHDQUOTE WHERE" \
                     " TDATE = {}".format(date)
        df = fetch_data_batch_hbs(sql_script)
        df = df[df['SYMBOL'].str[0].isin(['0', '3', '6'])]
        df.rename(columns={"SYMBOL": "ticker", "TDATE": "tradeDate", "TCAP": "marketValue",
                           "MCAP": "negMarketValue", "VATURNOVER": "turnoverValue",
                           "PCHG": "dailyReturnReinv"}, inplace=True)
        # BP
        sql_script = "SELECT a.TradingDay, a.PB, b.SecuCode From " \
                     "hsjy_gg.LC_DIndicesForValuation a join hsjy_gg.SecuMain b on a.InnerCode = b.InnerCode where " \
                     "to_char(a.TradingDay,'yyyymmdd') = {}".format(date)
        bp_data_main = fetch_data_batch_hbs(sql_script)
        bp_data_main = bp_data_main.rename(columns={"SECUCODE": "ticker"})[['ticker', 'PB']]
        sql_script = "SELECT a.TradingDay, a.PB, b.SecuCode From " \
                     "hsjy_gg.LC_STIBDIndiForValue a join hsjy_gg.SecuMain b on a.InnerCode = b.InnerCode where " \
                     "to_char(a.TradingDay,'yyyymmdd') = {}".format(date)
        res = hbs.db_data_query('readonly', sql_script, page_size=6000)
        if len(res['data']) == 0:
            bp_data = bp_data_main
        else:
            bp_data_stib = pd.DataFrame(res['data']).rename(columns={"SECUCODE": "ticker"})[['ticker', 'PB']]
            bp_data = pd.concat([bp_data_main, bp_data_stib])
            bp_data = bp_data[bp_data['ticker'].str[0].isin(['0', '3', '6'])]

        data = df.merge(bp_data, on='ticker')
        include_cols = ['ticker', 'negMarketValue', 'marketValue', 'turnoverValue', 'dailyReturnReinv', 'PB']
        data[include_cols].to_csv('D:\\MarketInfoSaver\\market_info_{}.csv'.format(date), index=False)
        print("{}: 有效数据{}条".format(date, data.shape[0]))


def save_price_data_to_csv(start_date, end_date):
    trading_day_list = get_trading_day_list(start_date, end_date)

    for date in tqdm(trading_day_list):
        sql_script = ("SELECT SYMBOL, TDATE, LCLOSE, TOPEN, HIGH, LOW, TCLOSE, VATURNOVER FROM finchina.CHDQUOTE WHERE "
                      "TDATE = {}".format(date))
        df = fetch_data_batch_hbs(sql_script)
        df = df[df['SYMBOL'].str[0].isin(['0', '3', '6'])]
        df.rename(columns={"SYMBOL": "ticker", "TDATE": "tradeDate", "VATURNOVER": "turnoverValue"}, inplace=True)
        include_cols = ['tradeDate', 'ticker', 'LCLOSE', 'TOPEN', 'HIGH', 'LOW', 'TCLOSE', 'turnoverValue']
        df[include_cols].to_csv('D:\\AlphaBase\\价格数据\\{}.csv'.format(date), index=False)
        print("{}: 有效数据{}条".format(date, df.shape[0]))


def save_dealAmount_data_to_csv():
    path = "D:\\AlphaBase\\原始成交笔数数据-Wind"
    listdir = os.listdir(path)
    for filename in listdir:
        t_data = pd.read_csv(os.path.join(path, filename)).dropna()
        t_data.columns = ['sec_code', 'sec_name', 'dealAmount']
        t_data['ticker'] = t_data['sec_code'].apply(lambda x: x.split('.')[0])
        t_data['dealAmount'] = t_data['dealAmount'].apply(lambda x: float(x.replace(',', '')))
        t_data[['ticker', 'dealAmount']].to_csv(
            'D:\\AlphaBase\\成交笔数数据\\{}.csv'.format(filename.split('.')[0]), index=False)


def check_mkt_data():
    path = "D:\\MarketInfoSaver"
    listdir = os.listdir(path)
    date_list = []
    count_list = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        # date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        # date_t_data['trade_date'] = trade_date
        date_list.append(trade_date)
        count_list.append(date_t_data.shape[0])

    count_series = pd.Series(index=date_list, data=count_list).sort_index()
    trading_day_list = get_trading_day_list(count_series.index[0], count_series.index[-1])

    assert (date_list == trading_day_list)

    return count_series


def cal_illiq_factor(start_date, end_date):
    """
    计算月度非流动性因子
    """
    month_list = get_trading_day_list(start_date, end_date, frequency="month")
    illiq = []
    for i in tqdm(range(1, len(month_list))):
        pre_date, t_date = month_list[i - 1], month_list[i]
        path = "D:\\MarketInfoSaver"
        listdir = os.listdir(path)
        listdir = [x for x in listdir if pre_date < x.split('_')[-1].split('.')[0] <= t_date]
        data = []
        for filename in listdir:
            trade_date = filename.split('.')[0].split('_')[-1]
            date_t_data = pd.read_csv(os.path.join(path, filename))
            date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
            date_t_data['trade_date'] = trade_date
            data.append(date_t_data)
        data = pd.concat(data)
        data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
        data['illiq'] = data['dailyReturnReinv'].abs() / (data['turnoverValue'] / 1e+9)
        data = pd.pivot_table(data, index='trade_date', columns='ticker', values='illiq').sort_index()

        na_counts = data.isnull().sum()
        exclude_list = na_counts[na_counts >= data.shape[0] * 0.7].index.tolist()

        t_factor = data.mean().to_frame('illiq')
        t_factor.loc[exclude_list] = np.NaN
        t_factor['trade_date'] = t_date
        t_factor = t_factor.reset_index()

        illiq.append(t_factor)

    illiq = pd.concat(illiq)
    illiq.to_csv("D:\\研究基地\\G-专题报告\\【2022.12】alpha策略的风控管理\\非流动性因子.csv", index=False)


def ols(y, x):
    if y.shape[0] < 10:
        return np.NaN, np.NaN
    else:
        x_ = sm.add_constant(x.copy())
        model = sm.OLS(y, x_, )
        results = model.fit()
        return np.std(results.resid), results.rsquared


def cal_ivff_factor(start_date, end_date):
    """
    计算周度特质波动率（特异度）因子
    """
    date_list = get_trading_day_list(start_date, end_date, frequency="week")
    s_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    s_pre = (s_dt - datetime.timedelta(days=60)).strftime('%Y%m%d')
    trading_day_list = get_trading_day_list(s_pre, end_date, frequency="day")
    # 读取行情数据
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if s_pre < x.split('_')[-1].split('.')[0] <= end_date]
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
    # 计算
    window = 20
    print("==============================开始计算==============================")
    for trade_date in date_list:
        period_start = trading_day_list[trading_day_list.index(trade_date) - window]
        period_data = stock_return[
            (stock_return['trade_date'] > period_start) & (stock_return['trade_date'] <= trade_date)]
        grouped_df = period_data.groupby('trade_date')
        quantile_df = grouped_df['negMarketValue'].quantile(0.33).to_frame('mkv_lower').merge(
            grouped_df['negMarketValue'].quantile(0.66).to_frame('mkv_upper'), left_index=True, right_index=True).merge(
            grouped_df['PB'].quantile(0.33).to_frame('pb_lower'), left_index=True, right_index=True).merge(
            grouped_df['PB'].quantile(0.66).to_frame('pb_upper'), left_index=True, right_index=True).reset_index()
        period_data = period_data.merge(quantile_df, on='trade_date')
        period_data['w_ret'] = period_data['dailyReturnReinv'] * period_data['negMarketValue']
        # 市场收益
        market_return = period_data.groupby('trade_date').apply(
            lambda x: (x['w_ret'] / x['negMarketValue'].sum()).sum())
        # 市值因子收益
        size_return_small = period_data.groupby('trade_date').apply(
            lambda x: (x[x['negMarketValue'] <= x['mkv_lower']]['w_ret']).sum() /
                      (x[x['negMarketValue'] <= x['mkv_lower']]['negMarketValue']).sum())
        size_return_large = period_data.groupby('trade_date').apply(
            lambda x: (x[x['negMarketValue'] >= x['mkv_upper']]['w_ret']).sum() /
                      (x[x['negMarketValue'] >= x['mkv_upper']]['negMarketValue']).sum())
        size_return = size_return_small - size_return_large
        # 估值因子收益
        pb_return_low = period_data.groupby('trade_date').apply(
            lambda x: (x[x['PB'] <= x['pb_lower']]['w_ret']).sum() /
            (x[x['PB'] <= x['pb_lower']]['negMarketValue']).sum())
        pb_return_high = period_data.groupby('trade_date').apply(
            lambda x: (x[x['PB'] >= x['pb_upper']]['w_ret']).sum() /
            (x[x['PB'] >= x['pb_upper']]['negMarketValue']).sum())
        pb_return = pb_return_low - pb_return_high
        reg_data = market_return.to_frame('beta').merge(
            size_return.to_frame('size'), left_index=True, right_index=True).merge(
            pb_return.to_frame('value'), left_index=True, right_index=True)
        assert (reg_data.shape == (20, 3))
        reg_data = period_data[['trade_date', 'ticker', 'dailyReturnReinv']].merge(reg_data, on='trade_date')
        reg_data.sort_values(by=['ticker', 'trade_date'], inplace=True)
        # regression
        res = reg_data.groupby(by='ticker').apply(lambda x: ols(x['dailyReturnReinv'], x[['beta', 'size', 'value']]))
        index = [i[0] for i in reg_data.groupby(by='ticker')]

        ivol = pd.Series(index=index, data=[x[0] for x in res]) * np.sqrt(252)
        ivr = 1 - pd.Series(index=index, data=[x[1] for x in res])

        t_factor = ivol.to_frame('ivff').merge(ivr.to_frame('ivr'), left_index=True, right_index=True).reset_index()
        t_factor = t_factor.dropna()
        # t_factor['trade_date'] = trade_date
        t_factor.rename(columns={"index": "ticker"}, inplace=True)
        print("计算日期: {}， 有因子的个股数目: {}".format(trade_date, t_factor.shape[0]))

        t_factor.to_csv("D:\\AlphaBase\\特质波动率因子\\{}.csv".format(trade_date), index=False)


def cal_M_reverse_factor(start_date, end_date):
    """
    计算周度M-反转因子
    """
    date_list = get_trading_day_list(start_date, end_date, frequency="week")
    s_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    s_pre = (s_dt - datetime.timedelta(days=60)).strftime('%Y%m%d')
    trading_day_list = get_trading_day_list(s_pre, end_date, frequency="day")
    # 读取行情数据
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if s_pre < x.split('_')[-1].split('.')[0] <= end_date]
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    stock_return = data[['trade_date', 'ticker', 'dailyReturnReinv', 'turnoverValue']].dropna()
    stock_return['turnoverValue'] /= 10000.
    stock_return['dailyReturnReinv'] /= 100.
    # 成交笔数数据
    path = 'D:\\AlphaBase\\成交笔数数据'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if s_pre < x.split('_')[-1].split('.')[0] <= end_date]
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    ndeals = pd.concat(data)
    ndeals = ndeals[ndeals['ticker'].str[0].isin(['0', '3', '6'])]
    stock_return = stock_return.merge(ndeals, on=['ticker', 'trade_date'])
    # 计算
    window = 20
    print("==============================开始计算==============================")
    for trade_date in date_list:
        period_start = trading_day_list[trading_day_list.index(trade_date) - window]
        period_data = stock_return[
            (stock_return['trade_date'] > period_start) & (stock_return['trade_date'] <= trade_date)]
        count_series = period_data['ticker'].value_counts()
        # filter
        include_list = count_series[count_series.gt(window - 1)].index.tolist()
        period_data = period_data[period_data['ticker'].isin(include_list)]
        period_data.eval("ave_value = turnoverValue / dealAmount", inplace=True)
        period_data['ave_med'] = period_data.groupby('ticker')['ave_value'].transform('median')
        period_data.loc[period_data['ave_value'] > period_data['ave_med'], 'sign'] = 'M_high'
        period_data.loc[period_data['ave_value'] < period_data['ave_med'], 'sign'] = 'M_low'
        t_factor = period_data.groupby(
            ['ticker', 'sign'])['dailyReturnReinv'].apply(lambda x: (1 + x).prod() - 1).reset_index()
        t_factor = t_factor.pivot_table(index='ticker', columns='sign', values='dailyReturnReinv').reset_index()
        print("计算日期: {}， 有因子的个股数目: {}".format(trade_date, t_factor.shape[0]))

        t_factor.to_csv("D:\\AlphaBase\\M-反转因子\\{}.csv".format(trade_date), index=False)


def cal_STR_and_GTR_factor(start_date, end_date):
    """
    计算周度STR和GTR因子
    """
    date_list = get_trading_day_list(start_date, end_date, frequency="week")
    s_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    s_pre = (s_dt - datetime.timedelta(days=60)).strftime('%Y%m%d')
    trading_day_list = get_trading_day_list(s_pre, end_date, frequency="day")
    # 读取行情数据
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if s_pre < x.split('_')[-1].split('.')[0] <= end_date]
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    data.eval("turn_rate = turnoverValue / negMarketValue", inplace=True)
    stock_return = data[['trade_date', 'ticker', 'dailyReturnReinv', 'turn_rate', 'marketValue']].dropna()
    stock_return['dailyReturnReinv'] /= 100.
    stock_return['marketValue'] = np.log(stock_return['marketValue'])
    # 计算
    window = 20
    print("==============================开始计算==============================")
    for trade_date in date_list:
        period_start = trading_day_list[trading_day_list.index(trade_date) - window]
        period_data = stock_return[
            (stock_return['trade_date'] >= period_start) & (stock_return['trade_date'] <= trade_date)]
        count_series = period_data['ticker'].value_counts()
        # filter
        include_list = count_series[count_series.gt(window)].index.tolist()
        period_data = period_data[period_data['ticker'].isin(include_list)]
        period_data.sort_values(by=['ticker', 'trade_date'], inplace=True)
        period_data['to_change'] = period_data.groupby('ticker')['turn_rate'].pct_change()
        period_data.dropna(inplace=True)
        merged_df = period_data.groupby('ticker')['turn_rate'].std().to_frame('STR_Bf').merge(
            period_data.groupby('ticker')['to_change'].std().to_frame('GTR_Bf'), left_index=True, right_index=True
        ).merge(period_data[period_data['trade_date'] == trade_date].set_index(
            'ticker')[['marketValue']], left_index=True, right_index=True)
        # 市值中性化
        y = merged_df['STR_Bf']
        x_ = sm.add_constant(merged_df['marketValue'])
        model = sm.OLS(y, x_,)
        results = model.fit()
        merged_df['STR_Af'] = results.resid

        y = merged_df['GTR_Bf']
        model = sm.OLS(y, x_,)
        results = model.fit()
        merged_df['GTR_Af'] = results.resid

        del merged_df['marketValue']
        merged_df.reset_index(inplace=True)

        print("计算日期: {}， 有因子的个股数目: {}".format(trade_date, merged_df.shape[0]))

        merged_df.to_csv("D:\\AlphaBase\\换手率因子\\{}.csv".format(trade_date), index=False)


def factor_preprocess(date_list):
    path = 'D:\\AlphaBase\\特质波动率因子'
    if date_list is None:
        listdir = os.listdir(path)
        date_list = sorted([x.split('.')[0] for x in listdir])
    raw_factor = []
    processed_factor = []
    for trade_date in tqdm(date_list):
        ivr = pd.read_csv(os.path.join(path, '{}.csv'.format(trade_date)))
        ivr['ticker'] = ivr['ticker'].apply(lambda x: str(x).zfill(6))

        m_reverse = pd.read_csv("D:\\AlphaBase\\M-反转因子\\{}.csv".format(trade_date))
        m_reverse['ticker'] = m_reverse['ticker'].apply(lambda x: str(x).zfill(6))

        str_gtr = pd.read_csv("D:\\AlphaBase\\换手率因子\\{}.csv".format(trade_date))
        str_gtr['ticker'] = str_gtr['ticker'].apply(lambda x: str(x).zfill(6))
        # 合成STR_Turbo（先去极值）
        median = str_gtr[['STR_Af', 'GTR_Af']].median()
        new_median = abs(str_gtr[['STR_Af', 'GTR_Af']] - median).median()
        up = median + 5 * new_median
        down = median - 5 * new_median
        win_df = str_gtr[['STR_Af', 'GTR_Af']].clip(down, up, axis=1)
        scaler = MinMaxScaler()
        win_df = (win_df - win_df.mean()) / win_df.std()
        win_df -= win_df.min()
        win_df['STR_Af'] = scaler.fit_transform(win_df[['STR_Af']])
        win_df['GTR_Af'] = scaler.fit_transform(win_df[['GTR_Af']])
        str_gtr['STR_Turbo'] = win_df.sum(axis=1)

        umr_momentum = pd.read_csv("D:\\AlphaBase\\umr动量因子\\{}.csv".format(trade_date))
        umr_momentum['ticker'] = umr_momentum['ticker'].apply(lambda x: str(x).zfill(6))
        umr_momentum['umr'] *= -1

        t_df = ivr.merge(m_reverse, on='ticker').merge(str_gtr, on='ticker').merge(
            umr_momentum, on='ticker').set_index('ticker')
        t_df.eval("M_reverse = M_high - M_low", inplace=True)
        cols = ['ivr', 'STR_Af', 'GTR_Af', 'STR_Turbo', 'M_reverse', 'umr']
        # t_df = ivr.merge(m_reverse, on='ticker').merge(str_gtr, on='ticker').set_index('ticker')
        # t_df.eval("M_reverse = M_high - M_low", inplace=True)
        # cols = ['ivr', 'STR_Af', 'GTR_Af', 'STR_Turbo', 'M_reverse']

        # universe(线上)
        # sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(trade_date)
        # res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        # style_factor = pd.DataFrame(res['data'])
        # include_cols = style_names + [x.lower() for x in list(industry_name['sw'].values())]
        # style_factor = style_factor.set_index('ticker')[include_cols].applymap(float)
        # universe(本地)
        style_factor = pd.read_csv(
            "D:\\kevin\\risk_model_jy\\RiskModel\\data\\zzqz_sw\\style_factor\\{}.csv".format(trade_date))
        style_factor['ticker'] = style_factor['ticker'].apply(lambda x: str(x).zfill(6))
        include_cols = style_names + list(industry_name['sw'].values())
        style_factor = style_factor.set_index('ticker')[include_cols].applymap(float)
        idx = set(t_df.index).intersection(set(style_factor.index))
        t_df = t_df.reindex(idx)[cols]
        # 去极值
        median = t_df.median()
        new_median = abs(t_df - median).median()
        up = median + 5 * new_median
        down = median - 5 * new_median
        t_df = t_df.clip(down, up, axis=1)
        # 中性化
        t_df = t_df.merge(style_factor, on='ticker')
        # include_cols_wo_size = [x for x in include_cols if x != 'size']
        # x1 = sm.add_constant(np.array(t_df[include_cols]))
        # model = sm.OLS(t_df[cols], x1, ).fit()
        # t_df_neu_1 = model.resid
        # x2 = sm.add_constant(np.array(t_df[include_cols_wo_size]))
        # model = sm.OLS(t_df[cols], x2, ).fit()
        # t_df_neu_2 = model.resid
        # t_df_neu = pd.concat([t_df_neu_1[['ivr', 'M_reverse']], t_df_neu_2[['STR_Af', 'GTR_Af', 'STR_Turbo']]], axis=1)
        x = np.array(t_df[include_cols])
        model = sm.OLS(t_df[cols], x).fit()
        t_df_neu = model.resid
        # 标准化
        t_df_std = (t_df_neu - t_df_neu.mean()) / t_df_neu.std()
        # 原始因子
        t_df = (t_df - t_df.mean()) / t_df.std()
        t_df = t_df[cols]
        t_df['combine'] = t_df[['ivr', 'STR_Turbo', 'M_reverse', 'umr']].mean(axis=1)
        rf = t_df.reset_index()
        rf['trade_date'] = trade_date
        raw_factor.append(rf)
        # 纯净因子
        t_df_std['combine'] = t_df_std[['ivr', 'STR_Turbo', 'M_reverse', 'umr']].mean(axis=1)
        pf = t_df_std.reset_index()
        pf['trade_date'] = trade_date
        processed_factor.append(pf)

        cols = [x for x in rf.columns if x != 'trade_date']
        rf[cols].to_csv('D:\\AlphaBase\\raw_factor\\{}.csv'.format(trade_date), index=False)
        pf[cols].to_csv('D:\\AlphaBase\\processed_factor\\{}.csv'.format(trade_date), index=False)

    raw_factor = pd.concat(raw_factor)
    processed_factor = pd.concat(processed_factor)

    return raw_factor, processed_factor


def cal_factor_ic(factor_df):
    # 读取行情数据
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    data.eval("turn_rate = turnoverValue / negMarketValue", inplace=True)
    stock_return = data[['trade_date', 'ticker', 'dailyReturnReinv']].dropna()
    stock_return['dailyReturnReinv'] /= 100.
    stock_return = pd.pivot_table(
        stock_return, index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index()

    factor_dates = sorted(factor_df['trade_date'].unique())
    trading_day_list = get_trading_day_list(factor_dates[0], factor_dates[-1], 'day')
    ic_list = []
    factor_cols = ['ivr', 'STR_Af', 'GTR_Af', 'STR_Turbo', 'M_reverse', 'umr', 'combine']
    include_cols = factor_cols + style_names
    # include_cols = [x for x in factor_df.columns if x not in ['ticker', 'trade_date']]
    corr_df = pd.DataFrame(index=include_cols, columns=include_cols).fillna(0.)
    cl = []
    window = 5
    for date in tqdm(factor_dates[:-1]):
        t_df = factor_df[factor_df['trade_date'] == date].set_index('ticker')[factor_cols]
        future_days = trading_day_list[trading_day_list.index(date) + 1: trading_day_list.index(date) + window + 1]
        future_ret = stock_return.loc[future_days].dropna(axis=1)
        # intersection
        idx = set(t_df.index).intersection(set(future_ret.columns))
        t_df = t_df.reindex(idx)
        future_ret = future_ret.T.reindex(idx).T
        future_ret = (1 + future_ret).prod() - 1
        t_df = t_df.merge(future_ret.to_frame('future_ret'), left_index=True, right_index=True)
        # 风格
        # sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
        # res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        # style_factor = pd.DataFrame(res['data']).set_index('ticker')[style_names]
        style_factor = pd.read_csv(
            "D:\\kevin\\risk_model_jy\\RiskModel\\data\\zzqz_sw\\style_factor\\{}.csv".format(date))
        style_factor['ticker'] = style_factor['ticker'].apply(lambda x: str(x).zfill(6))
        style_factor = style_factor.set_index('ticker')[style_names]
        t_df = t_df.merge(style_factor, left_index=True, right_index=True)
        # 测试一下combine因子在市值、波动率上的分组分布
        test_df = t_df.copy()
        test_df['f_type'] = pd.qcut(t_df['combine'], q=10, labels=False)
        # a = test_df.groupby('f_type')[['size', 'resvol', 'liquidity', 'sizenl']].mean()
        cl.append(t_df.corr('spearman').loc["combine"].to_frame(date))

        corr_series = t_df.corr('spearman').loc[factor_cols, 'future_ret']
        ic_list.append(corr_series.to_frame(date))
        corr_df += t_df.corr('spearman').loc[include_cols, include_cols]

    ic_df = pd.concat(ic_list, axis=1)
    ir = (ic_df.mean(axis=1) / ic_df.std(axis=1)) * 2
    corr_df /= len(factor_dates) - 1

    return ic_df, ir


def cal_factor_group_ret(factor_df):
    # 读取行情数据
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    data.eval("turn_rate = turnoverValue / negMarketValue", inplace=True)
    stock_return = data[['trade_date', 'ticker', 'dailyReturnReinv']].dropna()
    stock_return['dailyReturnReinv'] /= 100.
    stock_return = pd.pivot_table(
        stock_return, index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index()
    factor_dates = sorted(factor_df['trade_date'].unique())
    include_cols = [x for x in factor_df.columns if x not in ['ticker', 'trade_date']]
    group_ret_all = []
    for i in tqdm(range(1, len(factor_dates))):
        t_date, n_date = factor_dates[i - 1], factor_dates[i]
        t_df = factor_df[factor_df['trade_date'] == t_date].set_index('ticker')[include_cols]
        period_ret = stock_return.loc[t_date: n_date].dropna(axis=1)[1:]
        # intersection
        idx = set(t_df.index).intersection(set(period_ret.columns))
        t_df = t_df.reindex(idx)
        period_ret = period_ret.T.reindex(idx).T
        period_ret = (1 + period_ret).cumprod()
        # 核心
        group_df = t_df.apply(lambda x: pd.qcut(x, q=10, labels=False, duplicates='drop'), axis=0) + 1
        group_ret_period = []
        for col in group_df.columns:
            tmp = group_df[[col]].merge(period_ret.T, left_index=True, right_index=True)
            group_ret = tmp.groupby(col)[period_ret.index].mean().T
            group_ret.loc[t_date] = 1.
            group_ret = group_ret.sort_index().pct_change().dropna()
            group_ret.columns = ['{}-G{}'.format(col, x) for x in group_ret.columns]
            group_ret_period.append(group_ret)
        group_ret_period = pd.concat(group_ret_period, axis=1)
        group_ret_all.append(group_ret_period)

    group_ret_all = pd.concat(group_ret_all).sort_index()
    nav_df = (1 + group_ret_all).cumprod()
    nav_df.loc[factor_dates[0]] = 1.
    nav_df = nav_df.sort_index()
    return_df = []
    for col in include_cols:
        selected_cols = [x for x in nav_df.columns if col in x]
        annual_return = nav_df[selected_cols].iloc[-1] ** (252 / (len(nav_df) - 1)) - 1
        annual_return = annual_return.to_frame('年化收益')
        annual_return['tmp'] = annual_return.index
        annual_return[['因子', '组别']] = annual_return['tmp'].str.split('-', expand=True)
        annual_return = pd.pivot_table(annual_return, index='组别', columns='因子', values='年化收益')
        annual_return = annual_return.reindex(['G{}'.format(x) for x in range(1, 11)])
        return_df.append(annual_return)

    return_df = pd.concat(return_df, axis=1)

    return return_df


def load_shift_date(trade_date):
    trade_dt = datetime.datetime.strptime(trade_date, '%Y%m%d')
    pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

    sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM st_main.t_st_gg_jyrl WHERE JYRQ > {} and JYRQ < {}".format(
        pre_date, trade_date)
    res = hbs.db_data_query('alluser', sql_script, page_size=5000)
    df = pd.DataFrame(res['data']).rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
    df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
    df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

    trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

    return trading_day_list[-1]


def load_benchmark_weight_series(date, benchmark_id):
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
        benchmark_id)
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code = index_info.set_index('SECUCODE').loc[benchmark_id, 'INNERCODE']

    sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                 "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                 "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
    data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
    weight_df = data.rename(
        columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})

    return weight_df.set_index('consTickerSymbol')['weight'] / 100.


def prepare_weekly_benchmark(start_date, end_date, benchmark_id):
    """
    手动计算周度的基准权重
    """
    week_list = get_trading_day_list(start_date, end_date, "week")
    # 读取行情数据
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if start_date <= x.split('_')[-1].split('.')[0] <= end_date]
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    stock_return = data[['trade_date', 'ticker', 'dailyReturnReinv', 'turnoverValue']].dropna()
    stock_return['turnoverValue'] /= 10000.
    stock_return['dailyReturnReinv'] /= 100.
    stock_return = pd.pivot_table(
        stock_return, index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index()
    bm_name = '中证500' if benchmark_id == "000905" else "中证1000"
    for reb_date in tqdm(week_list):
        shift_date = load_shift_date(reb_date)
        benchmark_weight = load_benchmark_weight_series(shift_date, benchmark_id)
        if shift_date == reb_date:
            weight_df = benchmark_weight.reset_index().rename(columns={"consTickerSymbol": "ticker"})
        else:
            period_ret = stock_return.loc[shift_date: reb_date].copy()
            period_ret = period_ret.T.reindex(benchmark_weight.index).T.fillna(0.)
            period_ret.loc[shift_date] = 0.
            period_ret = (1 + period_ret).cumprod()
            benchmark_weight = benchmark_weight.multiply(period_ret)
            benchmark_weight = benchmark_weight.div(benchmark_weight.sum(axis=1), axis=0).loc[reb_date]
            weight_df = benchmark_weight.reset_index().rename(
                columns={"consTickerSymbol": "ticker", reb_date: "weight"})
        # assert (weight_df.shape == (1000, 2))
        weight_df.to_csv('D:\\AlphaBase\\周度基准权重\\{0}_{1}.csv'.format(bm_name, reb_date), index=False)


class PortfolioRiskPredict:
    """
    带有估值表的500指增产品的组合风险预测 + 市值敞口记录
    """
    def __init__(self, trade_date, benchmark_id="000905"):
        self.trade_date = trade_date
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_shift_date(self):
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM st_main.t_st_gg_jyrl WHERE JYRQ > {} and JYRQ < {}".format(
            pre_date, self.trade_date)
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    def _load_portfolio_weight(self):
        sql_script = "SELECT * FROM private_fund_holding where trade_date = {} and fund_type = '500指增'".format(
            self.trade_date)
        engine = create_engine(engine_params)
        holding_df = pd.read_sql(sql_script, engine)
        holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        # 剔除总仓位在0.9以下的标的
        weight_sum = holding_df.groupby('fund_name')['weight'].sum()
        selected_list = weight_sum[weight_sum > 90.].index.tolist()
        holding_df = holding_df[holding_df['fund_name'].isin(selected_list)]
        # format
        weight_df = pd.pivot_table(
            holding_df, index='ticker', columns='fund_name', values='weight').sort_index().fillna(0.) / 100.

        return weight_df

    def _load_benchmark_weight_series(self, date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            self.benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[self.benchmark_id, 'INNERCODE']

        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})

        return weight_df.set_index('consTickerSymbol')['weight'] / 100.

    @staticmethod
    def _load_style_exposure(date):
        sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
        exposure_df = fetch_data_batch_hbs(sql_script, "alluser").set_index('ticker')
        ind_names = [x.lower() for x in industry_name['sw'].values()]
        exposure_df = exposure_df[style_name + ind_names + ['country']]

        return exposure_df

    @staticmethod
    def _load_factor_cov(date):
        sql_script = "SELECT * FROM st_ashare.r_st_barra_factor_cov where TRADE_DATE = '{}'".format(date)
        factor_cov = fetch_data_batch_hbs(sql_script, "alluser")
        factor_cov['factor_name'] = factor_cov['factor_name'].apply(lambda x: x.lower())
        ind_names = [x.lower() for x in industry_name['sw'].values()]
        factor_list = style_name + ind_names + ['country']
        factor_cov = factor_cov.set_index('factor_name').reindex(factor_list)[factor_list]

        return factor_cov

    @staticmethod
    def _load_srisk(date):
        sql_script = "SELECT * FROM st_ashare.r_st_barra_s_risk where TRADE_DATE = '{}'".format(date)
        srisk = fetch_data_batch_hbs(sql_script, "alluser").set_index('ticker')
        srisk.rename(columns={"s_ret": "srisk"}, inplace=True)

        return srisk[['srisk']]

    def _load_data(self):
        shift_date = self._load_shift_date()
        self.portfolio_weight_df = self._load_portfolio_weight()
        self.benchmark_weight_series = self._load_benchmark_weight_series(shift_date)
        self.exposure_df = self._load_style_exposure(shift_date)
        self.factor_cov = self._load_factor_cov(shift_date)
        self.srisk = self._load_srisk(shift_date)


    def run(self):
        weight_df = self.portfolio_weight_df.merge(self.benchmark_weight_series.to_frame('benchmark'),
                                                   left_index=True, right_index=True, how='outer').fillna(0.)
        cols = weight_df.columns[:-1]
        for col in cols:
            weight_df[col] -= weight_df['benchmark'] * weight_df[col].sum()
        weight_df = weight_df[weight_df.columns[:-1]]
        exposure_df = self.exposure_df.astype(float)
        factor_cov = self.factor_cov.divide(12 * 10000)
        srisk = self.srisk ** 2 * 21
        idx = set(weight_df.index).intersection(set(exposure_df.index)).intersection(set(srisk.index))

        weight = weight_df.reindex(idx)
        exposure_df = exposure_df.reindex(idx)
        srisk = srisk.reindex(idx)['srisk']

        size_exposure = weight.T.dot(exposure_df)['size']
        common_risk = np.mat(weight).T.dot(
            np.mat(exposure_df).dot(np.mat(factor_cov)).dot(np.mat(exposure_df).T)).dot(np.mat(weight))
        specific_risk = np.mat(weight).T.dot(np.diag(srisk)).dot(np.mat(weight))

        risk_df = pd.DataFrame({"fund_name": weight.columns, "common_risk": np.diag(common_risk),
                                "srisk": np.diag(specific_risk)}).set_index('fund_name')
        risk_df['预期年化波动'] = np.sqrt(risk_df['common_risk'] + risk_df['srisk']) * np.sqrt(12)
        # print("{}_{}：预期风险: {}, 实际风险: {}".format(self.fund_name, self.trade_date, risk, actual_risk))

        risk_df = size_exposure.round(3).to_frame('市值敞口').merge(risk_df, left_index=True, right_index=True)
        risk_df['预期年化波动'] = risk_df['预期年化波动'].apply(lambda x: format(x, '.2%'))

        return risk_df[['市值敞口', '预期年化波动']]


def cal_weekly_ls_ret(factor_path, start_date):
    # 读取行情数据
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if start_date <= x.split('_')[-1].split('.')[0]]
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    data.eval("turn_rate = turnoverValue / negMarketValue", inplace=True)
    stock_return = data[['trade_date', 'ticker', 'dailyReturnReinv']].dropna()
    stock_return['dailyReturnReinv'] /= 100.
    stock_return = pd.pivot_table(
        stock_return, index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index()
    # 因子数据
    listdir = os.listdir(factor_path)
    listdir = [x for x in listdir if start_date <= x.split('_')[-1].split('.')[0]]
    data = []
    for filename in tqdm(listdir):
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(factor_path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    factor_df = pd.concat(data)
    # 多空收益计算
    factor_dates = sorted(factor_df['trade_date'].unique())
    include_cols = ['ivr', 'STR_Turbo', 'M_reverse', 'umr', 'combine']
    group_ret_all = []
    for i in tqdm(range(1, len(factor_dates))):
        t_date, n_date = factor_dates[i - 1], factor_dates[i]
        t_df = factor_df[factor_df['trade_date'] == t_date].set_index('ticker')[include_cols]
        period_ret = stock_return.loc[t_date: n_date].dropna(axis=1)[1:]
        # intersection
        idx = set(t_df.index).intersection(set(period_ret.columns))
        t_df = t_df.reindex(idx)
        period_ret = period_ret.T.reindex(idx).T
        period_ret = (1 + period_ret).cumprod()
        # 核心
        group_df = t_df.apply(lambda x: pd.qcut(x, q=10, labels=False, duplicates='drop'), axis=0) + 1
        group_ret_period = []
        for col in group_df.columns:
            tmp = group_df[[col]].merge(period_ret.T, left_index=True, right_index=True)
            group_ret = tmp.groupby(col)[period_ret.index].mean().T
            group_ret.loc[t_date] = 1.
            group_ret = group_ret.sort_index().pct_change().dropna()
            group_ret.columns = ['G{}'.format(x) for x in group_ret.columns]
            group_ret[col] = group_ret['G1'] - group_ret.mean(axis=1)
            # group_ret[col] = group_ret['G1'] - group_ret['G10']
            group_ret_period.append(group_ret[[col]])
        group_ret_period = pd.concat(group_ret_period, axis=1)
        group_ret_all.append(group_ret_period)

    group_ret_all = pd.concat(group_ret_all).sort_index()
    nav_df = (1 + group_ret_all).cumprod()
    nav_df.loc[factor_dates[0]] = 1.
    nav_df = nav_df.sort_index()

    nav_df['trade_date'] = nav_df.index
    nav_df['trade_date'] = nav_df['trade_date'].apply(
        lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    nav_df.set_index('trade_date', inplace=True)

    return nav_df


def weekly_update(trade_date, mode="update"):
    if mode == "update":
        # 周度更新dealAmount
        save_dealAmount_data_to_csv()
        # 更新因子
        cal_ivff_factor(trade_date, trade_date)
        cal_M_reverse_factor(trade_date, trade_date)
        cal_STR_and_GTR_factor(trade_date, trade_date)
        r_df = true_range_extractor(trade_date, 60, 10)
        _ = UMROperator(trade_date, r_df).run()
        # 因子处理
        r_factor, p_factor = factor_preprocess([trade_date])
        cols = [x for x in r_factor.columns if x != 'trade_date']
        r_factor[cols].to_csv('D:\\AlphaBase\\raw_factor\\{}.csv'.format(trade_date), index=False)
        p_factor[cols].to_csv('D:\\AlphaBase\\processed_factor\\{}.csv'.format(trade_date), index=False)
    # 周度基准
    prepare_weekly_benchmark(trade_date, trade_date, '000905')
    prepare_weekly_benchmark(trade_date, trade_date, '000852')
    # 分组回测 - 今年以来
    nav_df_raw = cal_weekly_ls_ret("D:\\AlphaBase\\raw_factor", "20211231")
    nav_df_p = cal_weekly_ls_ret("D:\\AlphaBase\\processed_factor", "20211231")

    excel_writer = pd.ExcelWriter('D:\\AlphaBase\\因子分组收益-周度.xlsx'.format(trade_date), engine='openpyxl')
    nav_df_raw.to_excel(excel_writer, sheet_name='原始因子')
    nav_df_p.to_excel(excel_writer, sheet_name='中性化因子')
    excel_writer.close()


def portfolio_test(start_date, end_date, benchmark_id):
    """
    优化组合回测函数
    :param start_date:
    :param end_date:
    :param benchmark_id:
    :return:
    """
    data_path = "D:\\AlphaBase\\opt_results\\原始因子1000指增组合权重"
    weight_dir = os.listdir(data_path)
    weight_dir = [x for x in weight_dir if start_date <= x.split('.')[0] <= end_date]
    reb_dates = [x.split('.')[0] for x in weight_dir]
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="day")
    price_path = "D:\\AlphaBase\\价格数据"
    price_dir = os.listdir(price_path)
    port_return = pd.Series(index=trading_day_list, data=np.NaN)
    port_return.loc[start_date] = 0.
    status_df = pd.DataFrame(index=reb_dates, columns=['days', 'turnover'])
    for i in tqdm(range(1, len(reb_dates))):
        t_date, n_date = reb_dates[i - 1], reb_dates[i]
        if i != len(reb_dates) - 1:
            n_date = trading_day_list[trading_day_list.index(n_date) + 1]
        t_weight = pd.read_csv(os.path.join(data_path, '{}.csv'.format(t_date)), dtype={"ticker": str})
        t_weight = t_weight[t_weight['ticker'] != "cash"]
        filenames = [x for x in price_dir if t_date < x.split('.')[0] <= n_date]
        period_data = []
        for filename in filenames:
            t_data = pd.read_csv(os.path.join(price_path, filename), dtype={"tradeDate": str, "ticker": str})
            period_data.append(t_data)
        period_df = pd.concat(period_data)
        period_df = period_df[period_df['ticker'].isin(t_weight['ticker'].tolist())]
        period_df['ret_c2c'] = period_df['TCLOSE'] / period_df['LCLOSE'] - 1
        period_df['ret_c2o'] = period_df['TCLOSE'] / period_df['TOPEN'] - 1
        period_df['ret_o2c'] = period_df['TOPEN'] / period_df['LCLOSE'] - 1
        first_date = trading_day_list[trading_day_list.index(t_date) + 1]
        period_df['ret'] = period_df['ret_c2c']
        period_df.loc[period_df['tradeDate'] == first_date, 'ret'] = (
            period_df.loc)[period_df['tradeDate'] == first_date, 'ret_c2o']
        period_df.loc[period_df['tradeDate'] == n_date, 'ret'] = (
            period_df.loc)[period_df['tradeDate'] == n_date, 'ret_o2c']
        # NaN
        period_df.loc[period_df['turnoverValue'] < 1e-8, 'ret'] = np.NaN
        ret_df = pd.pivot_table(period_df, index='tradeDate', columns='ticker', values='ret').sort_index().fillna(0.)
        stock_nav = (1 + ret_df).cumprod()
        stock_nav.loc[t_date] = 1.
        stock_nav.sort_index(inplace=True)
        # intersection
        stock_nav = stock_nav.T.reindex(t_weight['ticker']).T.fillna(1.)
        t_weight = t_weight.set_index('ticker')
        # mul
        weight_df = stock_nav.multiply(t_weight['weight'])
        period_ret = weight_df.sum(axis=1).pct_change().dropna()
        if i == 1:
            port_return.loc[period_ret.index] = period_ret
        else:
            port_return.loc[first_date] = (1 + port_return.loc[first_date]) * (1 + period_ret.loc[first_date]) - 1
            period_ret = period_ret[1:]
            port_return.loc[period_ret.index] = period_ret
        # weight compare
        next_date = reb_dates[i]
        next_weight = pd.read_csv(os.path.join(data_path, '{}.csv'.format(next_date)), dtype={"ticker": str})
        next_weight = next_weight[next_weight['ticker'] != "cash"]
        weight_bf = weight_df.loc[n_date].to_frame('before')
        weight_bf /= weight_bf.sum()
        compare_df = weight_bf.merge(
            next_weight.set_index('ticker')['weight'].to_frame('after'),
            left_index=True, right_index=True, how='outer').fillna(0.)
        compare_df['delta'] = (compare_df['before'] - compare_df['after']).abs()

        status_df.loc[next_date, 'days'] = period_ret.shape[0]
        status_df.loc[next_date, 'turnover'] = compare_df['delta'].sum()
        # 添加交易成本
        port_return.loc[n_date] = (1 + port_return.loc[n_date]) * (1 - compare_df['delta'].sum() * 0.0015) - 1

    status_df = status_df.dropna()
    status_df['ave_to'] = status_df['turnover'] / status_df['days']

    # 超额
    sql_script = ("SELECT JYRQ as TRADEDATE, SPJG as TCLOSE FROM st_market.t_st_zs_hq WHERE "
                  "ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}").format(benchmark_id, start_date, end_date)
    index_data = pd.DataFrame(hbs.db_data_query('alluser', sql_script, page_size=5000)['data'])
    index_data['TRADEDATE'] = index_data['TRADEDATE'].map(str)
    index_data.sort_values(by='TRADEDATE', inplace=True)
    index_data = index_data.set_index('TRADEDATE')['TCLOSE']
    index_nav = index_data.reindex(port_return.index).to_frame('benchmark')

    port_df = port_return.to_frame('port').merge(
        index_nav.pct_change().fillna(0.), left_index=True, right_index=True)
    port_df.eval("excess = port - benchmark", inplace=True)

    return port_df


if __name__ == '__main__':
    "==========================================数据=========================================="
    # save_mkt_data_to_csv('20211231', '20230720')
    # save_price_data_to_csv("20150105", "20230821")
    # check_mkt_data()
    "=========================================因子计算========================================="
    # cal_illiq_factor('20191120', '20221130')
    # cal_ivff_factor('20211231', '20230714')
    # cal_M_reverse_factor('20211231', '20230714')
    # cal_STR_and_GTR_factor('20211231', '20230714')
    "=======================================因子统一处理======================================="
    # r_factor, p_factor = factor_preprocess(None)
    # r_factor.to_csv('D:\\AlphaBase\\raw_factor.csv', index=False)
    # p_factor.to_csv('D:\\AlphaBase\\processed_factor.csv', index=False)
    "=====================================因子ic测试&分组测试======================================"
    # 原始因子测试
    # raw_factor_outer = pd.read_csv('D:\\AlphaBase\\raw_factor.csv', dtype={"trade_date": str})
    # raw_factor_outer['ticker'] = raw_factor_outer['ticker'].apply(lambda x: str(x).zfill(6))
    # ic_raw, ir_raw = cal_factor_ic(raw_factor_outer)
    # quantile_nav = cal_factor_group_ret(raw_factor_outer)
    # 纯净因子测试
    # processed_factor_outer = pd.read_csv('D:\\AlphaBase\\processed_factor.csv', dtype={"trade_date": str})
    # processed_factor_outer['ticker'] = processed_factor_outer['ticker'].apply(lambda x: str(x).zfill(6))
    # ic_pro, ir_pro = cal_factor_ic(processed_factor_outer)
    # quantile_nav = cal_factor_group_ret(processed_factor_outer)
    "=======================================优化======================================="
    # 准备周度的基准
    # prepare_weekly_benchmark("20211231", "20230512", '000852')

    # PortfolioRiskPredict('20230930').run()
    "=======================================因子更新======================================="
    weekly_update("20231229", "update")
    # portfolio_test("20221230", "20231229", "000852")