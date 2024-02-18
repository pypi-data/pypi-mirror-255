import hbshare as hbs
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import fetch_data_batch_hbs, get_trading_day_list
from tqdm import tqdm
from WindPy import w

w.start()


def get_price_data_from_Wind(start_date, end_date, ticker_list):
    w_list = ','.join([x + '.SH' if x[0] == '6' else x + '.SZ' for x in ticker_list])
    start_date = datetime.strptime(start_date, "%Y%m%d").strftime("%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y%m%d").strftime("%Y-%m-%d")
    # 收盘价
    res = w.wsd(w_list, "close", start_date, end_date, "")
    close_price = pd.DataFrame(index=res.Codes, columns=res.Times, data=res.Data).T.sort_index()
    # 开盘价
    res = w.wsd(w_list, "open", start_date, end_date, "")
    open_price = pd.DataFrame(index=res.Codes, columns=res.Times, data=res.Data).T.sort_index()
    assert (close_price.columns.tolist() == open_price.columns.tolist())
    # 复权因子
    res = w.wsd(w_list, "adjfactor", start_date, end_date, "")
    adj_factor = pd.DataFrame(index=res.Codes, columns=res.Times, data=res.Data).T.sort_index()
    # 整合
    close_price = close_price * adj_factor
    open_price = open_price * adj_factor
    close_price.iloc[0] = open_price.iloc[1]
    return_df = close_price.pct_change().fillna(0.)
    return_df['trade_date'] = return_df.index
    return_df['trade_date'] = return_df['trade_date'].apply(lambda x: x.strftime("%Y%m%d"))
    return_df = return_df.set_index('trade_date')

    return return_df


def get_price_data_from_db(start_date, end_date, ticker_list):
    sql_script = "SELECT SYMBOL, TDATE, LCLOSE, TOPEN, TCLOSE FROM finchina.CHDQUOTE WHERE " \
                 "SYMBOL in ({}) and TDATE > {} " \
                 "and TDATE <= {}".format(','.join("'{0}'".format(x) for x in ticker_list), start_date, end_date)
    data = fetch_data_batch_hbs(sql_script, "readonly")
    data['TDATE'] = data['TDATE'].map(str)
    data['d_ret'] = data['TCLOSE'] / data['LCLOSE'] - 1
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="day")
    first_date = sorted(trading_day_list)[1]
    data.loc[data['TDATE'] == first_date, 'd_ret'] = data['TCLOSE'] / data['TOPEN'] - 1
    return_df = pd.pivot_table(data, index='TDATE', columns='SYMBOL', values='d_ret').sort_index()
    return_df.loc[start_date] = 0.
    return_df.sort_index(inplace=True)

    return return_df


