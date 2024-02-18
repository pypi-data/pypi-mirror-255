from apscheduler.schedulers.background import BlockingScheduler
from hbshare.fe.mutual_analysis.nav_based import  mutual_fund_industry_exp
import  os,time
from datetime import date, datetime
from hbshare.fe.mutual_analysis import  holdind_based as hb
from  hbshare.fe.XZ import  functionality




# def test(abc):
#     print(abc)
#
scheduler = BlockingScheduler()

# scheduler.add_job(test,'interval',seconds=5,
#                   )
scheduler.add_job(mutual_fund_industry_exp().get_the_industry_exp,'date',run_date=datetime(2023, 8,19,15,47, 0),
                  args=['20230818', '20200601', '20221231'])

scheduler.start()

