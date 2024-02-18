# coding: utf-8

import pandas as pd
import hbshare as hbs

def get_df(sql, db, page_size=2000):
    data = hbs.db_data_query(db, sql, page_size=page_size, timeout=120)
    pages = data['pages']
    data = pd.DataFrame(data['data'])
    if pages > 1:
        for page in range(2, pages + 1):
            temp_data = hbs.db_data_query(db, sql, page_size=page_size, page_num=page, timeout=120)
            data = pd.concat([data, pd.DataFrame(temp_data['data'])], axis=0)
    return data

jj_list=pd.read_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/30list.xlsx")
###甄选30池(私募)---公募的最新业绩可直接从AMS中导入
sql="SELECT a.jjdm 基金代码, a.jjjc 基金简称, j.jgjc 机构简称, a.clrq 成立日期, b.jzrq 净值日期, round(b.hb1y, 2) 近1月,round(k.hb6y,2) 近6月,\
round(c.hbjn, 2) 今年以来, l.hb2022 2022年度收益率, round(d.hb1n, 2) 近1年, round(f.zdhc1n, 2) 近1年最大回撤, round(g.nhbdl1n, 2) 近1年年化波动率,\
round(h.nhxp1n, 2) 近1年年化夏普, round(i.km1n, 2) 近1年卡玛 FROM st_hedge.t_st_jjxx a left join(select jjdm, jzrq, zbnp hb1y \
from st_hedge.t_st_sm_qjhb_zx where zblb = '2101') b on a.jjdm = b.jjdm left join (select jjdm, jzrq, zbnp hb6y \
from st_hedge.t_st_sm_qjhb_zx where zblb = '2106') k on a.jjdm=k.jjdm and b.jzrq=k.jzrq left join (select jjdm, jzrq, zbnp hbjn \
from st_hedge.t_st_sm_qjhb_zx where zblb = '2998') c on a.jjdm = c.jjdm and b.jzrq = c.jzrq left join(select jjdm, jzrq, zbnp hb1n \
from st_hedge.t_st_sm_qjhb_zx where zblb = '2201') d on a.jjdm = d.jjdm and b.jzrq = d.jzrq left join (select jjdm,hb1n hb2022 \
from st_hedge.t_st_sm_nhb where tjnf='2022' and hblb='1' and m_opt_type<>'03') l on a.jjdm=l.jjdm left join(select jjdm, jzrq, zbnp zdhc1n \
from st_hedge.t_st_sm_qjzdhc_zx where zblb = '2201') f on a.jjdm = f.jjdm and b.jzrq = f.jzrq left join(select jjdm, jzrq, nhzbnp nhbdl1n \
from st_hedge.t_st_sm_qjbdlzp_zx where zblb = '2201') g on a.jjdm = g.jjdm and b.jzrq = g.jzrq left join(select jjdm, jzrq, nhzbnp nhxp1n \
from st_hedge.t_st_sm_qjxpblzp_zx where zblb = '2201') h on a.jjdm = h.jjdm and b.jzrq = h.jzrq left join(select jjdm, jzrq, zbnp km1n \
from st_hedge.t_st_sm_qjkmbl_zx where zblb = '2201') i on a.jjdm = i.jjdm and b.jzrq = i.jzrq join broadcast.t_st_gg_jgxx j on a.glrm = j.jgdm \
WHERE a.jjdm in {0}".format(tuple(jj_list['基金代码']))
data = hbs.db_data_query("highuser", sql, page_size=5000)
data = pd.DataFrame(data['data'])
data=data.replace(99999.00,None)
data=data[['基金简称','基金代码','成立日期','机构简称','净值日期','近1月','近6月','近1年','今年以来','2022年度收益率','近1年年化波动率','近1年最大回撤','近1年年化夏普','近1年卡玛']]
data.to_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/zx30.xlsx")

