"""
Kevin的标的池跟踪模块：tracker
"""
import os
import numpy as np
import pandas as pd
import hbshare as hbs
import datetime
from sqlalchemy import create_engine
from prettytable import PrettyTable
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list
from hbshare.quant.Kevin.quant_room.MyUtil.util_func import cal_annual_return, cal_annual_volatility
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
import plotly.express as px
import plotly
import plotly.graph_objs as go
from plotly.offline import plot as plot_ly
import plotly.figure_factory as ff


def get_track_config_from_db():
    params_tmp = {
        "ip": "192.168.223.152",
        "user": "readonly",
        "pass": "c24mg2e6",
        "port": "3306",
        "database": "riskmodel"
    }
    engine_tmp = "mysql+pymysql://{}:{}@{}:{}/{}".format(params_tmp['user'], params_tmp['pass'],
                                                         params_tmp['ip'],
                                                         params_tmp['port'], params_tmp['database'])

    sql_script = "SELECT * FROM tracker"
    engine = create_engine(engine_tmp)
    data = pd.read_sql(sql_script, engine)

    return data


def write_config_to_DB(table_name, is_increment=1):
    data = pd.read_excel(os.path.join("D:\\量化产品跟踪\\tracker", "config.xlsx"), sheet_name=0)
    if is_increment == 1:
        sql_script = "delete from {}".format(table_name)
        # delete first
        delete_duplicate_records(sql_script)
        # add new records
        WriteToDB().write_to_db(data, table_name)
    else:
        sql_script = """
            create table {}(
            id int auto_increment primary key,
            fund_id varchar(10),
            fund_name varchar(100),
            pool varchar(20),
            strategy_type varchar(20),
            level2type varchar(20),
            level3type varchar(20),
            abr varchar(20),
            aum varchar(20),
            start_date date)
        """.format(table_name)
        create_table(table_name, sql_script)
        WriteToDB().write_to_db(data, table_name)


