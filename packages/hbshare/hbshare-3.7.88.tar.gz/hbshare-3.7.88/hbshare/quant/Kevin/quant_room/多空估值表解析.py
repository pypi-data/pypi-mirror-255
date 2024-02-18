"""
磐松/衍合多空估值表解析模块
"""
import os
import pandas as pd
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import (
    get_benchmark_weight_from_sql, fetch_data_batch_hbs, get_style_exposure_from_sql, get_benchmark_components_from_sql)
from hbshare.fe.common.util.config import style_name, industry_name, factor_map_dict


def long_short_holding_extractor():
    data_path = "D:\\估值表基地\\磐松多空对冲"
    filenames = os.listdir(data_path)
    names_xls = [x for x in filenames if x.split('.')[-1] in ['xls', 'xlsx']]
    # 2-5号
    holding_list = []
    for name in names_xls:
        fund_name = name.split('_')[1]
        date = name.split('_')[-2]
        if fund_name in ['磐松多空对冲2号私募证券投资基金']:
            context = "市值占净值%"
            hd = 3
            data = pd.read_excel(
                os.path.join(data_path, name), sheet_name=0, header=hd).dropna(subset=['科目代码'])
            sh = data[data['科目代码'].str.startswith('11021101')]
            sz = data[data['科目代码'].str.startswith('11021201')]
            cyb = data[data['科目代码'].str.startswith('11021501')]
            kcb = data[data['科目代码'].str.startswith('1102D201')]
            long_df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
            long_df['direction'] = 'long'
            sh_short = data[data['科目代码'].str.startswith('21010101')]
            kcb_short = data[data['科目代码'].str.startswith('21010201')]
            sz_short = data[data['科目代码'].str.startswith('21013101')]
            cyb_short = data[data['科目代码'].str.startswith('21014101')]
            short_df = pd.concat([sh_short, sz_short, cyb_short, kcb_short], axis=0).dropna()
            short_df['direction'] = 'short'
            holding_df = pd.concat([long_df, short_df], axis=0)
            holding_df['ticker'] = holding_df['科目代码'].apply(lambda x: x[-6:])
            holding_df.rename(columns={"科目名称": "sec_name", context: "weight"}, inplace=True)
            holding_df = holding_df[['ticker', 'sec_name', 'weight', 'direction']]
        elif fund_name in ['磐松多空对冲3号私募证券投资基金', '磐松多空对冲5号私募证券投资基金']:
            data = pd.read_excel(
                os.path.join(data_path, name), sheet_name=0, header=6).dropna(subset=['科目代码'])
            data['科目代码'] = data['科目代码'].map(str)
            sh = data[data['科目代码'].str.endswith('SH')]
            sz = data[data['科目代码'].str.endswith('SZ')]
            holding_df = pd.concat([sh, sz], axis=0).dropna()
            holding_df = holding_df[
                (holding_df['科目代码'].str.startswith('1102')) | (holding_df['科目代码'].str.startswith('2101'))]
            holding_df['ticker'] = holding_df['科目代码'].apply(lambda x: x.split('.')[-1].split(' ')[0])
            holding_df.rename(columns={"科目名称": "sec_name", "市值占比": "weight"}, inplace=True)
            holding_df.loc[holding_df['科目代码'].str.startswith('2'), 'direction'] = 'short'
            holding_df['direction'].fillna('long', inplace=True)
        else:
            holding_df = pd.DataFrame()

        holding_df['fund_name'] = fund_name
        holding_df['trade_date'] = date
        holding_list.append(holding_df)

    inc = ['ticker', 'weight', 'direction', 'fund_name', 'trade_date']
    holding_df_other = pd.concat(holding_list)[inc]

    # 多空对冲1号
    path_inner = os.path.join(data_path, "LONGSHORT")
    filenames = os.listdir(path_inner)
    holding_list_one = []
    for file_name in filenames:
        fund_name = file_name.split('_')[1]
        date = file_name.split('_')[-1].split('.')[0]
        context = "市值占净值%"
        data = pd.read_excel(
            os.path.join(path_inner, file_name), sheet_name=0, header=3).dropna(subset=['科目代码'])
        sh = data[data['科目代码'].str.startswith('11021101')]
        sz = data[data['科目代码'].str.startswith('11021201')]
        cyb = data[data['科目代码'].str.startswith('11021501')]
        kcb = data[data['科目代码'].str.startswith('1102D201')]
        long_df = pd.concat([sh, sz, cyb, kcb], axis=0).dropna()
        long_df['direction'] = 'long'
        sh_short = data[data['科目代码'].str.startswith('21010101')]
        kcb_short = data[data['科目代码'].str.startswith('21010201')]
        sz_short = data[data['科目代码'].str.startswith('21013101')]
        cyb_short = data[data['科目代码'].str.startswith('21014101')]
        short_df = pd.concat([sh_short, sz_short, cyb_short, kcb_short], axis=0).dropna()
        short_df['direction'] = 'short'
        holding_df = pd.concat([long_df, short_df], axis=0)
        holding_df['ticker'] = holding_df['科目代码'].apply(lambda x: x[-6:])
        holding_df.rename(columns={"科目名称": "sec_name", context: "weight"}, inplace=True)
        holding_df = holding_df[['ticker', 'sec_name', 'weight', 'direction']]
        holding_df['fund_name'] = fund_name
        holding_df['trade_date'] = date
        holding_list_one.append(holding_df)

    inc = ['ticker', 'weight', 'direction', 'fund_name', 'trade_date']
    holding_df_1 = pd.concat(holding_list_one)[inc]

    return holding_df_other, holding_df_1

