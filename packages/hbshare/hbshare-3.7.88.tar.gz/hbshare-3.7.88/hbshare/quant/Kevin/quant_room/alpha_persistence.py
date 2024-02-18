"""
池内产品反转的持续性
"""
import numpy as np
import pandas as pd
from datetime import datetime
import hbshare as hbs
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list, \
    get_index_return_from_sql
from hbshare.quant.Kevin.quant_room.QuarterAssetAllocationReport import QuarterAssetAllocationReport


class TrendencyCheck:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, "week")
        config_df = pd.read_excel("D:\\研究基地\\私募量化基金池\\FOF-500指增池.xlsx", sheet_name="参数", dtype={"起始时间": str})
        fund_dict = config_df.set_index('管理人')['基金代码'].to_dict()
        fund_nav = get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict).reindex(
            trading_day_list)
        # 起始时间调整
        for name in config_df['管理人'].tolist():
            pool_in_date = config_df[config_df['管理人'] == name]['起始时间'].values[0]
            if pool_in_date == self.start_date:
                continue
            else:
                pre_date = trading_day_list[trading_day_list.index(pool_in_date) - 1]
                fund_nav.loc[:pre_date, name] = np.NaN
        benchmark_series = get_index_return_from_sql(self.start_date, self.end_date, '000905').reindex(
            trading_day_list).pct_change().dropna()
        return_df = fund_nav.pct_change(limit=1).dropna(axis=0, how='all').sort_index()
        excess_df = return_df.sub(benchmark_series, axis=0)
        # 相对强弱
        # ave_excess = pd.read_excel("D:\\研究基地\\私募量化基金池\\FOF-500指增池.xlsx", sheet_name="跟踪池平均超额", index_col=0)
        # ave_excess['trade_date'] = ave_excess.index
        # ave_excess['trade_date'] = ave_excess['trade_date'].map(str)
        # ave_excess.set_index('trade_date', inplace=True)
        allo_rep = QuarterAssetAllocationReport(
            start_date=self.start_date, end_date=self.end_date,
            data_path='D:\\量化产品跟踪\\指数增强', file_name='指增-{}.xlsx'.format(self.end_date), frequency="week")

        _, ave_excess, _ = allo_rep.calculate_excess_return()
        ave_excess = ave_excess.rename(columns={"500指增": "ave_excess"})[['ave_excess']]
        relative_df = excess_df.sub(ave_excess['ave_excess'], axis=0)
        excel_writer = pd.ExcelWriter(
            'D:\\研究基地\\Z-数据整理\\FOF池标的-相对强弱曲线_sub.xlsx', engine='xlsxwriter')
        for name in relative_df.columns:
            sub_df = relative_df[name].dropna()
            pre_date = trading_day_list[trading_day_list.index(sub_df.index[0]) - 1]
            sub_df.loc[pre_date] = 0.
            sub_df = (1 + sub_df.sort_index()).cumprod().to_frame(name)
            # 调整格式存储
            sub_df['trade_date'] = sub_df.index
            sub_df['trade_date'] = sub_df['trade_date'].apply(
                lambda x: datetime.strptime(x, '%Y%m%d').strftime('%Y/%m/%d'))
            sub_df.set_index('trade_date', inplace=True)
            sub_df['回撤序列'] = sub_df[name] / sub_df[name].cummax() - 1
            sub_df.to_excel(excel_writer, sheet_name=name)

        excel_writer.close()


if __name__ == '__main__':
    TrendencyCheck("20201231", "20231124").run()