#私募重点关注池业绩
sql_script1="SELECT a.jjdm 基金代码, a.jjjc 基金简称,a.clrq 成立日期,d.jzrq 净值日期,round(d.hb1y, 2)近1月,round(e.hb3y, 2)近3月, \
round(f.hb6y, 2)近6月,round(g.hbjn,2) 今年以来,round(j.hb1n, 2)近1年,round(k.zdhc1n, 2)近1年最大回撤 FROM st_hedge.t_st_jjxx a left join \
(select jjdm, jzrq, zbnp hb1y from st_hedge.t_st_sm_qjhb_zx where zblb = '2101') d on a.jjdm = d.jjdm left join \
(select jjdm, jzrq, zbnp hb3y from st_hedge.t_st_sm_qjhb_zx where zblb = '2103') e on a.jjdm = e.jjdm and d.jzrq = e.jzrq \
left join(select jjdm, jzrq, zbnp hb6y from st_hedge.t_st_sm_qjhb_zx where zblb = '2106') f on a.jjdm = f.jjdm and d.jzrq = f.jzrq \
left join(select jjdm, jzrq, zbnp hbjn from st_hedge.t_st_sm_qjhb_zx where zblb = '2998') g on a.jjdm = g.jjdm and d.jzrq = g.jzrq \
left join(select jjdm, jzrq, zbnp hb1n from st_hedge.t_st_sm_qjhb_zx where zblb = '2201') j on a.jjdm = j.jjdm and d.jzrq = j.jzrq \
left join(select jjdm, jzrq, zbnp zdhc1n from st_hedge.t_st_sm_qjzdhc_zx where zblb = '2201') k on a.jjdm = k.jjdm and d.jzrq = k.jzrq \
WHERE a.jjdm in ('P31955','P33712','SNR622','SLS817','SGS479','P00107','S64497','ST7318',\
'SEP463','SEU010','S83614','SQG281','SEM323','SLJ139','SLD634','S84924','SCP381','ST9804','SNA859','SR8969','SR6089','SS0221','S65362',\
'STD264','SEE186','SW3470','STA188','SJB208','SES760','SGB086','S27825','SJJ217','P49022','SX2090','SNR480','SGY379','SNL641','S66676',\
'SX9799','SY0344','SNL399','SK8618','6E0108','SNK854','P40769','S85909','SJ7016','P16556','STH711','SX6659','SJU280','SCW485','SN1819',\
'SJU836','SE6168','SEH477','SNU706','SLW375','SLW376','SNP701','SGR247','SJK215','P21481','S83994','S27518','SJF777','SEJ470','SSJ711',\
'SN1577','H00014','P12095','STP927','S20717','SL4437','P23195','246039','S22497','SXS233')"

data1 = hbs.db_data_query("highuser", sql_script1, page_size=5000)
data1 = pd.DataFrame(data1['data'])
data1=data1[['基金代码','基金简称','成立日期','净值日期','近1月','近3月','近6月','今年以来','近1年','近1年最大回撤']]
data1=data1.replace(99999,None)

# test=pd.read_excel(r"C:\Users\jiemin.yu\Desktop\业绩统计\月度-7-30池、重点关注指增业绩\2-重点关注指增\私募重点关注池202305.xlsx",sheet_name='数据库（原始数据）')

