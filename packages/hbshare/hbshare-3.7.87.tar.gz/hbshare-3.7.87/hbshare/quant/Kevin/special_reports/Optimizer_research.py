"""
信号和优化的错跑及持仓研究-代码
"""
import pandas as pd
import numpy as np
import hbshare as hbs
import os
import datetime
from tqdm import tqdm
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from hbshare.fe.common.util.data_loader import get_trading_day_list
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import fetch_data_batch_hbs
from hbshare.fe.common.util.config import style_name, industry_name


def signal_versus_portfolio(start_date, end_date):
    """
    信号 vs 持仓
    """
    factor_path = "D:\\AlphaBase\\processed_factor"
    listdir = os.listdir(factor_path)
    listdir = [x for x in listdir if start_date <= x.split('.')[0] <= end_date]
    factor_list = []
    for filename in listdir:
        t_factor = pd.read_csv(os.path.join(factor_path, filename), dtype={"ticker": str})[['ticker', 'combine']]
        t_factor['trade_date'] = filename.split('.')[0]
        factor_list.append(t_factor)
    factor_df = pd.concat(factor_list)
    factor_df = factor_df.pivot_table(index='ticker', columns='trade_date', values='combine').sort_index()

    # weight_df = pd.read_csv(
    #     'D:\\AlphaBase\\opt_results\\opt_weight_500_pure.csv', dtype={"trade_date": str})
    # weight_df = weight_df.query("ticker != 'cash'")
    # weight_df = weight_df.pivot_table(index='ticker', columns='trade_date', values='weight')

    weight_path = "D:\\AlphaBase\\opt_results_test"
    listdir = os.listdir(weight_path)
    listdir = [x for x in listdir if start_date <= x.split('.')[0] <= end_date]
    weight_list = []
    for filename in listdir:
        t_weight = pd.read_csv(os.path.join(weight_path, filename), dtype={"ticker": str, "trade_date": str})
        weight_list.append(t_weight)
    weight_df = pd.concat(weight_list)
    weight_df = weight_df.query("ticker != 'cash'")
    weight_df = weight_df.pivot_table(index='ticker', columns='trade_date', values='weight').sort_index()

    distribution_list = []
    for date in weight_df.columns:
        merged_df = factor_df[date].to_frame('factor').merge(
            weight_df[date].to_frame('weight'), left_index=True, right_index=True, how='left')
        merged_df.dropna(subset=['factor'], inplace=True)
        merged_df['weight'].fillna(0., inplace=True)
        merged_df['group'] = pd.qcut(merged_df['factor'], q=10, labels=False)
        merged_df['group'] += 1
        merged_df['f_rank'] = merged_df['factor'].rank()
        group_df = merged_df.groupby('group')['weight'].sum().to_frame(date)
        distribution_list.append(group_df)

    dis_df = pd.concat(distribution_list, axis=1)

    return dis_df


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


