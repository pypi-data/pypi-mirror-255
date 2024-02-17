"""
zeppelin上的相对强弱跟踪模块
"""
import os
import numpy as np
import pandas as pd
import hbshare as hbs
import datetime
from sqlalchemy import create_engine
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list
from hbshare.quant.Kevin.quant_room.MyUtil.util_func import cal_annual_return, cal_annual_volatility
from hbshare.quant.Kevin.periodic_reports.tracker import get_track_config_from_db
from hbshare.quant.CChen.cta_factor.zep import plot_lines


class ZepFundTracker:
    def __init__(self, start_date, end_date, type_list, select_list):
        self.start_date = start_date
        self.end_date = end_date
        self.type_list = type_list
        self.select_list = select_list
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
        self.config_df = config_df.copy()
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        # abr process
        config_df.loc[config_df['strategy_type'] == '量化多头', 'level2type'] = '量化多头'
        if len(self.type_list) > 1:
            config_df['abr'] = config_df.apply(lambda x: '-'.join([x['abr'], x['level2type']]), axis=1)
        # fetch data
        fund_dict = config_df[config_df['level2type'].isin(self.type_list)].set_index('abr')['fund_id'].to_dict()
        dt_df = config_df[(config_df['level2type'].isin(self.type_list)) & (~config_df['start_date'].isnull())]
        dt_df['start_date'] = dt_df['start_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        dt_dict = dt_df.set_index('abr')['start_date'].to_dict()
        fund_nav = get_fund_nav_from_sql(self.start_date, self.end_date, fund_dict).reindex(
            trading_day_list)
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
        # switch
        benchmark_id = '000905' if self.type_list == ['500指增'] else '000852'
        benchmark_series = self._load_benchmark(self.start_date, self.end_date, benchmark_id).reindex(
            trading_day_list).pct_change().dropna()
        self.return_df = fund_nav.pct_change(
            fill_method=None).dropna(how='all').sub(benchmark_series, axis=0).sort_index()

    def run(self):
        return_df = self.return_df
        # 截面去极值
        mean_return = pd.Series(index=return_df.index, dtype=float)
        for date in return_df.index.tolist():
            date_t_return = return_df.loc[date].dropna()
            median = date_t_return.median()
            new_median = abs(date_t_return - median).median()
            up = median + 5 * new_median
            down = median - 5 * new_median
            date_t_return = date_t_return[(date_t_return.gt(down)) & (date_t_return.lt(up))]
            mean_return.loc[date] = date_t_return.mean()

        rel_return = return_df[self.select_list].sub(mean_return, axis=0)
        rel_return.loc[self.start_date] = 0.
        rel_nav = (1 + rel_return.sort_index()).cumprod()

        ggg = plot_lines(
            data=rel_nav,
            height=500,
            width=1200,
            title=self.start_date + ' - ' + self.end_date,
        )
        html = ggg.render_embed()
        print("%html {}".format(html))


        return rel_nav


if __name__ == '__main__':
    ZepFundTracker("20221230", "20230901", ['1000指增', '量化多头'], ["凡二-量化多头", "衍复-1000指增"]).run()