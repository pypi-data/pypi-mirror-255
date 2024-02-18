#%% 库
import pandas as pd
import hbshare as hbs
hbs.set_token("qwertyuisdfghjkxcvbn1000")

#%% 取数据
def get_df(sql, db, page_size=2000):
    data = hbs.db_data_query(db, sql, page_size=page_size, timeout=120)
    pages = data['pages']
    data = pd.DataFrame(data['data'])
    if pages > 1:
        for page in range(2, pages + 1):
            temp_data = hbs.db_data_query(db, sql, page_size=page_size, page_num=page, timeout=120)
            data = pd.concat([data, pd.DataFrame(temp_data['data'])], axis=0)
    return data

def msci_without_881001(end_date):
    # msci
    sql_msci = "select zqdm 证券代码, jyrq 交易日期, hbdr 日回报\
                from st_market.t_st_zs_rhb\
                where zqdm = '892400' and jyrq>={0} and jyrq <={1} and hbdr != 99999".format('20120731',end_date)

    msci = get_df(sql_msci, db='alluser')
    msci = msci.pivot_table(values='日回报', index='交易日期', columns='证券代码')
    msci = msci.iloc[1:, :]

    # 881001
    sql_881001 = "select zqdm 证券代码, jyrq 交易日期, hbdr 日回报\
                from st_market.t_st_zs_rhb\
                where zqdm = '881001' and jyrq>={0} and jyrq <={1} and hbdr != 99999".format('20120731',end_date)

    wind_881001 = get_df(sql_881001, db='alluser')
    wind_881001 = wind_881001.pivot_table(values='日回报', index='交易日期', columns='证券代码')
    wind_881001 = wind_881001.iloc[1:, :]

    # 合并
    msci_final = pd.merge(msci, wind_881001, on='交易日期', how='left')

    """
    万得全A 比重: 0.05
    MSCI 剔除中国部分影响 比重: 0.95
    """
    wind_weight = 0.05
    msci_weight = 0.95

    msci_final['MSCI%'] = (msci_final['892400'] - (wind_weight * msci_final['881001'])) / msci_weight

    MSCI_without_881001 = msci_final[['MSCI%']]

    return MSCI_without_881001