def YH_extractor():
    data = pd.read_excel(
        "D:\\研究基地\\A2-中频量价类\\衍合\\STM861衍合量化市场中性23号私募证券投资基金估值表20231204.xlsx", sheet_name=0, header=2)
    data = data.dropna(subset=['科目代码'])
    # 股票多头仓位
    sh = data[data['科目代码'].str.startswith('11021101')].dropna()
    sz = data[data['科目代码'].str.startswith('11021201')].dropna()
    cyb = data[data['科目代码'].str.startswith('11021501')].dropna()
    kcb = data[data['科目代码'].str.startswith('1102D201')].dropna()
    stock_df = pd.concat([sh, sz, cyb, kcb], axis=0)
    stock_df['ticker'] = stock_df['科目代码'].apply(lambda x: x[-6:])
    stock_df.rename(columns={"市值占净值(%)": "wl"}, inplace=True)
    long_df = stock_df[['ticker', 'wl']]
    long_df['wl'] /= long_df['wl'].sum()
    # 融券仓位
    sh_debt = data[data['科目代码'].str.startswith('21010101')].dropna()
    kcb_debt = data[data['科目代码'].str.startswith('21010201')].dropna()
    sz_debt = data[data['科目代码'].str.startswith('21011301')].dropna()
    cyb_debt = data[data['科目代码'].str.startswith('21014101')].dropna()
    debt_df = pd.concat([sh_debt, sz_debt, cyb_debt, kcb_debt], axis=0)
    debt_df['ticker'] = debt_df['科目代码'].apply(lambda x: x[-6:])
    debt_df.rename(columns={"市值占净值(%)": "ws"}, inplace=True)
    short_df = debt_df[['ticker', 'ws']]
    # IC仓位
    bm_weight = get_benchmark_weight_from_sql("20231130", "000905") * 35.53
    bm_weight = bm_weight.to_frame('weight').reset_index()
    bm_weight.rename(columns={"consTickerSymbol": "ticker", "weight": "weight_ic"}, inplace=True)
    short_df = short_df.merge(bm_weight, on='ticker', how='outer').fillna(0.)
    short_df['ws'] += short_df['weight_ic']
    del short_df['weight_ic']
    short_df['ws'] /= short_df['ws'].sum()
    # 风格暴露
    exposure_df = get_style_exposure_from_sql("20231204")
    # 指数成分数据
    benchmark_components = get_benchmark_components_from_sql("20231130")

    "======计算======"
    weight_df = long_df.merge(short_df, on='ticker', how='outer').fillna(0.).set_index('ticker')
    idx = weight_df.index.intersection(exposure_df.index)
    sub_weight = weight_df.reindex(idx)
    exposure_df = exposure_df.reindex(idx).astype(float)
    style_expo = exposure_df.T.dot(sub_weight).loc[style_name]
    style_expo.index = style_expo.index.map(factor_map_dict)
    ind_exposure = exposure_df.T.dot(sub_weight).iloc[10:]
    reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])
    ind_exposure.index = [reverse_ind[x] for x in ind_exposure.index]

    w_df = pd.merge(weight_df.reset_index(), benchmark_components, on='ticker', how='left')
    w_df['benchmark_id'].fillna('other', inplace=True)
    bm_distribution = w_df.groupby('benchmark_id')[['wl', 'ws']].sum().reset_index().replace(
        {"000300": "沪深300", "000905": "中证500", "000852": "中证1000",
         "399303": "国证2000", "other": "超小票"}).set_index('benchmark_id')

    return bm_distribution


if __name__ == '__main__':
    # hd1, hd2 = long_short_holding_extractor()
    YH_extractor()