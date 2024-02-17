from hbshare.fe.nav_attr import nav_attribution as na
import numpy as np
import pandas as pd
from hbshare.fe.XZ import functionality
from hbshare.fe.XZ import db_engine as dben
from hbshare.fe.common.util.data_loader import NavAttributionLoader
from hbshare.fe.CYP import cyp_functions
import  warnings
from sklearn.impute import KNNImputer
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator
import statsmodels.api as sm
import  datetime

warnings.filterwarnings('ignore')
localdb = dben.PrvFunDB().engine
util = functionality.Untils()
hbdb = dben.HBDB()
get_df = cyp_functions.get_df


mutual_core_pool=['006624','377240','007449','001476','450004','000739','001583','010381','002910','519019','004868','001975',
                  '000979','161222','007346','001955','000612','011251','001717','001667','009049','005968','005241','002340',
                  '519133','450009','008328','003165','001810']

def TM_regression(end_date, jjdm_list,latest_HB1001_spjg):
    ###########################################################################
    # fri_df : 所有周五交易日的日期集合
    start_date = '20000101'

    sql_script = "SELECT jyrq JYRQ, sfjj SFJJ, sfzm SFZM FROM st_main.t_st_gg_jyrl\
                  WHERE jyrq >= {} and jyrq <= {}".format(start_date, end_date)
    dates_df = get_df(sql_script, db='alluser')
    dates_df = dates_df.sort_values(by='JYRQ').reset_index(drop=True)
    fri_df = dates_df[(dates_df['SFZM'] == '1') & (dates_df['SFJJ'] == '0')].reset_index(drop=True)
    fri_df = fri_df[['JYRQ']].rename(columns={"JYRQ": "date"})

    ###########################################################################
    # last_week, last_quarter

    # end_date 上一周日期
    last_week = fri_df.loc[fri_df[fri_df['date'] == end_date].index[0] - 1, 'date']

    # 季度回归 (往前推14周)
    last_quarter = fri_df.loc[fri_df[fri_df['date'] == end_date].index[0] - 14, 'date']

    # 季度回归每周日期
    weekdate = fri_df.loc[fri_df[fri_df['date'] == last_quarter].index[0]:, 'date'].to_frame().reset_index(drop=True)
    weekdate_list = weekdate['date'].to_list()

    ###########################################################################
    #  info_t1 : 基金净值 + 万得全A收盘价

    # 基金净值
    sql_jj = "select jjdm,jzrq 日期,fqdwjz from st_hedge.t_st_rhb\
       where jjdm in {0} and jzrq>={1} and jzrq <={2}".format(tuple(jjdm_list), last_quarter, end_date)
    jjjz = get_df(sql_jj, db='highuser')
    jjjz = jjjz.pivot_table(values='fqdwjz', index='日期', columns='jjdm')
    jjjz = jjjz.loc[weekdate_list, :]

    ## 如果基金净值序列有大于等于5个nan值, 则直接剔除该基金
    for cln in jjjz.columns:
        num_nan = jjjz[cln].isna().sum()
        if num_nan >= 5:
            jjjz = jjjz.drop(cln, axis=1)

    ## 如果基金净值在期初或期末出现nan值, 则直接剔除该基金
    for cln in jjjz.columns:
        e_jz = jjjz[cln].to_frame()
        if pd.isna(e_jz.iloc[0, 0]) or pd.isna(e_jz.iloc[-1, 0]):
            jjjz = jjjz.drop(cln, axis=1)

    ## 填充 期中nan值
    ### Test knn VS interpolate
    #### Test 使用数据集
    nan_rate = jjjz.isnull().sum().sum() / jjjz.size
    complete_jz = jjjz.dropna(axis=1, how='any')
    incomplete_jz = complete_jz.mask(np.random.RandomState(1).random(complete_jz.shape) <= nan_rate + 0.01, np.nan)
    position = incomplete_jz.isnull().stack()[lambda x: x].index.tolist()

    #### knn
    class KNNImputerWithScore(KNNImputer, BaseEstimator):
        def score(self, X, y=None):
            return -1.0 * self.transform(X).mean()

    param_grid = {'n_neighbors': list(range(3, 20, 2))}
    imputer = KNNImputerWithScore(weights='distance')
    grid_search = GridSearchCV(imputer, param_grid, cv=5)
    grid_search.fit(incomplete_jz)
    best_n_neighbors = grid_search.best_params_['n_neighbors']
    new_imputer = KNNImputer(n_neighbors=best_n_neighbors, weights='distance')
    incomplete_jz_fill_knn = pd.DataFrame(new_imputer.fit_transform(incomplete_jz),
                                          index=incomplete_jz.index,
                                          columns=incomplete_jz.columns)

    #### interpolate
    incomplete_jz_fill_interpolate = incomplete_jz.interpolate(method='linear',
                                                               limit_direction='both', axis=0)

    #### 与实际值百分比差异计算
    real_list = []
    unreal_list_knn = []
    unreal_list_interpolate = []

    for i in range(len(position)):
        index = position[i][0]
        cln = position[i][1]
        real_list.append(complete_jz.loc[index, cln])
        unreal_list_knn.append(incomplete_jz_fill_knn.loc[index, cln])
        unreal_list_interpolate.append(incomplete_jz_fill_interpolate.loc[index, cln])

    real = pd.DataFrame(real_list, columns=['real'])
    unreal_knn = pd.DataFrame(unreal_list_knn, columns=['unreal_knn'])
    unreal_interpolate = pd.DataFrame(unreal_list_interpolate, columns=['unreal_interpolate'])
    compare = pd.merge(real, unreal_knn, how='left', left_index=True, right_index=True)
    compare = pd.merge(compare, unreal_interpolate, how='left', left_index=True, right_index=True)
    compare['diff%_knn'] = abs((compare['real'] / compare['unreal_knn'] - 1) * 100)
    compare['diff%_interpolate'] = abs((compare['real'] / compare['unreal_interpolate'] - 1) * 100)

    # compare['diff%_knn'].mean()
    # compare['diff%_interpolate'].mean()

    if jjjz.isnull().sum().sum() != 0:
        if compare['diff%_knn'].mean() < compare['diff%_interpolate'].mean():
            jjjz = pd.DataFrame(new_imputer.fit_transform(jjjz), index=jjjz.index, columns=jjjz.columns)
            print("\n")
            print("使用 K最近邻 填充个基期中缺失净值")
        else:
            jjjz = jjjz.interpolate(method='linear', limit_direction='both', axis=0)
            print("\n")
            print("使用 线性插值 填充个基期中缺失净值")

    if jjjz.isnull().sum().sum() == 0:
        # 万得全A收盘价
        sql_wind = "select zqdm,jyrq 日期,spjg from st_market.t_st_zs_hq\
            where zqdm = '881001' and jyrq>={0} and jyrq<={1}".format(last_quarter, end_date)
        spj_881001 = get_df(sql_wind, db='alluser')
        spj_881001 = spj_881001.pivot_table(values='spjg', index='日期', columns='zqdm')
        spj_881001.index = spj_881001.index.astype(str)
        spj_881001 = spj_881001.loc[weekdate_list, :]

        # 合并表
        info_t1 = pd.merge(jjjz, spj_881001, on='日期', how='left')

    ###########################################################################
    #  Return : Rp, Rm, Rf

    ret_t1 = info_t1.pct_change().dropna(axis=0, how='all')
    ret_t1 = ret_t1.rename(columns={"881001": "Rm"})

    # 无风险利率=> 年化收益率=2% => 周收益率=(1+2%)^(1/52) - 1
    ret_t1['Rf'] = (1 + 0.02) ** (1 / 52) - 1

    table1 = pd.DataFrame(index=jjjz.columns,
                          columns=['alpha', 'beta1', 'beta2'])

    table2 = pd.DataFrame(index=jjjz.columns,
                          columns=['Rf', 'alpha', 'beta1*(Rm-Rf)',
                                   'beta2*(sqr_Rm-Rf)', 'error'])

    table2_bis = pd.DataFrame(index=jjjz.columns,
                              columns=['Rf', 'alpha', 'beta1*(Rm-Rf)',
                                       'beta2*(sqr_Rm-Rf)', 'error'])

    for portf in ret_t1.drop(['Rm', 'Rf'], axis=1).columns:
        each_ret = ret_t1[[portf, 'Rm', 'Rf']].copy()

        each_ret['Rp-Rf'] = each_ret[portf] - each_ret['Rf']
        each_ret['Rm-Rf'] = each_ret['Rm'] - each_ret['Rf']
        each_ret['sqr_Rm-Rf'] = each_ret['Rm-Rf'] ** 2

        # 输入-输出变量准备
        y = each_ret[['Rp-Rf']]  # 模型输出变量矩阵
        X_TM = sm.add_constant(each_ret[['Rm-Rf', 'sqr_Rm-Rf']])  # T-M模型输入变量矩阵

        # 模型训练
        TM = sm.OLS(y, X_TM).fit()  # T-M拟合模型

        # table1 : 个基暴露
        if portf in jjjz.columns:
            table1.loc[portf, 'alpha'] = 1
            table1.loc[portf, 'beta1'] = TM.params.to_frame().loc['Rm-Rf', 0]
            table1.loc[portf, 'beta2'] = TM.params.to_frame().loc['sqr_Rm-Rf', 0]

        # 贡献
        alpha = TM.params.to_frame().loc['const', 0]
        beta1 = TM.params.to_frame().loc['Rm-Rf', 0]
        beta2 = TM.params.to_frame().loc['sqr_Rm-Rf', 0]

        each_gx = each_ret[[portf]].copy()
        each_gx['Return'] = each_gx[portf]
        each_gx['Rf'] = each_ret['Rf']
        each_gx['alpha'] = alpha
        each_gx['beta1*(Rm-Rf)'] = beta1 * each_ret['Rm-Rf']
        each_gx['beta2*(sqr_Rm-Rf)'] = beta2 * each_ret['sqr_Rm-Rf']
        each_gx[portf] = (each_gx[portf] + 1).cumprod()
        each_gx_week = each_gx.copy()

        end_date_jz = each_gx.iloc[-1, 0]
        each_gx[portf] = each_gx[portf].shift(axis=0, periods=1)
        each_gx.iloc[0, 0] = 1

        each_gx['Rf'] = each_gx['Rf'] * each_gx[portf]
        each_gx['alpha'] = each_gx['alpha'] * each_gx[portf]
        each_gx['beta1*(Rm-Rf)'] = each_gx['beta1*(Rm-Rf)'] * each_gx[portf]
        each_gx['beta2*(sqr_Rm-Rf)'] = each_gx['beta2*(sqr_Rm-Rf)'] * each_gx[portf]

        each_gx['total'] = each_gx['Rf'] + each_gx['alpha'] \
                           + each_gx['beta1*(Rm-Rf)'] + each_gx['beta2*(sqr_Rm-Rf)']

        # table2 : 个基(季度)贡献
        if portf in jjjz.columns:
            quarter_ret = each_gx['total'].sum()
            end_date_ret = end_date_jz - 1

            table2.loc[portf, 'Rf'] = each_gx['Rf'].sum()
            table2.loc[portf, 'alpha'] = each_gx['alpha'].sum()
            table2.loc[portf, 'beta1*(Rm-Rf)'] = each_gx['beta1*(Rm-Rf)'].sum()
            table2.loc[portf, 'beta2*(sqr_Rm-Rf)'] = each_gx['beta2*(sqr_Rm-Rf)'].sum()
            table2.loc[portf, 'error'] = end_date_ret - quarter_ret

        # table2_bis : 个基(周度)贡献
        if portf in jjjz.columns:
            each_gx_week = each_gx_week.loc[last_week:, :]

            week_ret = each_gx_week.loc[end_date, ['Rf', 'alpha', 'beta1*(Rm-Rf)', 'beta2*(sqr_Rm-Rf)']].sum()
            real_week_ret = each_gx_week.loc[end_date, 'Return']

            table2_bis.loc[portf, 'Rf'] = each_gx_week.loc[end_date, 'Rf']
            table2_bis.loc[portf, 'alpha'] = each_gx_week.loc[end_date, 'alpha']
            table2_bis.loc[portf, 'beta1*(Rm-Rf)'] = each_gx_week.loc[end_date, 'beta1*(Rm-Rf)']
            table2_bis.loc[portf, 'beta2*(sqr_Rm-Rf)'] = each_gx.loc[end_date, 'beta2*(sqr_Rm-Rf)']
            table2_bis.loc[portf, 'error'] = real_week_ret - week_ret

    """
    table1: 个基暴露
    table2: 个基(季度)贡献

    table2_bis: 个基(周度)贡献

    table3: 池暴露 
    table4: 池(季度)贡献
    table5: 池(周度)贡献
    table6: 基准暴露
    table7: 基准(季度)贡献
    table8: 基准(周度)贡献
    """

    # table 数值化
    table1 = table1.astype(float)
    table2 = table2.astype(float)
    table2_bis = table2_bis.astype(float)

    # table3 : 池暴露
    table3 = table1.mean().to_frame().T.rename(index={0: "池暴露"})

    # table4 : 池(季度)贡献
    table4 = table2.mean().to_frame().T.rename(index={0: "池(季度)贡献"})

    # table5 : 池(周度)贡献
    table5 = table2_bis.mean().to_frame().T.rename(index={0: "池(周度)贡献"})

    ###########################################################################
    # 基准 HB1001 好买主观多头指数 t_st_sm_zhmzs
    sql_hb1001 = "select zsdm, jyrq 日期, spjg from st_hedge.t_st_sm_zhmzs\
        where zsdm = 'HB1001' and jyrq>={0} and jyrq<={1}".format(last_quarter, end_date)

    spj_hb1001 = get_df(sql_hb1001, db='highuser')
    spj_hb1001.loc[len(spj_hb1001)]=[end_date,'HB1001',latest_HB1001_spjg]
    spj_hb1001 = spj_hb1001.pivot_table(values='spjg', index='日期', columns='zsdm')
    spj_hb1001 = spj_hb1001.loc[weekdate_list, :]

    # 合并表
    info_t2 = pd.merge(spj_hb1001, spj_881001, on='日期', how='left')

    ret_bmk = info_t2.pct_change().dropna(axis=0, how='all')
    ret_bmk = ret_bmk.rename(columns={"881001": "Rm"})

    # 无风险利率=> 年化收益率=2% => 周收益率=(1+2%)^(1/52) - 1
    ret_bmk['Rf'] = (1 + 0.02) ** (1 / 52) - 1

    ret_bmk['Rp-Rf'] = ret_bmk['HB1001'] - ret_bmk['Rf']
    ret_bmk['Rm-Rf'] = ret_bmk['Rm'] - ret_bmk['Rf']
    ret_bmk['sqr_Rm-Rf'] = ret_bmk['Rm-Rf'] ** 2

    # 输入-输出变量准备
    y_bmk = ret_bmk[['Rp-Rf']]  # 模型输出变量矩阵
    X_TM_bmk = sm.add_constant(ret_bmk[['Rm-Rf', 'sqr_Rm-Rf']])  # T-M模型输入变量矩阵

    # 模型训练
    TM_bmk = sm.OLS(y_bmk, X_TM_bmk).fit()  # T-M拟合模型

    # table6 : 基准暴露
    table6 = pd.DataFrame(index=['基准暴露'],
                          columns=['alpha', 'beta1', 'beta2'])

    table6.loc['基准暴露', 'alpha'] = 1
    table6.loc['基准暴露', 'beta1'] = TM_bmk.params.to_frame().loc['Rm-Rf', 0]
    table6.loc['基准暴露', 'beta2'] = TM_bmk.params.to_frame().loc['sqr_Rm-Rf', 0]
    table6 = table6.astype(float)

    # 基准贡献
    alpha_bmk = TM_bmk.params.to_frame().loc['const', 0]
    beta1_bmk = TM_bmk.params.to_frame().loc['Rm-Rf', 0]
    beta2_bmk = TM_bmk.params.to_frame().loc['sqr_Rm-Rf', 0]

    bmk_gx = ret_bmk[['HB1001']].copy()
    bmk_gx['Return'] = bmk_gx['HB1001']
    bmk_gx['Rf'] = ret_bmk['Rf']
    bmk_gx['alpha'] = alpha_bmk
    bmk_gx['beta1*(Rm-Rf)'] = beta1_bmk * ret_bmk['Rm-Rf']
    bmk_gx['beta2*(sqr_Rm-Rf)'] = beta2_bmk * ret_bmk['sqr_Rm-Rf']
    bmk_gx['HB1001'] = (bmk_gx['HB1001'] + 1).cumprod()
    bmk_gx_week = bmk_gx.copy()

    end_date_bmk_jz = bmk_gx.iloc[-1, 0]
    bmk_gx['HB1001'] = bmk_gx['HB1001'].shift(axis=0, periods=1)
    bmk_gx.iloc[0, 0] = 1

    bmk_gx['Rf'] = bmk_gx['Rf'] * bmk_gx['HB1001']
    bmk_gx['alpha'] = bmk_gx['alpha'] * bmk_gx['HB1001']
    bmk_gx['beta1*(Rm-Rf)'] = bmk_gx['beta1*(Rm-Rf)'] * bmk_gx['HB1001']
    bmk_gx['beta2*(sqr_Rm-Rf)'] = bmk_gx['beta2*(sqr_Rm-Rf)'] * bmk_gx['HB1001']

    bmk_gx['total'] = bmk_gx['Rf'] + bmk_gx['alpha'] \
                      + bmk_gx['beta1*(Rm-Rf)'] + bmk_gx['beta2*(sqr_Rm-Rf)']

    # 基准(季度)贡献
    # table7 : 基准(季度)贡献
    table7 = pd.DataFrame(index=['基准(季度)贡献'],
                          columns=['Rf', 'alpha', 'beta1*(Rm-Rf)',
                                   'beta2*(sqr_Rm-Rf)', 'error'])

    quarter_bmk_ret = bmk_gx['total'].sum()
    end_date_bmk_ret = end_date_bmk_jz - 1

    table7.loc['基准(季度)贡献', 'Rf'] = bmk_gx['Rf'].sum()
    table7.loc['基准(季度)贡献', 'alpha'] = bmk_gx['alpha'].sum()
    table7.loc['基准(季度)贡献', 'beta1*(Rm-Rf)'] = bmk_gx['beta1*(Rm-Rf)'].sum()
    table7.loc['基准(季度)贡献', 'beta2*(sqr_Rm-Rf)'] = bmk_gx['beta2*(sqr_Rm-Rf)'].sum()
    table7.loc['基准(季度)贡献', 'error'] = end_date_bmk_ret - quarter_bmk_ret
    table7 = table7.astype(float)

    # 基准(周度)贡献
    # table8: 基准(周度)贡献
    table8 = pd.DataFrame(index=['基准(周度)贡献'],
                          columns=['Rf', 'alpha', 'beta1*(Rm-Rf)',
                                   'beta2*(sqr_Rm-Rf)', 'error'])

    bmk_gx_week = bmk_gx_week.loc[last_week:, :]

    bmk_week_ret = bmk_gx_week.loc[end_date, ['Rf', 'alpha', 'beta1*(Rm-Rf)', 'beta2*(sqr_Rm-Rf)']].sum()
    real_bmk_week_ret = bmk_gx_week.loc[end_date, 'Return']

    table8.loc['基准(周度)贡献', 'Rf'] = bmk_gx_week.loc[end_date, 'Rf']
    table8.loc['基准(周度)贡献', 'alpha'] = bmk_gx_week.loc[end_date, 'alpha']
    table8.loc['基准(周度)贡献', 'beta1*(Rm-Rf)'] = bmk_gx_week.loc[end_date, 'beta1*(Rm-Rf)']
    table8.loc['基准(周度)贡献', 'beta2*(sqr_Rm-Rf)'] = bmk_gx_week.loc[end_date, 'beta2*(sqr_Rm-Rf)']
    table8.loc['基准(周度)贡献', 'error'] = real_bmk_week_ret - bmk_week_ret
    table8 = table8.astype(float)

    """
    合并
    table3: 池暴露 
    table4: 池(季度)贡献
    table5: 池(周度)贡献
    table6: 基准暴露
    table7: 基准(季度)贡献
    table8: 基准(周度)贡献
    table9: 池/基准 暴露+贡献
    """

    # 合并 table3,4,5,6,7,8
    table3 = table3.T
    table4 = table4.T
    table5 = table5.T
    table6 = table6.T
    table7 = table7.T
    table8 = table8.T

    # 暴露:bl
    bl = pd.merge(table3, table6, how='left', left_index=True, right_index=True)

    # 池贡献:pool_gx
    pool_gx = pd.merge(table4, table5, how='left', left_index=True, right_index=True)

    # 基准贡献:bk_gx
    bk_gx = pd.merge(table7, table8, how='left', left_index=True, right_index=True)

    # 贡献:gx
    gx = pd.merge(pool_gx, bk_gx, how='left', left_index=True, right_index=True)
    gx = gx[['池(季度)贡献', '基准(季度)贡献', '池(周度)贡献', '基准(周度)贡献']]
    gx.rename(index={"beta1*(Rm-Rf)": "beta1",
                     "beta2*(sqr_Rm-Rf)": "beta2"}, inplace=True)

    # table9 : 池/基准 暴露+贡献
    table9 = pd.merge(bl, gx, how='outer', left_index=True, right_index=True)
    table9 = table9.reindex(['alpha', 'beta1', 'beta2', 'Rf', 'error'])
    table9.loc['Rf', ['池暴露', '基准暴露']] = 1
    table9.loc['error', ['池暴露', '基准暴露']] = 1
    table9.rename(index={"beta1": "市场",
                         "beta2": "平均择时能力",
                         "Rf": "无风险收益",
                         "error": "误差"}, inplace=True)

    # table1 改中文名
    table1.rename(columns={"alpha": "alpha暴露", "beta1": "市场暴露", "beta2": "择时暴露"}, inplace=True)

    # table2 改中文名
    table2.rename(columns={"Rf": "无风险收益贡献", "alpha": "alpha贡献",
                           "beta1*(Rm-Rf)": "市场贡献", "beta2*(sqr_Rm-Rf)": "择时贡献",
                           "error": "误差贡献"}, inplace=True)

    """
    output_table 
    table1: 个基暴露 => gj_bl
    table2: 个基(季度)贡献 => gj_gx

    table9: 池/基准 暴露+贡献 => pool_bmk_bl_gx
    """

    gj_bl = table1.copy()
    gj_bl = gj_bl.reset_index().rename(columns={"jjdm": "基金代码"})

    gj_gx = table2.copy()
    gj_gx = gj_gx.reset_index().rename(columns={"jjdm": "基金代码"})

    pool_bmk_bl_gx = table9.copy()
    pool_bmk_bl_gx = pool_bmk_bl_gx.reset_index().rename(columns={"index": "信息汇总"})

    return gj_bl.set_index('基金代码'), gj_gx.set_index('基金代码'), pool_bmk_bl_gx.set_index('信息汇总')

