# 更新产品信息
from hbshare.quant.CChen.fund_stats.db import update_fund_nav_db4, update_fund_list_db, update_fund_list_db2, update_fund_nav_out
from hbshare.quant.CChen.data.data import load_funds_data
import pandas as pd
from datetime import datetime
import pymysql
from hbshare.quant.CChen.db_const import sql_write_path_hb, sql_user_hb
import xlwings as xw
from time import sleep

pymysql.install_as_MySQLdb()

db_work = sql_write_path_hb['work']
db_daily = sql_write_path_hb['daily']
sql_info = sql_user_hb
fund_list_table = 'fund_list'

run_part = 1

data_class = [
    'cta',
    '指增',
    '中性',
]

if run_part == 1:
    # --------------------------------------------------------------------------
    # part 1

    funds = pd.read_excel('fund_list.xlsx')
    print('更新数据库产品表')
    update_fund_list_db(db_path=db_work, sql_info=sql_info, funds=funds)
    print('更新单个产品净值表（公司数据库）')
    update_fund_nav_db4(db_path=db_work, sql_info=sql_info)
#     print('更新数据库产品表日期信息')
#     update_fund_list_db2(db_path=db_work, sql_info=sql_info)
#
#     new_list = pd.read_sql_query(
#         'select * from ' + fund_list_table, db_work
#     )
#     new_list.to_excel('fund_list.xlsx', index=False)
#
#     xlsx = xw.Book('fund_temp_data.xlsx')
#     for i in data_class:
#         fund_list = pd.read_sql_query('select * from fund_list where class="' + i + '" order by name', db_work)
#         data = load_funds_data(
#             fund_list=fund_list,
#             first_date=datetime(2019, 1, 1).date(),
#             # end_date=datetime(2020, 6, 5).date(),
#             freq='w',
#             fillna=False,
#             # cal_db_path=db_daily,
#             db_path=db_work
#         )
#         # data.to_excel('d:/codes/work/weekly_update/data_temp/' + i + '.xlsx')
#         sht1 = xlsx.sheets(i)
#         sht1.clear_contents()
#         sht1.range('A1').value = data
#         xlsx.save()
#         print(i)
#         sleep(1)
#     xlsx.close()
#
#     print('更新数据库产品表日期信息')
#     update_fund_list_db2()
# else:
#     # --------------------------------------------------------------------------
#     for i in data_class:
#         data = pd.read_excel('fund_temp_data.xlsx', sheet_name=i, index_col=0)
#         data['t_date'] = data['t_date'].dt.date
#         update_fund_nav_out(data=data, db_path=db_work)
#
#     # print('更新单个产品净值表（外部数据）')
#     # update_fund_nav_db2(funds_data_path='jz_out.csv', out=True)
#     print('更新数据库产品表日期信息')
#     update_fund_list_db2(db_path=db_work, sql_info=sql_info)
#
#     new_list = pd.read_sql_query('select * from ' + fund_list_table, db_work)
#     new_list.to_excel('fund_list.xlsx', index=False)