def plot_render(plot_dic, width=1200, height=800, **kwargs):
    kwargs['output_type'] = 'div'
    plot_str = plotly.offline.plot(plot_dic, **kwargs)
    print('%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (height, width, plot_str))


class FundTracker:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    @staticmethod
    def _load_benchmark(start_date, end_date, benchmark_id):
        sql_script = ("SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE FROM st_market.t_st_zs_hq WHERE "
                      "ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}").format(benchmark_id, start_date, end_date)
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        data = pd.DataFrame(res['data'])
        data['TRADEDATE'] = data['TRADEDATE'].map(str)
        benchmark_df = data.set_index('TRADEDATE')['TCLOSE']

        return benchmark_df

    def _load_data(self):
        config_df = get_track_config_from_db()
        self.config_df = config_df
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        return_dict = {}
        "=================================================500指增======================================================="
        fund_dict = config_df[config_df['level2type'] == "500指增"].set_index('abr')['fund_id'].to_dict()
        dt_df = config_df[(config_df['level2type'] == "500指增") & (~config_df['start_date'].isnull())]
        dt_df['start_date'] = dt_df['start_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        dt_dict = dt_df.set_index('abr')['start_date'].to_dict()
        fund_nav = get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict).reindex(
            trading_day_list)
        # 净值缺失提醒
        print("===================================500指增净值缺失===================================")
        na_counts = fund_nav.isnull().sum(axis=1)
        na_dates = na_counts[na_counts > 0].index.tolist()
        for date in na_dates:
            na_names = fund_nav.loc[date][fund_nav.loc[date].isna()].index.to_list()
            true_na = []
            for name in na_names:
                if name in dt_df['abr'].tolist():
                    if dt_dict.get(name) <= date:
                        true_na.append(name)
                    else:
                        continue
                else:
                    true_na.append(name)
            if len(true_na) >= 1:
                print("{}期: 缺失{}".format(date, true_na))
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
        benchmark_series = self._load_benchmark(self.start_date, self.end_date, '000905').reindex(
            trading_day_list).pct_change().dropna()
        return_df = fund_nav.pct_change(fill_method=None).dropna(how='all').sub(benchmark_series, axis=0).sort_index()
        # return_df = return_df.dropna(axis=1)
        return_dict['500_alpha'] = return_df
        "=================================================1000指增======================================================"
        fund_dict = config_df[config_df['level2type'] == "1000指增"].set_index('abr')['fund_id'].to_dict()
        dt_df = config_df[(config_df['level2type'] == "1000指增") & (~config_df['start_date'].isnull())]
        dt_df['start_date'] = dt_df['start_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        dt_dict = dt_df.set_index('abr')['start_date'].to_dict()
        fund_nav = get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict).reindex(
            trading_day_list)
        # 净值缺失提醒
        print("===================================1000指增净值缺失===================================")
        na_counts = fund_nav.isnull().sum(axis=1)
        na_dates = na_counts[na_counts > 0].index.tolist()
        for date in na_dates:
            na_names = fund_nav.loc[date][fund_nav.loc[date].isna()].index.to_list()
            true_na = []
            for name in na_names:
                if name in dt_df['abr'].tolist():
                    if dt_dict.get(name) <= date:
                        true_na.append(name)
                    else:
                        continue
                else:
                    true_na.append(name)
            if len(true_na) >= 1:
                print("{}期: 缺失{}".format(date, true_na))
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
        benchmark_series = self._load_benchmark(self.start_date, self.end_date, '000852').reindex(
            trading_day_list).pct_change().dropna()
        return_df = fund_nav.pct_change(fill_method=None).dropna(how='all').sub(benchmark_series, axis=0).sort_index()
        # return_df = return_df.dropna(axis=1)
        return_dict['1000_alpha'] = return_df
        "==================================================量化多头======================================================"
        fund_dict = config_df[config_df['strategy_type'] == "量化多头"].set_index('abr')['fund_id'].to_dict()
        dt_df = config_df[(config_df['strategy_type'] == "量化多头") & (~config_df['start_date'].isnull())]
        dt_df['start_date'] = dt_df['start_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        dt_dict = dt_df.set_index('abr')['start_date'].to_dict()
        fund_nav = get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict).reindex(
            trading_day_list)
        # 净值缺失提醒
        print("===================================量化多头净值缺失===================================")
        na_counts = fund_nav.isnull().sum(axis=1)
        na_dates = na_counts[na_counts > 0].index.tolist()
        for date in na_dates:
            na_names = fund_nav.loc[date][fund_nav.loc[date].isna()].index.to_list()
            true_na = []
            for name in na_names:
                if name in dt_df['abr'].tolist():
                    if dt_dict.get(name) <= date:
                        true_na.append(name)
                    else:
                        continue
                else:
                    true_na.append(name)
            if len(true_na) >= 1:
                print("{}期: 缺失{}".format(date, true_na))
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
        benchmark_series = self._load_benchmark(self.start_date, self.end_date, '000852').reindex(
            trading_day_list).pct_change().dropna()
        return_df = fund_nav.pct_change(fill_method=None).dropna(how='all').sub(benchmark_series, axis=0).sort_index()
        return_dict['all_market'] = return_df
        # 市场中性
        # fund_dict = config_df[config_df['strategy_type'] == "市场中性"].set_index('fund_name')['fund_id'].to_dict()
        # fund_nav = get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict).reindex(
        #     trading_day_list).dropna(axis=1)
        # return_df = fund_nav.pct_change(fill_method=None).dropna().sort_index()
        # return_dict['market_neutral'] = return_df
        # 套利
        # fund_dict = config_df[config_df['strategy_type'] == "套利"].set_index('fund_name')['fund_id'].to_dict()
        # fund_nav = get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict).reindex(
        #     trading_day_list).dropna(axis=1)
        # return_df = fund_nav.pct_change(fill_method=None).dropna().sort_index()
        # return_dict['arbitrage'] = return_df

        self.return_dict = return_dict
        self.config_df = config_df

    def alpha_period_index_scatter(self, return_df):
        annual_return = return_df.apply(cal_annual_return, axis=0)
        annual_vol = return_df.apply(cal_annual_volatility, axis=0)
        df = pd.merge(annual_return.to_frame('超额年化收益'), annual_vol.to_frame('超额年化波动'),
                      left_index=True, right_index=True).round(4)
        df = pd.merge(df, self.config_df.set_index('fund_name')['abr'], left_index=True, right_index=True)
        df.rename(columns={"abr": "name"}, inplace=True)

        fig = px.scatter(df, x='超额年化波动', y='超额年化收益', text='name')
        fig.update_traces(
            textposition="top center",
            textfont={'color': '#bebebe', 'size': 12}
        )
        fig.update_layout(
            title_text="<b>500指增收益风险比（22年以来）<b>",
            template='plotly_white',
            width=1000,
            height=600,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.1%', showgrid=True),
            xaxis=dict(showgrid=True, tickformat=',.1%'),
        )

        return fig.data, fig.layout

    def alpha_performance(self, return_df):
        df = return_df.sort_index(ascending=False).iloc[:2].T.round(4)
        df.columns = ["current_week", "pre_week"]
        df = pd.merge(df, self.config_df.set_index('fund_name')['abr'], left_index=True, right_index=True)
        df.rename(columns={"abr": "name"}, inplace=True)

        fig = px.scatter(df, x='pre_week', y='current_week', text='name')
        fig.update_traces(
            textposition="top center",
            textfont={'color': '#bebebe', 'size': 12}
        )
        fig.update_layout(
            title_text="<b>500指增过去两周超额表现<b>",
            template='plotly_white',
            width=1000,
            height=600,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.1%', showgrid=True),
            xaxis=dict(showgrid=True, tickformat=',.1%'),
        )

        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=df['pre_week'].median(),
                      x1=df['pre_week'].max(),
                      y0=df['current_week'].median(),
                      y1=df['current_week'].max(),
                      fillcolor="lightgray",
                      line=dict(color='red', width=2, dash='dot'),
                      opacity=0.2
                      )
        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=df['pre_week'].min(),
                      x1=df['pre_week'].median(),
                      y0=df['current_week'].min(),
                      y1=df['current_week'].median(),
                      fillcolor="lightgray",
                      line=dict(color='green', width=2, dash='dot'),
                      opacity=0.2
                      )

        return fig.data, fig.layout

    @staticmethod
    def table_plot(return_df, fig_width, fig_height):
        cum_return = (1 + return_df).cumprod() - 1
        cum_return = cum_return.iloc[[0, 1, 3, 7]].T
        cum_return.columns = ['上周', '近两周', '近四周', '近八周']
        cum_return = cum_return.sort_values(by='上周', ascending=False)
        cum_return.index.name = "产品名称"
        for col in cum_return.columns:
            cum_return[col] = cum_return[col].apply(lambda x: format(x, '.2%'))
        fig = ff.create_table(cum_return.reset_index())
        fig.layout.autosize = False
        fig.layout.width = fig_width
        fig.layout.height = fig_height

        return fig.data, fig.layout

    @staticmethod
    def plotly_line(df, title_text, figsize=(1000, 600)):
        fig_width, fig_height = figsize
        data = []
        for col in df.columns:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines"
            )
            data.append(trace)

        date_list = df.index.tolist()
        n = int(len(date_list) / 4)
        tick_vals = [i for i in range(0, len(df), n)]
        tick_text = [date_list[i] for i in range(0, len(df), n)]

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
            legend=dict(orientation="h"),
            template='plotly_white'
        )

        return data, layout

    def run(self):
        return_dict = self.return_dict
        # 500指增
        return_df = return_dict['500_alpha']
        data, layout = self.alpha_period_index_scatter(return_df)
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        data, layout = self.alpha_performance(return_df)
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        # 1000指增
        return_df = return_dict['1000_alpha'].sort_index(ascending=False)
        nav_df = (1 + return_df.sort_index()).cumprod()
        nav_df = nav_df / nav_df.iloc[0]
        data, layout = self.plotly_line(nav_df, "<b>1000指增近期走势<b>")
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        data, layout = self.table_plot(return_df, 1000, 40 * return_df.shape[1])
        plot_render({"data": data, "layout": layout}, height=40 * return_df.shape[1])
        # 全市场选股
        return_df = return_dict['all_market'].sort_index(ascending=False).rename(columns={"benchmark": "中证全指"})
        nav_df = (1 + return_df.sort_index()).cumprod()
        nav_df = nav_df / nav_df.iloc[0]
        data, layout = self.plotly_line(nav_df, "<b>全市场选股近期走势<b>")
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        data, layout = self.table_plot(return_df, 1000, 40 * return_df.shape[1])
        plot_render({"data": data, "layout": layout}, height=40 * return_df.shape[1])
        # 市场中性
        return_df = return_dict['market_neutral'].sort_index(ascending=False)
        nav_df = (1 + return_df.sort_index()).cumprod()
        nav_df = nav_df / nav_df.iloc[0]
        data, layout = self.plotly_line(nav_df, "<b>市场中性近期走势<b>")
        plot_render({"data": data, "layout": layout}, width=1000, height=600)
        data, layout = self.table_plot(return_df, 1000, 40 * return_df.shape[1])
        plot_render({"data": data, "layout": layout}, height=40 * return_df.shape[1])

    def cate_analysis(self):
        config_df = self.config_df.copy()
        return_df = self.return_dict['500_alpha'].copy()
        config_df = config_df[config_df['level2type'] == "500指增"]
        config_df['level3type'] = config_df['level3type'].replace('另类', '基本面')
        config_df = config_df[config_df['level3type'] != 'T0']
        cate1 = pd.get_dummies(config_df.set_index('abr')['level3type'])
        cate2 = pd.get_dummies(config_df.set_index('abr')['aum'])
        cate = cate1.merge(cate2, left_index=True, right_index=True)

        # cate['100亿以上'] = cate['100-300亿'] + cate['300亿以上']
        # cate['100亿以下'] = cate[['20亿以下', '20-50亿', '50-100亿']].sum(axis=1)

        cate_list = []
        for col in cate.columns:
            cate_series = return_df[cate[cate[col].gt(0)].index.tolist()].mean(axis=1).to_frame(col)
            cate_list.append(cate_series)
        cate_ret = pd.concat(cate_list, axis=1)
        cate_ret.loc[self.start_date] = 0.
        cate_ret = cate_ret.sort_index()
        cate_nav = (1 + cate_ret).cumprod()

        dt_df = pd.DataFrame({"trade_date": cate_nav.index})
        dt_df['month'] = dt_df['trade_date'].apply(lambda x: datetime.datetime.strptime(x, "%Y%m%d").month)
        month_end = dt_df[dt_df['month'].shift(-1) != dt_df['month']]['trade_date'].tolist()
        month_alpha = cate_nav.reindex(month_end).pct_change().dropna()
        month_alpha['trade_date'] = month_alpha.index
        month_alpha['trade_date'] = month_alpha['trade_date'].apply(
            lambda x: str(datetime.datetime.strptime(x, "%Y%m%d").year) + '.' +
            str(datetime.datetime.strptime(x, "%Y%m%d").month))
        month_alpha = month_alpha.set_index('trade_date')

        return cate_nav, month_alpha

    def alpha_analysis(self):
        # 500指增
        return_df = self.return_dict['500_alpha'].copy()
        return_df_wo_na = return_df.dropna(axis=1)
        "================================================"
        # ori_factor = pd.read_excel("D:\\AlphaBase\\因子分组收益-周度.xlsx", sheet_name="原始因子")
        # ori_factor['trade_date'] = ori_factor['trade_date'].apply(lambda x: x.replace('-', ''))
        # ori_factor = ori_factor.set_index('trade_date')['combine'].to_frame('ori')
        # neu_factor = pd.read_excel("D:\\AlphaBase\\因子分组收益-周度.xlsx", sheet_name="中性化因子")
        # neu_factor['trade_date'] = neu_factor['trade_date'].apply(lambda x: x.replace('-', ''))
        # neu_factor = neu_factor.set_index('trade_date')['combine'].to_frame('neu')
        # trading_day_list = get_trading_day_list(self.start_date, self.end_date, "week")
        # style_df = ori_factor.merge(
        #     neu_factor, left_index=True, right_index=True).reindex(trading_day_list).pct_change().dropna()
        # df = return_df_wo_na.merge(style_df, left_index=True, right_index=True)
        "================================================"
        nav_df = (1 + return_df_wo_na).cumprod()
        nav_df.loc[self.start_date] = 1.
        nav_df = nav_df.sort_index()
        portfolio_index_df = pd.DataFrame(
            index=nav_df.columns, columns=['超额年化波动', '超额年化收益'])
        portfolio_index_df.loc[:, '超额年化收益'] = nav_df.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
        portfolio_index_df.loc[:, '超额年化波动'] = \
            nav_df.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
        portfolio_index_df['超额年化收益'] = portfolio_index_df['超额年化收益'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['超额年化波动'] = portfolio_index_df['超额年化波动'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df_500 = portfolio_index_df

        recent_df = return_df.tail(8).dropna(axis=1)
        relative_df = recent_df.sub(recent_df.median(axis=1), axis=0)
        w8 = (1 + relative_df).prod() - 1
        w4 = (1 + relative_df.tail(4)).prod() - 1
        rel_strength_500 = w4.to_frame('最近4周').merge(w8.to_frame('最近8周'), left_index=True, right_index=True)
        rel_strength_500['最近4周'] = rel_strength_500['最近4周'].apply(lambda x: format(x, '.2%'))
        rel_strength_500['最近8周'] = rel_strength_500['最近8周'].apply(lambda x: format(x, '.2%'))
        # 1000指增 + 量化多头
        return_df_1000 = self.return_dict['1000_alpha'].copy()
        return_df_am = self.return_dict['all_market'].copy()
        return_df_am.columns = [x + '+' for x in return_df_am.columns]
        return_df = pd.concat([return_df_1000, return_df_am], axis=1)
        return_df_wo_na = return_df.dropna(axis=1)
        # b[include_cols].plot(subplots=True, layout=(4, 4), figsize=(6, 6), sharex=False, title=False)
        nav_df = (1 + return_df_wo_na).cumprod()
        nav_df.loc[self.start_date] = 1.
        nav_df = nav_df.sort_index()
        portfolio_index_df = pd.DataFrame(
            index=nav_df.columns, columns=['超额年化波动', '超额年化收益'])
        portfolio_index_df.loc[:, '超额年化收益'] = nav_df.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
        portfolio_index_df.loc[:, '超额年化波动'] = \
            nav_df.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
        portfolio_index_df['超额年化收益'] = portfolio_index_df['超额年化收益'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['超额年化波动'] = portfolio_index_df['超额年化波动'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df_1000 = portfolio_index_df

        recent_df = return_df.tail(8).dropna(axis=1)
        relative_df = recent_df.sub(recent_df.median(axis=1), axis=0)
        w8 = (1 + relative_df.tail(8)).prod() - 1
        w4 = (1 + relative_df.tail(4)).prod() - 1
        rel_strength_1000 = w4.to_frame('最近4周').merge(w8.to_frame('最近8周'), left_index=True, right_index=True)
        rel_strength_1000['最近4周'] = rel_strength_1000['最近4周'].apply(lambda x: format(x, '.2%'))
        rel_strength_1000['最近8周'] = rel_strength_1000['最近8周'].apply(lambda x: format(x, '.2%'))

        # compare
        compare_df = (1 + self.return_dict['500_alpha'].mean(axis=1)).cumprod().to_frame('500指增').merge(
            (1 + self.return_dict['1000_alpha'].mean(axis=1)).cumprod().to_frame('1000指增'),
            left_index=True, right_index=True)
        compare_df.loc[self.start_date] = 1.
        compare_df = compare_df.sort_index()

        # 500的池子做个拆分 = 代销&FOF + 跟踪&未接触
        pool_500 = self.config_df[self.config_df['level2type'] == '500指增']
        pool_core = pool_500[pool_500['pool'].isin(['代销', 'FOF'])]
        idx = set(pool_core['abr']).intersection(set(rel_strength_500.index))
        rel_strength_500_core = rel_strength_500.loc[idx]
        pool_track = pool_500[pool_500['pool'].isin(['跟踪', '未接触'])]
        idx = set(pool_track['abr']).intersection(set(rel_strength_500.index))
        rel_strength_500_track = rel_strength_500.loc[idx]

        return portfolio_index_df_500, rel_strength_500_core, rel_strength_500_track, portfolio_index_df_1000, \
            rel_strength_1000, compare_df


def arb_tracker(start_date, end_date):
    """
    已接触的套利标的跟踪函数
    """
    fund_dict = {
        "百奕": "SNZ338",
        "悬铃C6": "SNY736",
        "展弘": "SSE631",
        "安值": "SCP765",
        "安值高频": "SXQ849",
        "雸昇": "SVB452",
        "纽达": "SGL183",
        "源晖": "SXA471",
        "锐耐": "SXV513"
    }
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    fund_nav = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(trading_day_list).dropna(axis=1)
    fund_nav /= fund_nav.iloc[0]
    period_return = fund_nav.iloc[-1] - 1
    period_return = period_return.apply(lambda x: format(x, ".2%"))

    table = PrettyTable()
    table.add_column('产品名称', period_return.index.tolist())
    table.add_column('区间收益', period_return.values)
    table.align['产品名称'] = 'c'
    table.align['区间收益'] = 'c'
    print(table)


if __name__ == '__main__':
    # write_config_to_DB("tracker", is_increment=0)
    # 类别分析
    # FundTracker('20211231', '20231215').cate_analysis()
    # 单基金分析: 23年初至今
    FundTracker('20221230', '20231222').alpha_analysis()
    # 套利策略跟踪
    # arb_tracker("20231215", "20231222")