# 使用示例
# gj_bl, gj_gx, pool_bmk_bl_gx = TM_regression(end_date,jjdm_list)

def fund_pool_brinson(last_month, last_week, end_date, jjdm_list):
    ###########################################################################
    # 中证全债收益 - H11001

    # 取收盘价然后再算收益
    sql_zzqz_spj = "select zqdm 证券代码, jyrq 交易日期, spjg 收盘价 from st_market.t_st_zs_hq\
                    where zqdm = 'H11001' and jyrq <={}".format(end_date)
    zzqz_spj = get_df(sql_zzqz_spj, db='alluser')

    # 周收益
    zzqz_spj_w = zzqz_spj.set_index('交易日期').loc[[int(last_week), int(end_date)], :]
    ret_bond_w = zzqz_spj_w.loc[int(end_date), '收盘价'] / zzqz_spj_w.loc[int(last_week), '收盘价'] - 1

    # 月收益
    zzqz_spj_m = zzqz_spj.set_index('交易日期').loc[[int(last_month), int(end_date)], :]
    ret_bond_m = zzqz_spj_m.loc[int(end_date), '收盘价'] / zzqz_spj_m.loc[int(last_month), '收盘价'] - 1

    ###########################################################################
    # 现金收益

    # 周收益
    ret_cash_w = 0

    # 月收益
    ret_cash_m = 0

    ###########################################################################
    # 公募非债池-组合平均收益

    """
    w: week
    m: month
    """

    # 取净值然后再算收益

    # 周收益
    sql_portf_nav_w = "select jjdm 基金代码, jzrq 净值日期, fqdwjz 基金净值 from st_fund.t_st_gm_rhb\
                       where jjdm in {0} and jzrq>={1} and jzrq<={2}".format(tuple(jjdm_list), last_week, end_date)
    portf_nav_w = get_df(sql_portf_nav_w, db='funduser')
    portf_nav_w = portf_nav_w.pivot_table('基金净值', '净值日期', '基金代码')
    portf_nav_w = portf_nav_w.loc[[int(last_week), int(end_date)], :]
    portf_return_w = pd.DataFrame(index=portf_nav_w.columns, columns=['周收益'])

    for i in range(len(portf_return_w)):
        e_jjdm = portf_return_w.index[i]
        portf_return_w.iloc[i, 0] = (
                    portf_nav_w.loc[int(end_date), e_jjdm] / portf_nav_w.loc[int(last_week), e_jjdm] - 1)
    portf_return_w['周收益'] = portf_return_w['周收益'].astype(float)

    ret_portf_w = portf_return_w['周收益'].mean()

    # 月收益
    sql_portf_nav_m = "select jjdm 基金代码, jzrq 净值日期, jjjz 基金净值 from st_fund.t_st_gm_jjjz\
                       where jjdm in {0} and jzrq>={1} and jzrq<={2}".format(tuple(jjdm_list), last_month, end_date)
    portf_nav_m = get_df(sql_portf_nav_m, db='funduser')
    portf_nav_m = portf_nav_m.pivot_table('基金净值', '净值日期', '基金代码')
    portf_nav_m = portf_nav_m.loc[[int(last_month), int(end_date)], :]
    portf_return_m = pd.DataFrame(index=portf_nav_m.columns, columns=['月收益'])

    for j in range(len(portf_return_m)):
        e_jjdm = portf_return_m.index[j]
        portf_return_m.iloc[j, 0] = (
                    portf_nav_m.loc[int(end_date), e_jjdm] / portf_nav_m.loc[int(last_month), e_jjdm] - 1)
    portf_return_m['月收益'] = portf_return_m['月收益'].astype(float)

    ret_portf_m = portf_return_m['月收益'].mean()

    ###########################################################################
    # 公募非债池-组合权重 [股票+货币+债券]

    sql_portf_weight = "select jjdm 基金代码, jsrq 结束日期, gptzzjb 股票, zqzszzjb 债券, hbzjzjb 货币 from st_fund.t_st_gm_zcpz\
                        where jjdm in {0} and jsrq <= {1}".format(tuple(jjdm_list), int(end_date))
    portf_weight = get_df(sql_portf_weight, db='funduser')
    portf_weight = portf_weight.drop_duplicates('基金代码', keep='last')
    portf_weight = portf_weight.reset_index(drop=True)
    portf_weight = portf_weight.fillna(0)
    portf_weight[['债券', '股票', '货币']] = portf_weight[['债券', '股票', '货币']] / 100

    weight_portf_bond = portf_weight['债券'].mean()
    weight_portf_equity = portf_weight['股票'].mean()
    weight_portf_cash = portf_weight['货币'].mean()

    ###########################################################################
    # 公募非债池-股票收益
    ret_equity_portf_w = (
                                     ret_portf_w - weight_portf_bond * ret_bond_w - weight_portf_cash * ret_cash_w) / weight_portf_equity

    ret_equity_portf_m = (
                                     ret_portf_m - weight_portf_bond * ret_bond_m - weight_portf_cash * ret_cash_m) / weight_portf_equity

    ###########################################################################
    # 930950-基准收益

    quarter_date = portf_weight['结束日期'].unique()[0]
    print("\n")
    print("季度日期: " + str(quarter_date))

    # 930950基准包含的全部基金代码
    jjdm_930950 = util.get_930950_funds(str(quarter_date))

    # 市值占比
    sql_market_value = "select jjdm 基金代码, jsrq 结束日期, jjzzc 市值 from st_fund.t_st_gm_zcpz\
                        where jjdm in {0} and jsrq = {1}".format(tuple(jjdm_930950), quarter_date)
    market_value = get_df(sql_market_value, db='funduser')
    market_value = market_value[~market_value['市值'].isna()]
    mv = market_value[['基金代码', '市值']]
    mv['市值占比'] = mv['市值'] / mv['市值'].sum()
    mv = mv[['基金代码', '市值占比']]

    # 取收盘价然后再算收益
    sql_930950_spj = "select zqdm 证券代码, jyrq 交易日期, spjg 收盘价 from st_market.t_st_zs_hq\
                      where zqdm = '930950' and jyrq <={}".format(end_date)
    spj_930950 = get_df(sql_930950_spj, db='alluser')

    # 周收益
    spj_930950_w = spj_930950.set_index('交易日期').loc[[int(last_week), int(end_date)], :]
    ret_bmk_w = spj_930950_w.loc[int(end_date), '收盘价'] / spj_930950_w.loc[int(last_week), '收盘价'] - 1

    # 月收益
    spj_930950_m = spj_930950.set_index('交易日期').loc[[int(last_month), int(end_date)], :]
    ret_bmk_m = spj_930950_m.loc[int(end_date), '收盘价'] / spj_930950_m.loc[int(last_month), '收盘价'] - 1

    ###########################################################################
    # 930950-基准权重 [股票+货币+债券](按市值加权)
    sql_bmk_weight = "select jjdm 基金代码, jsrq 结束日期, gptzzjb 股票, zqzszzjb 债券, hbzjzjb 货币 from st_fund.t_st_gm_zcpz\
                        where jjdm in {0} and jsrq = {1}".format(tuple(mv['基金代码'].unique()), quarter_date)
    bmk_weight = get_df(sql_bmk_weight, db='funduser')
    bmk_weight = bmk_weight.reset_index(drop=True)
    bmk_weight = bmk_weight.fillna(0)
    bmk_weight[['债券', '股票', '货币']] = bmk_weight[['债券', '股票', '货币']] / 100

    bmk_weight = pd.merge(bmk_weight, mv, on='基金代码', how='left')
    bmk_weight['加权债券'] = bmk_weight['债券'] * bmk_weight['市值占比']
    bmk_weight['加权股票'] = bmk_weight['股票'] * bmk_weight['市值占比']
    bmk_weight['加权货币'] = bmk_weight['货币'] * bmk_weight['市值占比']

    weight_bmk_bond = bmk_weight['加权债券'].sum()
    weight_bmk_equity = bmk_weight['加权股票'].sum()
    weight_bmk_cash = bmk_weight['加权货币'].sum()

    ###########################################################################
    # 930950-股票收益

    ret_equity_bmk_w = (ret_bmk_w - weight_bmk_bond * ret_bond_w - weight_bmk_cash * ret_cash_w) / weight_bmk_equity

    ret_equity_bmk_m = (ret_bmk_m - weight_bmk_bond * ret_bond_m - weight_bmk_cash * ret_cash_m) / weight_bmk_equity

    ###########################################################################
    # input df : df_w & df_m

    cln = ['return_bench_i', 'return_portf_i', 'weight_bench_i', 'weight_portf_i']
    idx = ['cash', 'equity', 'bond']

    df_w = pd.DataFrame(index=idx, columns=cln)
    df_w['return_bench_i'] = [ret_cash_w, ret_equity_bmk_w, ret_bond_w]
    df_w['return_portf_i'] = [ret_cash_w, ret_equity_portf_w, ret_bond_w]
    df_w['weight_bench_i'] = [weight_bmk_cash, weight_bmk_equity, weight_bmk_bond]
    df_w['weight_portf_i'] = [weight_portf_cash, weight_portf_equity, weight_portf_bond]
    df_w_initial = df_w.copy()

    df_m = pd.DataFrame(index=idx, columns=cln)
    df_m['return_bench_i'] = [ret_cash_m, ret_equity_bmk_m, ret_bond_m]
    df_m['return_portf_i'] = [ret_cash_m, ret_equity_portf_m, ret_bond_m]
    df_m['weight_bench_i'] = [weight_bmk_cash, weight_bmk_equity, weight_bmk_bond]
    df_m['weight_portf_i'] = [weight_portf_cash, weight_portf_equity, weight_portf_bond]
    df_m_initial = df_m.copy()

    ###########################################################################
    # 池+基准-信息汇总

    info_w = df_w_initial.copy()
    info_w = info_w.reset_index()
    info_w.rename(columns={"index": "资产类别", "return_portf_i": "池周收益率", "return_bench_i": "基准周收益率",
                           "weight_portf_i": "池暴露", "weight_bench_i": "基准暴露"}, inplace=True)
    info_w = info_w[['资产类别', '池暴露', '基准暴露', '池周收益率', '基准周收益率']]

    info_m = df_m_initial.copy()
    info_m = info_m.reset_index()
    info_m.rename(columns={"index": "资产类别", "return_portf_i": "池月收益率", "return_bench_i": "基准月收益率",
                           "weight_portf_i": "池暴露", "weight_bench_i": "基准暴露"}, inplace=True)
    info_m = info_m[['资产类别', '池暴露', '基准暴露', '池月收益率', '基准月收益率']]

    info_final = pd.merge(info_w, info_m, on=['资产类别', '池暴露', '基准暴露'], how='left')

    ###########################################################################
    # brinson

    def brinson_attribution(dff):
        # 基准收益率和组合收益率
        dff['bench_return'] = dff['return_bench_i'] * dff['weight_bench_i']
        dff['port_return'] = dff['return_portf_i'] * dff['weight_portf_i']

        # 超额收益
        dff['excess_return'] = dff['port_return'] - dff['bench_return']

        # 配置收益,用组合各类资产的权重减去基准各类资产的权重,乘以基准各类资产的收益率
        dff['allocation'] = (dff['weight_portf_i'] - dff['weight_bench_i']) * dff['return_bench_i']

        # 选股收益，用组合各类资产的收益率减去基准各类资产的收益率,乘以基准各类资产的权重
        dff['selection'] = (dff['return_portf_i'] - dff['return_bench_i']) * dff['weight_bench_i']

        # 交叉收益，用超额收益减去配置收益和选股收益
        dff['interactive'] = dff['excess_return'] - dff['allocation'] - dff['selection']

        result_df = dff[['allocation', 'selection', 'interactive', 'excess_return']].copy()
        result_df.loc['summary'] = result_df.sum()

        return result_df

    ###########################################################################
    # output df : brinson_w & brinson_m

    brinson_w = brinson_attribution(df_w)
    brinson_m = brinson_attribution(df_m)

    brinson_w = brinson_w.reset_index().rename(columns={"index": "asset_category"})
    brinson_m = brinson_m.reset_index().rename(columns={"index": "asset_category"})

    ###########################################################################
    # each_fund 个基 (月度:m)
    each_jj_return_m = portf_return_m.copy()
    each_jj_weight = portf_weight.copy()[['基金代码', '债券', '股票', '货币']].set_index('基金代码')

    table1 = pd.DataFrame(index=jjdm_list,
                          columns=['个基股票月度收益率', '个基股票暴露', '个基债券暴露', '个基现金暴露'])
    table2 = pd.DataFrame(index=jjdm_list, columns=['equity_allocation', 'equity_selection', 'equity_interactive',
                                                    'equity_excess_return', 'bond_excess_return'])

    for k in range(len(jjdm_list)):
        each_jjdm = jjdm_list[k]
        weight_jj_cash = each_jj_weight.loc[each_jjdm, '货币']
        weight_jj_equity = each_jj_weight.loc[each_jjdm, '股票']
        weight_jj_bond = each_jj_weight.loc[each_jjdm, '债券']
        ret_jj_m = each_jj_return_m.loc[each_jjdm, '月收益']

        ret_equity_jj_m = (ret_jj_m - weight_jj_bond * ret_bond_m - weight_jj_cash * ret_cash_m) / weight_jj_equity

        table1.loc[each_jjdm, '个基股票月度收益率'] = ret_equity_jj_m
        table1.loc[each_jjdm, '个基股票暴露'] = weight_jj_equity
        table1.loc[each_jjdm, '个基债券暴露'] = weight_jj_bond
        table1.loc[each_jjdm, '个基现金暴露'] = weight_jj_cash
        table1 = table1.astype(float)

        cln = ['return_bench_i', 'return_portf_i', 'weight_bench_i', 'weight_portf_i']
        idx = ['cash', 'equity', 'bond']
        e_df_m = pd.DataFrame(index=idx, columns=cln)
        e_df_m['return_bench_i'] = [ret_cash_m, ret_equity_bmk_m, ret_bond_m]
        e_df_m['return_portf_i'] = [ret_cash_m, ret_equity_jj_m, ret_bond_m]
        e_df_m['weight_bench_i'] = [weight_bmk_cash, weight_bmk_equity, weight_bmk_bond]
        e_df_m['weight_portf_i'] = [weight_jj_cash, weight_jj_equity, weight_jj_bond]
        e_df_m_initial = e_df_m.copy()

        each_brinson_m = brinson_attribution(e_df_m)

        table2.loc[each_jjdm, 'equity_allocation'] = each_brinson_m.loc['equity', 'allocation']
        table2.loc[each_jjdm, 'equity_selection'] = each_brinson_m.loc['equity', 'selection']
        table2.loc[each_jjdm, 'equity_interactive'] = each_brinson_m.loc['equity', 'interactive']
        table2.loc[each_jjdm, 'equity_excess_return'] = each_brinson_m.loc['equity', 'excess_return']
        table2.loc[each_jjdm, 'bond_excess_return'] = each_brinson_m.loc['bond', 'excess_return']
        table2 = table2.astype(float)

    table1 = table1.reset_index().rename(columns={"index": "基金代码"})
    table2 = table2.reset_index().rename(columns={"index": "基金代码"})

    # 英文名修改为中文名
    info_final = info_final.replace({"资产类别": {"cash": "现金", "equity": "股票", "bond": "债券"}})

    brinson_w.rename_axis('Brinson周度贡献', inplace=True)
    brinson_w.rename(columns={'asset_category': '资产类别',
                              'allocation': '配置',
                              'selection': '选股',
                              'interactive': '交互',
                              'excess_return': '超额'}, inplace=True)
    brinson_w = brinson_w.replace({"资产类别": {"cash": "现金", "equity": "股票", "bond": "债券", "summary": "合计"}})

    brinson_m.rename_axis('Brinson月度贡献', inplace=True)
    brinson_m.rename(columns={'asset_category': '资产类别',
                              'allocation': '配置',
                              'selection': '选股',
                              'interactive': '交互',
                              'excess_return': '超额'}, inplace=True)
    brinson_m = brinson_m.replace({"资产类别": {"cash": "现金", "equity": "股票", "bond": "债券", "summary": "合计"}})

    table2.rename(columns={"equity_allocation": "股票_配置",
                           "equity_selection": "股票_选股",
                           "equity_interactive": "股票_交互",
                           "equity_excess_return": "股票_超额",
                           "bond_excess_return": "债券_超额"}, inplace=True)

    return info_final, brinson_w, brinson_m, table1, table2

