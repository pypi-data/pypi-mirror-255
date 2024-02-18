# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import hbshare as hbs
from datetime import datetime, timedelta

def get_df(sql, db, page_size=2000):
    data = hbs.db_data_query(db, sql, page_size=page_size, timeout=120)
    pages = data['pages']
    data = pd.DataFrame(data['data'])
    if pages > 1:
        for page in range(2, pages + 1):
            temp_data = hbs.db_data_query(db, sql, page_size=page_size, page_num=page, timeout=120)
            data = pd.concat([data, pd.DataFrame(temp_data['data'])], axis=0)
    return data


end_date='20230714'  #统计的截至日
jnyl=(pd.to_datetime(end_date)-pd.to_datetime('20221230')).days
time_list=[365,180,90,30,jnyl]

#导入出入池记录的excel
zx_in=pd.read_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/好买30基金池名单（主池）-202301-含产品-202306-终版-XI-YI-yf.xlsx",sheet_name="入池记录")[['基金代码','调入时间','策略类型']]
zx_out=pd.read_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/好买30基金池名单（主池）-202301-含产品-202306-终版-XI-YI-yf.xlsx",sheet_name="出池记录")[['基金代码','调入时间','调出时间','策略类型']]
zx_pool = pd.concat([zx_out, zx_in], axis=0)
zx_pool['调入时间'] = zx_pool['调入时间'].astype(str).str.replace('-', '').str[0:8]
zx_pool['调出时间'] = zx_pool['调出时间'].astype(str).str.replace('-', '').str[0:8]
zx_pool['基金代码'] = zx_pool['基金代码'].str[0:6]
zx_pool.drop_duplicates('基金代码', inplace=True)
#分类
zx_zg = zx_pool[(zx_pool['策略类型'].isin(['私募主观']))]
zx_lh = zx_pool[(zx_pool['策略类型'].isin(['量化指增']))]
zx_cta = zx_pool[(zx_pool['策略类型'].isin(['CTA']))]
zx_zx = zx_pool[(zx_pool['策略类型'].isin(['市场中性']))]
zx_gmz = zx_pool[(zx_pool['策略类型'].isin(['公募债券']))]
zx_smz = zx_pool[(zx_pool['策略类型'].isin(['私募债券']))]
zx_hg = zx_pool[(zx_pool['策略类型'].isin(['宏观对冲']))]
###求私募产品周净值
def get_zx_nav(zx_group):
    if len(zx_group['基金代码'])==1:
        sql_smgd="select jjdm,hb1z,tjrq from st_hedge.t_st_sm_zhb where jjdm = '{0}' and tjrq>='20201228' and hb1z!=99999".format(zx_group['基金代码'].values[0])
    else:
        sql_smgd = "select jjdm,hb1z,tjrq from st_hedge.t_st_sm_zhb where jjdm in {0} and tjrq>='20201228' and hb1z!=99999".format(tuple(zx_group['基金代码']))
    smgd_jz = get_df(sql_smgd, db='highuser', page_size=2000000)
    smgd_jz = pd.merge(smgd_jz, zx_group, how='left', left_on='jjdm', right_on='基金代码')
    #把tjrq由每周一变为周五
    smgd_jz.index=pd.to_datetime(smgd_jz['tjrq'])
    smgd_jz.index=smgd_jz.index+timedelta(days=4)
    smgd_jz.index=smgd_jz.index.strftime('%Y%m%d')
    smgd_jz=smgd_jz.drop('tjrq',axis=1)
    smgd_jz.reset_index(inplace=True)
    smgd_jz = smgd_jz[(smgd_jz['调入时间'] < smgd_jz['tjrq']) & (smgd_jz['调出时间'] >= smgd_jz['tjrq'])]
    smgd_jz=smgd_jz.pivot('tjrq','jjdm','hb1z')
    smgd_jz=smgd_jz[smgd_jz.index <= end_date]
    # #smgd_jz = fill_na_with_previous_values(smgd_jz)
    smgd_jz=smgd_jz.mean(axis=1)/100
    smgd_jz = (smgd_jz + 1).cumprod()
    return smgd_jz

