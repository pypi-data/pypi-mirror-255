# -*- coding: utf-8 -*-


import pandas as pd
import hbshare as hbs
pd.options.display.precision = 8


#取竞品FOF业绩
sql_script="SELECT a.jjdm 基金代码, a.jjjc 基金简称, a.clrq 成立日期, o.jgjc 机构简称, b.jzrq 净值日期, round(b.hb1z,2) 近1周,\
round(c.hbsz,2) 前1周,round(d.hb1y,2) 近1月,round(e.hb3y,2) 近3月,round(f.hb6y,2) 近6月,round(g.hbjn,2) 今年以来,\
round(h.hbcl,2) 成立以来,round(y.hbcl,2) 成立以来年化收益率,round(j.hb1n,2) 近1年,round(r.hb2n,2) 近2年,round(s.hb3n,2) 近3年,concat(i.pmnp,'/',i.slnp) 近1年排名,round(k.zdhc1n,2) 近1年最大回撤,\
round(l.nhbdl1n,2) 近1年年化波动率,round(m.nhxp1n,2) 近1年年化夏普,round(n.km1n,2) 近1年卡玛 FROM st_hedge.t_st_jjxx a \
join broadcast.t_st_gg_jgxx o on a.glrm=o.jgdm left join (select jjdm,jzrq,zbnp hb1z from st_hedge.t_st_sm_qjhb_zx where \
zblb='2007') b on a.jjdm=b.jjdm left join (select jjdm,jzrq,zbnp hbsz from st_hedge.t_st_sm_qjhb_zx where zblb='2000') c \
on a.jjdm=c.jjdm and b.jzrq=c.jzrq left join (select jjdm,jzrq,zbnp hb1y from st_hedge.t_st_sm_qjhb_zx where zblb='2101') d \
on a.jjdm=d.jjdm and b.jzrq=d.jzrq left join (select jjdm,jzrq,zbnp hb3y from st_hedge.t_st_sm_qjhb_zx where zblb='2103') e \
on a.jjdm=e.jjdm and b.jzrq=e.jzrq left join (select jjdm,jzrq,zbnp hb6y from st_hedge.t_st_sm_qjhb_zx where zblb='2106') f \
on a.jjdm=f.jjdm and b.jzrq=f.jzrq left join (select jjdm,jzrq,zbnp hbjn from st_hedge.t_st_sm_qjhb_zx where zblb='2998') g \
on a.jjdm=g.jjdm and b.jzrq=g.jzrq left join (select jjdm,jzrq,zbnp hbcl from st_hedge.t_st_sm_qjhb_zx where zblb='2999') h \
on a.jjdm=h.jjdm and b.jzrq=h.jzrq left join (select jjdm,jzrq,nhzbnp hbcl from st_hedge.t_st_sm_qjhb_zx where zblb='2999') y \
on a.jjdm=y.jjdm and b.jzrq=y.jzrq left join (select * from st_hedge.t_st_sm_qjhbpm_zx where zblb='2201') i on a.jjdm=i.jjdm and b.jzrq=i.jzrq \
left join (select jjdm,jzrq,zbnp hb1n from st_hedge.t_st_sm_qjhb_zx where zblb='2201') j on a.jjdm=j.jjdm and b.jzrq=j.jzrq \
left join (select jjdm,jzrq,zbnp hb2n from st_hedge.t_st_sm_qjhb_zx where zblb='2202') r on a.jjdm=r.jjdm and b.jzrq=r.jzrq \
left join (select jjdm,jzrq,zbnp hb3n from st_hedge.t_st_sm_qjhb_zx where zblb='2203') s on a.jjdm=s.jjdm and b.jzrq=s.jzrq \
left join (select jjdm,jzrq,zbnp zdhc1n from st_hedge.t_st_sm_qjzdhc_zx where zblb='2201') k on a.jjdm=k.jjdm and b.jzrq=k.jzrq \
left join (select jjdm,jzrq,nhzbnp nhbdl1n from st_hedge.t_st_sm_qjbdlzp_zx where zblb='2201') l on a.jjdm=l.jjdm and b.jzrq=l.jzrq \
left join (select jjdm,jzrq,nhzbnp nhxp1n from st_hedge.t_st_sm_qjxpblzp_zx where zblb='2201') m on a.jjdm=m.jjdm and b.jzrq=m.jzrq \
left join (select jjdm,jzrq,zbnp km1n from st_hedge.t_st_sm_qjkmbl_zx where zblb='2201') n on a.jjdm=n.jjdm and b.jzrq=n.jzrq \
WHERE a.jjdm in ('SK1216', 'S21582', 'SCS026', 'SNQ525', 'SSY770', 'P48964', 'SEV618', 'SGR929', 'SGD165',\
'SNA926', 'SJV805', 'SNC380','SGG703','SSL554','SLJ259','SLN888','T11240','SND744','ST9786','SLG922','SJ4683','P48408','SM1593',\
'SLQ861','SQS733','B40029','SVE366','SJY901','SS6545','SJE919','SQQ425','T11393','S29494','ZJS03C','ZJS00C','SNX869','SXL639',\
'K00976','SNC004','P49480','SJT297','SNX811')"
data = hbs.db_data_query("highuser", sql_script, page_size=5000)
data = pd.DataFrame(data['data'])
data=data[['基金代码','基金简称','成立日期','机构简称','净值日期','近1周','前1周','近1月','近3月','近6月','今年以来','成立以来','近1年','近1年排名','近1年最大回撤','近1年年化波动率','近1年年化夏普','近1年卡玛','成立以来年化收益率','近2年','近3年',]]

data=data.replace(99999,None)
print(data)

writer= pd.ExcelWriter(r"D:/Git/hbshare/hbshare/fe/xwq/data/竞品FOF业绩统计/竞品FOF业绩统计.xlsx")
data.to_excel(writer,sheet_name='竞品FOF')
writer.save()


#取竞品年回报业绩
def get_nhb():
    sql_script="select a.jjdm,a.jjjc,b.hb2021,c.hb2022 from st_hedge.t_st_jjxx a left join (select jjdm,hb1n hb2021 from st_hedge.t_st_sm_nhb where tjnf='2021' and hblb='1' and m_opt_type<>'03') b \
    on a.jjdm=b.jjdm left join (select jjdm,hb1n hb2022 from st_hedge.t_st_sm_nhb where tjnf='2022' and hblb='1' and m_opt_type<>'03') c on a.jjdm=c.jjdm where a.m_opt_type<>'03' and a.jjdm in \
    ('SK1216','S21582','SCS026','SNQ525','SSY770','P48964','SEV618','SGR929','SGD165','SNA926','SJV805','SNC380','SGG703','SSL554','SLJ259','SLN888','T11240','SND744','ST9786',\
    'SLG922','SJ4683','P48408','SM1593','SLQ861','SQS733','B40029','SVE366','SJY901','SS6545','SJE919','SQQ425','T11393','S29494','ZJS03C','ZJS00C','SNX869','SXL639',\
    'K00976','SNC004','P49480','SJT297','SNX811')"
    data = hbs.db_data_query("highuser", sql_script, page_size=5000)
    data = pd.DataFrame(data['data'])