# 使用示例
# info_t0,brinson_w,brinson_m,gj_t1_m,gj_t2_m = fund_pool_brinson(last_month,last_week,end_date,jjdm_list)

def get_funds_barra_data(last_month,last_week, end_date,jjdm_list,factor_type='style',bmk_id='930950'):

    all_data=[]

    res = na.StyleAttribution(fund_id=bmk_id, fund_type='index', start_date=last_month, end_date=end_date,
                              factor_type=factor_type, benchmark_id='000985', nav_frequency='day',flexible_time_interval=True).get_all_xz(processed=True)
    bmk_data=res['attribution_summary']
    bmk_data['r_square']=res['attr_df'].iloc[-1]['value']
    bmk_data.set_index('style_factor',inplace=True)



    for jjdm in jjdm_list:

        res = na.StyleAttribution(fund_id=jjdm, fund_type='mutual', start_date=last_month, end_date=end_date,
                                  factor_type=factor_type, benchmark_id='000985', nav_frequency='day',flexible_time_interval=True).get_all_xz(processed=True)
        temp=res['attribution_summary']
        temp['r_square'] = res['attr_df'].iloc[-1]['value']
        all_data.append(temp)

    sql="select jzrq,jjdm,fqdwjz from st_fund.t_st_gm_rhb where jjdm in {0} and jzrq in {1}"\
        .format(tuple(jjdm_list),tuple([end_date,last_week]))
    pool_weekly_ret=hbdb.db2df(sql,db='funduser')
    pool_weekly_ret=pool_weekly_ret.groupby('jjdm').pct_change()['fqdwjz'].mean()

    sql="select spjg,jyrq from st_market.t_st_zs_hq where zqdm ='930950' and jyrq in {0}".format(tuple([end_date,last_week]))
    bmk_weekly_ret=hbdb.db2df(sql,db='alluser')
    bmk_weekly_ret=bmk_weekly_ret.pct_change()['spjg'].mean()

    all_data=pd.concat(all_data, axis=0)
    pool_data=all_data.groupby('style_factor').mean()

    #get factor return
    if(factor_type=='style'):

        index_list=['alpha','Beta','波动性','盈利','成长性','杠杆','流动性','动量','估值','规模','非线性规模','误差']
        data = NavAttributionLoader(
            '000001', 'mutual', last_week, end_date, factor_type, '000985').load()
        factor_ret = data['factor_data'].pct_change()

    elif(factor_type=='sector'):

        index_list=['TMT','alpha', '中证全债', '制造', '周期', '大金融', '消费','误差']
        data = NavAttributionLoader(
            '000001', 'mutual', last_week, end_date, factor_type, '000985').load()
        factor_ret = data['factor_data'].pct_change()

    else:
        index_list=['alpha','中盘价值', '中盘成长', '中证全债', '大盘价值', '大盘成长', '小盘价值', '小盘成长','误差']
        data = NavAttributionLoader(
            '000001', 'mutual', last_week, end_date, factor_type, '000985').load()
        factor_ret = data['factor_data'].pct_change()


    #add the weekly alpha return
    import  datetime
    factor_ret['alpha']=np.power(1+pool_data.loc['alpha']['return_attr'],
                                 1/(datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(last_month, '%Y%m%d')).days)-1
    factor_ret.loc[last_week,'alpha']=np.nan
    factor_ret['误差']=np.power(1+pool_data.loc['误差']['return_attr'],
                                 1/(datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(last_month, '%Y%m%d')).days)-1
    factor_ret.loc[last_week,'误差']=np.nan
    factor_cum_ret=(factor_ret+1).cumprod().iloc[-1]-1
    # factor_cum_ret.loc['误差']=pool_weekly_ret - factor_cum_ret.iloc[0:-1].sum()

    pool_data=pd.merge(pool_data,factor_cum_ret.to_frame('weekly_ret'),how='left',left_index=True,right_index=True)
    pool_data['weekly_attr']=pool_data['weekly_ret'] * pool_data['factor_exposure']
    pool_data.loc['alpha','weekly_attr']=pool_data.loc['alpha']['weekly_ret']
    pool_data.loc['误差','weekly_attr']=pool_weekly_ret - pool_data['weekly_attr'].sum()
    pool_data.columns = ['基金池风格暴露', '基金池月收益贡献', '基金池置信度', '因子周收益率', '基金池周收益贡献']
    pool_data.index=index_list

    #add the alpha return
    factor_ret['alpha']=np.power(1+bmk_data.loc['alpha']['return_attr'],
                                 1/(datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(last_month, '%Y%m%d')).days)-1
    factor_ret.loc[last_week,'alpha']=np.nan
    factor_ret['误差']=np.power(1+bmk_data.loc['误差']['return_attr'],
                                 1/(datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(last_month, '%Y%m%d')).days)-1
    factor_ret.loc[last_week,'误差']=np.nan
    factor_cum_ret=(factor_ret+1).cumprod().iloc[-1]-1
    # factor_cum_ret.loc['误差']=bmk_weekly_ret - factor_cum_ret.iloc[0:-1].sum()

    bmk_data=pd.merge(bmk_data,factor_cum_ret.to_frame('weekly_ret'),how='left',left_index=True,right_index=True)
    bmk_data['weekly_attr']=bmk_data['weekly_ret'] * bmk_data['factor_exposure']
    bmk_data.loc['alpha','weekly_attr']=bmk_data.loc['alpha']['weekly_ret']
    bmk_data.loc['误差','weekly_attr']=bmk_weekly_ret - bmk_data['weekly_attr'].sum()
    bmk_data.columns = ['BMK风格暴露', 'BMK月收益贡献','基金代码','类型', 'BMK置信度', 'BMK周收益率', 'BMK周收益贡献']
    bmk_data.index=index_list

    comparison=pd.merge(pool_data[['基金池风格暴露','基金池月收益贡献','基金池周收益贡献']]
                            ,bmk_data[['BMK风格暴露','BMK月收益贡献','BMK周收益贡献']],how='left',left_index=True,right_index=True)

    barra_exp=all_data.pivot_table('factor_exposure','fund_id','style_factor').fillna(0)
    barra_ret=all_data.pivot_table('return_attr','fund_id','style_factor').fillna(0)
    barra_exp.columns=index_list
    barra_ret.columns=index_list


    return comparison,barra_exp,barra_ret

