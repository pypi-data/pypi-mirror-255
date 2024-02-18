"""
小微盘股的统计模块
"""
import pandas as pd
import numpy as np
import hbshare as hbs
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_trading_day_list


def load_benchmark_components(date):
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                 "SecuCode in ('000300', '000905', '000852')"
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

    weight = []
    for benchmark_id in ['000300', '000905', '000852']:
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



def liquidity_analysis(start_date, end_date):
    date_list = get_trading_day_list(start_date, end_date, "month")
    date_list = [x for x in date_list if x[4:6] in ['06', '12']]
    date_list.append(end_date)
    # 上市时间数据
    ipo_data = pd.read_csv(
        "D:\\kevin\\risk_model_jy\\RiskModel\\data\\common_data\\list_status.csv", index_col=0,
        dtype={"ticker": str, "listDate": str})
    ipo_data['delistDate'] = ipo_data['delistDate'].fillna(20231231).astype(int).map(str)
    count_df = pd.DataFrame(index=date_list, columns=['流通市值', '上市&退市增量', '两市总市值'])
    for i in range(1, len(date_list)):
        t_date, n_date = date_list[i - 1], date_list[i]
        t_data = pd.read_csv("D:\\MarketInfoSaver\\market_info_{}.csv".format(t_date), dtype={"ticker": str})
        t_data.rename(columns={"negMarketValue": t_date}, inplace=True)
        n_data = pd.read_csv("D:\\MarketInfoSaver\\market_info_{}.csv".format(n_date), dtype={"ticker": str})
        n_data.rename(columns={"negMarketValue": n_date}, inplace=True)
        compare_df = t_data.set_index('ticker')[[t_date]].merge(
            n_data.set_index('ticker')[[n_date]], left_index=True, right_index=True, how='outer')
        benchmark_components = load_benchmark_components(n_date).set_index('ticker')
        compare_df = compare_df.merge(benchmark_components, left_index=True, right_index=True, how='outer')
        compare_df['benchmark_id'] = compare_df['benchmark_id'].fillna('other')
        # 退市 + 上市
        list_data = ipo_data[(ipo_data['listDate'] > t_date) & (ipo_data['listDate'] <= n_date)]
        delist_data = ipo_data[(ipo_data['delistDate'] > t_date) & (ipo_data['delistDate'] <= n_date)]
        idx = list(set(compare_df.index).intersection(set(list_data['ticker'])))
        compare_df.loc[idx, 'sign'] = 'L'
        idx = list(set(compare_df.index).intersection(set(delist_data['ticker'])))
        compare_df.loc[idx, 'sign'] = 'D'
        compare_df['sign'] = compare_df['sign'].fillna('N')
        # 发行&退市导致的市值变化
        group_df = compare_df.groupby(['benchmark_id', 'sign'])
        t_df = group_df[t_date].sum().reset_index()
        n_df = group_df[n_date].sum().reset_index()
        mkv_df = t_df.merge(n_df, on=['benchmark_id', 'sign'])
        mkv_df[[t_date, n_date]] /= 1e+8
        mkv_df['delta'] = mkv_df[n_date] - mkv_df[t_date]
        if i == 1:
            count_df.loc[t_date, '流通市值'] = compare_df[compare_df['benchmark_id'] == 'other'][t_date].sum() / 1e+8
            count_df.loc[t_date, '上市&退市增量'] = 0.
            count_df.loc[t_date, '两市总市值'] = compare_df[t_date].sum() / 1e+8

        count_df.loc[n_date, '流通市值'] = compare_df[compare_df['benchmark_id'] == 'other'][n_date].sum() / 1e+8
        count_df.loc[n_date, '上市&退市增量'] = (
            mkv_df[(mkv_df['benchmark_id'] == 'other') & (mkv_df['sign'] != 'N')]['delta'].sum())
        count_df.loc[n_date, '两市总市值'] = compare_df[n_date].sum() / 1e+8

    print(count_df)


    # 自由流通市值
    neg_data = pd.read_excel("D:\\微盘统计数据\\自由流通市值.xlsx", sheet_name=0)
    cols = neg_data.columns.tolist()
    adjust_cols = [x.split(' ')[1].split('\n')[0].replace('-', '') if '自由流通市值' in x else x for x in cols]
    neg_data.columns = adjust_cols
    # 剔除北交所
    neg_data['market'] = neg_data['证券代码'].apply(lambda x: x.split('.')[-1])
    neg_data = neg_data[neg_data['market'].isin(['SH', 'SZ'])]
    del neg_data['market']
    # neg_list = []
    # for date in date_list:
    #     t_data = neg_data[['证券代码', date]].dropna()
    #     t_data['ticker'] = t_data['证券代码'].apply(lambda x: x.split('.')[0])
    #     benchmark_components = load_benchmark_components(date)
    #     t_data = t_data.merge(benchmark_components, on='ticker', how='left').fillna('other')
    #     tmp = t_data.groupby('benchmark_id')[date].sum().to_frame(date)
    #     neg_list.append(tmp)
    # neg_df = pd.concat(neg_list, axis=1)
    # neg_ratio = neg_df.div(neg_df.sum())





    return neg_ratio


if __name__ == '__main__':
    liquidity_analysis("20161230", "20231031")