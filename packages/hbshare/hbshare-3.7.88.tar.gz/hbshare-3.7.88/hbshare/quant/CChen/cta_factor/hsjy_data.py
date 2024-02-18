import re

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from hbshare.quant.CChen.func import generate_table
import hbshare as hbs
import pymysql
from hbshare.quant.CChen.cons import (
    db,
    db_tables,
    HSJY_EXCHANGE_INE,
    HSJY_EXCHANGE_CZCE,
    HSJY_EXCHANGE_SHFE,
    HSJY_EXCHANGE_DCE,
    HSJY_EXCHANGE_CFFEX
)
from hbshare.quant.CChen.db_const import sql_write_path_hb as sql_path

page_size_con = 49999


def fut_mr_wz(t_date, path=sql_path['daily']):
    df_all = pd.read_sql_query(
        'select * from hsjy_mr_wz where TDATE=' + t_date.strftime('%Y%m%d'),
        path
    )

    df_all = df_all[
        np.array(df_all['INDICATORCODE'] == 3) | np.array(df_all['INDICATORCODE'] == 4)
    ]
    df_all['INDICATORCODE'] = df_all['INDICATORCODE'].apply(lambda x: 1 if x == 3 else -1)
    df_all['INDICATORVOL'] = df_all['INDICATORCODE'] * df_all['INDICATORVOL']
    df_all['product'] = df_all['CONTRACT'].apply(
        lambda x: re.findall(r'\D+', x)[0].upper()
    )
    df_g = df_all[['product', 'INDICATORVOL']].rename(columns={'INDICATORVOL': '外资持仓量'}
                                                      ).groupby('product').sum().reset_index()
    return df_g.sort_values(by='product').set_index('product')


def fut_mr_wz_si_ts(start_date, end_date, path=sql_path['daily']):
    df_all = pd.read_sql_query(
        'select * from hsjy_mr_wz where TDATE<=' + end_date.strftime('%Y%m%d')
        + ' and TDATE>=' + start_date.strftime('%Y%m%d')
        + ' and (CONTRACT like \'IH%\' or CONTRACT like \'IM%\' or CONTRACT like \'IF%\' or CONTRACT like \'IC%\')',
        path
    )

    df_all = df_all[
        np.array(df_all['INDICATORCODE'] == 3) | np.array(df_all['INDICATORCODE'] == 4)
    ]
    df_all['INDICATORCODE'] = df_all['INDICATORCODE'].apply(lambda x: 1 if x == 3 else -1)
    df_all['INDICATORVOL'] = df_all['INDICATORCODE'] * df_all['INDICATORVOL']
    df_all['product'] = df_all['CONTRACT'].apply(
        lambda x: re.findall(r'\D+', x)[0].upper()
    )
    df_g = df_all.groupby(['TDATE', 'product']).sum()[['INDICATORVOL']].reset_index()
    df_g['TDATE'] = pd.to_datetime(df_g['TDATE'], format='%Y-%m-%d %H:%M:%S').dt.date
    return df_g.pivot(index='TDATE', columns='product', values='INDICATORVOL')