def get_holding_based_data(last_month,last_week, end_date,jjdm_list,factor_type='style',bmk_id='930950'):


    # get funds return
    sql = "select jjdm,jzrq,fqdwjz from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ({1}) " \
        .format(util.list_sql_condition(jjdm_list)
                , util.list_sql_condition([last_month, last_week, end_date]))
    funds_nav = hbdb.db2df(sql, db='funduser').pivot_table('fqdwjz','jzrq','jjdm')
    funds_return = funds_nav.pct_change().iloc[-1].to_frame('周收益')
    funds_return['月收益'] = funds_nav.pct_change(2).iloc[-1]

    # get bmk return
    sql = "select jyrq,zqdm,spjg from st_market.t_st_zs_hq where jyrq in ({0}) and zqdm='{1}' " \
        .format(util.list_sql_condition([last_month, last_week, end_date]),bmk_id)
    bmk_nav = hbdb.db2df(sql, db='alluser').pivot_table('spjg','jyrq','zqdm')
    bmk_return = bmk_nav.pct_change().iloc[-1].to_frame('周收益')
    bmk_return['月收益'] = bmk_nav.pct_change(2).iloc[-1]

    if(factor_type=='style'):
        # get fund exp
        jsrq=pd.read_sql("select max(jsrq) as jsrq from hbs_9_lables_exp where jsrq<='{}'".format(end_date),con=localdb)['jsrq'].iloc[0]
        sql="select * from hbs_9_lables_exp where jjdm in ({0}) and jsrq='{1}'".format(util.list_sql_condition(jjdm_list),jsrq)
        fund_exp_data=pd.read_sql(sql,con=localdb)
        fund_exp_data['zjbl']=fund_exp_data['zjbl']/100
        fund_exp_data.rename(columns={'zjbl':'暴露'},inplace=True)

        # get bmk exp
        bmk_jjdm_list=util.get_930950_funds(end_date)
        sql = "select * from hbs_9_lables_exp where jjdm in ({0}) and jsrq='{1}'".format(
            util.list_sql_condition(bmk_jjdm_list), jsrq)
        bmk_exp_data=pd.read_sql(sql,con=localdb)
        bmk_exp_data['total_mv']=bmk_exp_data.groupby('jjdm')['jjzzc'].mean().sum()
        bmk_exp_data['zjbl']=bmk_exp_data['zjbl']*bmk_exp_data['jjzzc']/bmk_exp_data['total_mv']

        bmk_exp_data=bmk_exp_data.groupby('label')[['zjbl']].sum()
        bmk_exp_data['zjbl']=bmk_exp_data['zjbl']/100
        bmk_exp_data.rename(columns={'zjbl':'暴露'},inplace=True)

        # get factor return
        sql="select jyrq,zqdm,spjg from st_market.t_st_zs_hq where jyrq in ({0}) and zqdm in ({1})"\
            .format(util.list_sql_condition([last_month,last_week, end_date]),
                    util.list_sql_condition(['399376','399377','399374','399375','399372','399373','399316','399315','399314']))
        factor_nav=hbdb.db2df(sql,db='alluser').pivot_table('spjg','jyrq','zqdm')
        factor_nav.columns=['大盘均衡', '中盘均衡', '小盘均衡', '大盘成长', '大盘价值', '中盘成长', '中盘价值',
       '小盘成长', '小盘价值']

        factor_return=factor_nav.pct_change().iloc[-1].to_frame('周收益')
        factor_return['月收益']=factor_nav.pct_change(2).iloc[-1]

        fund_data=pd.merge(fund_exp_data,factor_return,
                           how='left',left_on='label',right_index=True).drop('jsrq',axis=1)
        bmk_data = pd.merge(bmk_exp_data, factor_return,
                             how='left', left_on='label', right_index=True)

    elif(factor_type=='sector'):

        # get fund exp
        jsrq = \
        hbdb.db2df("select max(jsrq) as jsrq from st_fund.t_st_gm_jjhyzhyszb where jsrq<='{}' and zclb='2' "
                   .format(end_date), db='funduser')['jsrq'].iloc[0]
        sql = "select jsrq,jjdm,zzjbl/100 as 暴露,flmc as label from st_fund.t_st_gm_jjhyzhyszb where jjdm in ({0}) and jsrq='{1}' and zclb='2' and hyhfbz='2'".format(
            util.list_sql_condition(jjdm_list), jsrq)
        fund_exp_data = hbdb.db2df(sql, db='funduser')

        # get bmk exp
        bmk_jjdm_list = util.get_930950_funds(end_date)
        sql = "select jjdm,jsrq,zzjbl/100 as 暴露,flmc as label from st_fund.t_st_gm_jjhyzhyszb where jjdm in ({0}) and jsrq='{1}' and zclb='2' and hyhfbz='2'".format(
            util.list_sql_condition(bmk_jjdm_list),         jsrq)
        bmk_exp_data = hbdb.db2df(sql, db='funduser')

        jsrq=pd.read_sql("select max(jsrq) as jsrq from hbs_9_lables_exp where jsrq<='{}'".format(end_date),con=localdb)['jsrq'].iloc[0]
        sql = "select jjdm,jjzzc from hbs_9_lables_exp where jjdm in ({0}) and jsrq='{1}'".format(
            util.list_sql_condition(bmk_jjdm_list), jsrq)
        bmk_mv_data=pd.read_sql(sql,con=localdb).drop_duplicates('jjdm')
        bmk_mv_data['total_mv']=bmk_mv_data.groupby('jjdm')['jjzzc'].mean().sum()
        bmk_mv_data['jjzzc']=bmk_mv_data['jjzzc']/bmk_mv_data['total_mv']

        bmk_exp_data=pd.merge(bmk_exp_data,bmk_mv_data.drop_duplicates('jjdm'),how='left',on='jjdm')
        bmk_exp_data['暴露']=bmk_exp_data['暴露']*bmk_exp_data['jjzzc']
        bmk_exp_data=bmk_exp_data.groupby('label')[['暴露']].sum()


        # get factor return
        new_col_name=['农林牧渔', '基础化工', '钢铁', '有色金属', '电子', '家用电器', '食品饮料',
         '纺织服饰', '轻工制造', '医药生物', '公用事业', '交通运输', '房地产', '商贸零售',
         '社会服务', '综合', '建筑材料', '建筑装饰', '电力设备', '国防军工', '计算机', '传媒',
         '通信', '银行', '非银金融', '汽车', '机械设备', '煤炭', '石油石化', '环保', '美容护理']
        index_code_list=['801010','801030','801040','801050','801080','801110',
                              '801120','801130','801140','801150','801160','801170',
                              '801180','801200','801210','801230','801710','801720',
                              '801730','801740','801750','801760','801770','801780',
                              '801790','801880','801890','801950','801960','801970','801980']
        index_code_map=dict(zip(index_code_list,new_col_name))

        sql = "select jyrq,zqdm,spjg from st_market.t_st_zs_hq where jyrq in ({0}) and zqdm in ({1})" \
            .format(util.list_sql_condition([last_month, last_week, end_date]),
                    util.list_sql_condition(['801010', '801030', '801040', '801050', '801080', '801110',
                         '801120', '801130', '801140', '801150', '801160', '801170',
                         '801180', '801200', '801210', '801230', '801710', '801720',
                         '801730', '801740', '801750', '801760', '801770', '801780',
                         '801790', '801880', '801890', '801950', '801960', '801970', '801980']))
        factor_nav = hbdb.db2df(sql, db='alluser').pivot_table('spjg', 'jyrq', 'zqdm').rename(columns=index_code_map)

        factor_return = factor_nav.pct_change().iloc[-1].to_frame('周收益')
        factor_return['月收益'] = factor_nav.pct_change(2).iloc[-1]

        fund_data = pd.merge(fund_exp_data, factor_return,
                             how='left', left_on='label', right_index=True).drop('jsrq',axis=1)
        bmk_data = pd.merge(bmk_exp_data, factor_return,
                             how='left', left_on='label', right_index=True)

    else:
        print('input factor_type is not supported, only style and sector is supported by now ')
        raise Exception

    fund_data['周收益']=fund_data['周收益']*fund_data['暴露']
    fund_data['月收益']=fund_data['月收益']*fund_data['暴露']
    temp=pd.merge(fund_data.groupby('jjdm')[['周收益','月收益']].sum(),
                  funds_return[['周收益','月收益']],how='left',on='jjdm')
    temp['周收益'] = temp['周收益_y'] - temp['周收益_x']
    temp['月收益'] = temp['月收益_y'] - temp['月收益_x']
    temp['label']='alpha-基金选股收益'
    fund_data=pd.concat([fund_data,temp[['周收益','月收益','label']].reset_index(drop=False)],axis=0)

    pool_data=fund_data.groupby('label').sum()/len(fund_data['jjdm'].unique())

    bmk_data['周收益']=bmk_data['周收益']*bmk_data['暴露']
    bmk_data['月收益']=bmk_data['月收益']*bmk_data['暴露']
    bmk_data.loc['alpha-基金选股收益','周收益']=bmk_return['周收益'].iloc[0]-bmk_data['周收益'].sum()
    bmk_data.loc['alpha-基金选股收益','月收益']=bmk_return['月收益'].iloc[0]-bmk_data['月收益'].sum()

    pool_data.columns=['池'+str(x) for  x in pool_data.columns]
    bmk_data.columns=['基准'+str(x) for  x in bmk_data.columns]
    pool_data=pd.merge(pool_data,bmk_data,how='outer',on='label')


    pool_data.index.name='池信息汇总'

    return  pool_data[['池暴露','基准暴露', '池周收益','基准周收益', '池月收益', '基准月收益']],\
        fund_data.pivot_table('暴露','jjdm','label'),\
        fund_data.pivot_table('月收益','jjdm','label'),\
        fund_data.pivot_table('周收益','jjdm','label')

