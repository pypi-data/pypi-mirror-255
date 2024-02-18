"""
公募量化的分析模块
"""
import pandas as pd
import numpy as np
import hbshare as hbs
import os
from hbshare.fe.common.util.config import style_name, industry_name
import datetime
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from hbshare.fe.common.util.config import factor_map_dict
from hbshare.fe.common.util.data_loader import get_trading_day_list
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import fetch_data_batch_hbs


class MutualFundAnalysor:
    def __init__(self, fund_name, fund_id, trade_date, benchmark_id):
        self.fund_name = fund_name
        self.fund_id = fund_id
        self.trade_date = trade_date
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_shift_date(self):
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM st_main.t_st_gg_jyrl WHERE JYRQ >= {} and JYRQ <= {}".format(
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

    def _load_portfolio_weight_series(self):
        # 公募单独分析
        sql_script = "SELECT jsrq as end_date, ggrq as report_date, zqdm as ticker, " \
                     "zjbl, zgbl, zlbl FROM st_fund.t_st_gm_gpzh where " \
                     "jjdm = '{}' and jsrq = {}".format(self.fund_id, self.trade_date)
        holding_df = fetch_data_batch_hbs(sql_script, "funduser")
        holding_df.rename(columns={"end_date": "trade_date", "zjbl": "weight"}, inplace=True)

        return holding_df.set_index('ticker')['weight'] / 100.

    def _load_benchmark_weight_series(self, date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            self.benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[self.benchmark_id, 'INNERCODE']

        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})

        return weight_df.set_index('consTickerSymbol')['weight'] / 100.

    @staticmethod
    def _load_benchmark_components(date):
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

    @staticmethod
    def _load_style_exposure(date):
        sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
        exposure_df = fetch_data_batch_hbs(sql_script, "alluser").set_index('ticker')
        ind_names = [x.lower() for x in industry_name['sw'].values()]
        exposure_df = exposure_df[style_name + ind_names]

        return exposure_df

    @staticmethod
    def _load_stock_conception(date):
        sql_script = "SELECT * FROM stock_conception where trade_date = {}".format(date)
        engine = create_engine(engine_params)
        concept_df = pd.read_sql(sql_script, engine)
        concept_df['trade_date'] = concept_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        concept_df = concept_df[['trade_date', 'ticker', 'concept']]

        return concept_df

    def _load_data(self):
        shift_date = self._load_shift_date()
        portfolio_weight_series = self._load_portfolio_weight_series()
        if self.benchmark_id in ['8841425.WI']:
            benchmark_weight_series = self._load_benchmark_weight_from_wind(shift_date)
        else:
            benchmark_weight_series = self._load_benchmark_weight_series(shift_date)
        benchmark_components = self._load_benchmark_components(shift_date)
        style_exposure_df = self._load_style_exposure(shift_date)
        concept_df = self._load_stock_conception(shift_date)

        self.data_param = {
            "portfolio_weight_series": portfolio_weight_series,
            "benchmark_weight_series": benchmark_weight_series,
            "benchmark_components": benchmark_components,
            "style_exposure_df": style_exposure_df,
            "concept_df": concept_df
        }

    def get_construct_result(self):
        portfolio_weight_series = self.data_param.get('portfolio_weight_series')
        benchmark_weight_series = self.data_param.get('benchmark_weight_series') * portfolio_weight_series.sum()
        benchmark_components = self.data_param.get('benchmark_components')
        style_exposure_df = self.data_param.get('style_exposure_df')
        concept_df = self.data_param.get('concept_df')

        # 板块分布
        weight_df = portfolio_weight_series.reset_index().rename(columns={"weight": "port"}).merge(
            benchmark_weight_series.reset_index().rename(columns={"consTickerSymbol": "ticker", "weight": "bm"}),
            on='ticker', how='outer').fillna(0.)
        weight_df.loc[weight_df['ticker'].str.startswith('0'), 'sector'] = '深市'
        weight_df.loc[weight_df['ticker'].str.startswith('60'), 'sector'] = '沪市'
        weight_df.loc[weight_df['ticker'].str.startswith('30'), 'sector'] = '创业板'
        weight_df.loc[weight_df['ticker'].str.startswith('688'), 'sector'] = '科创板'
        sector_distribution = weight_df.groupby('sector')[['port', 'bm']].sum().reset_index().set_index('sector')
        sector_distribution['active'] = sector_distribution['port'] - sector_distribution['bm']

        # 成分股分布
        w_df = pd.merge(portfolio_weight_series.reset_index(), benchmark_components, on='ticker', how='left')
        w_df['benchmark_id'].fillna('other', inplace=True)
        bm_distribution = w_df.groupby('benchmark_id')['weight'].sum().reset_index().replace(
            {"000300": "沪深300", "000905": "中证500", "000852": "中证1000",
             "399303": "国证2000", "other": "超小票"}).set_index('benchmark_id')
        bm_distribution = bm_distribution['weight']
        bm_distribution.loc['非权益仓位'] = 1 - bm_distribution.sum()

        # 风格及行业分布
        idx = portfolio_weight_series.index.union(benchmark_weight_series.index).intersection(
            style_exposure_df.index)

        portfolio_weight_series = portfolio_weight_series.reindex(idx).fillna(0.)
        benchmark_weight_series = benchmark_weight_series.reindex(idx).fillna(0.)
        style_exposure_df = style_exposure_df.reindex(idx).astype(float)
        portfolio_expo = style_exposure_df.T.dot(portfolio_weight_series)
        benchmark_expo = style_exposure_df.T.dot(benchmark_weight_series)
        style_expo = pd.concat([portfolio_expo.to_frame('port'), benchmark_expo.to_frame('bm')], axis=1)
        style_expo['active'] = style_expo['port'] - style_expo['bm']

        reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])
        benchmark_id_map = {"000300": "沪深300", "000905": "中证500", "000906": "中证800", "000852": "中证1000",
                            "8841425.WI": "万得小市值指数", "000985": "中证全指"}

        # 概念
        portfolio_weight_series = self.data_param.get('portfolio_weight_series')
        benchmark_weight_series = self.data_param.get('benchmark_weight_series') * portfolio_weight_series.sum()
        concept_num = len(concept_df['concept'].unique())
        concept_df = concept_df.join(pd.get_dummies(concept_df['concept']))
        concept_series = concept_df.groupby('ticker')[concept_df.columns[-concept_num:]].sum()
        idx = portfolio_weight_series.index.union(benchmark_weight_series.index).intersection(
            concept_series.index)
        portfolio_weight_series = portfolio_weight_series.reindex(idx).fillna(0.)
        benchmark_weight_series = benchmark_weight_series.reindex(idx).fillna(0.)
        concept_series = concept_series.reindex(idx).astype(float)
        portfolio_concept = concept_series.T.dot(portfolio_weight_series)
        benchmark_concept = concept_series.T.dot(benchmark_weight_series)
        concept_expo = pd.concat([portfolio_concept.to_frame('port'), benchmark_concept.to_frame('bm')], axis=1)
        concept_expo['active'] = concept_expo['port'] - concept_expo['bm']

        # 持股权重的CDF
        portfolio_weight_series = self.data_param.get('portfolio_weight_series')
        portfolio_weight_series_norm = portfolio_weight_series / portfolio_weight_series.sum()
        port_cdf = portfolio_weight_series_norm.sort_values(ascending=False).cumsum().reset_index(drop=True)

        # 风格
        style_df = style_expo[['port', 'bm', 'active']].rename(
            columns={"port": self.fund_name, "bm": benchmark_id_map[self.benchmark_id], "active": "主动暴露"}).loc[
            style_name]
        style_df.index = style_df.index.map(factor_map_dict)
        # 行业
        ind_df = style_expo[['port', 'bm', 'active']].rename(
            columns={"port": self.fund_name, "bm": benchmark_id_map[self.benchmark_id], "active": "主动暴露"}).iloc[10:]
        ind_df.index = [reverse_ind[x] for x in ind_df.index]
        # 板块分布
        sector_distribution = sector_distribution.rename(
            columns={"port": self.fund_name, "bm": benchmark_id_map[self.benchmark_id], "active": "相对暴露"})
        # 概念分布
        cp_dis_df = concept_expo[['port', 'bm', 'active']].rename(
            columns={"port": self.fund_name, "bm": benchmark_id_map[self.benchmark_id], "active": "主动暴露"})

        results = {"style_df": style_df, "ind_df": ind_df,
                   "sector_distribution": sector_distribution, "bm_distribution": bm_distribution,
                   "concept_df": cp_dis_df, "port_cdf": port_cdf,
                   "weight": self.data_param.get("portfolio_weight_series")}

        return results


if __name__ == '__main__':
    # MutualFundAnalysor(
    #     "博道远航", "007126", "20230630", "000852").get_construct_result()

    f_name = "华夏智胜价值成长"
    f_id = "002871"
    d_list = ["20210630", "20211231", "20220630", "20221231", "20230630"]

    exposure_list = []
    industry_list = []
    distribution_list = []
    weight_list = []
    for p_date in d_list:
        print(p_date)
        rs = MutualFundAnalysor(f_name, f_id, p_date, "000852").get_construct_result()
        exposure_list.append(rs['style_df'][f_name].to_frame(p_date))
        industry_list.append(rs['ind_df'][f_name].to_frame(p_date))
        distribution_list.append(rs['bm_distribution'].to_frame(p_date))
        weight_list.append(rs['weight'].to_frame(p_date))

    exp_df = pd.concat(exposure_list, axis=1)
    industry_df = pd.concat(industry_list, axis=1)
    dis_df = pd.concat(distribution_list, axis=1)
    ww_df = pd.concat(weight_list, axis=1)
    print("===============持仓分析结束==================")