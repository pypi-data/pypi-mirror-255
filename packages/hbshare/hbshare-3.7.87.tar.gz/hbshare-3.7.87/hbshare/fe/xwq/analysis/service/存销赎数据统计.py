#!/usr/bin/env python
# coding: utf-8
from datetime import datetime
import datetime
import math
import collections
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# todo: 根据最新需求文档修改产品分类代码
current_month='2023年9月'   #当月月份

xs_data=pd.read_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/存销赎数据统计/FOF交易确认数据.xlsx") #销售&赎回数据
cl_data=pd.read_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/存销赎数据统计/FOF存量-按月.xlsx")   #存量数据
ej_data=pd.read_excel(r"D:/Git/hbshare/hbshare/fe/xwq/data/存销赎数据统计/二级交易确认数据.xlsx")  #所有二级产品数据

#产品分类
dlpz_p=['SSY770','SK1216','SSD164','SNQ525','SXM130','SCS026','S21582','STQ402','STN120','STR813']
zx30_p=['SQQ779','SQP613','SQL942']
zz_p=['SGG703','SSL554','SVX353']
cta_p=['SLG922','SGR135','SJ4683','P48408']
tl_p=['SNX811','SB8283']
sp_p=['SXL638','SZD564','SJS293']
zggd_p=['S29494','SNY349','S22275','P48413','P10181']
zh_p=['SZH407','SVN990','STB453','SEB475','SST686','SSW281','STU728','SQG155','SB6486','S36248']
zx_p=['SJY901']

dlpz=['SSY770','SK1216','SSD164','SNQ525','SXM130','SCS026','S21582','STS126','STP163','SVW926','STQ404']
zx30=['SZX345','SZT053','SZJ122','SZJ176','STQ332','STE846','SSP687','STV741','STU416','STU037','SVE299','SVH187','SVM724','SVT788','SVV143','SVY113','SVY106','STY349','SXD511','SXE219','STJ323','STH865','STE833','STD495','STD456','STC036','SSZ137','SST971','SST962','SQS219']
zz=['SGG703','SSL554','SVX355']
cta=['SLG922','SGR135','SJ4683','P48408']
tl=['SNX811','SB8283']
sp=['SXL639','SZD565','SJS293']
zggd=['S29494','SNY349','S22275','P48413','P10181']
zh=['SZH407','SVN990','STB453','SEB475','SST686','SSW281','STU728','SQG155','SB6486','S36248']
zx=['SJY901']

def transfer_index(xl_xfcp):
    xl_xfcp.index = xl_xfcp.index.astype(str)
    xl_xfcp.index = pd.to_datetime(xl_xfcp.index, format='%Y年%m月')
    xl_xfcp.index = xl_xfcp.index.strftime('%Y-%m')
    xl_xfcp.sort_index(inplace=True)
    return xl_xfcp

def classify_fund(code):
    if code in dlpz:
        return '大类配置'
    elif code in zx30:
        return '甄选30'
    elif code in zz:
        return '指增'
    elif code in cta:
        return 'cta'
    elif code in tl:
        return '套利'
    elif code in sp:
        return '双拼'
    elif code in zggd:
        return '主观股多'
    elif code in zh:
        return '专户'
    elif code in zx:
        return '中性'      
###给基金产品分类打标签
xs_data['分类'] = xs_data['基金代码'].apply(lambda x: classify_fund(x))
cl_data['分类'] = cl_data['基金代码'].apply(lambda x: classify_fund(x))

###产品净申购分析
xs_data2=xs_data.copy()
xs_data2.set_index('交易日期（统计）',inplace=True)
xs_data2=transfer_index(xs_data2)
xs_data2.loc[xs_data2['交易类型'].isin(['认购确认', '申购确认']), '操作类型'] = 'buy'
xs_data2.loc[xs_data2['交易类型'].isin(['赎回确认', '强制赎回']), '操作类型'] = 'sell'
a=pd.DataFrame(xs_data2[xs_data2['操作类型']=='buy'].groupby(['分类','交易日期（统计）']).sum()['确认市值'])
b=pd.DataFrame(xs_data2[xs_data2['操作类型']=='sell'].groupby(['分类','交易日期（统计）']).sum()['确认市值'])
d=pd.merge(a,b,how='outer',left_index=True,right_index=True)
d=d.fillna(0)
d.columns=['buy','sell']
d['净申购']=d['buy']-d['sell']