def subjective_label_analysis(last_month,last_week, end_date,jjdm_info):


    asofdate=pd.read_sql("select max(asofdate) as asofdate from extra_table_funds where asofdate<={}"
                         .format(end_date),con=localdb)['asofdate'].iloc[0]

    type_return_summary=[]
    for type in jjdm_info['入池类型'].unique():

        if(type in ['价值','成长']):
            peer_group=pd.read_sql("select jjdm from jjpic_value_p_hbs where asofdate='{0}' and `风格偏好`='{1}' "
                                   .format(asofdate,type),con=localdb)['jjdm'].tolist()
            sql = "select jjdm,jzrq,fqdwjz from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ({1}) " \
                .format(util.list_sql_condition(peer_group)
                        , util.list_sql_condition([last_month, last_week, end_date]))
            type_nav = hbdb.db2df(sql, db='funduser').pivot_table('fqdwjz', 'jzrq', 'jjdm')
            type_return = type_nav.pct_change().iloc[-1].to_frame('周收益')
            type_return['月收益'] = type_nav.pct_change(2).iloc[-1]
            type_return_summary.append(type_return.mean().to_frame(str(type)))

        elif(type in ['TMT','制造','周期','消费','医药','大金融']+[x+'+' for x in ['TMT','制造','周期','消费','医药','大金融']]):
            peer_group=pd.read_sql("select jjdm from public_theme_pool_history where asofdate='{0}' and theme='{1}' "
                                   .format(asofdate,type),con=localdb)['jjdm'].tolist()
            sql = "select jjdm,jzrq,fqdwjz from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ({1}) " \
                .format(util.list_sql_condition(peer_group)
                        , util.list_sql_condition([last_month, last_week, end_date]))
            type_nav = hbdb.db2df(sql, db='funduser').pivot_table('fqdwjz', 'jzrq', 'jjdm')
            type_return = type_nav.pct_change().iloc[-1].to_frame('周收益')
            type_return['月收益'] = type_nav.pct_change(2).iloc[-1]
            type_return_summary.append(type_return.mean().to_frame(str(type)))

        elif(type=='超额稳定型'):
            peer_group=pd.read_sql("select jjdm from extra_table_funds where asofdate='{0}'"
                                   .format(asofdate),con=localdb)['jjdm'].tolist()
            sql = "select jjdm,jzrq,fqdwjz from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ({1}) " \
                .format(util.list_sql_condition(peer_group)
                        , util.list_sql_condition([last_month, last_week, end_date]))
            type_nav = hbdb.db2df(sql, db='funduser').pivot_table('fqdwjz', 'jzrq', 'jjdm')
            type_return = type_nav.pct_change().iloc[-1].to_frame('周收益')
            type_return['月收益'] = type_nav.pct_change(2).iloc[-1]
            type_return_summary.append(type_return.mean().to_frame(str(type)))

        else:
            if('价值' in type):
                peer_group1 = pd.read_sql("select jjdm from jjpic_value_p_hbs where asofdate='{0}' and `风格偏好`='{1}' "
                                         .format(asofdate, '价值'), con=localdb)['jjdm'].tolist()
            elif('成长' in type):
                peer_group1 = pd.read_sql("select jjdm from jjpic_value_p_hbs where asofdate='{0}' and `风格偏好`='{1}' "
                                         .format(asofdate, '成长' ), con=localdb)['jjdm'].tolist()
            if('大盘' in type):
                peer_group2 = pd.read_sql("select jjdm from jjpic_size_p_hbs where asofdate='{0}' and `规模偏好`='{1}' "
                                         .format(asofdate, '大盘' ), con=localdb)['jjdm'].tolist()
            elif('中小盘' in type):
                peer_group2 = pd.read_sql("select jjdm from jjpic_size_p_hbs where asofdate='{0}' and `规模偏好`='{1}' "
                                         .format(asofdate, '中小盘' ), con=localdb)['jjdm'].tolist()

            peer_group=list(set(peer_group1).intersection(set(peer_group2)))
            sql = "select jjdm,jzrq,fqdwjz from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ({1}) " \
                .format(util.list_sql_condition(peer_group)
                        , util.list_sql_condition([last_month, last_week, end_date]))
            type_nav = hbdb.db2df(sql, db='funduser').pivot_table('fqdwjz', 'jzrq', 'jjdm')
            type_return = type_nav.pct_change().iloc[-1].to_frame('周收益')
            type_return['月收益'] = type_nav.pct_change(2).iloc[-1]
            type_return_summary.append(type_return.mean().to_frame(str(type)))


    type_return_summary=\
        pd.concat(type_return_summary, axis=1)

    #get funds return
    sql = "select jjdm,jzrq,fqdwjz from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ({1}) " \
        .format(util.list_sql_condition(jjdm_info['基金代码'].unique().tolist())
                , util.list_sql_condition([last_month, last_week, end_date]))
    fund_nav = hbdb.db2df(sql, db='funduser').pivot_table('fqdwjz', 'jzrq', 'jjdm')
    fund_return = fund_nav.pct_change().iloc[-1].to_frame('周收益')
    fund_return['月收益'] = fund_nav.pct_change(2).iloc[-1]
    jjdm_info=pd.merge(jjdm_info,fund_return,how='left',left_on='基金代码',right_on='jjdm')
    jjdm_info=pd.merge(jjdm_info,type_return_summary.T,how='left',
                       left_on='入池类型',right_index=True)
    jjdm_info['月超额收益']= jjdm_info['月收益_x']- jjdm_info['月收益_y']
    jjdm_info['周超额收益']= jjdm_info['周收益_x']- jjdm_info['周收益_y']
    jjdm_info.rename(columns={'月收益_y':'同类平均月收益'
        ,'周收益_y':'同类平均周收益'},inplace=True)

    pool_info=jjdm_info.groupby('入池类型')[['月超额收益','同类平均月收益','周超额收益','同类平均周收益']].mean()
    return pool_info.reset_index(),jjdm_info[['基金代码', '入池类型','月超额收益','同类平均月收益', '周超额收益','同类平均周收益']]

def get_funds_barra_data_prv(last_month,last_week, end_date,jjdm_list,factor_type='style',missing_data=None):

    all_data=[]

    res = na.StyleAttribution(fund_id='HB1001', fund_type='prv_index', start_date=last_month, end_date=end_date,
                              factor_type=factor_type, benchmark_id='000985', nav_frequency='week',flexible_time_interval=True).get_all_xz(processed=True)
    bmk_data=res['attribution_summary']
    bmk_data['r_square']=res['attr_df'].iloc[-1]['value']
    bmk_data.set_index('style_factor',inplace=True)

    for jjdm in jjdm_list:

        res = na.StyleAttribution(fund_id=jjdm, fund_type='private', start_date=last_month, end_date=end_date,
                                  factor_type=factor_type, benchmark_id='000985', nav_frequency='week',flexible_time_interval=True).get_all_xz(processed=True)
        temp=res['attribution_summary']
        temp['r_square'] = res['attr_df'].iloc[-1]['value']
        all_data.append(temp)


    sql="select jzrq,jjdm,ljjz from st_hedge.t_st_jjjz where jjdm in {0} and jzrq in {1}"\
        .format(tuple(jjdm_list),tuple([end_date,last_week]))
    pool_weekly_ret=hbdb.db2df(sql,db='highuser')
    pool_weekly_ret=pool_weekly_ret.groupby('jjdm')['ljjz'].pct_change().mean()

    sql="select spjg,jyrq from st_hedge.t_st_sm_zhmzs where zsdm ='HB1001' and jyrq in {0}".format(tuple([end_date,last_week]))
    bmk_weekly_ret=hbdb.db2df(sql,db='highuser')
    if(missing_data is not None):
        bmk_weekly_ret.loc[len(bmk_weekly_ret)]=[end_date,missing_data]
    bmk_weekly_ret=bmk_weekly_ret['spjg'].pct_change().mean()

    all_data=pd.concat(all_data, axis=0)
    all_data['return_attr']=all_data['return_attr'].astype(float)
    pool_data=all_data.groupby('style_factor').mean()

    #get factor return
    if(factor_type=='style'):

        index_list=['alpha','Beta','波动性','盈利','成长性','杠杆','流动性','动量','估值','规模','非线性规模','误差']
        data = NavAttributionLoader(
            '000001', 'mutual', last_week, end_date, factor_type, '000985').load()
        factor_ret = data['factor_data'].pct_change()

    elif(factor_type=='sector'):

        index_list=['TMT','alpha', '中证全债', '制造', '周期', '大金融', '消费','误差']
        data = NavAttributionLoader(
            '000001', 'mutual', last_week, end_date, factor_type, '000985').load()
        factor_ret = data['factor_data'].pct_change()

    else:
        index_list=['alpha','中盘价值', '中盘成长', '中证全债', '大盘价值', '大盘成长', '小盘价值', '小盘成长','误差']
        data = NavAttributionLoader(
            '000001', 'mutual', last_week, end_date, factor_type, '000985').load()
        factor_ret = data['factor_data'].pct_change()


    #add the alpha return
    import  datetime
    factor_ret['alpha']=np.power(1+pool_data.loc['alpha']['return_attr'],
                                 1/(datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(last_month, '%Y%m%d')).days)-1
    factor_ret.loc[last_week,'alpha']=np.nan
    factor_ret['误差']=np.power(1+pool_data.loc['误差']['return_attr'],
                                 1/(datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(last_month, '%Y%m%d')).days)-1
    factor_ret.loc[last_week,'误差']=np.nan
    factor_cum_ret=(factor_ret+1).cumprod().iloc[-1]-1
    # factor_cum_ret.loc['误差']=pool_weekly_ret - factor_cum_ret.iloc[0:-1].sum()

    pool_data=pd.merge(pool_data,factor_cum_ret.to_frame('weekly_ret'),how='left',left_index=True,right_index=True)
    pool_data['weekly_attr']=pool_data['weekly_ret'] * pool_data['factor_exposure']
    pool_data.loc['alpha','weekly_attr']=pool_data.loc['alpha']['weekly_ret']
    pool_data.loc['误差','weekly_attr']=pool_weekly_ret - pool_data['weekly_attr'].sum()
    pool_data.columns = ['基金池风格暴露', '基金池季度收益贡献', '基金池置信度', '因子月收益率', '基金池月收益贡献']
    pool_data.index=index_list

    #add the alpha return
    factor_ret['alpha']=np.power(1+bmk_data.loc['alpha']['return_attr'],
                                 1/(datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(last_month, '%Y%m%d')).days)-1
    factor_ret.loc[last_week,'alpha']=np.nan
    factor_ret['误差']=np.power(1+bmk_data.loc['误差']['return_attr'],
                                 1/(datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(last_month, '%Y%m%d')).days)-1
    factor_ret.loc[last_week,'误差']=np.nan
    factor_cum_ret=(factor_ret+1).cumprod().iloc[-1]-1
    # factor_cum_ret.loc['误差']=bmk_weekly_ret - factor_cum_ret.iloc[0:-1].sum()

    bmk_data=pd.merge(bmk_data,factor_cum_ret.to_frame('weekly_ret'),how='left',left_index=True,right_index=True)
    bmk_data['weekly_attr']=bmk_data['weekly_ret'] * bmk_data['factor_exposure']
    bmk_data.loc['alpha','weekly_attr']=bmk_data.loc['alpha']['weekly_ret']
    bmk_data.loc['误差','weekly_attr']=bmk_weekly_ret - bmk_data['weekly_attr'].sum()
    bmk_data.columns = ['BMK风格暴露', 'BMK季度收益贡献','基金代码','类型', 'BMK置信度', 'BMK月收益率', 'BMK月收益贡献']
    bmk_data.index=index_list

    comparison=pd.merge(pool_data[['基金池风格暴露','基金池季度收益贡献','基金池月收益贡献']]
                            ,bmk_data[['BMK风格暴露','BMK季度收益贡献','BMK月收益贡献']],how='left',left_index=True,right_index=True)

    barra_exp=all_data.pivot_table('factor_exposure','fund_id','style_factor').fillna(0)
    barra_ret=all_data.pivot_table('return_attr','fund_id','style_factor').fillna(0)
    barra_exp.columns=index_list
    barra_ret.columns=index_list


    return comparison,barra_exp,barra_ret

def save_nav_based_result_history2db(start_date,end_date):


    sql_script = "SELECT jyrq JYRQ, sfjj SFJJ, sfzm SFZM FROM st_main.t_st_gg_jyrl\
                  WHERE jyrq >= {} and jyrq <= {}".format(start_date, end_date)
    df = hbdb.db2df(sql_script, db='alluser')
    df = df.rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    date_list=df[(df['SFZM'] == '1') & (df['isOpen'] == '0')]['calendarDate'].tolist()

    mutual_pool_jjdm_list=pd.read_excel(r"E:\GitFolder\docs\基金池业绩归因\公募基金池历史.xlsx")
    mutual_pool_jjdm_list['调入时间']=mutual_pool_jjdm_list['调入时间'].astype(str).str.replace('-', '')
    mutual_pool_jjdm_list['调出时间']=mutual_pool_jjdm_list['调出时间'].astype(str).str.replace('-', '')
    mutual_pool_jjdm_list.loc[mutual_pool_jjdm_list['调出时间']=='NaT','调出时间']='29999999'
    mutual_pool_jjdm_list['基金代码']=mutual_pool_jjdm_list['基金代码'].str[0:6]


    total_summary = []
    funds_summary = []
    for i in range(4,len(date_list)):

        latest_date=date_list[i]
        last_month =  date_list[i-4]
        last_week = date_list[i-1]


        jjdm_list=\
            mutual_pool_jjdm_list[(mutual_pool_jjdm_list['调入时间']<=last_month)
                                  &(mutual_pool_jjdm_list['调出时间']>=latest_date)]['基金代码'].tolist()

        summary, barra_exp, barra_ret = \
            get_funds_barra_data(last_month=last_month,
                                 last_week=last_week,
                                 end_date=str(latest_date), jjdm_list=jjdm_list, factor_type='style')
        summary['date'] = latest_date
        summary['type'] = 'barra'
        total_summary.append(summary)

        summary_sector, barra_exp_sector, barra_ret_sector = \
            get_funds_barra_data(last_month=last_month,
                                 last_week=last_week,
                                 end_date=str(latest_date), jjdm_list=jjdm_list, factor_type='sector')
        summary_sector['date'] = latest_date
        summary_sector['type'] = '行业'
        total_summary.append(summary_sector)

        summary_style, barra_exp_style, barra_ret_style = \
            get_funds_barra_data(last_month=last_month,
                                 last_week=last_week,
                                 end_date=str(latest_date), jjdm_list=jjdm_list, factor_type='style_allo')
        summary_style['date'] = latest_date
        summary_style['type'] = '风格'
        total_summary.append(summary_style)

        barra_ret_sector['date'] = latest_date
        barra_ret_sector['type'] = '行业'
        funds_summary.append(barra_ret_sector)

        barra_ret_style['date'] = latest_date
        barra_ret_style['type'] = '风格'
        funds_summary.append(barra_ret_style)



    total_summary = pd.concat(total_summary).reset_index().rename(columns={'index': '项目名称'})
    # localdb.execute("delete from pool_attribution_history where date in {}".format(tuple(total_summary['date'].unique().tolist())))
    # total_summary.to_sql('pool_attribution_history', con=localdb, index=False, if_exists='append')

    funds_summary=pd.concat(funds_summary).reset_index()
    funds_summary.to_excel('nav_based_funds.xlsx')
    # funds_summary.to_sql('pool_funds_attribution_history', con=localdb, index=False, if_exists='append')