def msci_rmb_without_881001(tjrq,path):
    # tjrq = 20231229
    # path = r'D:\cyp\Git\hbshare\hbshare\fe\QDII\QDII基金对(人民币-美元).xlsx'

    # QDII基金对
    qdii = pd.read_excel(path)

    # 基金规模
    from WindPy import w
    w.start()
    scale_wind = w.wss(
        "000041.OF,000043.OF,000044.OF,000055.OF,000071.OF,000075.OF,000076.OF,000369.OF,000370.OF,000593.OF,000614.OF,000834.OF,000906.OF,000927.OF,000988.OF,000989.OF,000990.OF,001092.OF,001093.OF,001481.OF,002379.OF,002380.OF,002423.OF,003718.OF,003719.OF,003720.OF,003721.OF,003722.OF,004243.OF,005675.OF,005676.OF,005801.OF,006075.OF,006105.OF,006127.OF,006263.OF,006282.OF,006327.OF,006328.OF,006329.OF,006330.OF,006381.OF,006479.OF,006480.OF,006555.OF,006679.OF,006680.OF,006792.OF,007280.OF,007455.OF,007721.OF,007722.OF,007844.OF,008401.OF,008706.OF,008707.OF,008708.OF,008763.OF,008764.OF,008971.OF,009225.OF,009226.OF,009562.OF,009563.OF,009975.OF,010583.OF,010789.OF,011706.OF,012348.OF,012349.OF,012570.OF,012571.OF,012751.OF,012752.OF,012753.OF,012804.OF,012805.OF,012860.OF,012861.OF,012864.OF,012865.OF,012866.OF,012867.OF,012868.OF,012869.OF,012870.OF,012871.OF,012979.OF,012980.OF,013127.OF,013128.OF,013171.OF,013172.OF,013308.OF,013309.OF,013328.OF,013329.OF,013402.OF,013403.OF,013404.OF,013425.OF,013499.OF,013945.OF,014002.OF,014424.OF,014425.OF,014438.OF,014439.OF,014978.OF,014982.OF,015016.OF,015204.OF,015205.OF,015282.OF,015283.OF,015299.OF,015300.OF,015310.OF,015311.OF,015518.OF,015545.OF,015546.OF,016055.OF,016056.OF,016057.OF,016058.OF,016280.OF,016281.OF,016452.OF,016453.OF,016470.OF,016471.OF,016532.OF,016533.OF,016534.OF,016535.OF,016667.OF,016668.OF,016742.OF,016823.OF,016970.OF,016971.OF,017028.OF,017030.OF,017091.OF,017092.OF,017093.OF,017144.OF,017145.OF,017204.OF,017429.OF,017430.OF,017431.OF,017436.OF,017437.OF,017641.OF,017642.OF,017643.OF,017653.OF,017654.OF,017730.OF,017731.OF,017894.OF,017895.OF,017951.OF,017952.OF,018036.OF,018043.OF,018044.OF,018064.OF,018065.OF,018066.OF,018078.OF,018079.OF,018200.OF,018201.OF,018336.OF,018337.OF,018432.OF,018433.OF,018475.OF,018476.OF,018523.OF,018524.OF,018577.OF,018578.OF,018738.OF,018851.OF,018852.OF,018853.OF,018854.OF,018966.OF,018967.OF,018968.OF,018969.OF,019102.OF,019103.OF,019118.OF,019172.OF,019173.OF,019174.OF,019175.OF,019305.OF,019441.OF,019442.OF,019449.OF,019450.OF,019454.OF,019455.OF,019524.OF,019525.OF,019549.OF,019550.OF,019670.OF,019671.OF,019710.OF,019711.OF,040018.OF,040021.OF,040046.OF,040047.OF,040048.OF,050015.OF,050025.OF,096001.OF,100055.OF,110031.OF,110032.OF,110033.OF,118001.OF,118002.OF,159501.OF,159509.OF,159513.OF,159518.OF,159519.OF,159605.OF,159607.OF,159612.OF,159615.OF,159632.OF,159655.OF,159659.OF,159660.OF,159687.OF,159688.OF,159696.OF,159699.OF,159740.OF,159741.OF,159742.OF,159747.OF,159750.OF,159822.OF,159823.OF,159850.OF,159866.OF,159892.OF,159920.OF,159941.OF,160125.OF,160140.OF,160141.OF,160213.OF,160416.OF,160644.OF,160717.OF,160924.OF,161124.OF,161125.OF,161126.OF,161127.OF,161128.OF,161130.OF,161229.OF,161831.OF,162411.OF,162415.OF,162719.OF,163208.OF,164212.OF,164705.OF,164824.OF,164906.OF,202801.OF,270023.OF,270042.OF,457001.OF,486001.OF,486002.OF,501021.OF,501225.OF,501226.OF,501312.OF,510900.OF,513000.OF,513010.OF,513030.OF,513050.OF,513060.OF,513080.OF,513100.OF,513110.OF,513120.OF,513130.OF,513140.OF,513180.OF,513220.OF,513260.OF,513280.OF,513290.OF,513300.OF,513310.OF,513330.OF,513360.OF,513380.OF,513390.OF,513500.OF,513520.OF,513530.OF,513580.OF,513650.OF,513800.OF,513810.OF,513850.OF,513870.OF,513880.OF,513890.OF,513950.OF,513970.OF,519981.OF,539001.OF,539003.OF,000934.OF,001668.OF,001691.OF,001984.OF,002230.OF,002891.OF,002892.OF,002893.OF,003243.OF,003244.OF,003245.OF,004877.OF,004878.OF,004879.OF,005534.OF,005698.OF,005699.OF,005700.OF,006308.OF,006309.OF,006310.OF,006370.OF,006373.OF,006374.OF,006445.OF,006446.OF,006447.OF,006448.OF,008253.OF,008254.OF,008284.OF,008285.OF,009108.OF,009193.OF,010591.OF,010644.OF,010645.OF,010671.OF,011420.OF,011421.OF,011422.OF,011423.OF,011583.OF,011584.OF,012060.OF,012061.OF,012062.OF,012208.OF,012209.OF,012379.OF,012380.OF,012535.OF,012536.OF,012584.OF,012585.OF,012920.OF,012921.OF,012922.OF,012923.OF,012924.OF,012925.OF,013363.OF,013364.OF,014127.OF,015202.OF,015203.OF,015884.OF,015885.OF,016199.OF,016200.OF,016201.OF,016202.OF,016664.OF,016665.OF,016701.OF,016702.OF,016988.OF,017873.OF,017970.OF,017971.OF,017972.OF,018147.OF,018229.OF,018230.OF,018231.OF,018232.OF,019035.OF,019036.OF,019155.OF,019156.OF,019157.OF,019158.OF,019265.OF,019266.OF,019415.OF,019416.OF,019447.OF,019448.OF,019573.OF,019578.OF,019641.OF,070012.OF,080006.OF,100061.OF,110011.OF,161620.OF,163813.OF,241001.OF,262001.OF,377016.OF,378006.OF,378546.OF,460010.OF,470888.OF,519601.OF,519696.OF,539002.OF,862001.OF,862011.OF,862012.OF",
        "fund_setupdate,netasset_total_cc", "unit=1;tradeDate={};currencyType=Cur=CNY".format(tjrq), usedf=True) \
        [1].reset_index(drop=False).rename(
        columns={'NETASSET_TOTAL_CC': '基金规模', 'index': '证券代码', 'FUND_SETUPDATE': '基金成立日'})
    w.stop()
    scale_wind['基金成立日'] = pd.to_datetime(scale_wind['基金成立日']).dt.strftime('%Y%m%d')

    qdii = pd.merge(qdii, scale_wind, on=['证券代码'], how='left')
    qdii['基金规模'] = pd.to_numeric(qdii['基金规模'], errors='coerce')

    # 基金代码修改
    qdii['证券代码'] = qdii['证券代码'].str[0:6]

    # 基金日回报
    sql2 = "select jjdm,jzrq,hbdr from st_fund.t_st_gm_rhb \
            where jjdm in {0} and jzrq<={1} and hbdr != 99999".format(tuple(qdii['证券代码']), str(tjrq))

    jjret = get_df(sql2, db='funduser')
    jjret = jjret.pivot_table('hbdr', 'jzrq', 'jjdm')
    jjret.index = jjret.index.astype(str)

    days = jjret.index.to_list()

    jjret = jjret.T
    jjret = jjret.reset_index()
    jjret = jjret.rename(columns={"jjdm":"证券代码"})

    jjret = pd.merge(jjret, qdii, on='证券代码', how='left')
    jjret = jjret.sort_values(by=['证券简称', '基金成立日'], ascending=True).reset_index(drop=True)

    # 基金规模占比
    jjret['基金规模占比'] = (jjret[~jjret['证券简称'].str.contains('美元')]['基金规模'] /
                             jjret[~jjret['证券简称'].str.contains('美元')]['基金规模'].sum())
    jjret['基金规模占比'] = round(jjret['基金规模占比'], 5)

    #人民币 - 美元 每日变动
    change_days = pd.DataFrame(index=days,columns=['change'])
    for day in days:
        if len(jjret[~jjret['证券简称'].str.contains('美元')][day]) == len(jjret[jjret['证券简称'].str.contains('美元')][day]):
            rmb_1d = pd.DataFrame(jjret[~jjret['证券简称'].str.contains('美元')][['证券简称', day, '基金规模占比']]).reset_index(drop=True)
            rmb_1d.rename(columns={day: day+"_人民币", "证券简称": "证券简称_人民币"}, inplace=True)
            dollar_1d = pd.DataFrame(jjret[jjret['证券简称'].str.contains('美元')][['证券简称', day]]).reset_index(drop=True)
            dollar_1d.rename(columns={day: day+"_美元", "证券简称": "证券简称_美元"}, inplace=True)

        diff_1d = pd.concat([rmb_1d, dollar_1d], axis=1)
        diff_1d = diff_1d[['证券简称_人民币', '证券简称_美元', day+"_人民币", day+"_美元", '基金规模占比']]

        # 计算 change_1day
        diff_1d[day+'_变动'] = ((1 + diff_1d[day+"_人民币"] / 100) / (1 + diff_1d[day+"_美元"] / 100)) - 1

        diff_1d[day+'变动_加权'] = diff_1d['基金规模占比'] * diff_1d[day+'_变动']

        change_1day = round(diff_1d[day+'变动_加权'].sum() * 100, 4)
        change_days.loc[day,'change'] = change_1day

    # msci 美元计价
    sql_msci = "select zqdm 证券代码, jyrq 交易日期, hbdr 日回报\
                from st_market.t_st_zs_rhb\
                where zqdm = '892400' and jyrq>={0} and jyrq <={1} and hbdr != 99999".format('20120731', tjrq)

    msci_dollar = get_df(sql_msci, db='alluser')
    msci_dollar = msci_dollar.pivot_table(values='日回报', index='交易日期', columns='证券代码')
    msci_dollar = msci_dollar.iloc[1:, :]
    msci_dollar.index = msci_dollar.index.astype(str)

    # msci 人民币计价
    msci_ = pd.merge(msci_dollar,change_days,how='left',left_index=True,right_index=True)

    msci_['msci_rmb'] = (((1+msci_['892400']/100) * (1+msci_['change']/100)) - 1)*100

    msci_rmb = msci_[['msci_rmb']]

    # msci 人民币计价 剔除中国部分影响

    # 881001
    sql_881001 = "select zqdm 证券代码, jyrq 交易日期, hbdr 日回报\
                    from st_market.t_st_zs_rhb\
                    where zqdm = '881001' and jyrq>={0} and jyrq <={1} and hbdr != 99999".format('20120731', tjrq)

    wind_881001 = get_df(sql_881001, db='alluser')
    wind_881001 = wind_881001.pivot_table(values='日回报', index='交易日期', columns='证券代码')
    wind_881001 = wind_881001.iloc[1:, :]

    # 合并
    msci_rmb.index = msci_rmb.index.astype(int)
    msci_rmb = msci_rmb.astype(float)
    msci_final = pd.merge(msci_rmb, wind_881001, on='交易日期', how='left')

    """
    万得全A 比重: 0.05
    MSCI 剔除中国部分影响 比重: 0.95
    """
    wind_weight = 0.05
    msci_weight = 0.95

    msci_final['MSCI%'] = (msci_final['msci_rmb'] - (wind_weight * msci_final['881001'])) / msci_weight

    MSCI_rmb_without_881001 = msci_final[['MSCI%']]

    return MSCI_rmb_without_881001

