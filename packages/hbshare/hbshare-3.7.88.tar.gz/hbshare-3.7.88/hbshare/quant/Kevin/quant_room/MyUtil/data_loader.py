"""
取数function模块
"""
import hbshare as hbs
import pandas as pd
import datetime
from sqlalchemy import create_engine
from hbshare.fe.common.util.config import style_name, industry_name

sql_params = {
    "ip": "192.168.223.152",
    "user": "readonly",
    "pass": "c24mg2e6",
    "port": "3306",
    "database": "work"
}
engine_params = "mysql+pymysql://{}:{}@{}:{}/{}".format(sql_params['user'], sql_params['pass'],
                                                        sql_params['ip'],
                                                        sql_params['port'], sql_params['database'])


def get_trading_day_list(start_date, end_date, frequency='day'):
    """
    获取日期序列
    """
    sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM st_main.t_st_gg_jyrl WHERE JYRQ >= {} and JYRQ <= {}".format(
        start_date, end_date)
    res = hbs.db_data_query('alluser', sql_script, page_size=5000)
    df = pd.DataFrame(res['data']).rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
    df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
    df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

    calendar_df = df[['calendarDate', 'isOpen', 'isWeekEnd', 'isMonthEnd']]

    if frequency == "day":
        trading_day_list = calendar_df[calendar_df['isOpen'] == 1]['calendarDate'].tolist()
    elif frequency == "week":
        trading_day_list = calendar_df[calendar_df['isWeekEnd'] == 1]['calendarDate'].tolist()
    elif frequency == 'month':
        trading_day_list = calendar_df[calendar_df['isMonthEnd'] == 1]['calendarDate'].tolist()
    else:
        trading_day_list = calendar_df['calendarDate'].tolist()

    return trading_day_list


def get_fund_nav_from_sql(start_date, end_date, fund_dict):
    """
    获取db的私募基金净值数据
    """
    nav_series_list = []
    for name, fund_id in fund_dict.items():
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


def get_fund_nav_from_work(start_date, end_date, fund_id):
    sql_script = "SELECT name, t_date, nav FROM fund_data where " \
                 "t_date >= {} and t_date <= {} and code = '{}'".format(start_date, end_date, fund_id)
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['t_date'] = data['t_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))

    return data


def get_daily_nav_from_work(start_date, end_date, fund_dict):
    nav_series_list = []
    for name, fund_id in fund_dict.items():
        sql_script = "SELECT * FROM daily_nav where code = '{}' and date >= '{}' and date <= '{}'".format(
            fund_id, start_date, end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['date'] = data['date'].map(str)

        data = data.set_index('date')['fqjz']
        data.name = name
        nav_series_list.append(data)

    df = pd.concat(nav_series_list, axis=1).sort_index()

    return df


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


def get_index_return_from_sql(start_date, end_date, benchmark_id):
    sql_script = ("SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE FROM st_market.t_st_zs_hq WHERE "
                  "ZQDM = '{}' and JYRQ >= {} and JYRQ <= {}").format(benchmark_id, start_date, end_date)
    res = hbs.db_data_query('alluser', sql_script, page_size=5000)
    data = pd.DataFrame(res['data'])
    data['TRADEDATE'] = data['TRADEDATE'].map(str)
    benchmark_df = data.set_index('TRADEDATE')['TCLOSE']

    return benchmark_df


def get_benchmark_weight_from_sql(date, benchmark_id="000905"):
    """
    月末指数成分权重数据
    """
    sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(benchmark_id)
    res = hbs.db_data_query('readonly', sql_script)
    index_info = pd.DataFrame(res['data'])
    inner_code = index_info.set_index('SECUCODE').loc[benchmark_id, 'INNERCODE']

    sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                 "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                 "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
    data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
    weight_df = data.rename(
        columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})

    return weight_df.set_index('consTickerSymbol')['weight'] / 100.


def fetch_data_batch_hbs(sql_script, authority="readonly"):
    res = hbs.db_data_query(authority, sql_script, page_size=5000)
    df_list = []
    n = res['pages']
    for i in range(1, n + 1):
        page_num = i
        res = hbs.db_data_query(authority, sql_script, page_size=5000, page_num=page_num)
        df_list.append(pd.DataFrame(res['data']))
    df = pd.concat(df_list)
    df.reset_index(drop=True, inplace=True)

    return df


def load_industry_sw3(date):
    sql_script = "SELECT * FROM st_fund.t_st_gm_zqhyflb WHERE hyhfbz = '2' and fljb = '1' and m_opt_type <> '03'"
    include_cols = ['qsrq', 'zqdm', 'jsrq', 'flmc']
    data = fetch_data_batch_hbs(sql_script, "funduser")[include_cols]
    data['qsrq'] = data['qsrq'].map(str)
    data['jsrq'] = data['jsrq'].fillna(20991231.0)
    data['jsrq'] = data['jsrq'].map(int)
    data['jsrq'] = data['jsrq'].map(str)
    data.rename(
        columns={"qsrq": "start_date", "jsrq": "end_date", "zqdm": "ticker", "flmc": "industryName1"}, inplace=True)

    period_data = data[(data['start_date'] < date) & (data['end_date'] >= date)]

    return period_data.set_index('ticker')['industryName1'].dropna()


def get_style_exposure_from_sql(date):
    """
    线上风险模型的风格暴露数据
    """
    sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
    exposure_df = fetch_data_batch_hbs(sql_script, "alluser").set_index('ticker')
    ind_names = [x.lower() for x in industry_name['sw'].values()]
    exposure_df = exposure_df[style_name + ind_names]

    return exposure_df


def get_benchmark_components_from_sql(date):
    """
    成分股标识数据
    """
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