def save_holding_based_result_history2db(start_date,end_date):


    sql_script = "SELECT jyrq JYRQ,sfjj SFJJ, sfym SFYM,sfzm SFZM FROM st_main.t_st_gg_jyrl WHERE jyrq >= {} and jyrq <= {}".format(
        start_date, end_date)
    df = hbdb.db2df(sql_script, db='alluser')
    df = df.rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    date_list=df[(df['SFZM'] == '1') & (df['isOpen'] == '0')]['calendarDate'].tolist()

    mutual_pool_jjdm_list=pd.read_excel(r"E:\GitFolder\docs\基金池业绩归因\公募基金池历史.xlsx")
    mutual_pool_jjdm_list['调入时间']=mutual_pool_jjdm_list['调入时间'].astype(str).str.replace('-', '')
    mutual_pool_jjdm_list['调出时间']=mutual_pool_jjdm_list['调出时间'].astype(str).str.replace('-', '')
    mutual_pool_jjdm_list.loc[mutual_pool_jjdm_list['调出时间']=='NaT','调出时间']='29999999'
    mutual_pool_jjdm_list['基金代码']=mutual_pool_jjdm_list['基金代码'].str[0:6]


    total_summary = []
    funds_summary=[]
    for i in range(1,len(date_list)):

        latest_date=date_list[i]
        last_month = util._shift_date(util.str_date_shift(str(latest_date), 30, '-'))
        last_week = date_list[i-1]


        jjdm_list=\
            mutual_pool_jjdm_list[(mutual_pool_jjdm_list['调入时间']<=last_month)
                                  &(mutual_pool_jjdm_list['调出时间']>=latest_date)]['基金代码'].tolist()

        # get the holding based analysis result
        summary_hbs, funds_exp, funds_month_ret, funds_week_ret = get_holding_based_data(
            last_month=util._shift_date(util.str_date_shift(str(latest_date), 30, '-')),
            last_week=last_week
            , end_date=str(latest_date),
            jjdm_list=jjdm_list, factor_type='style')
        summary_hbs_sector, funds_exp_sector, \
            funds_month_ret_sector, funds_week_ret_sector = get_holding_based_data(
            last_month=util._shift_date(util.str_date_shift(str(latest_date), 30, '-')),
            last_week=last_week, end_date=str(latest_date),
            jjdm_list=jjdm_list, factor_type='sector')



        summary_hbs['date'] = latest_date
        summary_hbs['type'] = '风格'
        total_summary.append(summary_hbs)


        summary_hbs_sector['date'] = latest_date
        summary_hbs_sector['type'] = '行业'
        total_summary.append(summary_hbs_sector)

        funds_week_ret['date'] = latest_date
        funds_week_ret['type'] = '风格'
        funds_summary.append(funds_week_ret)


        funds_week_ret_sector['date'] = latest_date
        funds_week_ret_sector['type'] = '行业'
        funds_summary.append(funds_week_ret_sector)


    total_summary = pd.concat(total_summary).reset_index().rename(columns={'index': '项目名称'})
    # localdb.execute("delete from pool_attribution_history_hldbased where date in {}".format(tuple(total_summary['date'].unique().tolist())))
    # total_summary.to_sql('pool_attribution_history_hldbased', con=localdb, index=False, if_exists='append')

    funds_summary=pd.concat(funds_summary).reset_index()
    funds_summary.to_excel('hld_base_funds.xlsx')
    # funds_summary.to_sql('pool_funds_attribution_history_hldbased', con=localdb, index=False, if_exists='append')


def save_prvfund_nav_based_result_history2db(start_date,end_date):


    sql_script = "SELECT jyrq JYRQ,sfjj SFJJ, sfym SFYM,sfzm SFZM FROM st_main.t_st_gg_jyrl WHERE jyrq >= {} and jyrq <= {}".format(
        start_date, end_date)
    df = hbdb.db2df(sql_script, db='alluser')
    df = df.rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    date_list=df[(df['SFZM'] == '1') & (df['isOpen'] == '0')]['calendarDate'].tolist()

    mutual_pool_jjdm_list=pd.read_excel(r"E:\GitFolder\docs\基金池业绩归因\私募基金池历史.xlsx")
    mutual_pool_jjdm_list['调入时间']=mutual_pool_jjdm_list['调入时间'].astype(str).str.replace('-', '')
    mutual_pool_jjdm_list['调出时间']=mutual_pool_jjdm_list['调出时间'].astype(str).str.replace('-', '')
    mutual_pool_jjdm_list.loc[mutual_pool_jjdm_list['调出时间']=='NaT','调出时间']='29999999'
    mutual_pool_jjdm_list['基金代码']=mutual_pool_jjdm_list['基金代码'].str[0:6]


    total_summary = []
    for i in range(13,len(date_list)):

        latest_date=date_list[i]
        #使用季度数据进行回归
        last_month =  date_list[i-13]
        last_week = date_list[i-1]
        print(i)

        jjdm_list=\
            mutual_pool_jjdm_list[(mutual_pool_jjdm_list['调入时间']<=last_month)
                                  &(mutual_pool_jjdm_list['调出时间']>=latest_date)]['基金代码'].tolist()

        summary, barra_exp, barra_ret = \
            get_funds_barra_data_prv(last_month=last_month,
                                 last_week=last_week,
                                 end_date=str(latest_date), jjdm_list=jjdm_list, factor_type='style')
        summary['date'] = latest_date
        summary['type'] = 'barra'
        total_summary.append(summary)

        summary_sector, barra_exp_sector, barra_ret_sector = \
            get_funds_barra_data_prv(last_month=last_month,
                                 last_week=last_week,
                                 end_date=str(latest_date), jjdm_list=jjdm_list, factor_type='sector')
        summary_sector['date'] = latest_date
        summary_sector['type'] = '行业'
        total_summary.append(summary_sector)

        summary_style, barra_exp_style, barra_ret_style = \
            get_funds_barra_data_prv(last_month=last_month,
                                 last_week=last_week,
                                 end_date=str(latest_date), jjdm_list=jjdm_list, factor_type='style_allo')
        summary_style['date'] = latest_date
        summary_style['type'] = '风格'
        total_summary.append(summary_style)

    total_summary = pd.concat(total_summary).reset_index().rename(columns={'index': '项目名称'})
    total_summary.to_excel('pool_attribution_history_prv.xlsx')
    # localdb.execute("delete from pool_attribution_history_prv where date in {}".format(tuple(total_summary['date'].unique().tolist())))
    total_summary.to_sql('pool_attribution_history_prv', con=localdb, index=False, if_exists='append')

def calculate_zone_return(df,pool_col,bmk_col,data_fre='week'):

    pool_nav=(df[pool_col].sum(axis=1)+1)
    bmk_nav=(df[bmk_col].sum(axis=1)+1)

    nav_df=pool_nav.to_frame('基金池')
    nav_df['基准']=bmk_nav

    summary=pd.DataFrame(index=['近1月','近3月','近6月','今年以来','2022','2021'])
    pool_array=[]
    bmk_array = []

    date_list_df=pool_nav.index.to_frame('date')
    date_list_df['year']=date_list_df['date'].str[0:4]
    date_list2=date_list_df.reset_index(drop=True).drop_duplicates('year', keep='last').index.to_list()[0:-1]
    date_list2.sort(reverse=True)

    jnyl_i=pool_nav.index.astype(str).str[0:4].to_frame('').drop_duplicates('date',keep='last').index[-2]
    if(data_fre=='week'):
        date_list=[-4,-13,-26,jnyl_i]

    elif(data_fre=='month'):
        date_list = [-2, -4, -7, jnyl_i]

    elif(data_fre=='quarter'):
        date_list = [-2, -2, -3, jnyl_i]


    for i in date_list:
        pool_array.append(pool_nav.iloc[-1]/pool_nav.iloc[i]-1)
        bmk_array.append(bmk_nav.iloc[-1] / bmk_nav.iloc[i] - 1)
    for i in range(len(date_list2)-1):
        pool_array.append(pool_nav.iloc[date_list2[i]]/pool_nav.iloc[date_list2[i+1]]-1)
        bmk_array.append(bmk_nav.iloc[date_list2[i]] / bmk_nav.iloc[date_list2[i+1]] - 1)

    summary['基金池']=pool_array
    summary['基准']=bmk_array

    for col in pool_col.tolist()+['基金池风格收益']:
        temparray=[]
        for i in date_list:
            temparray.append((df.iloc[-1][col]-df.iloc[i][col])/pool_nav.iloc[i])
        for i in range(len(date_list2)-1):
            temparray.append((df.iloc[date_list2[i]][col]-df.iloc[date_list2[i+1]][col])/pool_nav.iloc[date_list2[i+1]])
        summary[col+'']=temparray

    for col in bmk_col.tolist()+['基准风格收益']:
        temparray=[]
        for i in date_list:
            temparray.append((df.iloc[-1][col]-df.iloc[i][col])/bmk_nav.iloc[i])
        for i in range(len(date_list2)-1):
            temparray.append((df.iloc[date_list2[i]][col]-df.iloc[date_list2[i+1]][col])/bmk_nav.iloc[date_list2[i+1]])
        summary[col+'']=temparray

    return summary,nav_df


def plot_reasoning(df,col_list,title_name,data_fre='daily',extra_name='nav',pool_type='mutual',save_nav=False):


    #exposuer dimension
    exp_data=pd.merge(df.pivot_table('基金池风格暴露','date','风格').drop('alpha',axis=1)
                      ,df.pivot_table('BMK风格暴露','date','风格').drop('alpha',axis=1)
                      ,on='date',how='inner')
    exp_data.columns=[x.replace('_x','_基金池') for x in exp_data.columns]
    exp_data.columns=[x.replace('_y','_BMK') for x in exp_data.columns]
    for i in range(1,len(col_list)):
        exp_data[col_list[i]+'_BMK']=exp_data[col_list[i]+'_BMK']+exp_data[[x+'_基金池'for x in col_list[0:i]]].sum(axis=1)

    if(pool_type=='mutual'):
        exp_data.to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\{}暴露历史.xlsx".format(extra_name+title_name))
    else:
        exp_data.to_excel(r"E:\GitFolder\docs\基金池业绩归因\私募基金池归因数据\{}暴露历史.xlsx".format(extra_name+title_name))


    if(data_fre=='month'):
        #take each four weeks data only
        month_date_list=df['date'].unique().tolist()[-1::-4]
        df=df[df['date'].isin(month_date_list)]
        pool_con_col='基金池月收益贡献'
        bmk_con_col='BMK月收益贡献'
    elif(data_fre=='quarter'):
        #take each 13 weeks data only
        month_date_list=df['date'].unique().tolist()[-1::-13]
        df=df[df['date'].isin(month_date_list)]
        pool_con_col='基金池季度收益贡献'
        bmk_con_col='BMK季度收益贡献'
    else:
        pool_con_col='基金池周收益贡献'
        bmk_con_col='BMK周收益贡献'


    pool_weekly_nav=df.groupby('date')[pool_con_col].sum()
    pool_weekly_nav = (pool_weekly_nav + 1).cumprod().to_frame('nav')
    pool_weekly_nav['nav']=[1] + pool_weekly_nav['nav'].to_list()[0:-1]
    df=pd.merge(df,pool_weekly_nav,how='left',left_on='date',right_index=True)

    bmk_weekly_nav=df.groupby('date')[bmk_con_col].sum()
    bmk_weekly_nav = (bmk_weekly_nav + 1).cumprod().to_frame('bmk_nav')
    bmk_weekly_nav['bmk_nav']=[1] + bmk_weekly_nav['bmk_nav'].to_list()[0:-1]
    df=pd.merge(df,bmk_weekly_nav,how='left',left_on='date',right_index=True)

    df[pool_con_col+'_可加']=df[pool_con_col]*df['nav']
    df[bmk_con_col+'_可加']=df[bmk_con_col]*df['bmk_nav']

    contr_history=pd.merge(df.pivot_table(pool_con_col+'_可加','date','风格').cumsum(),
                           df.pivot_table(bmk_con_col+'_可加','date','风格').cumsum()
                           ,how='inner',on='date')
    contr_history.columns=[x.replace('_x','_基金池') for x in contr_history.columns]
    contr_history.columns=[x.replace('_y','_BMK') for x in contr_history.columns]

    pool_col=contr_history.columns[contr_history.columns.astype(str).str.contains('_基金池')]
    bmk_col=contr_history.columns[~contr_history.columns.astype(str).str.contains('_基金池')]
    pool_style_col=pool_col[~(pool_col.astype(str).str.contains('alpha')
                              |pool_col.astype(str).str.contains('中证全债')
                              |pool_col.astype(str).str.contains('误差'))].tolist()
    bmk_style_col = bmk_col[~(bmk_col.astype(str).str.contains('alpha')
                              |bmk_col.astype(str).str.contains('中证全债')
                              |bmk_col.astype(str).str.contains('误差'))].tolist()

    contr_history['基金池风格收益']=contr_history[pool_style_col].sum(axis=1)
    contr_history['基准风格收益']=contr_history[bmk_style_col].sum(axis=1)

    summary,nav_df=calculate_zone_return(contr_history,pool_col,bmk_col,data_fre)


    if(pool_type=='mutual'):
        contr_history.to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\{}贡献历史.xlsx".format(extra_name+title_name))
        summary.to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\{}收益总结.xlsx".format(extra_name+title_name))
        if(save_nav):
            nav_df.to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\{}净值时序.xlsx".format(extra_name+title_name))
    else:
        contr_history.to_excel(r"E:\GitFolder\docs\基金池业绩归因\私募基金池归因数据\{}贡献历史.xlsx".format(extra_name+title_name))
        summary.to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\{}收益总结.xlsx".format(extra_name+title_name))
        if (save_nav):
            nav_df.to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\{}净值时序.xlsx".format(extra_name+title_name))

    df=df[df['风格']=='alpha']

    weekly_ret_data=pd.merge(df.pivot_table(pool_con_col,'date','风格')
                      ,df.pivot_table(bmk_con_col,'date','风格')
                      ,on='date',how='inner')
    weekly_ret_data.columns=[x.replace('_x','_基金池') for x in weekly_ret_data.columns]
    weekly_ret_data.columns=[x.replace('_y','_BMK') for x in weekly_ret_data.columns]


    plot = functionality.Plot(1200, 600)
    data, layout=plot.plotly_line_and_area(exp_data,
                              line_col=[x+'_BMK' for x in col_list],
                              area_col=[x+'_基金池' for x in col_list],
                                           title_text='基金池{}暴露（基于净值）'.format(title_name))
    plot.plot_render(data, layout)

    plot = functionality.Plot(2000, 600)
    plot.plotly_style_bar(weekly_ret_data, title_text='{}月度选股贡献'.format(title_name))

    plot=functionality.Plot(1200,1000)
    plot.plotly_line_style(contr_history,'累计贡献')