writer= pd.ExcelWriter(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/私募重点关注池.xlsx")
data1.to_excel(writer,sheet_name='私募重点关注池')
writer.save()

#重点关注指增业绩
test=pd.read_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/重点关注指增产品名单.xlsx",sheet_name='指增名单')
sql_script2="SELECT a.jjdm 基金代码, a.jjjc 基金简称, d.jzrq 净值日期, round(d.hb1y, 2) 近1月, round(e.hb3y, 2) 近3月, round(f.hb6y, 2) 近6月,\
round(g.hbjn, 2) 今年以来, round(j.hb1n, 2) 近1年, round(k.zdhc1n, 2) 近1年最大回撤 FROM st_hedge.t_st_jjxx a left join(select \
jjdm, jzrq, zbnp hb1y from st_hedge.t_st_sm_qjhb_zx where zblb = '2101') d on a.jjdm = d.jjdm left join(select jjdm, jzrq, zbnp \
hb3y from st_hedge.t_st_sm_qjhb_zx where zblb = '2103') e on a.jjdm = e.jjdm and d.jzrq = e.jzrq left join(select jjdm, jzrq, zbnp hb6y from st_hedge.t_st_sm_qjhb_zx where \
zblb = '2106') f on a.jjdm = f.jjdm and d.jzrq = f.jzrq left join(select jjdm, jzrq, zbnp hbjn from st_hedge.t_st_sm_qjhb_zx where \
zblb = '2998') g on a.jjdm = g.jjdm and d.jzrq = g.jzrq left join(select jjdm, jzrq, zbnp hb1n from st_hedge.t_st_sm_qjhb_zx where \
zblb = '2201') j on a.jjdm = j.jjdm and d.jzrq = j.jzrq left join(select jjdm, jzrq, zbnp zdhc1n from st_hedge.t_st_sm_qjzdhc_zx where \
zblb = '2201') k on a.jjdm = k.jjdm and d.jzrq = k.jzrq WHERE a.jjdm in {0}".format(tuple(test['基金代码']))
data2 = hbs.db_data_query("highuser", sql_script2, page_size=5000)
data2 = pd.DataFrame(data2['data'])
data2=data2.replace(99999,None)
data2=data2[['基金简称','净值日期','近1月','近3月','近6月','今年以来','近1年','近1年最大回撤']]
writer= pd.ExcelWriter(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/重点指增区间收益.xlsx")
data2.to_excel(writer,sheet_name='重点指增区间收益')
writer.save()

#重点关注指增超额收益
sql_script3="select a.jjdm 基金代码,a.jjjc 基金简称,b.jzrq 净值日期,round(b.hb1y,4) 超额1月,round(c.hb3y,4) 超额3月,round(d.hb6y,4) 超额6月,\
round(e.hb1n,4) 超额1年,round(f.zdhc1n,4) 超额1年最大回撤, round(g.hbjn, 2) 超额今年以来超额 from st_hedge.t_st_jjxx a left join (select jjdm,jzrq,zbnp hb1y from st_hedge.t_st_sm_ceqjhb_zx where zblb='2101') b \
on a.jjdm=b.jjdm left join (select jjdm,jzrq,zbnp hb3y from st_hedge.t_st_sm_ceqjhb_zx where zblb='2103') c on a.jjdm=c.jjdm and b.jzrq=c.jzrq \
left join (select jjdm,jzrq,zbnp hb6y from st_hedge.t_st_sm_ceqjhb_zx where zblb='2106') d on a.jjdm=d.jjdm and b.jzrq=d.jzrq \
left join (select jjdm,jzrq,zbnp hb1n from st_hedge.t_st_sm_ceqjhb_zx where zblb='2201') e on a.jjdm=e.jjdm and b.jzrq=e.jzrq \
left join (select jjdm,jzrq,zbnp zdhc1n from st_hedge.t_st_sm_ceqjzdhc_zx where zblb='2201') f on a.jjdm=f.jjdm and b.jzrq=f.jzrq \
left join (select jjdm,jzrq,zbnp hbjn from st_hedge.t_st_sm_ceqjhb_zx where zblb='2998') g on a.jjdm=g.jjdm and b.jzrq=g.jzrq \
where a.jjdm in {0} ".format(tuple(test['基金代码']))
data3 = hbs.db_data_query("highuser", sql_script3, page_size=5000)
data3 = pd.DataFrame(data3['data'])
data3 = data3.replace(99999, None)
data3=data3[['基金简称','净值日期','超额1月','超额3月','超额6月','超额今年以来超额','超额1年','超额1年最大回撤']]

writer= pd.ExcelWriter(r"D:/Git/hbshare/hbshare/fe/xwq/data/臻选30池/重点指增超额收益.xlsx")
data3.to_excel(writer,sheet_name='重点指增超额收益')
writer.save()