def get_group_result(df):
    df_result=df.groupby('交易日期（统计）').sum()['确认市值']
    return df_result

xl=xs_data[xs_data['交易类型'].isin(['申购确认','认购确认'])]   #销量数据
sh=xs_data[xs_data['交易类型'].isin(['强制赎回','赎回确认'])]   #赎回数据
ej_data=ej_data[ej_data['交易类型'].isin(['申购确认','认购确认'])]   #二级产品销量数据

###销量月度打款情况
xl_yddk=xl.groupby('交易日期（统计）').sum()['确认市值']
sh_yddk=sh.groupby('交易日期（统计）').sum()['确认市值']
ej_data=ej_data.groupby('交易日期（统计）').sum()['确认市值']
#ej_data.set_index('Unnamed: 0',inplace=True)
xlzb=pd.DataFrame(xl_yddk/ej_data)  #fof销量占二级产品销量的占比

xl_yddk=transfer_index(xl_yddk)
sh_yddk=transfer_index(sh_yddk)
xlzb=transfer_index(xlzb)


### 重点产品销量走势 & 当月FOF销量细分产品
def cal_df(xl):
    xl_dlpz=xl[xl['基金代码'].isin(dlpz)]
    xl_zx30=xl[xl['基金代码'].isin(zx30)]
    xl_zz=xl[xl['基金代码'].isin(zz)]
    xl_cta=xl[xl['基金代码'].isin(cta)]
    xl_tl=xl[xl['基金代码'].isin(tl)]
    xl_sp=xl[xl['基金代码'].isin(sp)]
    xl_zggd=xl[xl['基金代码'].isin(zggd)]
    xl_zh=xl[xl['基金代码'].isin(zh)]
    xl_zx=xl[xl['基金代码'].isin(zx)]

    xl_xfcp=[]
    for i in [xl_dlpz,xl_zx30,xl_zz,xl_cta,xl_tl,xl_sp,xl_zggd,xl_zh,xl_zx]:
        xl_result=get_group_result(i)
        xl_xfcp.append(xl_result)
    xl_xfcp=pd.DataFrame(xl_xfcp).T
    xl_xfcp.columns=['大类配置','甄选30','指增','cta','套利','双拼','主观股多','专户','中性']

    xl_xfcp.index=xl_xfcp.index.astype(str)
    xl_xfcp.index=pd.to_datetime(xl_xfcp.index,format='%Y年%m月')
    xl_xfcp.index=xl_xfcp.index.strftime('%Y-%m')
    xl_xfcp.sort_index(inplace=True)
    return xl_xfcp
xl_xfcp=cal_df(xl)
sh_xfcp=cal_df(sh)
jsg_xfcp=xl_xfcp.fillna(0)-sh_xfcp.fillna(0)  #净申购产品细分

xl['二级组织名称'].fillna('其他',inplace=True)
xl_hbc=xl[(xl['一级组织名称']=='高端业务中心')&(xl['交易日期（统计）']==current_month)]
xl_ic=xl[(xl['一级组织名称']=='财富管理中心')&(xl['交易日期（统计）']==current_month)]
xl_hbc_all=xl[(xl['一级组织名称']=='高端业务中心')]
xl_ic_all=xl[(xl['一级组织名称']=='财富管理中心')]
xl_all=xl[xl['一级组织名称'].isin(['高端业务中心','财富管理中心'])&(xl['交易日期（统计）']==current_month)]