def funds_reasoning(dir,type='nav',data_fre='month'):

    style_data=pd.read_excel(dir,sheet_name='风格')
    theme_data = pd.read_excel(dir, sheet_name='行业')
    style_data['jjdm']=[("000000"+str(x))[-6:] for x in style_data['jjdm']]
    theme_data['jjdm']=[("000000"+str(x))[-6:] for x in theme_data['jjdm']]


    def take_month_or_quarter_data(df,data_fre):

        if(data_fre=='month'):
            #take each four weeks data only
            month_date_list=df['date'].unique().tolist()[-1::-4]
            df=df[df['date'].isin(month_date_list)]

        elif(data_fre=='quarter'):
            #take each 13 weeks data only
            month_date_list=df['date'].unique().tolist()[-1::-13]
            df=df[df['date'].isin(month_date_list)]

        return  df

    style_data=take_month_or_quarter_data(style_data,data_fre)
    theme_data = take_month_or_quarter_data(theme_data, data_fre)

    def get_the_addable_contribution(style_data):

        style_data['fund_ret']=style_data.drop('date',axis=1).sum(axis=1)


        pool_nav=style_data.groupby('date')['fund_ret'].mean()
        pool_nav=(pool_nav+1).cumprod()
        pool_nav=pool_nav.to_frame('nav')
        pool_nav['nav'] = [1] + pool_nav['nav'].iloc[0:-1].tolist()

        style_data=pd.merge(style_data,pool_nav,how='left',on='date').set_index('date')
        style_data=pd.merge(style_data,style_data.groupby('date')['jjdm'].count().to_frame('pool_size')
                            ,how='left',on='date')

        for col in style_data.drop(['jjdm','type','nav','pool_size'],axis=1).columns:
            style_data[col]=style_data[col]*style_data['nav']
        for col in style_data.drop(['jjdm','type','nav','pool_size'],axis=1).columns:
            style_data[col]=style_data[col]*style_data['nav']/style_data['pool_size']

        date_list_df=\
            pd.DataFrame(data=style_data.index.unique().tolist(),columns=['date'])
        date_list_df['year']=date_list_df['date'].astype(str).str[0:4]

        date_list_year =date_list_df.drop_duplicates('year',keep='first')['date'].tolist()

        if (data_fre == 'week'):
            date_list = [-4, -13, -26, date_list_year[-1]]

        elif (data_fre == 'month'):
            date_list = [-2, -4, -7, date_list_year[-1]]

        elif (data_fre == 'quarter'):
            date_list = [-2, -2, -3, date_list_year[-1]]

        date_list_year=date_list_year+[style_data.index[-1]]

        fund_summary=[]

        for i in range(1,len(date_list_year)):
            tempdf=style_data.loc[date_list_year[i-1]:date_list_year[i]]
            tempdf['year'] = tempdf.index.astype(str).str[0:4]
            tempdf = tempdf[tempdf['year'] == str(date_list_year[i - 1])[0:4]]

            tempdf=(tempdf.groupby('jjdm').sum()).drop(['pool_size','nav'],axis=1)/tempdf['nav'].iloc[1]
            tempdf['date']=str(date_list_year[i-1])[0:4]
            fund_summary.append(tempdf)

        return  style_data,pd.concat(fund_summary,axis=0)

    style_data,style_summary=get_the_addable_contribution(style_data)
    theme_data,theme_summary=get_the_addable_contribution(theme_data)

    pd.concat([style_summary,theme_summary],axis=1).to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\个基归因总结_{}.xlsx".format(type))

def mutual_pool_history_reasoning(start_date,end_date,type):

    if(type=='nav'):

        #read mutual pool style data
        sql="select * from pool_attribution_history where  date>='{0}' and date<='{1}'"\
            .format(start_date,end_date)
        raw_data=pd.read_sql(sql,con=localdb)

        style_data=raw_data[raw_data['type']=='风格']
        sector_data=raw_data[raw_data['type']=='行业']

        style_data.loc[style_data['项目名称'].isin(['中盘价值','小盘价值','大盘价值']),'风格'] ='价值'
        style_data.loc[style_data['项目名称'].isin(['中盘成长','小盘成长','大盘成长']),'风格'] ='成长'
        style_data.loc[style_data['项目名称']=='中证全债','风格'] ='中证全债'
        style_data.loc[style_data['项目名称']=='误差','风格'] ='误差'
        style_data.loc[style_data['项目名称']=='alpha','风格'] ='alpha'

        style_data2=style_data.copy()
        style_data2.loc[style_data2['项目名称'].isin(['大盘价值','大盘成长']),'风格'] ='大盘'
        style_data2.loc[style_data2['项目名称'].isin(['中盘成长','小盘成长','中盘价值','小盘价值']),'风格'] ='中小盘'
        style_data2.loc[style_data2['项目名称']=='中证全债','风格'] ='中证全债'
        style_data2.loc[style_data2['项目名称']=='误差','风格'] ='误差'
        style_data2.loc[style_data2['项目名称']=='alpha','风格'] ='alpha'


        sector_data['风格']=sector_data['项目名称']
        # sector_data.loc[sector_data['项目名称']=='误差','风格'] ='alpha'


        style_data=style_data.groupby(['date', '风格']).sum().reset_index()
        style_data2=style_data2.groupby(['date', '风格']).sum().reset_index()
        sector_data=sector_data.groupby(['date', '风格']).sum().reset_index()

        plot_reasoning(style_data, ['中证全债','价值','成长'], '风格','month',type,'mutual',True)
        plot_reasoning(style_data2, ['中小盘','中证全债', '大盘'], '市值风格','month',type)
        plot_reasoning(sector_data, ['TMT',  '中证全债', '制造', '周期', '大金融', '消费'],
                       '主题行业','month',type)

    else:
        # read mutual pool style data
        sql = "select * from pool_attribution_history_hldbased where  date>='{0}' and date<='{1}'" \
            .format(start_date, end_date)
        raw_data = pd.read_sql(sql, con=localdb)
        raw_data.columns=['池信息汇总', '基金池风格暴露', 'BMK风格暴露', '基金池周收益贡献',
                          'BMK周收益贡献', '基金池月收益贡献', 'BMK月收益贡献', 'date','type']


        style_data = raw_data[raw_data['type'] == '风格']
        sector_data = raw_data[raw_data['type'] == '行业']

        style_data.loc[style_data['池信息汇总'].isin(['中盘价值', '小盘价值', '大盘价值']), '风格'] = '价值'
        style_data.loc[style_data['池信息汇总'].isin(['中盘成长', '小盘成长', '大盘成长']), '风格'] = '成长'
        style_data.loc[style_data['池信息汇总'].isin(['中盘均衡', '大盘均衡', '小盘均衡']), '风格'] = '均衡'
        style_data.loc[style_data['池信息汇总'] == 'alpha-基金选股收益', '风格'] = 'alpha'

        style_data2 = style_data.copy()
        style_data2.loc[style_data2['池信息汇总'].isin(['大盘价值', '大盘成长','大盘均衡']), '风格'] = '大盘'
        style_data2.loc[style_data2['池信息汇总'].isin(['中盘成长', '小盘成长', '中盘价值', '小盘价值','中盘均衡','小盘均衡']), '风格'] = '中小盘'
        style_data2.loc[style_data2['池信息汇总'] == 'alpha-基金选股收益', '风格'] = 'alpha'


        from hbshare.fe.mutual_analysis.holdind_based import  Industry_analysis as ia
        IA=ia()

        sector_data=pd.merge(sector_data,IA.ind2thememap,how='left',left_on='池信息汇总',right_on='industry_name')

        sector_data['风格'] = sector_data['theme']
        sector_data.loc[sector_data['风格'].isnull(), '风格'] = 'alpha'
        # sector_data.loc[sector_data['项目名称']=='误差','风格'] ='alpha'

        style_data = style_data.groupby(['date', '风格']).sum().reset_index()
        style_data2 = style_data2.groupby(['date', '风格']).sum().reset_index()
        sector_data = sector_data.groupby(['date', '风格']).sum().reset_index()

        plot_reasoning(style_data,['价值','均衡','成长'],'风格','week',type,'mutual',True)
        plot_reasoning(style_data2,['中小盘','大盘'],'市值风格','week',type)
        plot_reasoning(sector_data,['TMT','制造','周期','大金融','消费'],'行业','week',type)

def prv_pool_history_reasoning(start_date,end_date):

    #read prv pool style data
    sql="select * from pool_attribution_history_prv where  date>='{0}' and date<='{1}'"\
        .format(start_date,end_date)
    raw_data=pd.read_sql(sql,con=localdb)

    style_data = raw_data[raw_data['type'] == '风格']
    sector_data = raw_data[raw_data['type'] == '行业']

    style_data.loc[style_data['项目名称'].isin(['中盘价值', '小盘价值', '大盘价值']), '风格'] = '价值'
    style_data.loc[style_data['项目名称'].isin(['中盘成长', '小盘成长', '大盘成长']), '风格'] = '成长'
    style_data.loc[style_data['项目名称'] == '中证全债', '风格'] = '中证全债'
    style_data.loc[style_data['项目名称'] == '误差', '风格'] = '误差'
    style_data.loc[style_data['项目名称'] == 'alpha', '风格'] = 'alpha'

    style_data2 = style_data.copy()
    style_data2.loc[style_data2['项目名称'].isin(['大盘价值', '大盘成长']), '风格'] = '大盘'
    style_data2.loc[style_data2['项目名称'].isin(['中盘成长', '小盘成长', '中盘价值', '小盘价值']), '风格'] = '中小盘'
    style_data2.loc[style_data2['项目名称'] == '中证全债', '风格'] = '中证全债'
    style_data2.loc[style_data2['项目名称'] == '误差', '风格'] = '误差'
    style_data2.loc[style_data2['项目名称'] == 'alpha', '风格'] = 'alpha'

    sector_data['风格'] = sector_data['项目名称']
    # sector_data.loc[sector_data['项目名称']=='误差','风格'] ='alpha'

    style_data = style_data.groupby(['date', '风格']).sum().reset_index()
    style_data2 = style_data2.groupby(['date', '风格']).sum().reset_index()
    sector_data = sector_data.groupby(['date', '风格']).sum().reset_index()

    plot_reasoning(style_data, ['中证全债', '价值', '成长'], '风格', 'quarter','nav','prv')
    plot_reasoning(style_data2, ['中小盘', '中证全债', '大盘'], '市值风格', 'quarter','nav','prv')
    plot_reasoning(sector_data, ['TMT', '中证全债', '制造', '周期', '大金融', '消费'],
                   '主题行业', 'quarter','nav','prv')

