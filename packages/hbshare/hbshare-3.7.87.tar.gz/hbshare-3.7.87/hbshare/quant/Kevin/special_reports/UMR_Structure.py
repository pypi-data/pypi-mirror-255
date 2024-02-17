"""
UMR-因子调整框架
"""
import os
from datetime import datetime, timedelta
import pandas as pd
import hbshare as hbs
import numpy as np
from tqdm import tqdm
import statsmodels.api as sm
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import fetch_data_batch_hbs, get_trading_day_list
from hbshare.quant.Kevin.rm_associated.config import style_names
from hbshare.fe.common.util.config import style_name, industry_name


data_path = "D:\\kevin\\risk_model_jy\\RiskModel\\data\\common_data"
price_data_path = "D:\\AlphaBase\\价格数据\\"


def turn_rate_extractor(trade_date, back_window, risk_window):
    """
    :param trade_date: 日期
    :param back_window: UMR因子计算的回溯周期
    :param risk_window: 风险时序调整的周期
    :return:
    """
    trade_dt = datetime.strptime(trade_date, '%Y%m%d')
    pre_date = (trade_dt - timedelta(days=3*back_window)).strftime('%Y%m%d')
    trading_day_list = get_trading_day_list(pre_date, trade_date, frequency="day")[-(back_window + risk_window):]
    to_path = os.path.join(data_path, r"turnover_rate")
    listdir = os.listdir(to_path)
    listdir = [x for x in listdir if x.split('.')[0] in trading_day_list]
    assert (len(listdir) == back_window + risk_window)
    turnover_list = []
    # print("---开始读取-{}-期换手率数据---".format(trade_date))
    for filename in listdir:
        date_t_rate = pd.read_json(os.path.join(to_path, filename), typ='series').to_frame('turnover_rate')
        date_t_rate.index.name = 'ticker'
        date_t_rate = date_t_rate.reset_index()
        date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_rate['trade_date'] = filename.split('.')[0]
        turnover_list.append(date_t_rate)
    turnover_df = pd.concat(turnover_list)
    turnover_df = turnover_df.pivot_table(index='trade_date', columns='ticker', values='turnover_rate').sort_index()
    # remove nan
    turnover_df.replace(0, np.NaN, inplace=True)
    turnover_df = turnover_df.dropna(axis=1, how='any')
    risk_df = (turnover_df.rolling(risk_window).mean() - turnover_df).iloc[risk_window:]

    return risk_df


def true_range_extractor(trade_date, back_window, risk_window):
    """
    :param trade_date: 日期
    :param back_window: UMR因子计算的回溯周期
    :param risk_window: 风险时序调整的周期
    :return:
    """
    trade_dt = datetime.strptime(trade_date, '%Y%m%d')
    pre_date = (trade_dt - timedelta(days=3*back_window)).strftime('%Y%m%d')
    trading_day_list = get_trading_day_list(pre_date, trade_date, frequency="day")[-(back_window + risk_window):]
    listdir = os.listdir(price_data_path)
    listdir = [x for x in listdir if x.split('.')[0] in trading_day_list]
    assert (len(listdir) == back_window + risk_window)
    tr_list = []
    # print("---开始读取-{}-期价格数据---".format(trade_date))
    for filename in listdir:
        date_t_rate = pd.read_csv(os.path.join(price_data_path, filename), dtype={"tradeDate": str, "ticker": str})
        date_t_rate.eval("descriptor1 = HIGH - LOW", inplace=True)
        date_t_rate['descriptor2'] = (date_t_rate['HIGH'] - date_t_rate['LCLOSE']).abs()
        date_t_rate['descriptor3'] = (date_t_rate['LOW'] - date_t_rate['LCLOSE']).abs()
        date_t_rate['numerator'] = date_t_rate[['descriptor1', 'descriptor2', 'descriptor3']].max(axis=1)
        date_t_rate.eval("tr = numerator / LCLOSE", inplace=True)
        date_t_rate.loc[date_t_rate['turnoverValue'] < 1e-8, 'tr'] = np.NaN
        tr_list.append(date_t_rate[['tradeDate', 'ticker', 'tr']])
    tr = pd.concat(tr_list)
    tr = tr.pivot_table(index='tradeDate', columns='ticker', values='tr').sort_index()
    tr = tr.dropna(axis=1, how='any')
    risk_df = (tr.rolling(risk_window).mean() - tr).iloc[risk_window:]

    return risk_df