def msci_rmb_fof(tjrq,path):
    # tjrq = 20240126
    # path = r'D:\cyp\业绩统计(fof&池)_run\FOF\数据源\QDII基金对(人民币-美元).xlsx'

    # MSCI日回报 人民币计价 (单位:%)
    msci_rmb_rhb = msci_rmb_without_881001(tjrq,path)
    msci_rmb_rhb.rename(columns={"MSCI%":"msci_rmb_rhb"},inplace=True)
    msci_rmb_rhb = msci_rmb_rhb.loc['20130104':,:]
    msci_rmb_rhb = msci_rmb_rhb.reset_index()
    msci_rmb_rhb['交易日期'] =  msci_rmb_rhb['交易日期'].astype(str)

    # 万得格式的日期
    from datetime import datetime
    wind_date = datetime.strptime(str(tjrq), '%Y%m%d').strftime('%Y-%m-%d')
    # 人民币存款利率 (单位:%)
    from WindPy import w
    w.start()
    save_rate = w.edb("M0043801", "2013-01-01", wind_date, "Fill=Previous", usedf=True) \
        [1].reset_index(drop=False).rename(columns={"index": "交易日期", "CLOSE": "存款利率"})
    w.stop()
    save_rate['交易日期'] = pd.to_datetime(save_rate['交易日期']).dt.strftime('%Y%m%d')
    save_rate['存款利率'] = save_rate['存款利率'] / 250
    save_rate_unique = save_rate['存款利率'].unique()[0]

    msci_rmb_save_rate = msci_rmb_rhb.copy()
    msci_rmb_save_rate['save_rate'] = save_rate_unique
    msci_rmb_save_rate['rmb_msci'] = 0.9*msci_rmb_save_rate['msci_rmb_rhb']+0.1*msci_rmb_save_rate['save_rate']

    #人民币MSCI = 90%*以人民币计价并剔除了万得全A影响的MSCI指数+ 10%*人民币存款利率
    rmb_msci = msci_rmb_save_rate[['交易日期','rmb_msci']]
    rmb_msci.set_index('交易日期',inplace=True)

    # 人民币MSCI-净值序列
    rmb_msci_nav = (rmb_msci / 100 + 1).cumprod()

    return rmb_msci_nav

#%% End