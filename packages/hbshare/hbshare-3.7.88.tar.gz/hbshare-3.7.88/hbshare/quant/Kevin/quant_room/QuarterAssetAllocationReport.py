"""
季度资产报告辅助程序
"""
import numpy as np
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
import os
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go
from Arbitrage_backtest import cal_annual_return
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_trading_day_list

plotly.offline.init_notebook_mode(connected=True)


class QuarterAssetAllocationReport:
    def __init__(self, start_date, end_date, data_path, file_name, frequency="week"):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.file_name = file_name
        self.frequency = frequency
        self._load_data()
        self._load_neu_data()

    def _load_data(self):
        data_with_header = pd.read_excel(
            os.path.join(self.data_path, r"{}".format(self.file_name)), sheet_name='原始净值')
        data = pd.read_excel(os.path.join(self.data_path, r"{}".format(self.file_name)), sheet_name='原始净值', header=1)
        data['t_date'] = data['t_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        data.index = data['t_date']
        cols = data_with_header.columns.tolist()
        # 月末日期
        df = data[['t_date']].sort_index()
        df['month'] = df['t_date'].apply(lambda x: datetime.strptime(x, '%Y%m%d').month)
        df['next_month'] = df['month'].shift(-1).fillna(0.).astype(int)
        df = df[(df['month'] != df['next_month']) & (df['t_date'] >= self.start_date)]
        trading_day_list = sorted(df['t_date'].tolist())

        if self.frequency == "week":
            trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")

        # type
        data_param = dict()
        type_list = [x for x in cols if not x.startswith('Unnamed')]
        for i in range(len(type_list) - 1):
            typ = type_list[i]
            s_index, e_index = cols.index(type_list[i]), cols.index(type_list[i + 1])
            data_slice = data[data.columns[s_index: e_index]]
            if typ in ['量价（500）', '机器学习', '基本面']:
                data_slice['benchmark'] = data['中证500']
            elif typ in ['量价（300）']:
                data_slice['benchmark'] = data['沪深300']
            elif typ in ['量价（1000）']:
                data_slice['benchmark'] = data['中证1000']
            else:
                 pass
            data_slice = data_slice[data_slice.index >= self.start_date].reindex(trading_day_list)
            data_param[type_list[i]] = data_slice
        # 指数
        index_df = data[['沪深300', '中证500', '中证1000']].reindex(trading_day_list)

        self.trading_day_list = trading_day_list
        self.data_param = data_param
        self.index_df = index_df

    def _load_neu_data(self):
        data_with_header = pd.read_excel(
            "D:\\量化产品跟踪\\市场中性\\中性-{}.xlsx".format(self.end_date), sheet_name='原始净值')
        data = pd.read_excel("D:\\量化产品跟踪\\市场中性\\中性-{}.xlsx".format(self.end_date), sheet_name='原始净值', header=1)
        data['t_date'] = data['t_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        data.index = data['t_date']
        cols = data_with_header.columns.tolist()
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        # type
        data_param = dict()
        type_list = [x for x in cols if not x.startswith('Unnamed')]
        for i in range(len(type_list) - 1):
            s_index, e_index = cols.index(type_list[i]), cols.index(type_list[i + 1])
            data_slice = data[data.columns[s_index: e_index]]
            data_slice = data_slice[data_slice.index >= self.start_date].reindex(trading_day_list)
            data_param[type_list[i]] = data_slice

        alpha_df = pd.concat([data_param['高频'], data_param['中低频']], axis=1)
        t0_df = data_param['T0']

        alpha_df = alpha_df.pct_change(limit=1).dropna(axis=0, how='all')
        t0_df = t0_df.pct_change(limit=1).dropna(axis=0, how='all')

        neu_df = alpha_df.mean(axis=1).to_frame('市场中性').merge(
            t0_df.mean(axis=1).to_frame('T0'), left_index=True, right_index=True)
        neu_df.loc[self.start_date] = 0.
        nav_df = (1 + neu_df.sort_index()).cumprod()
        nav_df['trade_date'] = nav_df.index
        nav_df['trade_date'] = nav_df['trade_date'].apply(
            lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        nav_df.set_index('trade_date', inplace=True)

        self.neu_df = nav_df

    def calculate_excess_return(self):
        data_lj = self.data_param['量价（500）']
        data_ml = self.data_param['机器学习']
        data_fd = self.data_param['基本面']
        data_300 = self.data_param['量价（300）']
        data_1000 = self.data_param['量价（1000）']

        return_lj = data_lj.pct_change(limit=1).dropna(axis=0, how='all')
        return_lj['average'] = return_lj[return_lj.columns[:-1]].mean(axis=1)
        return_lj.eval("ave_excess = average - benchmark", inplace=True)

        return_fd = data_fd.pct_change(limit=1).dropna(axis=0, how='all')
        return_fd['average'] = return_fd[return_fd.columns[:-1]].mean(axis=1)
        return_fd.eval("ave_excess = average - benchmark", inplace=True)

        return_ml = data_ml.pct_change(limit=1).dropna(axis=0, how='all')
        return_ml['average'] = return_ml[return_ml.columns[:-1]].mean(axis=1)
        return_ml.eval("ave_excess = average - benchmark", inplace=True)

        return_300 = data_300.pct_change(limit=1).dropna(axis=0, how='all')
        return_300['average'] = return_300[return_300.columns[:-1]].mean(axis=1)
        return_300.eval("ave_excess = average - benchmark", inplace=True)

        return_1000 = data_1000.pct_change(limit=1).dropna(axis=0, how='all')
        return_1000['average'] = return_1000[return_1000.columns[:-1]].mean(axis=1)
        return_1000.eval("ave_excess = average - benchmark", inplace=True)

        data_500 = data_lj[data_lj.columns[:-1]].merge(
            data_fd[data_fd.columns[:-1]], left_index=True, right_index=True).merge(
            data_ml, left_index=True, right_index=True)

        return_500 = data_500.pct_change(limit=1).dropna(axis=0, how='all')
        return_500['average'] = return_500[return_500.columns[:-1]].mean(axis=1)
        return_500.eval("ave_excess = average - benchmark", inplace=True)

        # 指增的趋同度
        include_cols = [x for x in return_500.columns if x not in ['benchmark', 'average', 'ave_excess']]
        week_excess = return_500[include_cols].sub(return_500['benchmark'], axis=0)
        conver_df = week_excess.apply(lambda x: x.dropna().std(), axis=1).sort_index()

        compare_df = return_lj['ave_excess'].to_frame('量价类').merge(
            return_fd['ave_excess'].to_frame('基本面'), left_index=True, right_index=True).merge(
            return_ml['ave_excess'].to_frame('机器学习'), left_index=True, right_index=True)

        compare_df2 = return_300['ave_excess'].to_frame('300指增').merge(
            return_500['ave_excess'].to_frame('500指增'), left_index=True, right_index=True).merge(
            return_1000['ave_excess'].to_frame('1000指增'), left_index=True, right_index=True)

        # if necessary
        df = return_500[['average', 'benchmark', 'ave_excess']].copy()
        df['超额净值'] = (1 + df['ave_excess']).cumprod()
        df['超额最大回撤（右）'] = df['超额净值'] / df['超额净值'].cummax() - 1
        df['滚动半年年化超额'] = df['ave_excess'].rolling(26).apply(cal_annual_return)
        df['500指增平均绝对收益'] = (1 + df['average']).cumprod()
        df['中证500'] = (1 + df['benchmark']).cumprod()

        return compare_df, compare_df2, conver_df, df

    def calculate_index_return(self):
        index_df = self.index_df.copy()
        return_df = index_df.pct_change().dropna(axis=0, how='all')

        return return_df

    def calculate_market_vol(self):
        # 直接从本地取
        path = 'D:\\kevin\\risk_model_jy\\RiskModel\\data\\common_data\\chg_pct'
        filenames = os.listdir(path)
        filenames = [x for x in filenames if (
                    not x.split('.')[0] < self.start_date and x.split('.')[0] <= self.end_date)]
        date_list = []
        vol_list = []
        for name in filenames:
            date_list.append(name.split('.')[0])
            df = pd.read_csv(os.path.join(path, name)).dropna()
            df = df[(df['dailyReturnReinv'] >= -0.2) & (df['dailyReturnReinv'] <= 0.2)]
            vol_list.append(df['dailyReturnReinv'].std())

        vol_df = pd.DataFrame({"date": date_list, "vol": vol_list})

        return vol_df


def plotly_bar(df, title_text, save_path):
    cols = df.columns.tolist()
    color_list = ['rgb(216, 0, 18)', 'rgb(60, 127, 175)', 'rgb(35, 35, 35)']
    data = []
    for i in range(len(cols)):
        col = cols[i]
        trace = go.Bar(
            x=df.index.tolist(),
            y=df[col],
            name=col,
            marker=dict(color=color_list[i]),
            # width=0.2,
        )
        data.append(trace)

    layout = go.Layout(
        title=dict(text=title_text, x=0.07, y=0.85),
        autosize=False, width=1200, height=500,
        yaxis=dict(tickfont=dict(size=12), tickformat=',.1%', showgrid=True),
        xaxis=dict(showgrid=True),
        legend=dict(orientation="h", x=0.35),
        template='plotly_white'
    )
    fig = go.Figure(data=data, layout=layout)

    plot_ly(fig, filename=save_path, auto_open=False)


def plotly_line(df, day_list, title_text, save_path):
    trace = go.Scatter(
        x=df['date'],
        y=df['vol'],
        mode="lines",
        marker=dict(color='rgb(35, 35, 35)')
    )

    data = [trace]

    tick_vals = [df['date'].tolist().index(x) for x in day_list]
    tick_text = [x[:6] for x in day_list]

    layout = go.Layout(
        title=dict(text=title_text, x=0.07, y=0.85),
        autosize=False, width=1200, height=400,
        yaxis=dict(tickfont=dict(size=12), tickformat=',.1%', showgrid=True),
        xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
        template='plotly_white'
    )

    fig = go.Figure(data=data, layout=layout)

    plot_ly(fig, filename=save_path, auto_open=False)


def save_excess_data_to_excel(df1, df2, df3, conver_series, s_date):
    writer = pd.ExcelWriter(
        'D:\\Alpha_Monthly_Report\\alpha_data\\超额数据.xlsx', engine='xlsxwriter')
    # excess_df1
    return_df = df1.copy()
    return_df.loc[s_date] = 0.
    nav_df = (1 + return_df.sort_index()).cumprod()
    nav_df['trade_date'] = nav_df.index
    nav_df['trade_date'] = nav_df['trade_date'].apply(
        lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    nav_df.set_index('trade_date', inplace=True)
    nav_df.to_excel(writer, sheet_name="500指增分类别")
    # excess_df2
    return_df = df2.copy()
    return_df.loc[s_date] = 0.
    nav_df = (1 + return_df.sort_index()).cumprod()
    nav_df['trade_date'] = nav_df.index
    nav_df['trade_date'] = nav_df['trade_date'].apply(
        lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    nav_df.set_index('trade_date', inplace=True)
    nav_df.to_excel(writer, sheet_name="分对标基准")
    # neu_df
    df3.to_excel(writer, sheet_name="中性")
    # alpha_conver
    conver_df = conver_series.to_frame('指增超额分散度')
    conver_df['trade_date'] = conver_df.index
    conver_df['trade_date'] = conver_df['trade_date'].apply(
        lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    conver_df.set_index('trade_date', inplace=True)
    conver_df.to_excel(writer, sheet_name="指增超额分散度")

    writer.close()


def cross_sectional_vol(start_date, end_date):
    """
    1800以外的截面波动率数据
    """
    sql_script = "SELECT * FROM mac_stock_cross_section_vol"
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    data = data.set_index('trade_date')[['OTHER']]
    data['10日平均'] = data['OTHER'].rolling(10).mean()
    data['20日平均'] = data['OTHER'].rolling(20).mean()

    data = data.rename(
        columns={"OTHER": "截面波动率"})[['截面波动率', '10日平均', '20日平均']].loc[start_date: end_date].sort_index()
    data['trade_date'] = data.index
    data['trade_date'] = data['trade_date'].apply(
        lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
    data.set_index('trade_date', inplace=True)

    return data


if __name__ == '__main__':
    # cross_sectional_vol("20150105", "20230630")

    allo_rep = QuarterAssetAllocationReport(
        start_date='20161230', end_date='20231229',
        data_path='D:\\量化产品跟踪\\指数增强', file_name='指增-20231229.xlsx', frequency="week")

    excess_df, excess_df2, alpha_conver, _ = allo_rep.calculate_excess_return()

    # 新增超额净值数据
    # neu_nav_df = allo_rep.neu_df
    # save_excess_data_to_excel(excess_df, excess_df2, neu_nav_df, alpha_conver, allo_rep.start_date)

    excess_df['date'] = excess_df.index
    excess_df['date'] = excess_df['date'].apply(lambda x: x[:6])
    excess_df = excess_df.set_index('date')[['机器学习', '基本面', '量价类']]
    plotly_bar(excess_df, "股票量化策略超额表现", "D:\\市场微观结构图\\股票量化策略超额表现-分策略.html")

    excess_df2['date'] = excess_df2.index
    excess_df2['date'] = excess_df2['date'].apply(lambda x: x[:6])
    excess_df2 = excess_df2.set_index('date')[['300指增', '500指增', '1000指增']]
    plotly_bar(excess_df2, "股票量化策略超额表现", "D:\\市场微观结构图\\股票量化策略超额表现-分基准.html")

    index_return_df = allo_rep.calculate_index_return()
    index_return_df['date'] = index_return_df.index
    index_return_df['date'] = index_return_df['date'].apply(lambda x: x[:6])
    index_return_df = index_return_df.set_index('date')
    plotly_bar(index_return_df, "指数表现", "D:\\市场微观结构图\\指数表现.html")

    market_vol = allo_rep.calculate_market_vol()
    plotly_line(market_vol, allo_rep.trading_day_list,
                "市场横截面波动率", "D:\\市场微观结构图\\市场横截面波动率.html")