class UMROperator:
    def __init__(self, trade_date, risk_df, benchmark_id='000985', back_window=60):
        """
        :param trade_date: 日期
        :param risk_df: 风险系数
        :param benchmark_id: 指数代码
        :param back_window: 回溯窗口
        """
        self.trade_date = trade_date
        self.risk_df = risk_df
        self.benchmark_id = benchmark_id
        self.back_window = back_window
        self._load_data()

    def _load_data(self):
        self._load_index_return()
        self._load_stock_return()

    def _load_index_return(self):
        trade_dt = datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - timedelta(days=2*self.back_window)).strftime('%Y%m%d')
        trading_day_list = get_trading_day_list(pre_date, self.trade_date, frequency="day")[-(self.back_window + 1):]
        sql_script = ("SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE FROM st_market.t_st_zs_hq WHERE "
                      "ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}").format(self.benchmark_id, pre_date, self.trade_date)
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        data = pd.DataFrame(res['data'])
        data['TRADEDATE'] = data['TRADEDATE'].map(str)
        data = data.set_index('TRADEDATE')['TCLOSE']
        self.index_return = data.reindex(trading_day_list).pct_change().dropna()

    def _load_stock_return(self):
        trade_dt = datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - timedelta(days=2*self.back_window)).strftime('%Y%m%d')
        trading_day_list = get_trading_day_list(pre_date, self.trade_date, frequency="day")[-self.back_window:]
        path = "D:\\MarketInfoSaver"
        listdir = os.listdir(path)
        listdir = [x for x in listdir if x.split('_')[-1].split('.')[0] in trading_day_list]
        data = []
        # print("---开始读取-{}-期个股数据---".format(self.trade_date))
        for filename in listdir:
            trade_date = filename.split('.')[0].split('_')[-1]
            date_t_data = pd.read_csv(os.path.join(path, filename))
            date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
            date_t_data['trade_date'] = trade_date
            data.append(date_t_data)
        data = pd.concat(data)
        data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
        stock_return = data.pivot_table(index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index()
        # stock_return /= 100.
        self.stock_return = stock_return.dropna(axis=1, how='any')

    @staticmethod
    def half_life_weight(n, half_life):
        """
        半衰期加权函数
        :param n: 样本长度
        :param half_life: 半衰期
        :return: 加权序列
        """
        if half_life > n:
            raise ValueError('半衰期应小于样本长度')
        else:
            weight = np.array([2 ** (-i / half_life) for i in range(n)])
            weight = weight / weight.sum()
            return weight[::-1]

    def run(self):
        # universe
        # univ = pd.read_csv('D:\\kevin\\risk_model_jy\\RiskModel\\data\\common_data\\univ\\zzqz\\{}.csv'.format(
        #     self.trade_date), index_col=0)
        # univ['ticker'] = univ.index
        # univ['ticker'] = univ['ticker'].apply(lambda x: str(x).zfill(6))
        # universe = univ['ticker'].tolist()
        # align
        index_return = self.index_return * 100
        stock_return = self.stock_return
        risk_df = self.risk_df * 100
        idx = set(stock_return.columns).intersection(set(risk_df.columns))
        idx = sorted(list(idx))
        stock_return = stock_return[idx]
        risk_df = risk_df[idx]
        # calculate
        excess_return = stock_return.sub(index_return, axis=0)
        weights = self.half_life_weight(self.back_window, 0.5 * self.back_window)
        weights = pd.Series(index=excess_return.index, data=weights)
        umr_factor = (excess_return * risk_df).T.dot(weights)
        # process
        umr_factor = umr_factor.to_frame('umr')
        p_alpha_neg = excess_return.lt(0).sum() / excess_return.shape[0]
        p_risk_neg = risk_df.lt(0).sum() / risk_df.shape[0]
        # 极值拉回正常区间
        median = umr_factor.median()
        new_median = abs(umr_factor - median).median()
        up = median + 5 * new_median
        down = median - 5 * new_median
        umr_factor = umr_factor.clip(down, up, axis=1)
        umr_factor = umr_factor.merge(p_alpha_neg.to_frame('alpha_neg'), left_index=True, right_index=True).merge(
            p_risk_neg.to_frame('risk_neg'), left_index=True, right_index=True)
        # 中性化
        style_factor = pd.read_csv(
            "D:\\kevin\\risk_model_jy\\RiskModel\\data\\zzqz_sw\\style_factor\\{}.csv".format(self.trade_date))
        style_factor['ticker'] = style_factor['ticker'].apply(lambda x: str(x).zfill(6))
        include_cols = ['size'] + list(industry_name['sw'].values())
        style_factor = style_factor.set_index('ticker')[include_cols].applymap(float)
        idx = set(umr_factor.index).intersection(set(style_factor.index))
        t_df = umr_factor.merge(style_factor, left_index=True, right_index=True).reindex(idx)
        cols = [x for x in t_df.columns if x != 'umr']
        # 中性化
        x_array = np.array(t_df[cols])
        model = sm.OLS(t_df['umr'], x_array).fit()
        t_df['umr'] = model.resid
        umr_factor = t_df[['umr']].copy()
        umr_factor['ticker'] = umr_factor.index
        umr_factor.reset_index(drop=True, inplace=True)

        print("计算日期: {}， 有因子的个股数目: {}".format(self.trade_date, umr_factor.shape[0]))
        umr_factor[['ticker', 'umr']].to_csv("D:\\AlphaBase\\umr动量因子\\{}.csv".format(self.trade_date), index=False)

        return umr_factor[['ticker', 'umr']]


def calculation_loop(start_date, end_date):
    date_list = get_trading_day_list(start_date, end_date, frequency="week")
    print("==============================开始计算==============================")
    for date in date_list:
        r_df = turn_rate_extractor(date, 60, 10)
        t_factor = UMROperator(date, r_df, back_window=60).run()
        print("计算日期: {}， 有因子的个股数目: {}".format(date, t_factor.shape[0]))

        t_factor.to_csv("D:\\AlphaBase\\umr动量因子\\{}.csv".format(date), index=False)


if __name__ == '__main__':
    # date = "20230731"
    # r_df = turn_rate_extractor(date, 20, 10)
    # r_df = true_range_extractor(date, 60, 10)
    # UMROperator(date, r_df, back_window=60).run()
    calculation_loop("20151231", "20230825")