zx_zg_nav=get_zx_nav(zx_zg,)
zx_lh_nav=get_zx_nav(zx_lh)
zx_cta_nav=get_zx_nav(zx_cta)
zx_zx_nav=get_zx_nav(zx_zx)  #中性
zx_hg_nav=get_zx_nav(zx_hg)  #宏观
zx_smz_nav=get_zx_nav(zx_smz)

###求公募债日净值
def get_zx_gm_nav(zx_group):
    sql_gmfz = "select jjdm,hbdr,jzrq from st_fund.t_st_gm_rhb where jjdm in {0} and jzrq>='20201228' and hbdr!=99999" .format(tuple(zx_group['基金代码']))
    gmfz_jz= get_df(sql_gmfz,db='funduser',page_size=200000)
    gmfz_jz = pd.merge(gmfz_jz, zx_group, how='left', left_on='jjdm', right_on='基金代码')
    gmfz_jz['jzrq'] = gmfz_jz['jzrq'].astype(str)
    smgd_jz = gmfz_jz[(gmfz_jz['调入时间'] < gmfz_jz['jzrq']) & (gmfz_jz['调出时间'] >= gmfz_jz['jzrq'])]
    smgd_jz = smgd_jz.groupby(['jzrq']).mean()['hbdr'] / 100
    smgd_jz = (smgd_jz + 1).cumprod()
    return smgd_jz
zx_gmz_nav=get_zx_gm_nav(zx_gmz)

#计算区间收益率
def cal_return(frame_data, date, days_list):
    output = {}
    frame_data.index = pd.to_datetime(frame_data.index, format='%Y-%m-%d')
    dt = pd.to_datetime(date)
    for day in days_list:
        delta = timedelta(days=day)
        if frame_data.index[0] > dt - delta:
            cal_return = (frame_data.iloc[-1] / np.nan - 1) * 100
        else:
            idx = frame_data.index[frame_data.index.get_loc(dt - delta, method='nearest')]
            stop_date = np.where(frame_data.index == pd.to_datetime(idx))[0][0]
            cal_return = (frame_data.loc[date] / frame_data.iloc[stop_date] - 1) *100
        output[day] = {'截止日': date, '收益率': cal_return}
    output = pd.DataFrame(output)
    output = output.iloc[1]
    output.index = ['近1年', '近6月', '近3月','近1月','今年以来']
    output = pd.DataFrame(output)
    return output

zx_lh_return=cal_return(zx_lh_nav,end_date,time_list)
zx_zg_return=cal_return(zx_zg_nav,end_date,time_list)
zx_cta_return=cal_return(zx_cta_nav,end_date,time_list)
zx_zx_return=cal_return(zx_zx_nav,end_date,time_list)  #中性
#zx_hg_return=cal_return(zx_hg_nav,end_date,time_list)  #宏观
zx_smz_return=cal_return(zx_smz_nav,end_date,time_list)  #私募债  2023-7-14
zx_gmz_return=cal_return(zx_gmz_nav,end_date,time_list)
final=pd.concat([zx_lh_return, zx_zg_return,zx_cta_return,zx_zx_return,zx_smz_return,zx_gmz_return], axis=1)#zx_hg_return,
final.columns=['量化指增','主观','CTA','中性','私募债','公募债']

#计算年区间收益
final2=pd.concat([zx_lh_nav, zx_zg_nav,zx_cta_nav,zx_zx_nav,zx_smz_nav], axis=1) #,zx_gmz_nav
final2.columns=['量化指增','主观','CTA','中性','私募债']
result_22=((final2.loc['2022-12-30']/final2.loc['2021-12-31']-1)*100).to_frame('2022')
result_21=((final2.loc['2021-12-31']/final2.loc['2021-01-01']-1)*100).to_frame('2021')
result_22_gmz=(zx_gmz_nav.loc['2022-12-30']/zx_gmz_nav.loc['2021-12-31']-1)*100
result_21_gmz=(zx_gmz_nav.loc['2021-12-31']/zx_gmz_nav.loc['2020-12-31']-1)*100
result_22.loc['公募债']=result_22_gmz
result_21.loc['公募债']=result_21_gmz

