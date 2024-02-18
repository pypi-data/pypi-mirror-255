from hbshare.quant.CChen.fund_stats.to_xl import FundStats
from datetime import datetime
import pandas as pd
from hbshare.quant.CChen.data.data import fund_pool_to_hb
from hbshare.quant.CChen.db_const import sql_write_path_hb, sql_user_hb
from hbshare.quant.CChen.fund_stats.fund_cons import order_dict_cta, order_dict_zx, order_dict_zz, month_release

start_date = datetime(2010, 12, 30).date()
end_date = datetime(2023, 12, 15).date()
output_path = 'E:/codes/QWork/analysis/update_weekly/output/'

t1 = datetime.now()

main = FundStats(
    start_date=start_date,
    end_date=end_date,
    output_path=output_path,
    fund_data_path=sql_write_path_hb['work'],
)
main.fund_stats(fund_dict=order_dict_cta, month_list=month_release, fund_type='cta')
main.fund_stats(fund_dict=order_dict_zx, month_list=month_release, fund_type='zx')
main.fund_stats(fund_dict=order_dict_zz, month_list=month_release, fund_type='zz')
main.sum_info()

t2 = datetime.now()
print(t2 - t1)

main.avg_to_hb(
    sql_path=sql_write_path_hb['work'],
    sql_ip=sql_user_hb['ip'],
    sql_user=sql_user_hb['user'],
    sql_pass=sql_user_hb['pass'],
    db='work',
    table='fund_avg'
)

fund_df = pd.DataFrame()
for t in order_dict_cta:
    t_df = pd.DataFrame(order_dict_cta[t]).rename(columns={0: 'name'})
    t_df['type0'] = 'cta'
    t_df['type1'] = t
    fund_df = pd.concat([fund_df, t_df])

for t in order_dict_zx:
    t_df = pd.DataFrame(order_dict_zx[t]).rename(columns={0: 'name'})
    t_df['type0'] = 'zx'
    t_df['type1'] = t
    fund_df = pd.concat([fund_df, t_df])

for t in order_dict_zz:
    t_df = pd.DataFrame(order_dict_zz[t]).rename(columns={0: 'name'})
    t_df['type0'] = 'zz'
    t_df['type1'] = t
    fund_df = pd.concat([fund_df, t_df])

fund_pool_to_hb(
    fund_df=fund_df,
    sql_path=sql_write_path_hb['work'],
    sql_ip=sql_user_hb['ip'],
    sql_user=sql_user_hb['user'],
    sql_pass=sql_user_hb['pass'],
    database='work'
)
# fund_data_to_hb(
#     path_local=sql_write_path_work['work'],
#     path_hb=sql_write_path_hb['work'],
#     sql_hb=sql_user_hb,
#     database='work'
# )