sh['二级组织名称'].fillna('其他',inplace=True)
sh_hbc=sh[(sh['一级组织名称']=='高端业务中心')&(sh['交易日期（统计）']==current_month)]
sh_ic=sh[(sh['一级组织名称']=='财富管理中心')&(sh['交易日期（统计）']==current_month)]
sh_hbc_all=sh[(sh['一级组织名称']=='高端业务中心')]
sh_ic_all=sh[(sh['一级组织名称']=='财富管理中心')]
#sh_all=xl[(sh['一级组织名称']=='高端业务中心')&(sh['交易日期（统计）']== current_month)&(sh['一级组织名称']=='财富管理中心')]
sh_all=sh[sh['一级组织名称'].isin(['高端业务中心','财富管理中心'])&(sh['交易日期（统计）']== current_month)]

#按产品标签维度(当月)
xl_cp=pd.DataFrame(xl_all.groupby(['分类','一级组织名称','二级组织名称','三级组织名称']).sum()['确认市值'])
sh_cp=pd.DataFrame(sh_all.groupby(['分类','一级组织名称','二级组织名称','三级组织名称']).sum()['确认市值'])

###ic & hbc 总的时序销赎数据

xl_hbc_yddk=xl_hbc_all.groupby('交易日期（统计）').sum()['确认市值']
xl_ic_yddk=xl_ic_all.groupby('交易日期（统计）').sum()['确认市值']
sh_hbc_yddk=sh_hbc_all.groupby('交易日期（统计）').sum()['确认市值']
sh_ic_yddk=sh_ic_all.groupby('交易日期（统计）').sum()['确认市值']

xl_hbc_yddk=transfer_index(xl_hbc_yddk)
xl_ic_yddk=transfer_index(xl_ic_yddk)
sh_hbc_yddk=transfer_index(sh_hbc_yddk)
sh_ic_yddk=transfer_index(sh_ic_yddk)

###ic & hbc 细分产品的时序销赎数据
xl_hbc_xfcp=cal_df(xl_hbc_all)
xl_ic_xfcp=cal_df(xl_ic_all)
sh_hbc_xfcp=cal_df(sh_hbc_all)
sh_ic_xfcp=cal_df(sh_ic_all)

###FOF月度各区域  IC & HBC
def get_xf_group(xl_hbc):
    #各区域fof产品销售
    xl_hbc_qy=pd.DataFrame(xl_hbc.groupby(['二级组织名称']).sum()['确认市值'])
    #各分公司fof销量
    xl_hbc_fgs=pd.DataFrame(xl_hbc.groupby(['二级组织名称','三级组织名称']).sum()['确认市值'])#.head(3)
    #按产品分-各分公司
    xl_hbc_cp=pd.DataFrame(xl_hbc.groupby(['二级组织名称','三级组织名称','基金代码']).sum()['确认市值'])
    xl_hbc_cpfl=pd.DataFrame(xl_hbc.groupby(['二级组织名称','三级组织名称','分类']).sum()['确认市值'])
    return xl_hbc_qy,xl_hbc_fgs,xl_hbc_cp,xl_hbc_cpfl

xl_hbc_qy,xl_hbc_fgs,xl_hbc_cp,xl_hbc_cpfl=get_xf_group(xl_hbc)
xl_ic_qy,xl_ic_fgs,xl_ic_cp,xl_ic_cpfl=get_xf_group(xl_ic)
sh_hbc_qy,sh_hbc_fgs,sh_hbc_cp,sh_hbc_cpfl=get_xf_group(sh_hbc)
sh_ic_qy,sh_ic_fgs,sh_ic_cp,sh_ic_cpfl=get_xf_group(sh_ic)