#整合收益结果
final=pd.concat([final,result_22.T,result_21.T])

###臻选30池业绩明细
jj_list=pd.read_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/30list.xlsx")
sql_script="SELECT a.jjdm 基金代码, a.jjjc 基金简称,  a.clrq 成立日期, MAX(b.jzrq) 净值日期,\
             round(b.hb1n, 2) 近1年, round(c.hb6y, 2) 近6月, round(d.hb3y, 2) 近3月,\
             round(e.hb1y, 2) 近1月, round(f.hbjn, 2) 今年以来, round(g.hb2n, 2) 近2年,\
             round(h.hb3n, 2) 近3年, round(i.hbcl, 2) 成立以来, l.hb2022 2022年度收益率, m.hb2021 2021年度收益率 \
             FROM st_hedge.t_st_jjxx a left join (select jjdm, jzrq, zbnp hb1n from st_hedge.t_st_sm_qjhb_zj where zblb = '2201') b\
             on a.jjdm = b.jjdm left join(select jjdm, jzrq, zbnp hb6y from st_hedge.t_st_sm_qjhb_zj where zblb = '2106') c\
             on a.jjdm = c.jjdm and b.jzrq = c.jzrq left join(select jjdm, jzrq, zbnp hb3y from st_hedge.t_st_sm_qjhb_zj where zblb = '2103') d\
             on a.jjdm = d.jjdm and b.jzrq = d.jzrq left join(select jjdm, jzrq, zbnp hb1y from st_hedge.t_st_sm_qjhb_zj where zblb = '2101') e\
             on a.jjdm = e.jjdm and b.jzrq = e.jzrq left join(select jjdm, jzrq, zbnp hbjn from st_hedge.t_st_sm_qjhb_zj where zblb = '2998') f\
             on a.jjdm = f.jjdm and b.jzrq = f.jzrq left join(select jjdm, jzrq, zbnp hb2n from st_hedge.t_st_sm_qjhb_zj where zblb = '2202') g\
             on a.jjdm = g.jjdm and b.jzrq = g.jzrq left join(select jjdm, jzrq, zbnp hb3n from st_hedge.t_st_sm_qjhb_zj where zblb = '2203') h\
             on a.jjdm = h.jjdm and b.jzrq = h.jzrq left join(select jjdm, jzrq, zbnp hbcl from st_hedge.t_st_sm_qjhb_zj where zblb = '2999') i\
             on a.jjdm = i.jjdm and b.jzrq = i.jzrq left join (select jjdm,hb1n hb2022 from st_hedge.t_st_sm_nhb where tjnf='2022' and hblb='1' and m_opt_type<>'03') l \
             on a.jjdm=l.jjdm left join (select jjdm,hb1n hb2021 from st_hedge.t_st_sm_nhb where tjnf='2021' and hblb='1' and m_opt_type<>'03') m \
             on a.jjdm=m.jjdm\
             WHERE b.jzrq <='{0}'\
             AND a.jjdm in {1} GROUP BY a.jjdm ORDER BY b.jzrq DESC".format(end_date,tuple(jj_list['基金代码']))

sm_result = get_df(sql_script,db='highuser',page_size=200000)
sm_result=sm_result.replace(99999.00,None)
sm_result=sm_result[['基金简称','基金代码','成立日期','净值日期','近1年','近6月','近3月','近1月','今年以来','2022年度收益率','2021年度收益率']]

