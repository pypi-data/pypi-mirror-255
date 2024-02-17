"""
H1&N1的季度归因模块
"""
import os
import Levenshtein
import pandas as pd
import hbshare as hbs
from datetime import datetime
from hbshare.fe.common.util.data_loader import get_trading_day_list
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from hbshare.db.simu import valuation


def calc_cate_attr_h1(data_path, s_date, e_date, date):
    # 逐月持仓
    holding_df = pd.read_excel(os.path.join(data_path, "H1-底表-{}.xlsx".format(date)), sheet_name="逐月持仓")
    holding_df.rename(columns={"Unnamed: 0": "type_1", "Unnamed: 1": "type_2",
                               "Unnamed: 2": "type_3", "Unnamed: 3": "name"}, inplace=True)
    holding_df.dropna(subset=['type_1', 'type_2'], inplace=True)
    holding_df.columns = [str(x) for x in holding_df.columns]
    include_list = ['type_1', 'type_2', 'type_3', 'name', s_date, e_date]
    holding_df = holding_df[include_list]
    # 交易信息
    trading_df = pd.read_excel(os.path.join(data_path, "H1-底表-{}.xlsx".format(date)), sheet_name="历史交易")
    trading_df = trading_df[trading_df.columns[:8]]
    trading_df = trading_df[['交易日期', '资产名称', '交易方向', '交易金额（万元）']]
    trading_df['交易日期'] = trading_df['交易日期'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    trading_df = trading_df[(trading_df['交易日期'] > s_date) & (trading_df['交易日期'] < e_date)]
    # set1 = set(holding_df['name'])
    # set2 = set(trading_df['资产名称'])
    # set_minus = set2 - set1
    map_dict = {
        "乾象股票对冲3号私募证券投资基金": "乾象股票对冲3号私募证券投资基金B类",
        "卓识利民二号私募证券投资基金": "卓识利民二号私募证券投资基金A类",
        "景顺长城环保优势（001975）": "景顺长城环保优势股票",
        "正松云睿全球私募证券投资基金": "正松云睿全球私募证券投资基金A类",
        "浙商智选价值C（010382.OF）": "浙商智选价值混合C",
        "诚奇睿盈对冲私募证券投资基金": "诚奇睿盈对冲私募证券投资基金A类",
    }
    trading_df['资产名称'].replace(map_dict, inplace=True)
    trading_df.rename(columns={"资产名称": "name"}, inplace=True)
    pivot_tr = pd.pivot_table(trading_df, index='name', columns="交易方向", values='交易金额（万元）').fillna(0.)
    pivot_tr *= 10000.

    df = holding_df.merge(pivot_tr, left_on='name', right_index=True, how='left').fillna(0.)
    # special treat
    df.loc[df['name'] == '英仕曼宏量1号私募基金C类（单外包）', e_date] = 0.
    df.rename(columns={s_date: "起始日期", e_date: "结束日期"}, inplace=True)
    df.eval("pnl = 结束日期 - 起始日期 + 赎回 - 申购", inplace=True)
    df.eval("市值 = 结束日期 + 赎回", inplace=True)
    df.loc[df['type_2'] == "股票", 'type_2'] = df['type_3']
    attr_df = df.groupby(['type_1', 'type_2'])['pnl', '市值'].sum().reset_index()
    attr_df['收益率'] = attr_df['pnl'] / attr_df['市值']
    attr_df.rename(columns={"type_1": "超一级", "type_2": "一级", "pnl": "盈亏"}, inplace=True)

    s_date = "20221230"
    sql_script = "SELECT * FROM st_hedge.t_st_sm_zhmzs WHERE zsdm in ('HB0011', 'HB1001', 'HB1002', 'HB0015', 'HB0018') and " \
                 "jyrq >= {} and jyrq <= {}".format(s_date, e_date)
    res = hbs.db_data_query('highuser', sql_script)
    data = pd.DataFrame(res['data'])
    hb_index = data.pivot_table(index='jyrq', columns='zsdm', values='spjg').sort_index()
    bm_ret = hb_index.loc[e_date] / hb_index.loc[s_date] - 1

    return attr_df, bm_ret


def calc_cate_attr_n1(data_path, s_date, e_date, date):
    # 逐月持仓
    holding_df = pd.read_excel(os.path.join(data_path, "N1-底表-{}.xlsx".format(date)), sheet_name="逐月持仓")
    holding_df.rename(columns={"Unnamed: 0": "type_1", "Unnamed: 1": "type_2",
                               "Unnamed: 2": "type_3", "Unnamed: 3": "name"}, inplace=True)
    holding_df.dropna(subset=['type_1', 'type_2'], inplace=True)
    holding_df.columns = [str(x) for x in holding_df.columns]
    include_list = ['type_1', 'type_2', 'type_3', 'name', s_date, e_date]
    holding_df = holding_df[include_list]
    # 交易信息
    trading_df = pd.read_excel(os.path.join(data_path, "N1-底表-{}.xlsx".format(date)), sheet_name="历史交易")
    trading_df = trading_df[trading_df.columns[:9]]
    trading_df = trading_df[['交易日期', '投资基金', '投资类型', '交易金额(万元)']]
    trading_df['交易日期'] = trading_df['交易日期'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    trading_df = trading_df[(trading_df['交易日期'] > s_date) & (trading_df['交易日期'] < e_date)]
    # set1 = set(holding_df['name'])
    # set2 = set(trading_df['投资基金'])
    # set_minus = set2 - set1
    map_dict = {
        "国富中小盘": "国富中小盘股票",
    }
    trading_df['投资基金'].replace(map_dict, inplace=True)
    trading_df.rename(columns={"投资基金": "name"}, inplace=True)
    trading_df = trading_df.groupby(['name', '投资类型'])['交易金额(万元)'].sum().reset_index()
    pivot_tr = pd.pivot_table(trading_df, index='name', columns="投资类型", values='交易金额(万元)').fillna(0.)
    pivot_tr *= 10000.

    df = holding_df.merge(pivot_tr, left_on='name', right_index=True, how='left').fillna(0.)
    # special treat
    # df.loc[df['name'] == '勤辰森裕2号私募证券投资基金', e_date] = 4361143.26
    # df.loc[df['name'] == '易方达供给改革', e_date] = 4361143.26
    df.rename(columns={s_date: "起始日期", e_date: "结束日期"}, inplace=True)
    df.eval("pnl = 结束日期 - 起始日期 + 赎回 - 申购", inplace=True)
    df.eval("市值 = 结束日期 + 赎回", inplace=True)
    df.loc[df['type_2'] == "股票", 'type_2'] = df['type_3']
    attr_df = df.groupby(['type_1', 'type_2'])['pnl', '市值'].sum().reset_index()
    attr_df['收益率'] = attr_df['pnl'] / attr_df['市值']
    attr_df.rename(columns={"type_1": "超一级", "type_2": "一级", "pnl": "盈亏"}, inplace=True)

    s_date = "20221230"
    sql_script = "SELECT * FROM st_hedge.t_st_sm_zhmzs WHERE zsdm in ('HB0011', 'HB1001', 'HB1002', 'HB0015', 'HB0018') and " \
                 "jyrq >= {} and jyrq <= {}".format(s_date, e_date)
    res = hbs.db_data_query('highuser', sql_script)
    data = pd.DataFrame(res['data'])
    hb_index = data.pivot_table(index='jyrq', columns='zsdm', values='spjg').sort_index()
    bm_ret = hb_index.loc[e_date] / hb_index.loc[s_date] - 1

    return attr_df, bm_ret


def get_daily_nav_from_hbs(start_date, end_date, token):
    """
    获取h1和n1的成分周度净值的函数
    """
    include_cols = ['jjdm', 'jjmc', 'jzrq', 'jjjz', 'ljjz', 'xnjz']
    map_dict = {
        "jjdm": "fund_id",
        "jjmc": "fund_name",
        "jzrq": "trade_date",
        "jjjz": "单位净值",
        "ljjz": "累计净值",
        "xnjz": "虚拟净值"
    }
    "=======================================================H1========================================================="
    basic_df = pd.read_excel(
        "D:\\研究基地\\Y-H1&N1\\底表\\A-H1-底表.xlsx", sheet_name="交易", header=12).dropna(subset=['仓位%', '超一级'])
    current_fund_list = basic_df[basic_df['一级'] != 'MF EQUITY']['投资标的'].tolist()
    all_data = hbs.commonQuery('FOF_ZJJLIST', startDate=start_date, endDate=end_date, access_token=token)
    all_data = all_data[include_cols].rename(columns=map_dict).dropna(subset=['单位净值', '累计净值', '虚拟净值'])
    all_data['虚拟净值'] = all_data['虚拟净值'].map(float)
    nav_list = []
    for fund_name in current_fund_list:
        if fund_name in all_data['fund_name'].unique():
            target_id = all_data[all_data['fund_name'] == fund_name]['fund_id'].unique()[0]
            correlated_df = all_data[all_data['fund_id'] == target_id]
        else:
            distance_series = pd.Series(index=all_data['fund_name'].unique(), data=0.)
            for exist_name in all_data['fund_name'].unique():
                distance_series.loc[exist_name] = Levenshtein.distance(fund_name, exist_name)
            correlated_names = distance_series[distance_series < 3.].index.tolist()
            # 特殊处理
            if fund_name == '睿璞投资-睿信私募证券投资基金B类':
                correlated_names = ['睿璞投资-睿信私募证券投资基金B', '睿璞投资-睿信基金B类']
            if fund_name == '明汯CTA白羊二号私募投资基金':
                correlated_names = ['明汯CTA白羊二号私募投资基金B', '明汯CTA白羊二号B类']
            correlated_df = all_data[all_data['fund_name'].isin(correlated_names)]

        correlated_df = correlated_df.pivot_table(index='trade_date', columns='fund_name', values='虚拟净值').sort_index()
        nav_list.append(correlated_df.mean(axis=1).to_frame(fund_name))
    week_list = get_trading_day_list(start_date, end_date, "week")
    nav_df = pd.concat(nav_list, axis=1).sort_index().reindex(week_list)
    nav_h1 = nav_df.copy()
    "=======================================================N1========================================================="
    basic_df = pd.read_excel(
        "D:\\研究基地\\Y-H1&N1\\底表\\A-N1-底表.xlsx", sheet_name="交易", header=12).dropna(subset=['仓位%', '超一级'])
    current_fund_list = basic_df[basic_df['一级'] != 'MF EQUITY']['投资标的'].tolist()
    all_data = hbs.commonQuery('FOF_ZJJLIST', startDate=start_date, endDate=end_date, access_token=token)
    all_data = all_data[include_cols].rename(columns=map_dict).dropna(subset=['单位净值', '累计净值', '虚拟净值'])
    all_data['虚拟净值'] = all_data['虚拟净值'].map(float)
    nav_list = []
    for fund_name in current_fund_list:
        if fund_name in all_data['fund_name'].unique():
            target_id = all_data[all_data['fund_name'] == fund_name]['fund_id'].unique()[0]
            correlated_df = all_data[all_data['fund_id'] == target_id]
        else:
            distance_series = pd.Series(index=all_data['fund_name'].unique(), data=0.)
            for exist_name in all_data['fund_name'].unique():
                distance_series.loc[exist_name] = Levenshtein.distance(fund_name, exist_name)
            correlated_names = distance_series[distance_series < 3.].index.tolist()
            # 特殊处理
            if fund_name == '睿璞投资-睿信私募证券投资基金B类':
                correlated_names = ['睿璞投资-睿信私募证券投资基金B', '睿璞投资-睿信基金B类']
            if fund_name == '蒙玺竞起17号私募证券投资基金':
                correlated_names = ['蒙玺竞起17号私募证券投资基金A类']
            correlated_df = all_data[all_data['fund_name'].isin(correlated_names)]

        correlated_df = correlated_df.pivot_table(index='trade_date', columns='fund_name', values='虚拟净值').sort_index()
        print(fund_name, correlated_df.columns.tolist())
        nav_list.append(correlated_df.mean(axis=1).to_frame(fund_name))
    week_list = get_trading_day_list(start_date, end_date, "week")
    nav_df = pd.concat(nav_list, axis=1).sort_index().reindex(week_list)
    nav_n1 = nav_df.copy()

    return nav_h1, nav_n1


def getZlJjdmGzrq(lastModifiedDate):

    ZL_URL = "http://%s/data/query/guzhi/dates"
    import requests

    zl = {}
    try:
        domain = "ams-data.intelnal.howbuy.com"
        if hbs.is_prod_env():
            domain = "ams.inner.howbuy.com"
        res = requests.get(
            url=ZL_URL % domain, params={"date": lastModifiedDate}
        ).json()
        if res.get("code") != "0000":
            raise Exception("查询估值表增量出错: %s" % res.get("desc"))
        for data in res.get("body"):
            gzrqList = zl.setdefault(data["jjdm"], [])
            gzrqList.append(data["gzrq"])
    except Exception as e:
        raise Exception(str(e))
    return zl


def penetrated_style_analysis(trade_date, fund_dict):
    """
    N1&H1的持仓穿透风格分析
    """
    holding_list = []  # 存储所有类型的持仓
    # 1、量化
    hf_quants = fund_dict['量化']
    for key, value in hf_quants.items():
        sql_script = "SELECT * FROM private_fund_holding where trade_date = {} and fund_name = '{}'".format(
            trade_date, key)
        engine = create_engine(engine_params)
        holding_df = pd.read_sql(sql_script, engine)[['ticker', 'weight', 'fund_name']]
        holding_df['weight'] *= value
        holding_list.append(holding_df)
    # 2、公募
    mf_equity = fund_dict['公募']
    for key, value in mf_equity.items():
        sql_script = "SELECT jsrq as end_date, ggrq as report_date, zqdm as ticker, " \
                     "zjbl, zgbl, zlbl FROM st_fund.t_st_gm_gpzh where " \
                     "jjdm = '{}' and jsrq = {}".format(key, trade_date)
        holding_df = pd.DataFrame(hbs.db_data_query('funduser', sql_script, page_size=5000)['data'])
        holding_df.rename(columns={"end_date": "trade_date", "zjbl": "weight"}, inplace=True)
        holding_df['fund_name'] = key
        holding_df = holding_df[['ticker', 'weight', 'fund_name']]
        # print(holding_df.shape, holding_df['weight'].sum())
        holding_df['weight'] *= value
        holding_list.append(holding_df)
    # 3、主观股多
    # hf_equity = fund_dict['主观股多']
    #
    # date_dict = getZlJjdmGzrq("{} 00:00:00".format("2001-05-04"))
    # sql_script = "SELECT jjdm, jjmc, jjjc from st_hedge.t_st_jjxx where cpfl='4' and m_opt_type<>'03' and jjdm in ({})".format(
    #     ','.join("'{0}'".format(x) for x in date_dict.keys()))
    # fund_info = hbs.db_data_query("highuser", sql_script)
    # fund_info = pd.DataFrame(fund_info['data'])


if __name__ == '__main__':
    "==============================================================================="
    path = "D:\\研究基地\\Y-H1&N1\\底表"
    start_date = "20221231"
    end_date = "20230331"
    trade_date = "20230414"
    calc_cate_attr_h1(path, start_date, end_date, trade_date)
    calc_cate_attr_n1(path, start_date, end_date, trade_date)
    "==============================================================================="
    # nav_df_h1, nav_df_n1 = get_daily_nav_from_hbs("20230331", "20230616", "af19d1712f7c430a8548114a0b29d0cd")
    "==============================================================================="
    # f_dict = {
    #     "量化": {
    #         "衍复臻选中证1000指数增强一号": 8.76,
    #         "乾象中证500指数增强1号": 8.58,
    #         "伯兄至道": 6.48
    #     },
    #     "公募": {
    #         "002910": 1.69,
    #         "450009": 2.68,
    #         "006624": 4.07
    #     },
    #     "主观股多": {
    #         "慎知思知9号": 2.35,
    #         "勤辰森裕2号": 2.60,
    #         "睿璞投资-睿信B": 1.71
    #     }
    # }
    # t_date = "20230331"
    # penetrated_style_analysis(t_date, f_dict)