def future_ret_analysor(trade_date, fund_name, benchmark_id, mode="all"):
    """
    :param trade_date:
    :param fund_name:
    :param benchmark_id:
    :param mode: all对应全市场分组, ind对应分行业整合
    :return:
    """
    # 日期平移
    trade_dt = datetime.datetime.strptime(trade_date, '%Y%m%d')
    n_date = (trade_dt + datetime.timedelta(days=20)).strftime('%Y%m%d')
    end_date = get_trading_day_list(trade_date, n_date, frequency="day")[5]
    # 持仓
    sql_script = "SELECT * FROM private_fund_holding where trade_date = {} and fund_name = '{}'".format(
        trade_date, fund_name)
    engine = create_engine(engine_params)
    holding_df = pd.read_sql(sql_script, engine)
    holding_df['trade_date'] = holding_df['trade_date'].apply(
        lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    holding_df = holding_df.set_index('ticker')['weight']
    holding_df /= holding_df.sum()

    benchmark_weight_series = load_benchmark_weight_series(trade_date, benchmark_id)
    weight_df = holding_df.to_frame('port').merge(
        benchmark_weight_series.to_frame('bm'), left_index=True, right_index=True, how='outer').fillna(0.)
    weight_df.eval("active = port - bm", inplace=True)
    # holding_df = weight_df['active']
    holding_df = weight_df['port']
    # 收益
    trading_day_list = get_trading_day_list(trade_date, end_date, frequency="day")[1:]
    path = "D:\\MarketInfoSaver"
    listdir = os.listdir(path)
    listdir = [x for x in listdir if x.split('_')[-1].split('.')[0] in trading_day_list]
    data = []
    # print("---开始读取-{}-期个股数据---".format(self.trade_date))
    for filename in listdir:
        t_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = t_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    stock_return = data.pivot_table(
        index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index().fillna(0.) / 100.
    stock_return = (1 + stock_return).cumprod() - 1
    if mode == "all":
        ret_group = stock_return.T.apply(lambda x: pd.qcut(x, q=10, labels=False)) + 1
    else:
        sql_script = "SELECT * FROM st_fund.t_st_gm_zqhyflb WHERE hyhfbz = '2' and fljb = '1' and m_opt_type <> '03'"
        include_cols = ['qsrq', 'zqdm', 'jsrq', 'flmc']
        data = fetch_data_batch_hbs(sql_script, "funduser")[include_cols]
        data['qsrq'] = data['qsrq'].map(str)
        data['jsrq'] = data['jsrq'].fillna(20991231.0)
        data['jsrq'] = data['jsrq'].map(int)
        data['jsrq'] = data['jsrq'].map(str)
        data.rename(
            columns={"qsrq": "start_date", "jsrq": "end_date", "zqdm": "ticker", "flmc": "industryName1"}, inplace=True)
        period_data = data[(data['start_date'] < trade_date) & (data['end_date'] >= trade_date)]
        ind_df = period_data.set_index('ticker')['industryName1'].dropna()
        ret_group = ind_df.to_frame('industry').merge(stock_return.T, left_index=True, right_index=True)
        for date in ret_group.columns[1:]:
            ret_group[date] = ret_group.groupby(
                'industry', group_keys=False)[date].apply(lambda x: pd.qcut(x, q=10, labels=False, duplicates='drop') + 1)
    # 整合
    df = holding_df.to_frame('weight').merge(ret_group, left_index=True, right_index=True)
    count_list = []
    for date in stock_return.index:
        tmp = df.groupby(date)['weight'].sum().sort_index().to_frame(date)
        count_list.append(tmp)
    count_df = pd.concat(count_list, axis=1)
    count_df.columns = ['T+{}'.format(x) for x in range(1, 6)]

    # a = count_df.reset_index().corr().loc["index"][1:4]

    return count_df


class RiskPredictor:
    """
    组合风险预测类
    """
    def __init__(self, start_date, end_date, fund_type="500指增", benchmark_id="000905"):
        self.start_date = start_date
        self.end_date = end_date
        self.fund_type = fund_type
        self.benchmark_id = benchmark_id

    @staticmethod
    def _load_shift_date(date):
        trade_dt = datetime.datetime.strptime(date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM st_main.t_st_gg_jyrl WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, date)
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    def _load_portfolio_weight_series(self):
        sql_script = ("SELECT * FROM private_fund_holding where fund_type = '{}' and trade_date >= {} and "
                      "trade_date <= {}").format(self.fund_type, self.start_date, self.end_date)
        engine = create_engine(engine_params)
        holding_df = pd.read_sql(sql_script, engine)
        holding_df['trade_date'] = holding_df['trade_date'].apply(
            lambda x: datetime.datetime.strftime(x, '%Y%m%d'))

        return holding_df[['trade_date', 'ticker', 'weight', 'fund_name']]

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

    def run(self):
        holding_df = self._load_portfolio_weight_series()
        weight_date_list = sorted(holding_df['trade_date'].unique())
        month_end = list(pd.date_range(self.start_date, self.end_date, freq="M"))
        month_end = [datetime.datetime.strftime(x, "%Y%m%d") for x in month_end]
        weight_date_list = [x for x in weight_date_list if x in month_end]
        all_risk = []
        for date in tqdm(weight_date_list):
            shift_date = self._load_shift_date(date)
            t_weight = holding_df.query("trade_date == @date")
            t_weight = t_weight.pivot_table(index='ticker', columns='fund_name', values='weight') / 100.
            benchmark_weight_series = self._load_benchmark_weight_series(shift_date)
            # 补齐仓位至100%
            cols = t_weight.columns
            t_weight = t_weight.merge(benchmark_weight_series.to_frame('benchmark'),
                                      left_index=True, right_index=True, how='outer').fillna(0.)
            for col in cols:
                t_weight[col] += t_weight['benchmark'] * (1 - t_weight[col].sum())
            exposure_df = self._load_style_exposure(shift_date)
            factor_cov = self._load_factor_cov(shift_date)
            srisk = self._load_srisk(shift_date)

            active_weight = t_weight.sub(t_weight['benchmark'], axis=0)
            exposure_df = exposure_df.astype(float)
            factor_cov = factor_cov.divide(12 * 10000)
            srisk = srisk ** 2 * 21

            idx = set(active_weight.index).intersection(set(exposure_df.index)).intersection(set(srisk.index))

            active_weight = active_weight.reindex(idx)
            exposure_df = exposure_df.reindex(idx)
            srisk = srisk.reindex(idx)['srisk']

            common_risk = np.mat(active_weight).T.dot(
                np.mat(exposure_df).dot(np.mat(factor_cov)).dot(np.mat(exposure_df).T)).dot(np.mat(active_weight))
            specific_risk = np.mat(active_weight).T.dot(np.diag(srisk)).dot(np.mat(active_weight))

            risk_df = pd.DataFrame({"fund_name": active_weight.columns[:-1],
                                    "common_risk": np.diag(common_risk)[:-1],
                                    "specific_risk": np.diag(specific_risk)[:-1]})
            risk_df = risk_df.set_index('fund_name') * 12
            risk_df['exante_te'] = np.sqrt(risk_df['common_risk'] + risk_df['specific_risk'])
            risk_df['fund_name'] = risk_df.index
            risk_df.reset_index(drop=True, inplace=True)
            risk_df['trade_date'] = date
            all_risk.append(risk_df)

        all_risk = pd.concat(all_risk)
        risk_pivot = pd.pivot_table(all_risk, index='trade_date', columns='fund_name', values='exante_te').sort_index()

        return all_risk, risk_pivot


if __name__ == '__main__':
    # signal_versus_portfolio("20221230", "20230811")
    # results = future_ret_analysor("20230630", "凡二量化选股3号1期", '000852', mode="all")
    # print(results)
    RiskPredictor("20220630", "20230821").run()