####################################################################################################
###存量数据分析
cl_data.rename(columns={'一级架构':'一级组织名称','二级架构':'二级组织名称','三级架构':'三级组织名称','四级架构':'四级组织名称','存量日期':'交易日期（统计）','存量市值':'确认市值'},inplace=True)
cl_data['二级组织名称'].fillna('其他',inplace=True)
cl_data = cl_data[cl_data['基金代码'].isin(dlpz + zx30 + zz + cta + tl + sp + zggd + zh + zx)]
cl_data_p = cl_data[cl_data['基金代码'].isin(dlpz_p + zx30_p + zz_p + cta_p + tl_p + sp_p + zggd_p + zh_p + zx_p)]
#总存量
cl_zcl=cl_data_p.groupby('交易日期（统计）').sum()['确认市值']
cl_zcl=cl_zcl.reset_index()
cl_zcl['年']=cl_zcl['交易日期（统计）'].apply(lambda x: x.split('年')[0])
cl_zcl['月']=cl_zcl['交易日期（统计）'].apply(lambda x: x.split('年')[1].split('月')[0].zfill(2))
cl_zcl['交易日期（统计）']=cl_zcl.apply(lambda x: x['年'] + '-' + x['月'], axis=1)
cl_zcl=cl_zcl.drop(['年', '月'], axis=1).set_index('交易日期（统计）')
cl_zcl=cl_zcl.sort_index()
#月度存量走势 & 当月各产品存量占比
cl_xfcp=cal_df(cl_data_p)
#按产品标签维度(当月)
cl_all=cl_data[cl_data['一级组织名称'].isin(['高端业务中心','财富管理中心'])&(cl_data['交易日期（统计）']== current_month)]
cl_cp=pd.DataFrame(cl_all.groupby(['分类','一级组织名称','二级组织名称','三级组织名称']).sum()['确认市值'])

cl_hbc=cl_data[(cl_data['一级组织名称']=='高端业务中心')&(cl_data['交易日期（统计）']== current_month)]
cl_ic=cl_data[(cl_data['一级组织名称']=='财富管理中心')&(cl_data['交易日期（统计）']== current_month)]
cl_hbc_all=cl_data[(cl_data['一级组织名称']=='高端业务中心')]
cl_ic_all=cl_data[(cl_data['一级组织名称']=='财富管理中心')]

cl_hbc_yddk=cl_hbc_all.groupby('交易日期（统计）').sum()['确认市值']
cl_ic_yddk=cl_ic_all.groupby('交易日期（统计）').sum()['确认市值']
cl_hbc_yddk=transfer_index(cl_hbc_yddk)
cl_ic_yddk=transfer_index(cl_ic_yddk)

cl_hbc_xfcp=cal_df(cl_hbc_all)
cl_ic_xfcp=cal_df(cl_ic_all)

###FOF月度各区域  IC & HBC
cl_hbc_qy,cl_hbc_fgs,cl_hbc_cp,cl_hbc_cpfl=get_xf_group(cl_hbc)
cl_ic_qy,cl_ic_fgs,cl_ic_cp,cl_ic_cpfl=get_xf_group(cl_ic)

###HBC、IC的当月前10大销售
cl_hbc_xs=pd.DataFrame(cl_hbc.groupby(['四级组织名称']).sum()['确认市值'].sort_values(ascending=False).head(10))
cl_ic_xs=pd.DataFrame(cl_ic.groupby(['四级组织名称']).sum()['确认市值'].sort_values(ascending=False).head(10))

######导出到Excel
###销赎部分导出
writer1= pd.ExcelWriter(r"D:/Git/hbshare/hbshare/fe/xwq/data/存销赎数据统计/销赎数据result.xlsx")
xl_yddk.to_excel(writer1,sheet_name='销量月度打款')
sh_yddk.to_excel(writer1,sheet_name='赎回月度打款')
xl_hbc_yddk.to_excel(writer1,sheet_name='销量hbc月度打款')
xl_ic_yddk.to_excel(writer1,sheet_name='销量ic月度打款')
sh_hbc_yddk.to_excel(writer1,sheet_name='赎回hbc月度打款')
sh_ic_yddk.to_excel(writer1,sheet_name='赎回ic月度打款')

xlzb.to_excel(writer1,sheet_name='fof销量占整体二级的比例')
d.to_excel(writer1,sheet_name='产品净申购')
jsg_xfcp.to_excel(writer1,sheet_name='产品净申购',startcol=10)

