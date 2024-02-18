"""
基于私募基金估值表的截面持仓风格归因模块
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
import plotly
import plotly.graph_objs as go
import plotly.figure_factory as ff
# from WindPy import w
#
# w.start()


def plot_render(plot_dic, width=1000, height=600, **kwargs):
    kwargs['output_type'] = 'div'
    plot_str = plotly.offline.plot(plot_dic, **kwargs)
    print('%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (height, width, plot_str))


class HoldingAnalysor:
    def __init__(self, fund_name, trade_date, benchmark_id, mode="single"):
        self.fund_name = fund_name
        self.trade_date = trade_date
        self.benchmark_id = benchmark_id
        self.mode = mode
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
        if self.mode == "single":
            sql_script = "SELECT * FROM private_fund_holding where fund_name = '{}' and trade_date = {}".format(
                self.fund_name, self.trade_date)
            engine = create_engine(engine_params)
            holding_df = pd.read_sql(sql_script, engine)
            holding_df['trade_date'] = holding_df['trade_date'].apply(
                lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
            return holding_df.set_index('ticker')['weight'] / 100.

            # sql_script = "SELECT * FROM private_fund_holding where fund_type = '{}' and trade_date = {}".format(
            #     "500指增", self.trade_date)
            # engine = create_engine(engine_params)
            # holding_df = pd.read_sql(sql_script, engine)
            # holding_df['trade_date'] = holding_df['trade_date'].apply(
            #     lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
            # inc = ['乾象中证500指数增强1号', '因诺聚配中证500指数增强', '星阔广厦1号中证500指数增强',
            #        '白鹭精选量化鲲鹏十号', '衍复臻选指数增强一号', '赫富500指数增强一号']
            # holding_df = holding_df[holding_df['fund_name'].isin(inc)]
            # holding_df['weight_sum'] = holding_df.groupby('fund_name')['weight'].transform('sum')
            # holding_df['weight'] = holding_df['weight'] / holding_df['weight_sum']
            # tmp = holding_df.groupby('ticker')['weight'].sum() / len(holding_df['fund_name'].unique())
            #
            # return tmp

            # data = pd.read_excel("D:\\估值表基地\\磐松多空对冲\\处理后的持仓数据\\holding_data.xlsx", sheet_name=1,
            #                      dtype={"trade_date": str, "ticker": str})
            # sub_data = data[data['fund_name'] == '磐松多空对冲2号私募证券投资基金']
            # sub_data = data[data['trade_date'] == "20230531"]
            # sub_data = sub_data[sub_data['direction'] == 'short']
            #
            # return sub_data.set_index('ticker')['weight'] / 100.

            # 公募单独分析
            # sql_script = "SELECT jsrq as end_date, ggrq as report_date, zqdm as ticker, " \
            #              "zjbl, zgbl, zlbl FROM st_fund.t_st_gm_gpzh where " \
            #              "jjdm = '014155' and jsrq = {}".format("20221231")
            # holding_df = pd.DataFrame(hbs.db_data_query('funduser', sql_script, page_size=5000)['data'])
            # holding_df.rename(columns={"end_date": "trade_date", "zjbl": "weight"}, inplace=True)
            #
            # return holding_df.set_index('ticker')['weight'] / 100.
        else:
            # FOF持仓穿透分析
            # weight_dict = {
            #     "宽德九臻": 8.77,
            #     "千衍六和3号": 5.59,
            #     "超量子500增强2号": 9.83,
            #     "稳博1000指数增强1号": 7.98,
            #     "信弘征程2号": 9.83,
            #     "铭量中证500增强1号": 3.24,
            #     "概率1000指增1号": 4.41,
            #     "顽岩中证500指数增强5号": 16.94,
            #     "伯兄至道": 1.95,
            #     "半鞅量化精选": 5.79,
            #     "乾象中证500指数增强1号": 17.96,
            #     "衍复小市值指数增强一号": 8.25
            # }
            weight_dict = {
                "信弘征程2号": 12.49,
                "顽岩中证500指数增强5号": 4.42,
                "乾象中证500指数增强1号": 7.38,
                "磐松500指增": 11.21,
                "千衍六和3号": 6.64,
                "凡二量化选股3号1期": 15.50,
                "半鞅量化精选": 5.88,
                "稳博1000指数增强1号": 14.20,
                "铭量中证500增强1号": 4.28,
                "仲阳500指增": 6.39,
                "托特中证1000指数增强1号": 8.06
            }
            weight_df = pd.DataFrame.from_dict(weight_dict, orient="index", columns=['fof_weight'])

            sql_script = "SELECT * FROM private_fund_holding where trade_date = {}".format(self.trade_date)
            engine = create_engine(engine_params)
            holding_df = pd.read_sql(sql_script, engine)
            holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
            include_list = weight_df.index.tolist()

            include_list = list(set(include_list).intersection(set(holding_df['fund_name'].unique())))
            weight_df = weight_df.reindex(include_list)
            # 归一化
            # weight_df = 100 * weight_df / weight_df.sum()

            holding_df = holding_df[holding_df['fund_name'].isin(include_list)]
            holding_df = holding_df.merge(weight_df, left_on='fund_name', right_index=True)
            holding_df['adj_weight'] = holding_df['weight'] * holding_df['fof_weight'] / 100.

            grouped_weight = holding_df.groupby('ticker')['adj_weight'].sum() / 100.
            grouped_weight.name = 'weight'

            return grouped_weight

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

    def _load_benchmark_weight_from_wind(self, date):
        sql_script = "SELECT * FROM benchmark_holding where benchmark_id = '{}' and trade_date = {}".format(
            self.benchmark_id, date)
        engine = create_engine(engine_params)
        weight_df = pd.read_sql(sql_script, engine)
        weight_df.rename(columns={"ticker": "consTickerSymbol"}, inplace=True)
        # 剔除北交所
        weight_df = weight_df[weight_df['consTickerSymbol'].str[0].isin(['0', '3', '6'])]
        weight_df['weight'] = weight_df['weight'] / weight_df['weight'].sum()

        return weight_df.set_index('consTickerSymbol')['weight']

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

    @staticmethod
    def plotly_style_bar(df, title_text, figsize=(1000, 600), legend_x=0.30):
        fig_width, fig_height = figsize
        cols = df.columns.tolist()
        color_list = ['rgb(49, 130, 189)', 'rgb(204, 204, 204)', 'rgb(216, 0, 18)']
        data = []
        for i in range(len(cols)):
            col = cols[i]
            trace = go.Bar(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                marker=dict(color=color_list[i])
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="h", x=legend_x),
            template='plotly_white'
        )

        # fig = go.Figure(data=data, layout=layout)

        return data, layout

    @staticmethod
    def plotly_bar(df, title_text, figsize=(1200, 800)):
        fig_width, fig_height = figsize
        cols = df.columns.tolist()
        color_list = ['rgb(49, 130, 189)', 'rgb(204, 204, 204)']
        data = []
        for i in range(len(cols)):
            col = cols[i]
            trace = go.Bar(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                marker=dict(color=color_list[i])
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="h", x=0.38),
            template='plotly_white'
        )

        # fig = go.Figure(data=data, layout=layout)

        return data, layout

    @staticmethod
    def plotly_pie(df, title_text, figsize=(800, 600)):
        fig_width, fig_height = figsize
        labels = df.index.tolist()
        values = df.values.round(3).tolist()
        data = [go.Pie(labels=labels, values=values, hoverinfo="label+percent",
                       texttemplate="%{label}: %{percent}")]
        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height
        )

        # fig = go.Figure(data=data, layout=layout)

        return data, layout

    @staticmethod
    def plotly_line(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        data = []
        trace = go.Scatter(
            x=df.index.tolist(),
            y=df.values.tolist(),
            name='权重',
            mode="lines",
            line_width=3.0
        )
        data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            xaxis_title='股票数量',
            yaxis_title='归一化累计权重',
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True, tickformat=".0%"),
            xaxis=dict(showgrid=True),
            template='plotly_white'
        )

        return data, layout

    def get_construct_result(self, isPlot=True):
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
        if isPlot:
            data, layout = self.plotly_style_bar(style_df, "横截面持仓风格暴露")
            plot_render({"data": data, "layout": layout})
        # 行业
        ind_df = style_expo[['port', 'bm', 'active']].rename(
            columns={"port": self.fund_name, "bm": benchmark_id_map[self.benchmark_id], "active": "主动暴露"}).iloc[10:]
        ind_df.index = [reverse_ind[x] for x in ind_df.index]
        if isPlot:
            data, layout = self.plotly_style_bar(ind_df, "横截面持仓行业暴露", figsize=(1500, 600), legend_x=0.35)
            plot_render({"data": data, "layout": layout}, width=1500, height=600)
        # 板块分布
        sector_distribution = sector_distribution.rename(
            columns={"port": self.fund_name, "bm": benchmark_id_map[self.benchmark_id], "active": "相对暴露"})
        if isPlot:
            data, layout = self.plotly_style_bar(sector_distribution, "横截面持仓板块暴露")
            plot_render({"data": data, "layout": layout})
        # 成分股分布
        if isPlot:
            data, layout = self.plotly_pie(bm_distribution, "持仓指数成分分布", figsize=(800, 600))
            plot_render({"data": data, "layout": layout}, width=800, height=600)
        # 概念分布
        cp_dis_df = concept_expo[['port', 'bm', 'active']].rename(
            columns={"port": self.fund_name, "bm": benchmark_id_map[self.benchmark_id], "active": "主动暴露"})
        if isPlot:
            data, layout = self.plotly_style_bar(cp_dis_df, "横截面概念持仓暴露")
            plot_render({"data": data, "layout": layout})
        # 持股权重的CDF
        if isPlot:
            data, layout = self.plotly_line(port_cdf, "组合权重归一化CDF曲线")
            plot_render({"data": data, "layout": layout})
            # fig = go.Figure(data=data, layout=layout)
            # from plotly.offline import plot as plot_ly
            # plot_ly(fig, filename="D:\\123.html", auto_open=False)
            # plot_render({"data": data, "layout": layout})

        results = {"style_df": style_df, "ind_df": ind_df,
                   "sector_distribution": sector_distribution, "bm_distribution": bm_distribution,
                   "concept_df": cp_dis_df, "port_cdf": port_cdf}

        return results


class HoldingDistribution:
    def __init__(self, start_date, end_date, fund_name):
        self.start_date = start_date
        self.end_date = end_date
        self.fund_name = fund_name
        self._load_data()

    def _load_portfolio_weight(self):
        sql_script = "SELECT * FROM private_fund_holding where fund_name = '{}' and " \
                     "trade_date >= {} and trade_date <= {}".format(self.fund_name, self.start_date, self.end_date)
        engine = create_engine(engine_params)
        holding_df = pd.read_sql(sql_script, engine)
        holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        # 归一化
        # holding_df['weight_sum'] = holding_df.groupby('trade_date')['weight'].transform('sum')
        # holding_df['weight'] /= holding_df['weight_sum']

        holding_df['weight'] /= 100.

        return holding_df[['trade_date', 'ticker', 'weight']]

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
    def _load_benchmark_weight(benchmark_id, shift_date, date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[benchmark_id, 'INNERCODE']

        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, shift_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
        weight_df['benchmark_id'] = benchmark_id
        weight_df['trade_date'] = date

        return weight_df[['trade_date', 'ticker', 'weight', 'benchmark_id']]

    def _load_data(self):
        portfolio_weight_df = self._load_portfolio_weight()
        date_list = sorted(portfolio_weight_df['trade_date'].unique())
        benchmark_weight = []
        for date in date_list:
            shift_date = self._load_shift_date(date)
            weight = self._load_benchmark_components(shift_date)
            weight['trade_date'] = date
            benchmark_weight.append(weight)

        benchmark_weight = pd.concat(benchmark_weight)

        self.data_param = {"portfolio_weight": portfolio_weight_df, "benchmark_weight": benchmark_weight}

    def get_construct_result(self):
        data_param = self.data_param
        portfolio_weight = data_param['portfolio_weight']
        benchmark_weight = pd.DataFrame(data_param['benchmark_weight'])

        df = pd.merge(
            portfolio_weight, benchmark_weight, on=['trade_date', 'ticker'], how='left').fillna('other')
        distribution_df = df.groupby(['trade_date', 'benchmark_id'])['weight'].sum().reset_index()
        distribution_df = pd.pivot_table(
            distribution_df, index='trade_date', columns='benchmark_id', values='weight').sort_index()
        distribution_df['not_equity'] = 1 - distribution_df.sum(axis=1)

        return distribution_df


class HoldingCompare:
    def __init__(self, trade_date, benchmark_id, include_list):
        self.trade_date = trade_date
        self.benchmark_id = benchmark_id
        self.include_list = include_list
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
        sql_script = "SELECT * FROM private_fund_holding where trade_date = {}".format(self.trade_date)
        engine = create_engine(engine_params)
        holding_df = pd.read_sql(sql_script, engine)
        holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        holding_df = holding_df[holding_df['fund_name'].isin(self.include_list)]
        # 归一化
        holding_df['total_weight'] = holding_df.groupby('fund_name')['weight'].transform('sum')
        holding_df['weight'] = holding_df['weight'] / holding_df['total_weight']

        return holding_df[['fund_name', 'ticker', 'weight']]

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

    @staticmethod
    def plotly_style_bar(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        cols = df.columns.tolist()
        data = []
        for i in range(len(cols)):
            col = cols[i]
            trace = go.Bar(
                x=df.index.tolist(),
                y=df[col],
                name=col
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="v"),
            template='plotly_white'
        )

        # fig = go.Figure(data=data, layout=layout)

        return data, layout

    @staticmethod
    def plotly_bar(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        cols = df.columns.tolist()
        data = []
        for i in range(len(cols)):
            col = cols[i]
            trace = go.Bar(
                x=df.index.tolist(),
                y=df[col],
                name=col
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True, tickformat=".0%"),
            xaxis=dict(showgrid=True),
            legend=dict(orientation="v"),
            template='plotly_white'
        )

        # fig = go.Figure(data=data, layout=layout)

        return data, layout

    def run(self):
        portfolio_weight_df = self.data_param.get('portfolio_weight_series')
        portfolio_weight_df = pd.pivot_table(
            portfolio_weight_df, index='ticker', columns='fund_name', values='weight').fillna(0.)
        benchmark_weight_series = self.data_param.get('benchmark_weight_series')
        benchmark_components = self.data_param.get('benchmark_components')
        style_exposure_df = self.data_param.get('style_exposure_df')
        concept_df = self.data_param.get('concept_df')

        # 板块分布
        weight_df = portfolio_weight_df.merge(
            benchmark_weight_series.reset_index().rename(columns={"consTickerSymbol": "ticker", "weight": "bm"}),
            on='ticker', how='outer').fillna(0.)
        weight_df.loc[weight_df['ticker'].str.startswith('0'), 'sector'] = '深市'
        weight_df.loc[weight_df['ticker'].str.startswith('60'), 'sector'] = '沪市'
        weight_df.loc[weight_df['ticker'].str.startswith('30'), 'sector'] = '创业板'
        weight_df.loc[weight_df['ticker'].str.startswith('688'), 'sector'] = '科创板'
        sector_distribution = weight_df.groupby('sector')[self.include_list].sum()
        # 成分股分布
        w_df = pd.merge(portfolio_weight_df.reset_index(), benchmark_components, on='ticker', how='left')
        w_df['benchmark_id'].fillna('other', inplace=True)
        bm_distribution = w_df.groupby('benchmark_id').sum().reset_index().replace(
            {"000300": "沪深300", "000905": "中证500", "000852": "中证1000",
             "399303": "国证2000", "other": "超小票"}).set_index('benchmark_id')
        bm_distribution.loc['非权益仓位'] = 1. - bm_distribution.sum()
        # 风格及行业分布
        idx = portfolio_weight_df.index.union(benchmark_weight_series.index).intersection(
            style_exposure_df.index)

        portfolio_weight_series = portfolio_weight_df.reindex(idx).fillna(0.)
        benchmark_weight_series = benchmark_weight_series.reindex(idx).fillna(0.)
        style_exposure_df = style_exposure_df.reindex(idx).astype(float)
        portfolio_expo = style_exposure_df.T.dot(portfolio_weight_series)
        benchmark_expo = style_exposure_df.T.dot(benchmark_weight_series)
        style_expo = pd.concat([portfolio_expo, benchmark_expo.to_frame('bm')], axis=1)
        style_expo = style_expo.sub(style_expo['bm'], axis=0)
        # 概念
        concept_num = len(concept_df['concept'].unique())
        concept_df = concept_df.join(pd.get_dummies(concept_df['concept']))
        concept_series = concept_df.groupby('ticker')[concept_df.columns[-concept_num:]].sum()
        idx = portfolio_weight_df.index.union(benchmark_weight_series.index).intersection(
            concept_series.index)
        portfolio_weight_series = portfolio_weight_df.reindex(idx).fillna(0.)
        benchmark_weight_series = benchmark_weight_series.reindex(idx).fillna(0.)
        concept_series = concept_series.reindex(idx).astype(float)
        portfolio_concept = concept_series.T.dot(portfolio_weight_series)
        benchmark_concept = concept_series.T.dot(benchmark_weight_series)
        concept_expo = pd.concat([portfolio_concept, benchmark_concept.to_frame('bm')], axis=1)
        concept_expo['bm'] *= 100.
        # 持仓重合度
        portfolio_weight_df = self.data_param.get('portfolio_weight_series')
        portfolio_weight_df = pd.pivot_table(
            portfolio_weight_df, index='ticker', columns='fund_name', values='weight').fillna(0.)
        overlap_df = pd.DataFrame(index=portfolio_weight_df.columns, columns=portfolio_weight_df.columns)
        for i in range(len(portfolio_weight_df.columns)):
            for j in range(len(portfolio_weight_df.columns)):
                if i == j:
                    overlap_df.iloc[i, j] = 1.
                else:
                    overlap_df.iloc[i, j] = portfolio_weight_df.T.iloc[[i, j], :].T.min(axis=1).sum()
        # process
        sector_distribution = sector_distribution.reindex(["沪市", "深市", "创业板", "科创板"])
        bm_distribution = bm_distribution.reindex(["沪深300", "中证500", "中证1000", "国证2000", "超小票"])
        style_expo = style_expo.loc[style_name, self.include_list]
        style_expo.index = style_expo.index.map(factor_map_dict)

        data, layout = self.plotly_style_bar(style_expo, "主动风格暴露横截面对比")
        plot_render({"data": data, "layout": layout})

        data, layout = self.plotly_bar(bm_distribution, "宽基指数成分权重分布对比")
        plot_render({"data": data, "layout": layout})

        data, layout = self.plotly_bar(sector_distribution, "板块权重分布对比")
        plot_render({"data": data, "layout": layout})

        results = {
            "sector_dis": sector_distribution,
            "bm_dis": bm_distribution,
            "style_expo": style_expo,
            "concept_expo": concept_expo,
            "overlap_df": overlap_df
        }

        return results


def prediction_test(trade_date, fund_list):
    # 权重
    sql_script = "SELECT * FROM private_fund_holding where trade_date = {}".format(trade_date)
    engine = create_engine(engine_params)
    holding_df = pd.read_sql(sql_script, engine)
    holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    holding_df = holding_df[holding_df['fund_name'].isin(fund_list)]
    # 收益
    trade_dt = datetime.datetime.strptime(trade_date, '%Y%m%d')
    next_date = (trade_dt + datetime.timedelta(days=30)).strftime('%Y%m%d')
    date_list = get_trading_day_list(trade_date, next_date)
    date_list = [x for x in date_list if x > trade_date][:10]
    path = 'D:\\MarketInfoSaver'
    listdir = os.listdir(path)
    listdir = [x for x in listdir if date_list[0] <= x.split('_')[-1].split('.')[0] <= date_list[-1]]
    data = []
    for filename in listdir:
        trade_date = filename.split('.')[0].split('_')[-1]
        date_t_data = pd.read_csv(os.path.join(path, filename))
        date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
        date_t_data['trade_date'] = trade_date
        data.append(date_t_data)
    data = pd.concat(data)
    data.loc[data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
    data = pd.pivot_table(
        data, index='trade_date', columns='ticker', values='dailyReturnReinv').sort_index().fillna(0.) / 100.
    data = (1 + data).cumprod() - 1
    predict_list = []
    for fund_name in holding_df['fund_name'].unique():
        weight_df = holding_df[holding_df['fund_name'] == fund_name].set_index('ticker')[['weight']]
        merged_df = weight_df.merge(data.T, left_index=True, right_index=True)
        predict_list.append(merged_df.corr('pearson')['weight'].to_frame(fund_name))

    predict_df = pd.concat(predict_list, axis=1)

    return predict_df


def concept_compare(trade_date, include_fund_list):
    # 持仓
    sql_script = "SELECT * FROM private_fund_holding where trade_date = '{}'".format(trade_date)
    engine = create_engine(engine_params)
    holding_df = pd.read_sql(sql_script, engine)
    holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    holding_df = holding_df[holding_df['fund_name'].isin(include_fund_list)]
    # holding_ori = holding_df.copy()
    holding_df = pd.pivot_table(holding_df, index='ticker', columns='fund_name', values='weight').fillna(0.)
    # 基准权重
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format('000905')
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code = index_info.set_index('SECUCODE').loc['000905', 'INNERCODE']
    sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                 "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                 "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, trade_date)
    data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
    weight_df = data.rename(
        columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})
    benchmark_weight = weight_df.rename(columns={"consTickerSymbol": "ticker", "weight": "benchmark"}).set_index(
        'ticker')['benchmark']
    # 仓位补齐至100%
    idx = set(holding_df.index).union(set(benchmark_weight.index))
    holding_df = holding_df.reindex(idx).fillna(0.)
    benchmark_weight = benchmark_weight.reindex(idx).fillna(0.)
    for fund in holding_df.columns:
        holding_df[fund] += (100 - holding_df[fund].sum()) * (benchmark_weight * 0.01)
    holding_df = holding_df.merge(benchmark_weight.to_frame('中证500'), left_index=True, right_index=True)
    holding_df /= 100.
    # 概念
    sql_script = "SELECT * FROM stock_conception where trade_date = {}".format(trade_date)
    engine = create_engine(engine_params)
    concept_df = pd.read_sql(sql_script, engine)
    concept_df['trade_date'] = concept_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    concept_df = concept_df[['trade_date', 'ticker', 'concept']]
    # 计算
    concept_num = len(concept_df['concept'].unique())
    concept_df = concept_df.join(pd.get_dummies(concept_df['concept']))
    concept_series = concept_df.groupby('ticker')[concept_df.columns[-concept_num:]].sum()
    idx = holding_df.index.intersection(concept_series.index)
    holding_df = holding_df.reindex(idx).fillna(0.)
    concept_series = concept_series.reindex(idx).astype(float)
    portfolio_concept = concept_series.T.dot(holding_df)

    # ai_stock = concept_series[concept_series['AI概念'] == 1.].index.tolist()
    # df = holding_ori[holding_ori['fund_name'] == '宽德九臻'][['ticker', 'sec_name', 'weight']]
    # df.set_index('ticker', inplace=True)
    # idx = set(df.index).intersection(set(ai_stock))
    # df.loc[idx, 'AI-标记'] = 1.
    # df['AI-标记'].fillna(0., inplace=True)
    # df.sort_values(by='weight', ascending=False, inplace=True)

    return portfolio_concept


def small_cap_stocks_counts(trade_date, include_fund_list):
    # 持仓
    sql_script = "SELECT * FROM private_fund_holding where trade_date = '{}'".format(trade_date)
    engine = create_engine(engine_params)
    holding_df = pd.read_sql(sql_script, engine)
    holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    holding_df = holding_df[holding_df['fund_name'].isin(include_fund_list)]
    holding_df = pd.pivot_table(holding_df, index='ticker', columns='fund_name', values='weight').fillna(0.)
    # 微盘指数成分股
    trade_date_wind = datetime.datetime.strptime(trade_date, "%Y%m%d").strftime('%Y-%m-%d')
    res = w.wset("sectorconstituent", "date={};windcode=8841431.WI".format(trade_date_wind))
    index_components = pd.DataFrame(res.Data, index=res.Fields).T
    index_components['trade_date'] = index_components['date'].apply(lambda x: x.strftime('%Y%m%d'))
    index_components['ticker'] = index_components['wind_code'].apply(lambda x: x.split('.')[0])
    include_ticker_list = index_components['ticker'].tolist()
    # 统计
    count_df = pd.DataFrame(index=holding_df.columns, columns=['总持仓权重', '微盘股持仓权重', '总持股数量', '持微盘股数量'])
    for name in holding_df.columns:
        t_df = holding_df[name].copy()
        t_df = t_df[t_df.gt(1e-6)]
        count_df.loc[name, '总持仓权重'] = t_df.sum()
        count_df.loc[name, '微盘股持仓权重'] = t_df.reindex(include_ticker_list).sum()
        count_df.loc[name, '总持股数量'] = t_df.shape[0]
        count_df.loc[name, '持微盘股数量'] = t_df.reindex(include_ticker_list).dropna().shape[0]

    return count_df


if __name__ == '__main__':
    # tmp = HoldingAnalysor("宽德九臻", "20230930",
    #                       "000905", mode="single").get_construct_result(isPlot=False)

    # dis_df = HoldingDistribution('20221220', '20230331', '因诺聚配中证500指数增强').get_construct_result()
    # print(dis_df)

    # name_list = ['托特中证1000指数增强1号', '因诺聚配中证500指数增强', '凡二量化选股3号1期', '千衍六和3号',
    #              '乾象中证500指数增强1号', '超量子500增强2号', '衍复臻选指数增强一号', '衍复臻选中证1000指数增强一号']
    # name_list = ['超量子500增强2号', '凡二量化选股3号1期', '星阔广厦1号中证500指数增强', '千衍六和3号', '铭量中证500增强1号']
    # HoldingCompare('20230930', '000905', name_list).run()
    # concept_compare("20230331", name_list)
    # small_cap_stocks_counts("20230331", ['博普万维量化多头1号'])

    f_name = "乾象中证500指数增强1号"
    d_list = pd.read_sql("SELECT distinct trade_date FROM private_fund_holding where fund_name = '{}'".format(
        f_name), create_engine(engine_params))
    d_list = [datetime.datetime.strftime(x, '%Y%m%d') for x in d_list['trade_date'].tolist()]
    d_list = [x for x in d_list if x >= '20230930']
    exposure_list = []
    industry_list = []
    distribution_list = []
    concept_list = []
    for p_date in d_list:
        print(p_date)
        rs = HoldingAnalysor(f_name, p_date, "000905").get_construct_result(isPlot=False)
        exposure_list.append(rs['style_df']['主动暴露'].to_frame(p_date))
        industry_list.append(rs['ind_df']['主动暴露'].to_frame(p_date))
        distribution_list.append(rs['bm_distribution'].to_frame(p_date))
        concept_list.append(rs['concept_df']['主动暴露'].to_frame(p_date))

    exp_df = pd.concat(exposure_list, axis=1)
    industry_df = pd.concat(industry_list, axis=1)
    dis_df = pd.concat(distribution_list, axis=1)
    cp_df = pd.concat(concept_list, axis=1)
    print("===============持仓分析结束==================")

    # res = prediction_test("20230930", ['白鹭精选量化鲲鹏十号', '衍复臻选指数增强一号', '乾象中证500指数增强1号', '磐松500指增'])
    # print(res)
