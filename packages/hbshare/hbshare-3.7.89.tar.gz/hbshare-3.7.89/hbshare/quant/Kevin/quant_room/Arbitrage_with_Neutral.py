"""
套利 + 市场中性回测模块
"""
import numpy as np
import hbshare as hbs
from MyUtil.data_loader import get_trading_day_list, get_fund_nav_from_sql
from MyUtil.util_func import cal_annual_return, cal_annual_volatility, cal_max_drawdown, cal_sharpe_ratio
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_daily_nav_from_work, fetch_data_batch_hbs
from hbshare.quant.Kevin.quant_room.QuarterAssetAllocationReport import QuarterAssetAllocationReport
import pandas as pd
import datetime
import riskfolio as rp
from tqdm import tqdm


class test:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        arb_dict = {
            "展弘稳进1号1期": "SE8723",
            # "盛冠达股指套利3号": "SGS597",
            "蒙玺分形3号": "SGP290",
            # "稳博中睿6号": "SJB143",
            "稳博中性稳稳系列1号": "SQP800",
            "蒙玺竞起6号": "SSM855",
            "展弘量化精选1号1期": "SSE967",
            "百奕传家一号": "SJS027",
            "平行公理同余4号": "STT643",
            "悬铃C号6期": "SNY736",
        }

        date_list = get_trading_day_list(self.start_date, self.end_date, frequency='week')
        df = get_fund_nav_from_sql(self.start_date, self.end_date, arb_dict).reindex(date_list)
        # 稳博
        df.loc[:"20210618", "稳博中性稳稳系列1号"] = np.NAN
        # 展弘精选
        df.loc[:"20220304", "展弘量化精选1号1期"] = np.NAN
        df.loc["20220902", "展弘量化精选1号1期"] = 1.0522
        df.loc["20220909", "展弘量化精选1号1期"] = 1.0513
        return_df = df.pct_change().dropna(how='all')
        # 蒙玺
        mx_df = pd.read_excel('D:\\蒙玺竞起6号净值.xlsx', sheet_name=0)
        mx_df['trade_date'] = mx_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        mx_df.rename(columns={"nav": "蒙玺竞起6号"}, inplace=True)
        tmp = mx_df.set_index('trade_date').reindex(date_list).dropna().pct_change().dropna()
        return_df.loc[tmp.index, "蒙玺竞起6号"] = tmp.loc[tmp.index, '蒙玺竞起6号']
        return_df.loc[:"20210104", "蒙玺分形3号"] = np.NAN
        # 百奕
        return_df.loc[:"20200508", '百奕传家一号'] = np.NAN
        # 悬铃
        return_df.loc[:"20210528", '悬铃C号6期'] = np.NAN

        tmp = get_daily_nav_from_work(self.start_date, self.end_date, {"平行公理同余4号": "STT643"})
        tmp = tmp.reindex(date_list).loc["20220701":].pct_change().dropna()
        return_df.loc[tmp.index, "平行公理同余4号"] = tmp.loc[tmp.index, '平行公理同余4号']

        arb_return = return_df.mean(axis=1)

        # neu_dict = {
        #     "量锐": "SX4966",
        #     "明汯": "SCQ804",
        #     "启林": "SEA766",
        #     "卓识": "SCL316",
        #     "衍复": "SJH864",
        #     "伯兄": "SL3246",
        #     "概率": "SNM976",
        #     "星阔": "SNU704",
        #     "诚奇": "SNR622",
        #     "乾象": "P48467"
        # }
        # neu_df = get_fund_nav_from_sql(self.start_date, self.end_date, neu_dict).reindex(
        #     date_list)
        # neu_return = neu_df.pct_change().dropna(how='all').mean(axis=1)

        data_with_header = pd.read_excel('D:\\量化产品跟踪\\市场中性\\中性-20220909.xlsx', sheet_name='原始净值')
        data = pd.read_excel('D:\\量化产品跟踪\\市场中性\\中性-20220909.xlsx', sheet_name='原始净值', header=1)
        data['t_date'] = data['t_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        data.index = data['t_date']
        cols = data_with_header.columns.tolist()

        data_param = dict()
        type_list = [x for x in cols if not x.startswith('Unnamed')]
        for i in range(len(type_list) - 1):
            s_index, e_index = cols.index(type_list[i]), cols.index(type_list[i + 1])
            data_slice = data[data.columns[s_index: e_index]]
            data_slice = data_slice[data_slice.index >= self.start_date].reindex(date_list)
            data_param[type_list[i]] = data_slice

        nav_df = pd.concat([data_param['高频'], data_param['中低频']], axis=1)
        cols = [x for x in nav_df.columns if x not in ['英旷尊享1号', '天算顺势1号', '茂源资本-巴舍里耶2期', '星阔云起1号市场中性',
                                                       '佳期星际一期', '概率一号', '世纪前沿量化对冲9号', '龙旗紫微量化对冲',
                                                       '量锐18号', '平方和智增1号']]
        nav_df = nav_df[cols]
        neu_return = nav_df.pct_change(limit=1).dropna(how='all').mean(axis=1)

        return_df = arb_return.to_frame('arbitrage').merge(
            neu_return.to_frame('neutral'), left_index=True, right_index=True)
        # nav_df = (1 + return_df).cumprod()

        self.return_df = return_df

    def run(self):
        return_df = self.return_df
        nav_df = (1 + return_df).cumprod()
        # 固定权重再平衡
        nav_df['trade_date'] = nav_df.index
        nav_df['trade_dt'] = nav_df['trade_date'].apply(lambda x: datetime.datetime.strptime(x, "%Y%m%d"))
        nav_df['month'] = nav_df['trade_dt'].apply(lambda x: x.month)
        nav_df['year'] = nav_df['trade_dt'].apply(lambda x: x.year)
        month_end = nav_df[nav_df['month'].shift(-1) != nav_df['month']]['trade_date'].tolist()
        month_end.append("20181228")
        reb_list = sorted(month_end)[::3]

        weight_df = pd.DataFrame(index=reb_list, columns=["arbitrage", "neutral"])
        weight_df.iloc[0] = 0.5
        weight_df.iloc[1] = 0.5

        for i in range(0, len(reb_list) - 1):
            pre_date, t_date = reb_list[i], reb_list[i + 1]
            period_data = return_df[(return_df.index > pre_date) & (return_df.index <= t_date)]
            port = rp.Portfolio(returns=period_data)
            model = 'Classic'  # 可以为Classic (historical), BL (Black Litterman)、FM (Factor Model)或BLFM
            rm = 'MV'  # 风险度量指标，MV表示方差，本工具包共支持13种风险度量指标
            # obj = 'Sharpe'  # 目标函数, 可选有MinRisk, MaxRet, Utility或Sharpe
            hist = True  # 是否基于历史数据计算风险收益
            rf = 0  # 无风险利率
            # l = 0

            method_mu = 'hist'  # 还支持其他方法，详见文档
            method_cov = 'hist'  # 还支持其他方法，详见文档
            port.assets_stats(method_mu=method_mu, method_cov=method_cov)

            # w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)

            w = port.rp_optimization(model=model, rm=rm, rf=rf, hist=hist)

            weight_df.loc[t_date] = w['weights']

        # weight_df = pd.DataFrame(index=reb_list, columns=["arbitrage", "neutral"])
        # weight_df['arbitrage'] = 0.7
        # weight_df['neutral'] = 0.3

        ret_list = []
        for i in range(len(reb_list) - 1):
            t_date, next_date = reb_list[i], reb_list[i + 1]
            t_weight = weight_df.loc[t_date]
            period_data = return_df[(return_df.index > t_date) & (return_df.index <= next_date)]
            port = t_weight.dot((1 + period_data).cumprod().T)
            port_return = port.pct_change()
            port_return.iloc[0] = port.iloc[0] - 1

            ret_list.append(port_return)

        ret_series = pd.concat(ret_list).sort_index()

        return_df = return_df.merge(ret_series.to_frame('port'), left_index=True, right_index=True)
        nav_df = (1 + return_df).cumprod()

        portfolio_index_df = pd.DataFrame(
            index=nav_df.columns, columns=['超额年化收益', '超额年化波动', '最大回撤', 'Sharpe', '胜率', '平均损益比',
                                           '2019', '2020', '2021', '2022', '2022(年化)'])
        portfolio_index_df.loc[:, '超额年化收益'] = nav_df.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
        portfolio_index_df.loc[:, '超额年化波动'] = \
            nav_df.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
        portfolio_index_df.loc[:, '最大回撤'] = nav_df.apply(cal_max_drawdown, axis=0)
        portfolio_index_df.loc[:, 'Sharpe'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
        portfolio_index_df.loc[:, '胜率'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: x.gt(0).sum() / len(x), axis=0)
        portfolio_index_df.loc[:, '平均损益比'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
        portfolio_index_df['2019'] = (nav_df.loc["20191227"] - 1).tolist()
        portfolio_index_df['2020'] = (nav_df.loc["20201231"] / nav_df.loc["20191227"] - 1).tolist()
        portfolio_index_df['2021'] = (nav_df.loc["20211231"] / nav_df.loc["20201231"] - 1).tolist()
        portfolio_index_df['2022'] = ((nav_df.loc["20220909"] / nav_df.loc["20211231"]) - 1).tolist()
        portfolio_index_df['2022(年化)'] = ((nav_df.loc["20220909"] / nav_df.loc["20211231"]) ** (52 / 35) - 1).tolist()
        portfolio_index_df.index.name = '产品名称'
        portfolio_index_df.reset_index(inplace=True)
        # 格式处理
        portfolio_index_df['超额年化收益'] = portfolio_index_df['超额年化收益'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['超额年化波动'] = portfolio_index_df['超额年化波动'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['最大回撤'] = portfolio_index_df['最大回撤'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['Sharpe'] = portfolio_index_df['Sharpe'].round(2)
        portfolio_index_df['胜率'] = portfolio_index_df['胜率'].apply(lambda x: format(x, '.1%'))
        portfolio_index_df['平均损益比'] = portfolio_index_df['平均损益比'].round(2)
        portfolio_index_df['2019'] = portfolio_index_df['2019'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['2020'] = portfolio_index_df['2020'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['2021'] = portfolio_index_df['2021'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['2022'] = portfolio_index_df['2022'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['2022(年化)'] = portfolio_index_df['2022(年化)'].apply(lambda x: format(x, '.2%'))

        portfolio_index_df.to_clipboard()


class ArbitrageSimulation:
    def __init__(self, start_date, end_date, join_date):
        self.start_date = start_date
        self.end_date = end_date
        self.join_date = join_date

    @staticmethod
    def _get_arbitrage_fund_info():
        sql_script = ("SELECT clrq, jjdm, jjmc, jjfl, ejfl FROM st_hedge.t_st_jjxx where "
                      "cpfl = '4' and jjfl = '7' and jjzt = '0' and m_opt_type <> '03'")
        data = fetch_data_batch_hbs(sql_script, "highuser")
        # 剔除：计划、信托
        data = data[~data['jjmc'].str.contains('计划')]
        data = data[~data['jjmc'].str.contains('信托')]
        # 成立满一年以上
        data = data[data['clrq'] <= '20220804']

        fund_dict = data.set_index('jjmc')['jjdm'].to_dict()

        return fund_dict

    @staticmethod
    def _get_fund_nav_from_sql(start_date, end_date, fund_dict):
        """
        获取db的私募基金净值数据
        """
        nav_series_list = []
        for name, fund_id in tqdm(fund_dict.items()):
            sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                         "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(fund_id, start_date, end_date)
            res = hbs.db_data_query("highuser", sql_script, page_size=5000)
            if len(res['data']) != 0:
                data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
                data.name = name
                nav_series_list.append(data)
            else:
                pass
        df = pd.concat(nav_series_list, axis=1).sort_index()

        return df

    def run(self):
        fund_dict = self._get_arbitrage_fund_info()
        nav_df = self._get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict)
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        nav_df = nav_df.reindex(trading_day_list)
        # 数据缺失剔除
        selected_names = []
        for col in nav_df.columns:
            s_date, e_date = nav_df[col].first_valid_index(), nav_df[col].last_valid_index()
            tmp = nav_df.loc[s_date: e_date, col]
            na_ratio = tmp.isnull().sum() / len(tmp)
            if na_ratio < 0.1 and len(tmp) >= 52:
                selected_names.append(col)
            else:
                continue
        nav_df = nav_df[selected_names]
        return_df = nav_df.pct_change(limit=1).dropna(axis=0, how='all')
        # 截面去极值
        arb_return = pd.Series(index=return_df.index, dtype=float)
        for date in return_df.index.tolist():
            date_t_return = return_df.loc[date].dropna()
            median = date_t_return.median()
            new_median = abs(date_t_return - median).median()
            up = median + 5 * new_median
            down = median - 5 * new_median
            date_t_return = date_t_return[(date_t_return.gt(down)) & (date_t_return.lt(up))]
            arb_return.loc[date] = date_t_return.mean()
        "===========================中性==============================="
        data_with_header = pd.read_excel('D:\\量化产品跟踪\\市场中性\\中性-20230908.xlsx', sheet_name='原始净值')
        data = pd.read_excel('D:\\量化产品跟踪\\市场中性\\中性-20230908.xlsx', sheet_name='原始净值', header=1)
        data['t_date'] = data['t_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        data.index = data['t_date']
        cols = data_with_header.columns.tolist()

        data_param = dict()
        type_list = [x for x in cols if not x.startswith('Unnamed')]
        for i in range(len(type_list) - 1):
            s_index, e_index = cols.index(type_list[i]), cols.index(type_list[i + 1])
            data_slice = data[data.columns[s_index: e_index]]
            # data_slice = data_slice[data_slice.index >= self.start_date].reindex(date_list)
            data_param[type_list[i]] = data_slice

        nav_df = pd.concat([data_param['高频'], data_param['中低频']], axis=1)
        nav_df = nav_df.reindex(trading_day_list)
        # 数据缺失剔除
        selected_names = []
        for col in nav_df.columns:
            s_date, e_date = nav_df[col].first_valid_index(), nav_df[col].last_valid_index()
            tmp = nav_df.loc[s_date: e_date, col]
            na_ratio = tmp.isnull().sum() / len(tmp)
            if na_ratio < 0.1 and len(tmp) >= 52:
                selected_names.append(col)
            else:
                continue
        nav_df = nav_df[selected_names]
        return_df = nav_df.pct_change(limit=1).dropna(axis=0, how='all')
        # 截面去极值
        neu_return = pd.Series(index=return_df.index, dtype=float)
        for date in return_df.index.tolist():
            date_t_return = return_df.loc[date].dropna()
            median = date_t_return.median()
            new_median = abs(date_t_return - median).median()
            up = median + 5 * new_median
            down = median - 5 * new_median
            date_t_return = date_t_return[(date_t_return.gt(down)) & (date_t_return.lt(up))]
            neu_return.loc[date] = date_t_return.mean()

        return_compare = arb_return.to_frame('arbitrage').merge(
            neu_return.to_frame('neutral'), left_index=True, right_index=True)
        # 添加DMA模拟
        return_compare['dma'] = (return_compare['neutral'] - 0.03 / 52) * 4
        return_compare.loc[self.start_date] = 0.
        return_compare.sort_index(inplace=True)
        nav_df = (1 + return_compare).cumprod()
        nav_df['combine'] = nav_df['arbitrage'] * 0.5 + nav_df['neutral'] * 0.5
        nav_df['10%dma'] = nav_df['arbitrage'] * 0.5 + nav_df['neutral'] * 0.4 + nav_df['dma'] * 0.1
        nav_df['20%dma'] = nav_df['arbitrage'] * 0.5 + nav_df['neutral'] * 0.3 + nav_df['dma'] * 0.2
        # 指标计算
        portfolio_index_df = pd.DataFrame(
            index=nav_df.columns, columns=['年化收益', '年化波动', '最大回撤', 'Sharpe', '胜率', '平均损益比',
                                           '2019', '2020', '2021', '2022', '2023(年化)'])
        portfolio_index_df.loc[:, '年化收益'] = nav_df.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
        portfolio_index_df.loc[:, '年化波动'] = \
            nav_df.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
        portfolio_index_df.loc[:, '最大回撤'] = nav_df.apply(cal_max_drawdown, axis=0)
        portfolio_index_df.loc[:, 'Sharpe'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
        portfolio_index_df.loc[:, '胜率'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: x.gt(0).sum() / len(x), axis=0)
        portfolio_index_df.loc[:, '平均损益比'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
        portfolio_index_df['2019'] = (nav_df.loc["20191227"] - 1).tolist()
        portfolio_index_df['2020'] = (nav_df.loc["20201231"] / nav_df.loc["20191227"] - 1).tolist()
        portfolio_index_df['2021'] = (nav_df.loc["20211231"] / nav_df.loc["20201231"] - 1).tolist()
        portfolio_index_df['2022'] = ((nav_df.loc["20221230"] / nav_df.loc["20211231"]) - 1).tolist()
        portfolio_index_df['2023(年化)'] = ((nav_df.loc["20230825"] / nav_df.loc["20221230"]) ** (52 / 33) - 1).tolist()
        portfolio_index_df.index.name = '产品名称'
        portfolio_index_df.reset_index(inplace=True)
        # 格式处理
        portfolio_index_df['年化收益'] = portfolio_index_df['年化收益'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['年化波动'] = portfolio_index_df['年化波动'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['最大回撤'] = portfolio_index_df['最大回撤'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['Sharpe'] = portfolio_index_df['Sharpe'].round(2)
        portfolio_index_df['胜率'] = portfolio_index_df['胜率'].apply(lambda x: format(x, '.1%'))
        portfolio_index_df['平均损益比'] = portfolio_index_df['平均损益比'].round(2)
        portfolio_index_df['2019'] = portfolio_index_df['2019'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['2020'] = portfolio_index_df['2020'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['2021'] = portfolio_index_df['2021'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['2022'] = portfolio_index_df['2022'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['2023(年化)'] = portfolio_index_df['2023(年化)'].apply(lambda x: format(x, '.2%'))

        return nav_df, portfolio_index_df


class NewFundSimulation:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    @staticmethod
    def _get_fund_nav_from_sql(start_date, end_date, fund_dict):
        """
        获取db的私募基金净值数据
        """
        nav_series_list = []
        for name, fund_id in tqdm(fund_dict.items()):
            sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                         "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                         "and a.jjzt not in ('3') " \
                         "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                         "order by b.jzrq".format(fund_id, start_date, end_date)
            res = hbs.db_data_query("highuser", sql_script, page_size=5000)
            if len(res['data']) != 0:
                data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
                data.name = name
                nav_series_list.append(data)
            else:
                pass
        df = pd.concat(nav_series_list, axis=1).sort_index()

        return df

    def _load_data(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        # DMA
        dma_dict = {
            "半鞅": "SB5848",
            "磐松": "SB6407",
            "千衍": "STF334",
            "信弘": "SXH465"
        }
        fund_nav = self._get_fund_nav_from_sql(self.start_date, self.end_date, dma_dict).reindex(trading_day_list)
        hy_nav = pd.read_excel("D:\\黑翼DMA净值.xlsx", sheet_name=0)
        col = hy_nav.columns[-1]
        hy_nav.rename(columns={"净值日期": "TRADEDATE", col: "黑翼"}, inplace=True)
        hy_nav['TRADEDATE'] = hy_nav['TRADEDATE'].apply(lambda x: x.replace('-', ''))
        fund_nav = fund_nav.merge(hy_nav.set_index('TRADEDATE')[['黑翼']], left_index=True, right_index=True, how='left')
        # @日期的微调
        fund_nav.loc[:"20230811", "半鞅"] = np.NaN
        fund_nav.loc[:"20230804", "磐松"] = np.NaN
        fund_nav.loc[:"20230519", "信弘"] = np.NAN
        return_df = fund_nav.pct_change(limit=1)
        return_df.loc["20230908", "千衍"] = np.NAN
        return_df.loc["20230310", "黑翼"] = np.NAN
        dma_return = return_df.mean(axis=1).fillna(0.)
        dma_nav = (1 + dma_return).cumprod()
        dma_nav = (dma_nav - 1) * 0.7 + 1  # 30% carry
        dma_return = dma_nav.pct_change().fillna(0.)
        # CTA: 5亿CTA指数
        cta_nav = pd.read_excel("D:\\研究基地\\Y-H1&N1\\5亿CTA指数\\5亿CTA指数20231124.xlsx", sheet_name="净值")
        cta_nav['t_date'] = cta_nav['t_date'].apply(lambda x: datetime.datetime.strftime(x, "%Y%m%d"))
        cta_nav = cta_nav.set_index('t_date')[['5亿CTA指数']]
        cta_return = cta_nav.pct_change().dropna()
        # 指增&中性
        allo_rep = QuarterAssetAllocationReport(
            start_date='20161230', end_date='20231124',
            data_path='D:\\量化产品跟踪\\指数增强', file_name='指增-20231124.xlsx', frequency="week")
        _, _, _, alpha_df = allo_rep.calculate_excess_return()
        neu_nav = allo_rep.neu_df
        neu_nav['TRADEDATE'] = neu_nav.index
        neu_nav['TRADEDATE'] = neu_nav['TRADEDATE'].apply(lambda x: x.replace('-', ''))
        neu_nav = neu_nav.set_index('TRADEDATE')[['市场中性']]
        alpha_rt = alpha_df[['average']].merge(neu_nav.pct_change(), left_index=True, right_index=True)
        # 套利
        data = pd.read_excel("D:\\量化产品日净值收益统计_20231201.xlsx", sheet_name="套利策略")
        cols = [x for x in data.columns if 'Unnamed' not in x]
        data1 = pd.read_excel("D:\\量化产品日净值收益统计_20231201.xlsx", sheet_name="套利策略", header=2, index_col=0)
        data1 = data1[data1.columns[1::3]]
        data1.columns = cols
        data1['TRADEDATE'] = data1.index
        data1['TRADEDATE'] = data1['TRADEDATE'].apply(lambda x: x.replace('-', ''))
        arb_data = data1.set_index('TRADEDATE').sort_index().reindex(trading_day_list)
        include_cols = ['雸昇香农一号', '百奕传家二号', '泓倍商品相对价值1号A', '悬铃C号6期C', '展弘量化精选1号1期',
                        '安值福慧量化1号', '云堡杉阳1号']
        arb_return = arb_data[include_cols].pct_change(limit=1).mean(axis=1)

        ret_df = dma_return.to_frame('dma').merge(cta_return, left_index=True, right_index=True, how='outer').merge(
            alpha_rt, left_index=True, right_index=True, how='outer').merge(
            arb_return.to_frame('arb'), left_index=True, right_index=True, how='outer')
        ret_df.rename(columns={"5亿CTA指数": "CTA", "average": "指增"}, inplace=True)
        "=============================================================================================================="
        # 指增 + 中性
        sub_df = ret_df.loc["20181228":, ['指增', '市场中性']].copy()
        sub_df.loc["20181228"] = 0.
        sub_df['组合'] = sub_df.mean(axis=1)
        ubi_nav = get_fund_nav_from_sql("20181228", "20231124", {"九坤多空": "SEF596"}).reindex(sub_df.index)
        sub_df = sub_df.merge(ubi_nav.pct_change().fillna(0.), left_index=True, right_index=True)

        nav_df = (1 + sub_df).cumprod()
        # DMA相关
        sub_df = ret_df.loc["20230106":].copy()
        del sub_df['市场中性']
        sub_nav = (1 + sub_df).cumprod()
        select_cols = [x for x in sub_df.columns if x != 'dma']
        ratio_list = np.linspace(0.1, 0.9, 9)
        results = pd.DataFrame(index=ratio_list, columns=select_cols)
        combin_nav = pd.DataFrame(index=sub_nav.index)
        for col in select_cols:
            for ratio in ratio_list:
                tmp = sub_nav['dma'] * ratio + sub_nav[col] * (1 - ratio)
                results.loc[ratio, col] = tmp.iloc[-1] - 1
                combin_nav['dma_{}+{}_{}'.format(ratio, col, 1-ratio)] = tmp

        combin_nav.loc["20221230"] = 1.
        combin_nav.sort_index(inplace=True)
        # 添加回测：40%DMA 40%CTA 20%指增
        # 40%DMA 20%CTA 40%指增
        # 另两种，CTA替换为套利
        sub_nav.loc["20221230", :] = 1.
        sub_nav.sort_index(inplace=True)
        sub_nav['port1'] = 0.4 * sub_nav['dma'] + 0.4 * sub_nav['CTA'] + 0.2 * sub_nav['指增']
        sub_nav['port2'] = 0.4 * sub_nav['dma'] + 0.2 * sub_nav['CTA'] + 0.4 * sub_nav['指增']
        sub_nav['port3'] = 0.4 * sub_nav['dma'] + 0.4 * sub_nav['arb'] + 0.2 * sub_nav['指增']
        sub_nav['port4'] = 0.4 * sub_nav['dma'] + 0.2 * sub_nav['arb'] + 0.4 * sub_nav['指增']

        return nav_df, combin_nav, sub_nav[sub_nav.columns[-4:]]


if __name__ == '__main__':
    # test('20190101', '20220909').run()
    # ArbitrageSimulation("20181228", "20230908", "20181228").run()
    NewFundSimulation("20181228", "20231124")