###求公募（债）日净值
def get_zx_gm_nav(zx_group,start_date):
    sql_gmfz = "select jjdm,hbdr,jzrq from st_fund.t_st_gm_rhb where jjdm in {0} and jzrq>='{1}' and hbdr!=99999" .format(tuple(zx_group['基金代码']),start_date)
    smgd_jz= get_df(sql_gmfz,db='funduser',page_size=200000)
    smgd_jz=smgd_jz.pivot('jzrq', 'jjdm', 'hbdr')
    smgd_jz=smgd_jz/100
    smgd_jz = (smgd_jz + 1).cumprod()
    return smgd_jz
zx_gmz_nav=get_zx_gm_nav(jj_list,'20201228')
summary = pd.DataFrame(index=['近1年','近6月','近3月','近1月','今年以来','2022年度收益率','2021年度收益率'],columns=zx_gmz_nav.columns)
jyn=(pd.to_datetime(end_date)-timedelta(days=365)).strftime(format="%Y%m%d")
jly=(pd.to_datetime(end_date)-timedelta(days=180)).strftime(format="%Y%m%d")
jsy=(pd.to_datetime(end_date)-timedelta(days=90)).strftime(format="%Y%m%d")
jyy=(pd.to_datetime(end_date)-timedelta(days=30)).strftime(format="%Y%m%d")
summary.iloc[0]=(zx_gmz_nav.loc[int(end_date)]/zx_gmz_nav.iloc[zx_gmz.index[zx_gmz.index.get_loc(int(jyn), method='nearest')]]-1)*100
summary.iloc[1]=(zx_gmz_nav.loc[int(end_date)]/zx_gmz_nav.iloc[zx_gmz.index[zx_gmz.index.get_loc(int(jly), method='nearest')]]-1)*100
summary.iloc[2]=(zx_gmz_nav.loc[int(end_date)]/zx_gmz_nav.iloc[zx_gmz.index[zx_gmz.index.get_loc(int(jsy), method='nearest')]]-1)*100
summary.iloc[3]=(zx_gmz_nav.loc[int(end_date)]/zx_gmz_nav.iloc[zx_gmz.index[zx_gmz.index.get_loc(int(jyy), method='nearest')]]-1)*100
summary.iloc[4]=(zx_gmz_nav.loc[int(end_date)]/zx_gmz_nav.loc[20221231]-1)*100
summary.iloc[5]=(zx_gmz_nav.loc[20221230]/zx_gmz_nav.loc[20211231]-1)*100
summary.iloc[6]=(zx_gmz_nav.loc[20211231]/zx_gmz_nav.loc[20201231]-1)*100
summary=summary.T

#求臻选30池bmk的回报
# #求好买指数年回报
# sql="select zsdm 指数代码, tjnf 统计月份, hb1n 回报1年 from st_hedge.t_st_sm_zhmzsnhb where zsdm='HB0018' and tjnf='2022'"
# return_n=get_df(sql,db='highuser',page_size=2000000)

# #求好买指数周回报
def get_hmzs_return(date_month):  #date_month:202306
    sql_script="select zsdm 指数代码, jyrq 交易日期, hb1y 近1月, hb3y 近3月, hb6y 近6月,hbjn 今年以来, hb1n 近1年, hb2n\
     近2年, hb3n 近3年 from st_hedge.t_st_sm_zhmzs where zsdm in ('HB0011','HB0012','HB0014','HB0015','HB0017','HB0018'\
     ,'HB001b','HB001d','HB0001','HB0000','HB0002','HB1001','HB1002','HB001c','HB0004','HB0005','HB0006') and jyrq ={0}".format(date_month)
    hmzs_return=get_df(sql_script,db='highuser',page_size=2000000)
    return hmzs_return
bmk_result=get_hmzs_return(int(end_date))

writer= pd.ExcelWriter(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/臻选30池result.xlsx")
final.to_excel(writer,sheet_name='整池业绩')
sm_result.to_excel(writer,sheet_name='私募明细')
summary.to_excel(writer,sheet_name='公募明细')
bmk_result.to_excel(writer,sheet_name='bmk业绩')
writer.save()