class BigMomStrategy:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def _load_data(trade_date, pre_date):
        # 所需数据: 收盘价、总市值、股息率、PEG
        sql_script = "SELECT SYMBOL, TDATE, TCLOSE, TCAP FROM finchina.CHDQUOTE WHERE" \
                     " TDATE = {}".format(trade_date)
        df = fetch_data_batch_hbs(sql_script, "readonly")
        df = df[df['SYMBOL'].str[0].isin(['0', '3', '6'])]
        df.rename(columns={"SYMBOL": "ticker", "TDATE": "trade_date",
                           "TCAP": "marketValue", "TCLOSE": "close_price"}, inplace=True)
        # 剔除ST、停牌、涨跌停的个股，剔除上市不满3个月的新股
        univ = pd.read_csv('D:\\kevin\\risk_model_jy\\RiskModel\\data\\common_data\\univ\\zzqz\\{}.csv'.format(
            pre_date), index_col=0)
        univ['ticker'] = univ.index
        univ['ticker'] = univ['ticker'].apply(lambda x: str(x).zfill(6))
        universe = univ['ticker'].tolist()
        # 股息率、PETTM
        sql_script = "SELECT a.SecuCode, b.TradingDay, b.DividendRatio, b.PE FROM " \
                     "hsjy_gg.LC_DIndicesForValuation b join hsjy_gg.SecuMain a on " \
                     "a.InnerCode = b.InnerCode where a.SecuCategory = 1 and " \
                     "a.SecuMarket in (83, 90) and to_char(b.TradingDay,'yyyymmdd') = '{}'".format(trade_date)
        fin_data_main = fetch_data_batch_hbs(sql_script)
        sql_script = "SELECT a.SecuCode, b.TradingDay, b.DividendRatioTTM, b.PETTM FROM " \
                     "hsjy_gg.LC_STIBDIndiForValue b join hsjy_gg.SecuMain a on " \
                     "a.InnerCode = b.InnerCode where a.SecuCategory = 1 and " \
                     "a.SecuMarket in (83, 90) and to_char(b.TradingDay,'yyyymmdd') = '{}'".format(trade_date)
        res = hbs.db_data_query("readonly", sql_script, page_size=500)
        fin_data_stib = pd.DataFrame(res['data'])
        fin_data_stib.rename(columns={"DIVIDENDRATIOTTM": "DIVIDENDRATIO", "PETTM": "PE"}, inplace=True)
        fin_data = pd.concat([fin_data_main, fin_data_stib])
        fin_data.rename(columns={"SECUCODE": "ticker"}, inplace=True)
        # 净利润同比增速
        trade_dt = datetime.strptime(trade_date, '%Y%m%d')
        pre_date = (trade_dt - timedelta(days=360)).strftime('%Y%m%d')
        # 单季度
        sql_script = "SELECT a.SecuCode, b.EndDate, b.InfoPublDate, b.NetProfitGrowRate FROM " \
                     "hsjy_gg.LC_QFinancialIndexNew b join hsjy_gg.SecuMain a on " \
                     "a.CompanyCode = b.CompanyCode where b.AccountingStandards = 1 and " \
                     "a.SecuMarket in (83, 90) and a.SecuCategory = 1 and " \
                     "to_char(b.InfoPublDate,'yyyymmdd') >= '{}' and " \
                     "to_char(b.InfoPublDate,'yyyymmdd') <= '{}'".format(pre_date, trade_date)
        # 合并
        # sql_script = "SELECT a.SecuCode, b.EndDate, b.InfoPublDate, b.NetProfitGrowRate FROM " \
        #              "hsjy_gg.LC_MainIndexNew b join hsjy_gg.SecuMain a on " \
        #              "a.CompanyCode = b.CompanyCode where " \
        #              "a.SecuMarket in (83, 90) and a.SecuCategory = 1 and " \
        #              "to_char(b.InfoPublDate,'yyyymmdd') >= '{}' and " \
        #              "to_char(b.InfoPublDate,'yyyymmdd') <= '{}'".format(pre_date, trade_date)
        growth_main = fetch_data_batch_hbs(sql_script)
        growth_main = growth_main[~growth_main['SECUCODE'].str[:2].isin(['68'])]
        # sql_script = "SELECT a.SecuCode, b.EndDate, b.InfoPublDate, b.NetProfitYOY FROM " \
        #              "hsjy_gg.LC_STIBMainIndex b join hsjy_gg.SecuMain a on " \
        #              "a.CompanyCode = b.CompanyCode where " \
        #              "a.SecuMarket in (83, 90) and a.SecuCategory = 1 and " \
        #              "to_char(b.InfoPublDate,'yyyymmdd') >= '{}' and " \
        #              "to_char(b.InfoPublDate,'yyyymmdd') <= '{}'".format(pre_date, trade_date)
        # growth_stib = fetch_data_batch_hbs(sql_script)
        # growth_stib.rename(columns={"NETPROFITYOY": "NETPROFITGROWRATE"}, inplace=True)
        # growth_stib = growth_stib[growth_stib['SECUCODE'].str[:2].isin(['68'])]
        # growth_data = pd.concat([growth_main, growth_stib])
        # growth_data.rename(columns={"SECUCODE": "ticker"}, inplace=True)
        # growth_data = growth_data[growth_data['ticker'].str[0].isin(['0', '3', '6'])]
        # 不包括科创板
        growth_data = growth_main.copy()
        growth_data.rename(columns={"SECUCODE": "ticker"}, inplace=True)
        growth_data = growth_data[growth_data['ticker'].str[0].isin(['0', '3', '6'])]
        # 序列化
        growth_data['publish_date'] = growth_data['INFOPUBLDATE'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d'))
        growth_data['report_date'] = growth_data['ENDDATE'].apply(
            lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d'))
        growth_data['latest_report_date'] = growth_data.groupby('ticker')['report_date'].transform('max')
        growth_data = growth_data[growth_data['report_date'] == growth_data['latest_report_date']].dropna().sort_values(
            by=['ticker', 'publish_date'])
        newest_data = growth_data.drop_duplicates(subset=['ticker', 'ENDDATE'], keep='last')
        # 整合数据
        processed_data = df[['ticker', 'marketValue', 'close_price']].merge(
            fin_data[['ticker', 'PE', 'DIVIDENDRATIO']], on='ticker').merge(
            newest_data[['ticker', 'NETPROFITGROWRATE']], on='ticker')
        processed_data['PEG'] = processed_data['PE'] / processed_data['NETPROFITGROWRATE']
        processed_data = processed_data[processed_data['ticker'].isin(universe)]

        return processed_data

    def select_stocks(self):
        reb_dates = get_trading_day_list(self.start_date, self.end_date, frequency="month")
        if self.end_date not in reb_dates:
            reb_dates.append(self.end_date)
        select_list = []
        for i in tqdm(range(len(reb_dates) - 1)):
            t_date = reb_dates[i]
            n_date = reb_dates[i + 1]
            df = self._load_data(t_date, t_date)
            # 股息率位于全市场前20%分位
            df = df[df['DIVIDENDRATIO'] >= df['DIVIDENDRATIO'].quantile(0.75)]
            # -1 < PEG < 3
            df = df[(df['PEG'] > -1) & (df['PEG'] < 3)]
            # 市值小于100亿
            df = df[df['marketValue'] <= 1e+10]
            # 股价位于【2，9】区间
            df = df[(df['close_price'] > 2) & (df['close_price'] < 9)]
            # 市值排序选前10
            df.sort_values(by='marketValue', inplace=True)
            df['reb_date'] = t_date
            df['next_date'] = n_date
            print("调仓日期: {}, 符合条件的个股数量={}".format(t_date, df.shape[0]))
            df['marketValue'] /= 1e+8
            select_list.append(df[['ticker', 'marketValue', 'reb_date', 'next_date']][:20])

        selected_df = pd.concat(select_list)

        return selected_df

    def update_portfolio(self, trade_date, pre_date):
        df = self._load_data(trade_date, pre_date)
        # 股息率位于全市场前20%分位
        df = df[df['DIVIDENDRATIO'] >= df['DIVIDENDRATIO'].quantile(0.75)]
        # -1 < PEG < 3
        df = df[(df['PEG'] > -1) & (df['PEG'] < 3)]
        # 市值小于100亿
        df = df[df['marketValue'] <= 1e+10]
        # 股价位于【2，9】区间
        df = df[(df['close_price'] > 2) & (df['close_price'] < 9)]
        # 市值排序选前10
        df.sort_values(by='marketValue', inplace=True)
        df['reb_date'] = trade_date
        print("调仓日期: {}, 符合条件的个股数量={}".format(trade_date, df.shape[0]))
        df['marketValue'] /= 1e+8
        selected_df = df[['ticker', 'marketValue', 'close_price']][:10]

        return selected_df


def save_30_minutes_data_to_csv(weight_df, start_date, end_date):
    reb_dates = sorted(weight_df['reb_date'].unique())
    reb_dates = [x for x in reb_dates if start_date <= x <= end_date]
    if end_date not in reb_dates:
        reb_dates.append(end_date)
    for i in range(len(reb_dates) - 1):
        t_date, n_date = reb_dates[i], reb_dates[i + 1]
        w_date1 = datetime.strptime(t_date, "%Y%m%d")
        w_date1 += timedelta(hours=9, minutes=30)
        w_date1 = w_date1.strftime("%Y-%m-%d %H:%M:%S")
        w_date2 = datetime.strptime(n_date, "%Y%m%d")
        w_date2 += timedelta(hours=14, minutes=30)
        w_date2 = w_date2.strftime("%Y-%m-%d %H:%M:%S")
        t_weight = weight_df.query("reb_date == @t_date").sort_values(by='marketValue')
        w_ticker = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in t_weight['ticker'].tolist()]
        res = w.wsi(','.join(w_ticker), "close,volume", w_date1, w_date2, "BarSize=30")
        minute_df = pd.DataFrame(index=res.Fields, columns=res.Times, data=res.Data).T
        minute_df['time'] = minute_df.index
        minute_df.reset_index(drop=True, inplace=True)
        minute_df['date'] = minute_df['time'].apply(lambda x: x.to_pydatetime().strftime("%Y%m%d"))
        minute_df['hm'] = minute_df['time'].apply(lambda x: x.to_pydatetime().strftime("%H:%M"))

        price_df = minute_df.query("hm == '14:00'").pivot_table(
            index="date", columns="windcode", values="close").sort_index()
        price_df.columns = [x.split('.')[0] for x in price_df.columns]
        print("选股日期: {}, 价格数据个股数量={}".format(t_date, price_df.shape[1]))
        price_df.to_csv('D:\\Strategy_Base\\price_data1\\{}.csv'.format(t_date))

        price_df = minute_df.query("hm == '14:30'").pivot_table(
            index="date", columns="windcode", values="close").sort_index()
        price_df.columns = [x.split('.')[0] for x in price_df.columns]
        print("选股日期: {}, 价格数据个股数量={}".format(t_date, price_df.shape[1]))
        price_df.to_csv('D:\\Strategy_Base\\price_data2\\{}.csv'.format(t_date))

        volume_df = minute_df[minute_df['hm'] != "15:00"].groupby(['windcode', 'date'])['volume'].sum().reset_index()
        volume_df = volume_df.pivot_table(index='date', columns='windcode', values='volume').sort_index()
        volume_df.columns = [x.split('.')[0] for x in volume_df.columns]
        print("选股日期: {}, 成交量数据个股数量={}".format(t_date, volume_df.shape[1]))
        volume_df.to_csv('D:\\Strategy_Base\\volume_data\\{}.csv'.format(t_date))


def calc_signal_matrix(weight_df, start_date, end_date, type="daily"):
    """
    计算日度信号矩阵
    """
    reb_dates = sorted(weight_df['reb_date'].unique())
    reb_dates = [x for x in reb_dates if start_date <= x <= end_date]
    # if end_date not in reb_dates:
    #     reb_dates.append(end_date)
    # loop
    ret_list = []
    for reb_date in tqdm(reb_dates):
        trade_dt = datetime.strptime(reb_date, '%Y%m%d')
        pre_date = (trade_dt - timedelta(days=30)).strftime('%Y%m%d')
        selected_df = weight_df.query("reb_date == @reb_date").sort_values(by='marketValue')
        ticker_list = selected_df['ticker'].tolist()
        period_end = selected_df['next_date'].unique()[0]
        # 市场数据-日度
        sql_script = "SELECT SYMBOL, TDATE, LCLOSE, TOPEN, TCLOSE, VOTURNOVER FROM finchina.CHDQUOTE WHERE " \
                     "SYMBOL in ({}) and TDATE > {} " \
                     "and TDATE <= {}".format(','.join("'{0}'".format(x) for x in ticker_list),
                                              pre_date, period_end)
        mkt_data = fetch_data_batch_hbs(sql_script, "readonly")
        mkt_data['TDATE'] = mkt_data['TDATE'].map(str)
        mkt_data.rename(columns={"SYMBOL": "ticker"}, inplace=True)
        # 成交量信号
        vol_df = pd.pivot_table(mkt_data, index='TDATE', columns='ticker', values='VOTURNOVER').sort_index()
        vol_df = vol_df.rolling(10).mean().shift(1).dropna().loc[reb_date:]
        vol_df['trade_date'] = vol_df.index
        vol_df = pd.melt(vol_df, id_vars=['trade_date'], var_name='ticker', value_name='mean_vol')
        volume_data = pd.read_csv('D:\\Strategy_Base\\volume_data\\{}.csv'.format(
            reb_date), dtype={"date": str})
        volume_data.rename(columns={"date": "trade_date"}, inplace=True)
        volume_data = pd.melt(volume_data, id_vars=['trade_date'], var_name='ticker', value_name='vol_today')
        vol_df = vol_df.merge(volume_data, on=['trade_date', 'ticker'])
        vol_df.loc[vol_df['vol_today'] >= vol_df['mean_vol'] * 3, 'vol_sign'] = 1.
        vol_df['vol_sign'].fillna(0., inplace=True)
        # 价格数据：日度 + Minute_Bar
        price_d = mkt_data.query("TDATE >= @reb_date")[['TDATE', 'ticker', 'TCLOSE']]
        price_d.rename(columns={"TDATE": "trade_date", "TCLOSE": "price_15"}, inplace=True)
        price_m = pd.read_csv("D:\\Strategy_Base\\price_data1\\{}.csv".format(
            reb_date), dtype={"date": str})
        price_m.rename(columns={"date": "trade_date"}, inplace=True)
        price_m = pd.melt(price_m, id_vars=['trade_date'], var_name='ticker', value_name='price_14')
        price_df = price_d.merge(price_m, on=['trade_date', 'ticker']).sort_values(by=['ticker', 'trade_date'])

        price_m = pd.read_csv("D:\\Strategy_Base\\price_data2\\{}.csv".format(
            reb_date), dtype={"date": str})
        price_m.rename(columns={"date": "trade_date"}, inplace=True)
        price_m = pd.melt(price_m, id_vars=['trade_date'], var_name='ticker', value_name='price_145')
        price_df = price_df.merge(price_m, on=['trade_date', 'ticker']).sort_values(by=['ticker', 'trade_date'])

        price_df['price_15_pre'] = price_df.groupby('ticker')['price_15'].shift(1)
        price_df.dropna(inplace=True)
        price_df.loc[price_df['ticker'].str[0] == '3', 'limit'] = 0.195
        price_df['limit'].fillna(0.098, inplace=True)
        price_df.loc[price_df['price_15'] / price_df['price_15_pre'] - 1 > price_df['limit'], '今日涨停'] = 1.
        price_df.loc[price_df['price_14'] / price_df['price_15_pre'] - 1 > price_df['limit'], '2点前涨停'] = 1.
        price_df.loc[price_df['price_145'] / price_df['price_15_pre'] - 1 > price_df['limit'], '2点半前涨停'] = 1.
        price_df['今日涨停'].fillna(0., inplace=True)
        price_df['2点前涨停'].fillna(0., inplace=True)
        price_df['2点半前涨停'].fillna(0., inplace=True)
        price_df['昨日涨停'] = price_df.groupby('ticker')['今日涨停'].shift(1).fillna(0.)
        # 整合
        df = vol_df[['trade_date', 'ticker', 'vol_sign']].merge(price_df, on=['trade_date', 'ticker'])
        df.loc[(df['昨日涨停'] == 1) & (df['2点前涨停'] == 0.), 'price_sign'] = 1.
        df.loc[(df['vol_sign'] == 1) & (df['2点半前涨停'] == 0), 'volume_sign'] = 2.
        df['price_sign'].fillna(0., inplace=True)
        df['volume_sign'].fillna(0., inplace=True)
        df.eval("sign = price_sign + volume_sign", inplace=True)
        df['sign'].replace(3, 1, inplace=True)
        sign_df = pd.pivot_table(df, index='trade_date', columns='ticker', values='sign').sort_index().fillna(0.)
        "============================================用权重估算==========================================="
        # 可投
        mkt_data['open_ret'] = mkt_data['TOPEN'] / mkt_data['LCLOSE'] - 1
        mkt_data.loc[mkt_data['ticker'].str[0] == '3', 'limit'] = 0.195
        mkt_data['limit'].fillna(0.098, inplace=True)
        first_date = [x for x in sorted(mkt_data['TDATE'].unique()) if x > reb_date][0]
        idx_ava1 = mkt_data.query("TDATE == @first_date").query("VOTURNOVER > 0")['ticker'].tolist()
        idx_ava2 = mkt_data.query("TDATE == @first_date").query("open_ret < limit")['ticker'].tolist()
        idx = list(set(idx_ava1).intersection(set(idx_ava2)))
        buy_list = [x for x in ticker_list if x in idx][:10]
        alternative_stocks = selected_df[~selected_df['ticker'].isin(buy_list)]['ticker'].tolist()  # 备选股票列表
        if type == "daily":
            # 每日调整
            adjust_df = pd.DataFrame(index=sign_df.index, columns=['port_' + str(x) for x in range(1, 11)])
            adjust_df.loc[first_date] = buy_list
            sign_df = sign_df.shift(1).fillna(0.)
            date_list = [x for x in sorted(mkt_data['TDATE'].unique()) if x > first_date]
            for date in date_list:
                if sign_df.loc[date, buy_list].sum() == 0.:
                    adjust_df.loc[date] = buy_list
                    continue
                else:
                    tmp = sign_df.loc[date, buy_list]
                    remove_list = tmp[tmp.gt(0)].index.tolist()
                    append_list = alternative_stocks[:len(remove_list)]
                    alternative_stocks = [x for x in alternative_stocks if x not in append_list]
                    alternative_stocks += remove_list
                    # 替换
                    for j in range(len(remove_list)):
                        buy_list[buy_list.index(remove_list[j])] = append_list[j]
                    adjust_df.loc[date] = buy_list
        else:
            # 持仓不动
            adjust_df = pd.DataFrame(index=sign_df.index, columns=['port_' + str(x) for x in range(1, 11)])
            adjust_df.loc[:, ] = buy_list

        # stock_return = get_price_data_from_db(reb_date, period_end, ticker_list)
        stock_return = get_price_data_from_Wind(reb_date, period_end, ticker_list)
        stock_return.columns = [x.split('.')[0] for x in stock_return.columns]
        # 映射
        return_df = pd.DataFrame(index=adjust_df.index, columns=adjust_df.columns)
        for i in range(return_df.shape[0]):
            for j in range(return_df.shape[1]):
                trading_day = adjust_df.index[i]
                ticker = adjust_df.iloc[i, j]
                return_df.iloc[i, j] = stock_return.loc[trading_day, ticker]

        period_nav = (1 + return_df).cumprod().mean(axis=1)
        period_nav.loc[reb_date] = 1.
        period_nav.sort_index(inplace=True)

        ret_list.append(period_nav.pct_change().dropna())

    port_ret = pd.concat(ret_list)
    port_ret.loc[reb_dates[0]] = 0.
    port_ret.sort_index(inplace=True)
    port_nav = (1 + port_ret).cumprod()

    return port_nav


if __name__ == '__main__':
    # 更新
    s_date = "20231220"
    e_date = "20231229"
    results = BigMomStrategy(s_date, e_date).update_portfolio(e_date, e_date)
    # results = BigMomStrategy("20230720", "20230901").select_stocks()
    # results.to_csv('D:\\Strategy_Base\\策略截面持股备选池.csv', index=False)
    # 回测
    # weight = pd.read_csv('D:\\Strategy_Base\\策略截面持股备选池.csv',
    #                      dtype={"ticker": str, "reb_date": str, "next_date": str})
    # weight['ticker'] = weight['ticker'].apply(lambda x: str(x).zfill(6))
    # # save_30_minutes_data_to_csv(weight, "20231120", "20231229")
    # calc_signal_matrix(weight, "20200720", "20231229", type="monthly")