xl_xfcp.to_excel(writer1,sheet_name='销量产品细分')
sh_xfcp.to_excel(writer1,sheet_name='赎回产品细分')

xl_cp.to_excel(writer1,sheet_name='销量-按产品标签分')
sh_cp.to_excel(writer1,sheet_name='赎回-按产品标签分')

xl_hbc_xfcp.to_excel(writer1,sheet_name='销量hbc产品细分')
xl_ic_xfcp.to_excel(writer1,sheet_name='销量ic产品细分')
sh_hbc_xfcp.to_excel(writer1,sheet_name='赎回hbc产品细分')
sh_ic_xfcp.to_excel(writer1,sheet_name='赎回ic产品细分')

xl_hbc_qy.to_excel(writer1,sheet_name='销量hbc')
xl_hbc_fgs.to_excel(writer1,sheet_name='销量hbc',startcol=10)
xl_hbc_cp.to_excel(writer1,sheet_name='销量hbc',startrow=20)
xl_hbc_cpfl.to_excel(writer1,sheet_name='销量hbc',startrow=20,startcol=10)

xl_ic_qy.to_excel(writer1,sheet_name='销量ic')
xl_ic_fgs.to_excel(writer1,sheet_name='销量ic',startcol=10)
xl_ic_cp.to_excel(writer1,sheet_name='销量ic',startrow=20)
xl_ic_cpfl.to_excel(writer1,sheet_name='销量ic',startrow=20,startcol=10)

sh_hbc_qy.to_excel(writer1,sheet_name='赎回hbc')
sh_hbc_fgs.to_excel(writer1,sheet_name='赎回hbc',startcol=10)
sh_hbc_cp.to_excel(writer1,sheet_name='赎回hbc',startrow=20)
sh_hbc_cpfl.to_excel(writer1,sheet_name='赎回hbc',startrow=20,startcol=10)

sh_ic_qy.to_excel(writer1,sheet_name='赎回ic')
sh_ic_fgs.to_excel(writer1,sheet_name='赎回ic',startcol=10)
sh_ic_cp.to_excel(writer1,sheet_name='赎回ic',startrow=20)
sh_ic_cpfl.to_excel(writer1,sheet_name='赎回ic',startrow=20,startcol=10)
writer1.save()
###存量部分导出
writer2= pd.ExcelWriter(r"D:/Git/hbshare/hbshare/fe/xwq/data/存销赎数据统计/存量数据result.xlsx")
cl_zcl.to_excel(writer2,sheet_name='总存量')
cl_hbc_yddk.to_excel(writer2,sheet_name='存量hbc月度打款')
cl_ic_yddk.to_excel(writer2,sheet_name='存量ic月度打款')

cl_xfcp.to_excel(writer2,sheet_name='存量产品细分')
cl_cp.to_excel(writer2,sheet_name='存量-按产品标签分')

cl_hbc_xfcp.to_excel(writer2,sheet_name='存量hbc产品细分')
cl_ic_xfcp.to_excel(writer2,sheet_name='存量ic产品细分')

cl_hbc_qy.to_excel(writer2,sheet_name='存量hbc')
cl_hbc_fgs.to_excel(writer2,sheet_name='存量hbc',startcol=10)
cl_hbc_cp.to_excel(writer2,sheet_name='存量hbc',startrow=200)
cl_hbc_cpfl.to_excel(writer2,sheet_name='存量hbc',startcol=10,startrow=200)

cl_ic_qy.to_excel(writer2,sheet_name='存量ic')
cl_ic_fgs.to_excel(writer2,sheet_name='存量ic',startcol=10)
cl_ic_cp.to_excel(writer2,sheet_name='存量ic',startrow=200)
cl_ic_cpfl.to_excel(writer2,sheet_name='存量ic',startcol=10,startrow=200)

cl_hbc_xs.to_excel(writer2,sheet_name='存量hbc销售(TOP10)')
cl_ic_xs.to_excel(writer2,sheet_name='存量ic销售(TOP10)')
writer2.save()