def pool_features_analyse(dir,start_date, end_date):

    pool_his=pd.read_excel(dir)
    pool_his['调入时间']=pool_his['调入时间'].astype(str).str.replace('-', '')
    pool_his['调出时间']=pool_his['调出时间'].astype(str).str.replace('-', '')
    pool_his.loc[pool_his['调出时间']=='NaT','调出时间']='29999999'
    pool_his['基金代码']=pool_his['基金代码'].str[0:6]


    def pool_adjust_ret(change_date_list,type='in'):
        if(type=='in'):
            col='调入时间'
        else:
            col='调出时间'

        in_funds_ext_ret=[]
        in_funds_ret=[]
        for date_og in change_date_list:


            temp_jjdm_list=\
                pool_his[pool_his[col]==date_og]['基金代码'].tolist()
            date=util._shift_date(date_og)

            sql="select jjdm, zbnp,zblb from st_fund.t_st_gm_rqjhb where jjdm in ({0}) and jzrq='{1}' and zblb in ('2103','2106','2201','2202') and zbnp<=1000 "\
                .format(util.list_sql_condition(temp_jjdm_list),date)
            fund_ret=hbdb.db2df(sql,db='funduser')

            sql="select zbnp,zblb from st_market.t_st_zs_rqjhb where zqdm ='885001' and jyrq='{0}' and  zblb in ('2103','2106','2201','2202') and zbnp<=1000"\
                .format(date)
            bmk_ret=hbdb.db2df(sql,db='alluser')

            fund_ret=pd.merge(fund_ret,bmk_ret,how='left',on='zblb')
            fund_ret['ext_ret']=fund_ret['zbnp_x']-fund_ret['zbnp_y']

            ext_df=fund_ret.pivot_table('ext_ret','jjdm','zblb')
            ret_df=fund_ret.pivot_table('zbnp_x','jjdm','zblb')

            ext_df[col]=date_og
            ret_df[col] = date_og

            in_funds_ext_ret.append(ext_df)
            in_funds_ret.append(ret_df)

        in_funds_ext_ret=pd.concat(in_funds_ext_ret,axis=0)
        in_funds_ret=pd.concat(in_funds_ret, axis=0)
        in_funds_ext_ret.columns=['近3月','近6月','近1年','近2年',col]
        in_funds_ret.columns = ['近3月', '近6月', '近1年', '近2年',col]

        return in_funds_ext_ret,in_funds_ret

    in_ext_ret,in_ret=pool_adjust_ret(pool_his['调入时间'].unique().tolist())
    out_ext_ret, out_ret = pool_adjust_ret(pool_his[pool_his['调出时间']!='29999999']['调出时间'].unique().tolist(),type='out')

    sql_script = "SELECT jyrq JYRQ,sfjj SFJJ, sfym SFYM,sfzm SFZM FROM st_main.t_st_gg_jyrl WHERE jyrq >= {} and jyrq <= {}".format(
        start_date, end_date)
    df = hbdb.db2df(sql_script, db='alluser')
    df = df.rename(
        columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                 "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
    date_list=df[(df['isMonthEnd'] == '1') & (df['isOpen'] == '0')]['calendarDate'].tolist()

    funds_count=[]
    manager_avg_size=[]
    manager_avg_time=[]

    for date in date_list:

        temp_jjdm_list=pool_his[(pool_his['调入时间']<=date)&
                                (pool_his['调出时间']>=date)]
        funds_count.append(len(temp_jjdm_list))

        sql="select jjdm,rydm,ryxm,rzrq from st_fund.t_st_gm_jjjl where rzrq<='{0}' and lrrq>='{0}' and ryzw='基金经理' and jjdm in {1}"\
            .format(date,tuple(temp_jjdm_list['基金代码'].tolist()))
        temp_manager_infor=hbdb.db2df(sql,db='funduser').sort_values('rzrq').drop_duplicates('jjdm',keep='first')

        temp_manager_infor['rzsjcd']=[  (datetime.datetime.strptime(date, '%Y%m%d')-datetime.datetime.strptime(str(x), '%Y%m%d')).days/365
                                        for x in temp_manager_infor['rzrq']]

        sql="select rydm,zgcpgm,zgcpsl,jsrq from st_fund.t_st_gm_jlzgcptj where rydm in {0} and jsrq<='{1}' "\
            .format( tuple(temp_manager_infor['rydm'].tolist()),date)
        temp_manager_size=hbdb.db2df(sql,db='funduser').sort_values('jsrq').drop_duplicates('rydm',keep='last')

        temp_manager_infor['rydm']=temp_manager_infor['rydm'].astype(str)
        temp_manager_infor=pd.merge(temp_manager_infor,temp_manager_size,how='left',on='rydm')
        temp_jjdm_list=pd.merge(temp_jjdm_list,temp_manager_infor,how='left'
                                ,right_on='jjdm',left_on='基金代码')

        manager_avg_size.append(temp_jjdm_list['zgcpgm'].mean()/100000000)
        manager_avg_time.append(temp_jjdm_list['rzsjcd'].mean())

    final_df=pd.DataFrame(index=date_list)
    final_df['个基数量'] = funds_count
    final_df['个基平均规模'] = manager_avg_size
    final_df['基金经理平均任职时间'] = manager_avg_time

    final_df.to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\基金池历史特征.xlsx")
    pool_his=pd.merge(pool_his,in_ext_ret,how='left',
                      left_on=['基金代码','调入时间'],right_on=['jjdm','调入时间'])
    pool_his=pd.merge(pool_his,in_ret,how='left',
                      left_on=['基金代码','调入时间'],right_on=['jjdm','调入时间'])
    pool_his=pd.merge(pool_his,out_ext_ret,how='left',
                      left_on=['基金代码','调出时间'],right_on=['jjdm','调出时间'])
    pool_his=pd.merge(pool_his,out_ret,how='left',
                      left_on=['基金代码','调出时间'],right_on=['jjdm','调出时间'])
    pool_his.to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\基金池进出时点特征.xlsx")

def mutual_fund_core_classification_return():

    data=pd.read_excel(r"E:\GitFolder\docs\基金池业绩归因\公募基金池历史.xlsx")
    data['基金代码']=data['基金代码'].astype(str).str[0:6]
    data['调入时间']=data['调入时间'].astype(str).str.replace('-','')
    data['调出时间']=data['调出时间'].astype(str).str.replace('-','')
    data.loc[data['调出时间'] == 'NaT','调出时间']='29999999'

    pool_dm_list=data['基金代码'].tolist()

    sql="SELECT jjdm,asofdate from extra_table_funds where asofdate in ('20210630','20220630','20230630') "
    ext_fund_list=pd.read_sql(sql,con=localdb)
    ext_fund_list['ym'] = (ext_fund_list['asofdate'].astype(str).str[0:4]).astype(str)

    sql="SELECT jjdm,theme,asofdate from public_theme_pool_history where asofdate in ('20210630','20220630','20230630') "
    theme_fund_list=pd.read_sql(sql,con=localdb)
    theme_fund_list['ym'] = (theme_fund_list['asofdate'].astype(str).str[0:4]).astype(str)

    sql="SELECT jjdm,`风格偏好` as theme  ,asofdate from jjpic_value_p_hbs where asofdate in ('20210630','20220630','20230630') "
    style_fund_list=pd.read_sql(sql,con=localdb)
    style_fund_list['ym'] = (style_fund_list['asofdate'].astype(str).str[0:4]).astype(str)


    sql="select hb1y,jjdm,tjyf  from st_fund.t_st_gm_yhb  where jjdm in {0} and tjyf>='202101' and tjyf<='2023111'  "\
        .format(tuple(list(set(pool_dm_list+ext_fund_list['jjdm'].tolist()+theme_fund_list['jjdm'].tolist()))))
    fund_daily_ret=hbdb.db2df(sql,db='funduser')
    fund_daily_ret['tjyf']=fund_daily_ret['tjyf'].astype(str)

    pool_return_df=[]
    ext_return_df=[]
    theme_return_df=[]
    style_return_df=[]

    for ym in fund_daily_ret['tjyf'].unique():
        # print(ym)
        temp_list=data[(data['调入时间']<=str(ym)+'31')&(data['调出时间']>=str(ym)+'31')]
        temp_list=pd.merge(temp_list,fund_daily_ret[fund_daily_ret['tjyf']==str(ym)],
                           how='left',left_on='基金代码',right_on='jjdm').drop('基金代码',axis=1)
        pool_return_df.append(temp_list)

        ext_return_df.append(fund_daily_ret[(fund_daily_ret['tjyf'] == str(ym))
                       &(fund_daily_ret['jjdm'].isin(ext_fund_list[ext_fund_list['ym'] == str(ym)[0:4]]['jjdm'].tolist()))]['hb1y'].mean())


        temp_list =theme_fund_list[theme_fund_list['ym'] == str(ym)[0:4]]
        temp_list=pd.merge(temp_list,fund_daily_ret[fund_daily_ret['tjyf']==str(ym)],
                           how='left',on='jjdm')
        theme_return_df.append(temp_list.groupby('theme')['hb1y'].mean().to_frame(str(ym)).T)

        temp_list =style_fund_list[style_fund_list['ym'] == str(ym)[0:4]]
        temp_list=pd.merge(temp_list,fund_daily_ret[fund_daily_ret['tjyf']==str(ym)],
                           how='left',on='jjdm')
        style_return_df.append(temp_list.groupby('theme')['hb1y'].mean().to_frame(str(ym)).T)


    pool_return_df=pd.concat(pool_return_df,axis=0)
    theme_return_df=pd.concat(theme_return_df,axis=0)
    style_return_df=pd.concat(style_return_df,axis=0)


    pool_return_df_2021=((pool_return_df.groupby(['tjyf', '2021标签'])['hb1y'].mean() / 100).reset_index()).pivot_table('hb1y','tjyf','2021标签')
    pool_return_df_2022=((pool_return_df.groupby(['tjyf', '2022标签'])['hb1y'].mean() / 100).reset_index()).pivot_table('hb1y','tjyf','2022标签')
    pool_return_df_2023=((pool_return_df.groupby(['tjyf', '2023标签'])['hb1y'].mean() / 100).reset_index()).pivot_table('hb1y','tjyf','2023标签')



    theme_return_df=theme_return_df.fillna(0) / 100
    style_return_df=style_return_df.fillna(0) / 100
    ext_return_df=\
        pd.DataFrame(data=np.array(ext_return_df)/100,columns=['超额稳定'],index=fund_daily_ret['tjyf'].unique().tolist())

    col_list=pool_return_df_2021.columns.tolist()
    pool_return_df_2021=pd.merge(pool_return_df_2021,theme_return_df,left_index=True,right_index=True,how='left')
    pool_return_df_2021=pd.merge(pool_return_df_2021,ext_return_df,left_index=True,right_index=True,how='left')
    pool_return_df_2021=pd.merge(pool_return_df_2021,style_return_df,left_index=True,right_index=True,how='left')
    for col in col_list:
        pool_return_df_2021.loc[pool_return_df_2021[col+'_x'].isnull(),col+'_x']=\
            pool_return_df_2021.loc[pool_return_df_2021[col+'_x'].isnull()][col+'_y']

    col_list=pool_return_df_2022.columns.tolist()
    pool_return_df_2022=pd.merge(pool_return_df_2022,theme_return_df,left_index=True,right_index=True,how='left')
    pool_return_df_2022=pd.merge(pool_return_df_2022,ext_return_df,left_index=True,right_index=True,how='left')
    pool_return_df_2022=pd.merge(pool_return_df_2022,style_return_df,left_index=True,right_index=True,how='left')
    for col in col_list:
        pool_return_df_2022.loc[pool_return_df_2022[col+'_x'].isnull(),col+'_x']=\
            pool_return_df_2022.loc[pool_return_df_2022[col+'_x'].isnull()][col+'_y']

    col_list=pool_return_df_2023.columns.tolist()
    pool_return_df_2023=pd.merge(pool_return_df_2023,theme_return_df,left_index=True,right_index=True,how='left')
    pool_return_df_2023=pd.merge(pool_return_df_2023,ext_return_df,left_index=True,right_index=True,how='left')
    pool_return_df_2023=pd.merge(pool_return_df_2023,style_return_df,left_index=True,right_index=True,how='left')
    for col in col_list:
        pool_return_df_2023.loc[pool_return_df_2023[col+'_x'].isnull(),col+'_x']=\
            pool_return_df_2023.loc[pool_return_df_2023[col+'_x'].isnull()][col+'_y']

    pool_return_df_2021['ym']=pool_return_df_2021.index.astype(str).str[0:4]
    pool_return_df_2022['ym']=pool_return_df_2022.index.astype(str).str[0:4]
    pool_return_df_2023['ym']=pool_return_df_2023.index.astype(str).str[0:4]

    final_df=[]
    final_df.append( (pool_return_df_2021[pool_return_df_2021['ym']=='2021'].drop('ym',axis=1)+1).cumprod() )
    final_df.append( (pool_return_df_2022[pool_return_df_2022['ym']=='2022'].drop('ym',axis=1)+1).cumprod() )
    final_df.append( (pool_return_df_2023[pool_return_df_2023['ym']=='2023'].drop('ym',axis=1)+1).cumprod() )

    pd.concat(final_df,axis=1).to_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\核心策略收益率曲线.xlsx")

if __name__ == '__main__':

    # funds_reasoning(r"E:\GitFolder\hbshare\fe\return_analysis\nav_based_funds.xlsx")
    # funds_reasoning(r"E:\GitFolder\hbshare\fe\return_analysis\hld_base_funds.xlsx",type='hld',data_fre='week')
    # mutual_fund_core_classification_return()


    # save_nav_based_result_history2db('20231101','20231228')
    # save_holding_based_result_history2db('20231101', '20231228')
    # save_prvfund_nav_based_result_history2db('20200201', '20231231')


    prv_pool_history_reasoning('20200201','20231231')
    # mutual_pool_history_reasoning('20200201','20231201','nav')
    # mutual_pool_history_reasoning('20200201','20231201','hld')
    # pool_features_analyse(r"E:\GitFolder\docs\基金池业绩归因\公募基金池历史.xlsx",'20200201','20231201')

    # pool_jjdm_list=pd.read_excel(r"E:\GitFolder\docs\基金池跟踪\股多池跟踪\私募主观股多池跟踪表20231110.xlsx",sheet_name='Dashboard',header=1)['基金代码'].to_list()
    # jjdm_list=pool_jjdm_list
    # latest_date='20231110'

    # brinson_w,brinson_m = fund_pool_brinson(last_month,last_week,end_date,jjdm_list)
    # summary, barra_exp, barra_ret = \
    #     get_funds_barra_data_prv(last_month='20230512',
    #                          last_week='20231103',
    #                          end_date=str(latest_date), jjdm_list=jjdm_list, factor_type='style')

    #get the barra analysis result histroy
    # latest_date='20231116'
    #
    # summary,barra_exp,barra_ret=\
    #     get_funds_barra_data(last_month=util._shift_date(util.str_date_shift(str(latest_date),30,'-')),
    #                                                      last_week=util._shift_date(util.str_date_shift(str(latest_date),7,'-')),
    #                                                  end_date=str(latest_date),jjdm_list=jjdm_list,factor_type='style')




    # jjdm_info=pd.DataFrame(data=['006624', '377240','007449','001810'],columns=['基金代码'])
    # jjdm_info['入池类型']=['价值','成长','超额稳定型','中小盘价值']

    # pool_summary,funds_summary=subjective_label_analysis(last_month='20230831',last_week='20230922',
    #                                                  end_date='20230927',jjdm_info=jjdm_info)

    # summary,funds_exp,funds_month_ret,funds_week_ret=get_holding_based_data(last_month='20230831',last_week='20230922',
    #                                                  end_date='20230927',jjdm_list=pool_jjdm_list[0:2],factor_type='sector')
    #nav based test
    # summary,barra_exp,barra_ret=get_funds_barra_data(last_month='20230831',last_week='20230922',
    #                                                  end_date='20230927',jjdm_list=pool_jjdm_list[0:2],factor_type='sector')
