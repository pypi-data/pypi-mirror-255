import datetime
import shlex

import numpy as np
import pandas as pd
from hbshare.fe.XZ import functionality
from hbshare.fe.XZ import db_engine as dben

localdb = dben.PrvFunDB().engine
util = functionality.Untils()
hbdb=dben.HBDB()
class Projects:

    def __init__(self):

        from hbshare.fe.XZ.config import config_pfa as config
        self.config_pfa=config.Config()

    # 1.资产配置时序：A股 / 港股 / 债券 / 基金 / 现金等类别时序的累计区域图；
    def asset_allocation_pic(self,plot,asset_allocation_df):

        # 1.资产配置时序：A股 / 港股 / 债券 / 基金 / 现金等类别时序的累计区域图；
        plot.plotly_area(asset_allocation_df[['活期存款', '债券', '基金', '权证', '其他', 'A股',
                                              '港股', '日期']], '资产配置时序')

    # 2.行业配置时序：基于申万一级行业分别规则，对持仓的行业分布做一个时序统计；
    def industry_allocation_pic(self,plot,ind_hld):
        plot.plotly_area(ind_hld, '行业配置时序')

    # 3. 行业集中度时序：持仓前一 / 三 / 五大行业的权重时序
    def industry_centralization_pci(self,plot,indutry_allocation_df_ranked):

        # 3. 行业集中度时序：持仓前一 / 三 / 五大行业的权重时序
        inputdf = indutry_allocation_df_ranked.copy()
        cols = inputdf.columns.tolist()
        cols.remove('日期')
        for col in cols:
            inputdf[col] = [x[0].sum() for x in inputdf[col]]
        plot.plotly_line(inputdf, '行业集中度时序')

    # 4.重仓明细：时序上各个时间点的持仓明细（表格）；
    def stock_holding_pic(self,plot,stk_hld):
        # 4.重仓明细：时序上各个时间点的持仓明细（表格）；
        tempdf = stk_hld.drop('日期',axis=1).T
        input_df=pd.DataFrame()
        for date in tempdf.columns:
            input_df[date]=tempdf[date].sort_values(ascending=False).index[0:20]\
                           +'( '+tempdf[date].sort_values(ascending=False).values[0:20].astype(str)+' )'

        plot.plotly_table(input_df, 5000, '持仓明细')

    # 5.持股集中度时序：持仓前三 / 五 / 十大权重和的时序折线图；
    def stock_centralization_pic(self,plot,asset_allocation_df_ranked):
        # 5.持股集中度时序：持仓前三 / 五 / 十大权重和的时序折线图；
        inputdf = asset_allocation_df_ranked.copy()
        cols = inputdf.columns.tolist()
        cols.remove('日期')
        for col in cols:
            inputdf[col] = [x[0].sum() for x in inputdf[col]]
        plot.plotly_line(inputdf, '持股集中度时序')

    # 6.组合中A股持仓的平均PE / PB / 股息率的折线图；
    def valuation_pic(self,plot,fin_hld,stk_hld,date_list):
        # 6.组合中A股持仓的平均PE / PB / 股息率的折线图；
        tempdf = pd.DataFrame()
        for item in ['PE', 'PB', 'DIVIDENDRATIO']:
            tempdf[item] = ((fin_hld.loc[:, (item, slice(None))].values) * (stk_hld.drop('日期', axis=1).values)).sum(
                axis=1) / stk_hld.drop('日期', axis=1).values.sum(axis=1)
        tempdf['日期'] = date_list
        plot.plotly_line_multi_yaxis(tempdf, '持股估值分析', ['PB', 'DIVIDENDRATIO'])

    # 7.持股分布：所持股票在各类宽基成分股中的权重时序的折线图，包括：沪深300、中证500、中证1000、1800以外。
    def hodling_in_benchmark(self,plot,ben_hld):
        # 7.持股分布：所持股票在各类宽基成分股中的权重时序的折线图，包括：沪深300、中证500、中证1000、1800以外。
        plot.plotly_area(ben_hld, '宽基成分股配置走势')

    # 8 单只基金Alpha R_Square 散点图
    def alpha_rsquare_pic(self,plot,fun,df1,date_list,Jydb):

        #read the factors information from hb database
        sec_code_A=df1['Stock_code'].dropna()[~df1['Stock_code'].dropna().str.contains('H')].unique()
        raw_factors=Jydb.extract_factors(sec_code_A,date_list)

        #calcualte the risk exposure for the fund as a whole
        fund_factors=fun.fund_risk_exposure(fun.purified_stk_hld[['Stock_code','Name','Weight','Stamp_date']].dropna(),
                                            raw_factors,
                                            ['Stamp_date','Stock_code','Weight'])

        #get the return of benchmark index as factors
        index_list=['000905','000300']
        factors_benchmark=Jydb.extract_benchmark_return(date_list,index_list+['000012'])
        factors_benchmark=fun.aggregate_by(factors_benchmark,['TJYF','ZQDM'],'sum','HB')

        #join the classical risk factors with benchmark factors
        fund_factors=pd.merge(fund_factors,factors_benchmark,how='inner',left_on='JYYF',right_on='日期').drop('日期',axis=1)
        factors_list=fund_factors.columns.drop(['JYYF']+index_list).tolist()

        #get the return of the fund by valuation table as the y input for the ols model
        ret_df=fun.generate_ret_df()
        ret_df['JYYF'] = [x.split('-')[0] + x.split('-')[1] for x in ret_df['Stamp_date'].astype(str)]
        ret_df.drop('Stamp_date',axis=1,inplace=True)
        ret_df['Return']=ret_df['Return'].shift(-1)
        ret_df.drop(ret_df.index[-1], axis=0, inplace=True)

        #combine all the data for ols in one dataframe
        ols_df=pd.merge(fund_factors,ret_df,how='inner',left_on='JYYF',right_on='JYYF')
        ols_df['const']=1
        del fund_factors,ret_df,raw_factors

        #8 单只基金Alpha R_Square 散点图

        for num_factors in [6]:
            # pick 6 factors for each round of run as suggested by the research paper of haitong security
            summary_df,simulated_df,selected_factors=fun.calculate_alpha(ols_df, factors_list, num_factors,
                                                                         ret_col= 'Return',date_col='JYYF',
                                                                         bench_factor=index_list)

            plot.plotly_scatter(summary_df[['alpha','rsquar']],'因子组合Alpha_R_square散点图',fix_range=True)

            plot.plotly_line(simulated_df[['simulated_ret', 'real_ret', '日期']], '基金多因子模型拟合效果_因子：{0}'.format(selected_factors))
            # plot.plotly_scatter(simulated_df[['simulated_ret','real_ret']].sort_values('real_ret'), '基金多因子模型拟合效果')

    def prv_hld_analysis (self,prd_name,tablename,pic_list=None):

        ########################################Collecting data########################################
        config=self.config_pfa

        # initial the temp database class
        Pfdb = dben.PrvFunDB()

        # write fold files to DB
        # Pfdb.write2DB(table_name='prvfund',fold_dir="E:\私募主观\主观股多估值表基地",increment=0)

        # initial the class
        Jydb = dben.HBDB()

        # extra data from the temp database
        df1 = Pfdb.extract_from_db(prd_name=prd_name, columns='*', tablename=tablename)

        # get the unique date list and stock code list
        date_list = df1['Stamp_date'].dropna().unique()
        sec_code = df1['Stock_code'].dropna().unique()

        # extra industry data from the JY database
        df2 = Jydb.extract_industry(sec_code)

        # extra financial data from the JY database
        df3 = Jydb.extract_fin_info(sec_code,date_list)

        # extra benchmark data from the JY database
        df4 = Jydb.extract_benchmark(config.Index_type, sec_code=sec_code,date_list=date_list)

        fun = functionality.Untils(df1[['Code','Name','Weight','Stamp_date','Stock_code']], df2, df3, df4)

        asset_allocation_df = fun.asset_allocation_stats()

        ind_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'FIRSTINDUSTRYNAME'], method='sum',
                                   method_on='Weight')
        indutry_allocation_df_ranked = fun.rank_filter(ind_hld, [1, 3, 5])

        stk_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'Name'], method='sum',
                                   method_on='Weight')
        asset_allocation_df_ranked = fun.rank_filter(stk_hld, [3, 5, 10])

        fin_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'Name'], method='sum',
                                   method_on=['PE', 'PB', 'DIVIDENDRATIO'])
        ben_hld = fun.aggregate_by(fun.bench_info, groupby=['Stamp_date', 'Index_type'], method='sum',
                                   method_on='Weight')

        ########################################Drawing Pictures ########################################

        # drawing the pics ,initial the instant
        plot = functionality.Plot(fig_width=1200, fig_height=600)

        if(pic_list is None):

            self.asset_allocation_pic(plot,asset_allocation_df)
            self.industry_allocation_pic(plot,ind_hld)
            self.industry_centralization_pci(plot, indutry_allocation_df_ranked)
            self.stock_holding_pic(plot, stk_hld)
            self.stock_centralization_pic(plot, asset_allocation_df_ranked)
            self.valuation_pic(plot, fin_hld, stk_hld, date_list)
            self.hodling_in_benchmark(plot,ben_hld)
            self.alpha_rsquare_pic(plot, fun, df1, date_list, Jydb)

        else:
            pic_list=[x+'_pic' for x in pic_list]

            if('asset_allocation_pic' in pic_list):
                self.asset_allocation_pic(plot, asset_allocation_df)
            if ('industry_allocation_pic' in pic_list):
                self.industry_allocation_pic(plot,ind_hld)
            if ('industry_centralization_pci' in pic_list):
                self.industry_centralization_pci(plot, indutry_allocation_df_ranked)
            if ('stock_holding_pic' in pic_list):
                self.stock_holding_pic(plot, stk_hld)
            if ('stock_centralization_pic' in pic_list):
                self.stock_centralization_pic(plot, asset_allocation_df_ranked)
            if ('valuation_pic' in pic_list):
                self.valuation_pic(plot, fin_hld, stk_hld, date_list)
            if ('hodling_in_benchmark' in pic_list):
                self.hodling_in_benchmark(plot,ben_hld)
            if ('alpha_rsquare_pic' in pic_list):
                self.alpha_rsquare_pic(plot, fun, df1, date_list, Jydb)

    def prv_fof_analysis(self,fund_code):

        hbdb=dben.HBDB()

        sql = """ 
        select d.*,b.jzrq,b.jjjz,b.ljjz  
        from 
        (
        select a.jjdm,a.jjjc,a.cpfl,a.jjfl,c.mjjdm,c.lhbz,c.sfzz,c.fofjjdl,c.fofejfl,c.tzmb,c.tzfw,c.tzcl,c.tzbz,c.fxsytz 
        from st_hedge.t_st_jjxx a, st_hedge.t_st_sm_jjxx c 
        where a.jjdm=c.jjdm and a.jjdm='{0}'
        ) d left join st_hedge.t_st_jjjz b on d.jjdm=b.jjdm """.format(fund_code)

        hld_prv=hbdb.db2df(sql,db='highuser')

        sql="select jzdm,yxj,moddt_etl from st_hedge.t_st_sm_jjbjjz a where jjdm='{}' ".format(fund_code)
        benchmark_code=hbdb.db2df(sql,db='highuser')

        print('Done')

    def fund_alpha_analysis(self,fund_list):

        fun=functionality.Untils()
        ########################################Collecting data########################################
        hbdb=dben.HBDB()

        fund_score=[]

        for fund in fund_list:

            #read the holding info for the fund
            sql="select jjdm,jsrq,zqdm,zqmc,zjbl from st_fund.t_st_gm_gpzh where jjdm='{0}'".format(fund)
            fund_hld=hbdb.db2df(sql,db='funduser')

            #read the net value info for the fund
            sql="select jjdm,tjyf,hb1y from st_fund.t_st_gm_yhb where jjdm='{0}'".format(fund)
            ret_df=hbdb.db2df(sql,db='funduser')
            ret_df['hb1y']=ret_df['hb1y'] / 100
            ret_df['tjyf']=ret_df['tjyf'].astype(str)


            # read the factors information from hb database
            sec_code= fund_hld['zqdm'][~fund_hld['zqdm'].dropna().str.contains('H')].unique()
            date_list=fund_hld['jsrq'].unique()
            raw_factors = hbdb.extract_factors(sec_code, date_list)

            industry=False
            if(industry==True):
                #add the industry factors if necessary, i am not using the industry factors in the st_ashare.r_st_barra_style_factor
                #because it contains too many industries i am using the 中证指数行业分类2016版 which is less to reduce the computing burder

                sql = """
                select a.SecuCode,b.FirstIndustryName,b.XGRQ from HSJY_GG.SecuMain a 
                left join HSJY_GG.LC_ExgIndustry b on a.CompanyCode=b.CompanyCode  
                where Standard=28 and a.SecuCode in({0}) """.format("'"+"','".join(sec_code)+"'")
                industry_factors=hbdb.db2df(sql,db='readonly').sort_values('XGRQ').drop(['ROW_ID','XGRQ'],axis=1)
                industry_factors.drop_duplicates('SECUCODE',keep='last',inplace=True)

                # sql = """
                # select a.SecuCode,b.FirstIndustryName,b.UpdateTime from HSJY_GG.SecuMain a
                # left join HSJY_GP.LC_STIBExgIndustry b on a.CompanyCode=b.CompanyCode
                # where Standard=28 and a.SecuCode in({0}) """.format("'"+"','".join(sec_code)+"'")
                # industry_factors2=hbdb.db2df(sql,db='readonly').sort_values('UpdateTime').drop(['ROW_ID','UpdateTime'],axis=1)
                # industry_factors2.drop_duplicates('SECUCODE',keep='last',inplace=True)

                industry_factors=pd.concat([industry_factors,pd.get_dummies(industry_factors['FIRSTINDUSTRYNAME'])],axis=1).drop('FIRSTINDUSTRYNAME',axis=1)

                raw_factors=pd.merge(raw_factors,industry_factors,how='left',left_on='ticker',right_on=['SECUCODE']).drop('SECUCODE',axis=1)

            # calcualte the risk exposure for the fund as a whole
            fund_factors = fun.fund_risk_exposure(fund_hld,raw_factors,['jsrq','zqdm','zjbl'])

            jjfl=hbdb.db2df("select jjfl from st_fund.t_st_gm_flls where jjdm='{0}' ".format(fund),db='funduser')['jjfl'][0]
            jzdm_list=hbdb.db2df("select jzdm from st_hedge.t_st_sm_jjflbjjz where jjfl='{}' and jzdm not like 'H%%' ".format(jjfl),db='highuser')['jzdm']\
                .values.tolist()

            sql="select hb1y,zqdm,tjyf from st_market.t_st_zs_yhb  where zqdm in ({0}) ".format(','.join(jzdm_list+['000012']))
            benchmark_df=hbdb.db2df(sql,db='alluser')
            benchmark_df=benchmark_df[benchmark_df['hb1y']!=999]
            benchmark_df=benchmark_df.groupby(['zqdm', 'tjyf']).sum('hb1y').unstack().T
            benchmark_df['日期']=benchmark_df.index.get_level_values(1).astype(str)

            fund_factors=pd.merge(fund_factors,benchmark_df,how='inner',left_on='JYYF',right_on='日期').drop('日期',axis=1)

            factors_list=fund_factors.columns.drop(['JYYF']+jzdm_list).tolist()

            #standardlize the factors to be mean 1 std 1
            for col in factors_list:
                mean=fund_factors[col].mean()
                std=fund_factors[col].std()
                fund_factors[col]=fund_factors[col]/std+1-mean

            # combine all the data for ols in one dataframe
            ols_df = pd.merge(fund_factors, ret_df, how='inner', left_on='JYYF', right_on='tjyf')
            ols_df['const'] = 1
            del fund_factors, ret_df, raw_factors

            plot = functionality.Plot(fig_width=1200, fig_height=600)
            fund_name = \
            hbdb.db2df("select jjjc from st_fund.t_st_gm_jjxx where jjdm='{0}'".format(fund), db='funduser').values[0]
            try:
                for num_factors in [6]:
                    # pick 6 factors for each round of run as suggested by the research paper of haitong security
                    summary_df, simulated_df,selected_factors = fun.calculate_alpha(ols_df, factors_list, num_factors, ret_col='hb1y',
                                                                   date_col='JYYF',bench_factor=jzdm_list)

                    plot.plotly_markers(summary_df[['alpha', 'rsquar']].set_index('alpha'), '因子组合Alpha_R_square散点图_{0}'.format(fund_name), fix_range=True,
                                        x_text='',y_text='')

                    plot.plotly_line(simulated_df[['simulated_ret', 'real_ret', '日期']], '基金多因子模型拟合效果_{0}_因子：{1}'.format(fund_name,selected_factors))

                fund_score.append(pd.DataFrame(columns=['fund_name', 'alpha', 'T-value', 'Rsquare'],
                                               data=np.array(
                                                   [[fund_name[0]], [summary_df.sort_values('rsquar')['alpha'].iloc[-1]],
                                                    [abs(summary_df['alpha'].mean() / summary_df['alpha'].std())],
                                                    [summary_df.sort_values('rsquar')['rsquar'].iloc[-1]]]).T))
                print('the alpha is {0}, T value is {1} and the Rsquare is {2} for fund {3}'
                      .format(summary_df.sort_values('rsquar')['alpha'].iloc[-1],abs(summary_df['alpha'].mean()/summary_df['alpha'].std())
                              ,summary_df.sort_values('rsquar')['rsquar'].iloc[-1],fund_name))
            except Exception as e:
                print("error occure for {0}".format(fund_name))

        fund_score=pd.concat(fund_score,axis=0)
        from sklearn import preprocessing as pp
        fund_score['Rsquare']=1 / fund_score['Rsquare'].astype(float)
        for col in fund_score.columns.tolist()[1:]:
            fund_score[col]=pp.scale(fund_score[col])
        fund_score['final_socre']=fund_score['alpha']*0.25\
                                  +fund_score['T-value']*0.5+\
                                  fund_score['Rsquare']*0.25

        # fund_score.to_excel('alpha_得分.xlsx')

    def read_riskaversionfromdb(self,date):

        sql = "select risk_aversion from bl_risk_aversion where date='{0}'".format(date)
        risk_aversion=pd.read_sql(sql,con=dben.PrvFunDB().engine)
        return risk_aversion['risk_aversion'].values[0]

    def bl_model_data_preparation(self,end_date,version):


        from ..AAM.blmodel import  blmodel

        blm=blmodel.BL_Model()
        localdb_engine=dben.PrvFunDB().engine

        #get the assets from pool
        sql=" select * from bl_assets_pool where version='{0}' ".format(version)
        assets_df=pd.read_sql(sql, con=localdb_engine)
        index_assets=assets_df[assets_df['asset_type']=='index']['code'].values.tolist()
        public_funds = assets_df[assets_df['asset_type'] == 'public_fund']['code'].values.tolist()

        blm.bl_model_index_data_preparation(end_date=end_date,asset_list=index_assets,version=version)
        blm.bl_model_publicfund_data_preparation(end_date=end_date, asset_list=public_funds,version=version)

    def bl_model(self,end_date,asset_list,version,tau,ub,lb,asset_type,risk_aversion):

        from ..AAM.blmodel import blmodel

        blm = blmodel.BL_Model()
        engine = dben.PrvFunDB().engine

        # get the cov matrix from local database
        cov_matrix = blm.read_cov_fromdb(engine, asset_list, version, end_date,asset_type)

        # the cov matrix of average return is a shrink of the cov matrix of return itself
        cov_matrix = tau * cov_matrix.values

        # get prio_return from local db
        prio_return = blm.read_return_fromdb(asset_list, engine, version, end_date, 'bl_implied_return', 'implied_ret')

        # get the view_ret from local db
        view_ret = blm.read_return_fromdb(asset_list, engine, version, end_date, 'bl_view_return', 'view_ret')

        views = np.eye(len(asset_list))

        # calculate the view confidence if not read from database directlly
        view_confidence = np.dot(np.dot(views, cov_matrix), views.T) * np.eye(len(views))

        # set upper and lower bound

        constrains = blm.set_boundary(len(asset_list), lb, ub)

        opt_weight = blm.blm_solver(sigma=cov_matrix, mu=prio_return, P=views, Q=view_ret,
                                    Omega=view_confidence, delta=risk_aversion, constrains=constrains)

        opt_restul = pd.DataFrame()
        opt_restul['Asset'] = asset_list
        opt_restul['Weight'] = opt_weight

        return opt_restul

    def fund_classification(self):

        from ..Fund_classifier import classification
        fc = classification.Classifier_Ml()
        #fc.wind_risk_data2localdb(asofdate='2016-01-01')

        #
        # fc.wind_theme_data2localdb(asofdate='2016-01-01')
        #
        #fc.wind_stock_style_data2localdb(asofdate='2016-01-01')
        #
        # fc.model_generation_style()
        #
        # fc.model_generation_theme()
        #
        fc.model_generation_style(value_style='hld')

        fc.model_generation_theme(value_style='hld')
        #
        # fc.model_generation_risk_level()

        # #['2021-12-31','2021-09-30','2021-06-30','2021-03-31','2020-12-31',
        #                  '2020-09-30','2020-06-30','2020-03-31']
        #

        for asofdate in ['2021-12-31','2021-09-30','2021-06-30','2021-03-31','2020-12-31',
                         '2020-09-30','2020-06-30','2020-03-31']:
            fc=classification.Classifier_Ml(asofdate=asofdate)
            #fc.classify()
            fc.classify_hldbase()
            print("{0} done ".format(asofdate))

    def style_distribution(self,plot,table,style_list,clbz='全部'):

        map_dict=dict(zip(['R1','R2','R3','R4','R5','D1','D2','D3','D4','D5'],['低风险','较低风险','中风险','较高风险','高风险','低回撤','较低回撤','中回撤','较高回撤','高回撤',]))

        if(clbz=='全部'):
            sql="select * from {0}".format(table)
        else:
            sql = "select * from {1} where clbz='{0}'".format(clbz,table)

        test = pd.read_sql(sql, con=dben.PrvFunDB().engine)
        date_list=test['style_updated_date'].unique().tolist()

        for col in style_list:

            sql="select distinct {0} from {1} ".format(col,table)
            unique_items= pd.read_sql(sql, con=dben.PrvFunDB().engine)[col].tolist()
            unique_items.remove('')
            plot_df = pd.DataFrame()
            plot_df['items'] = unique_items
            for date in date_list:
                tempdf=test[test['style_updated_date']==date].groupby(col).count()
                tempdf['items']=tempdf.index
                plot_df=pd.merge(plot_df,tempdf[['items','jjdm']],how='left',on='items').fillna(0)
                plot_df.rename(columns={'jjdm':date},inplace=True)
                plot_df[date]=plot_df[date]/plot_df[date].sum(axis=0)*100
            plot_df.sort_values('items',inplace=True)
            if(col=='risk_level' or col=='draw_back_level'):
                plot_df['items']=[map_dict[x] for x in plot_df['items']]
            plot_df.set_index('items',drop=True,inplace=True)
            plot.plotly_style_bar(plot_df.T,'{}分布'.format(col))

    def fund_classification_advance(self):
        from ..Fund_classifier import classification
        #fc=classification.Classifier()
        #fc.classify_threshold(20)
        fc2=classification.Classifier_brinson()
        fc2.classify_socring()

    def brinson_score_pic(self,jjdm):

        sql="select * from brinson_score where jjdm='{}'".format(jjdm)
        scoredf=pd.read_sql(sql,con=dben.PrvFunDB().engine)
        plot=functionality.Plot(fig_width=1000,fig_height=600)

        new_name=['jjdm','交易能力_短期','交易能力_长期','行业配置能力_短期',
                  '行业配置能力_长期','选股能力_短期','选股能力_长期','大类资产配置能力_短期',
                  '大类资产配置能力_长期','asofdate']
        scoredf.columns=new_name
        col=['交易能力_短期','交易能力_长期','行业配置能力_短期',
                  '行业配置能力_长期','选股能力_短期','选股能力_长期','大类资产配置能力_短期',
                  '大类资产配置能力_长期']

        plot.ploty_polar(scoredf[col],'Brinson能力图')

    def fund_classification_barra(self):

        from ..Fund_classifier import classification
        fc=classification.Classifier_barra()
        fc.data_preparation()
        # for jjdm in ['000362','005821','009636','001487']:
        #     fc.classify(jjdm=jjdm,start_date='20181231',end_date='20211231')

    def mutual_fund_concept(self,asofdate):

        engine=dben.PrvFunDB().engine

        q3df = pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\重仓持股(汇总).xlsx")[
            ['代码', '名称', '持股总量(万股)', '季报持仓变动(万股)', '持股市值占基金净值比(%)']]
        target_list = q3df['代码'].fillna('0').tolist()
        q3df.fillna(0)
        q3df = q3df[q3df['持股总量(万股)'] > 0]

        sql = "select * from stock_concept where 证券代码 in ({0})".format("'" + "','".join(target_list) + "'")
        conceptdf = pd.read_sql(sql, con=engine).fillna('')

        df = pd.merge(q3df, conceptdf, how='inner', left_on='代码', right_on='证券代码')
        concept_listdf = pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\概念分类.xlsx")
        concept_class = concept_listdf.columns
        csv_df = pd.DataFrame()
        for cls in concept_class:
            con_weight = []
            con_change = []
            con_total = []
            outputdf = pd.DataFrame()
            concept_list = concept_listdf[concept_listdf[cls].notnull()][cls].astype(str)
            for concept in concept_list:
                try:
                    df[concept] = df['所属概念板块[交易日期] 最新收盘日'].str.contains(concept).astype(int)
                    df[concept + '_w'] = df[concept] * df['持股市值占基金净值比(%)']
                    df[concept + '_n'] = df[concept] * df['季报持仓变动(万股)']
                    df[concept + '_t'] = df[concept] * df['持股总量(万股)']
                    con_weight.append(df[concept + '_w'].sum(axis=0))
                    con_change.append(df[concept + '_n'].sum(axis=0))
                    con_total.append(df[concept + '_t'].sum(axis=0))
                except Exception:
                    print(concept)
                    concept_list.remove(concept)
                    continue

            outputdf[cls] = concept_list
            outputdf['持仓权重(%)_' + cls] = con_weight
            outputdf['季报持仓变动(万股)'] = con_change
            outputdf['持股总量(万股)'] = con_total

            outputdf['上季度持股总量(万股)'] = outputdf['持股总量(万股)'] - outputdf['季报持仓变动(万股)']
            outputdf['持股变动%_' + cls] = outputdf['季报持仓变动(万股)'].fillna(0) / outputdf['上季度持股总量(万股)'] * 100
            outputdf.loc[outputdf['持股变动%_' + cls]==np.inf,'持股变动%_' + cls]='新增'
            outputdf.drop(['上季度持股总量(万股)', '季报持仓变动(万股)', '持股总量(万股)'], axis=1, inplace=True)
            outputdf.sort_values(['持仓权重(%)_' + cls, '持股变动%_' + cls], inplace=True, ascending=False)
            outputdf = outputdf[outputdf['持仓权重(%)_' + cls] > 0].reset_index(drop=True)
            csv_df = pd.concat([csv_df, outputdf], axis=1)

        csv_df['asofdate'] = asofdate
        #check if data already exist
        sql='select distinct asofdate from mutual_fund_highlighthld_concept'
        asofdatelist=pd.read_sql(sql,con=engine)['asofdate']
        if(asofdate in asofdatelist):
            sql="delete from mutual_fund_highlighthld_concept where asofdate='{0}'".format(asofdate)
            engine.execute(sql)
        csv_df.to_sql('mutual_fund_highlighthld_concept', con=engine,index=False,if_exists='append')
        print('The concept distribution data has been inserted into tbale mutual_fund_highlighthld_concept')

    def mutual_fund_summary_20220115(self,date):

        outputdf=pd.DataFrame()

        theme_map={'大金融' : ['银行','券商','房地产','保险','非银金融'],
                   '消费' : ['美容护理','家用电器','酒类','制药','医疗保健','生物科技','商业服务','零售','纺织服装','食品','农业','家居用品','餐饮旅游','软饮料','医药生物','商业贸易','商贸零售','食品饮料','农林牧渔','休闲服务','纺织服饰'],
                   'TMT' : ['半导体','电子元器件','电脑硬件','软件','互联网','文化传媒','电子','计算机','传媒','通信'],
                   '周期': ['采掘','有色金属','化工原料','基本金属','贵金属','钢铁','化纤','建筑','煤炭','化肥农药','石油天然气','日用化工','建材','石油化工','石油石化','化工','基础化工','黑色金属'],
                   '制造' : ['精细化工','建筑材料','工业机械','电工电网','电力','发电设备','汽车零部件','航天军工','能源设备','航空','环保','汽车','通信设备','海运','工程机械','国防军工','电力设备','电气设备','机械设备','建筑装饰','公用事业','环保','交通运输','制造','社会服务','轻工制造'],
                   }

        hld_summary=pd.read_excel(r"E:\基金分类\重仓持股(汇总){}.xlsx".format(date))[
            ['代码', '名称', '持股市值占基金净值比(%)']]

        style_ind=pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\股票风格行业.xlsx")
        sql="select * from juchao_style where record_date='20220126'"
        style_juchao=pd.read_sql(sql,con=dben.PrvFunDB().engine)
        style_juchao['所属规模风格类型']=[x+'型' for x in style_juchao['所属规模风格类型']]
        style_ind=pd.merge(style_ind,style_juchao[['证券简称','所属规模风格类型']],how='left',on='证券简称')
        style_ind.loc[style_ind['所属规模风格类型_y'].notnull(),'所属规模风格类型_x']\
            =style_ind.loc[style_ind['所属规模风格类型_y'].notnull()]['所属规模风格类型_y']
        style_ind.drop('所属规模风格类型_y',axis=1,inplace=True)
        style_ind.rename(columns={'所属规模风格类型_x':'所属规模风格类型'},inplace=True)

        theme_list=['新能源','碳科技','芯片','锂电池','光伏','新基建','白酒']
        theme_w=[]
        for theme in theme_list:
            tempdf=pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\{}.xls".format(theme))
            tempdf=pd.merge(tempdf,hld_summary,how='left',left_on='证券代码',right_on='代码')
            theme_w.append(tempdf['持股市值占基金净值比(%)'].sum())

        outputdf['主题']=theme_list
        outputdf['持仓权重(%)_主题']=theme_w

        style_ind['宽基']=''
        index_list=['沪深300','中证500','中证1000']
        for ind in index_list:
            style_ind.loc[style_ind[ind]=='是','宽基']=ind

        style_ind['宽基2'] = ''
        index_list = ['上证50']
        for ind in index_list:
            style_ind.loc[style_ind[ind] == '是', '宽基2'] = ind


        style_ind.drop(index_list,axis=1,inplace=True)
        style_ind['大类行业']=''
        for big_ind in theme_map.keys():
            style_ind.loc[[x in theme_map[big_ind] for x in style_ind['申万行业']],'大类行业']=big_ind

        style_ind=pd.merge(hld_summary,style_ind,how='left',left_on='代码',right_on='证券代码')

        for col in ['所属规模风格类型','申万行业','宽基','宽基2','大类行业']:

            tempdf=style_ind.groupby(col).sum()
            tempdf.reset_index(drop=False,inplace=True)
            tempdf.rename(columns={'持股市值占基金净值比(%)':"持仓权重(%)_{}".format(col)},inplace=True)
            tempdf.drop(tempdf[tempdf[col] == ''].index, axis=0, inplace=True)
            outputdf=pd.concat([outputdf,tempdf],axis=1)

        outputdf.to_csv('持仓汇总_{}.csv'.format(date),index=False,encoding='gbk')
        print('Done')

    def mutual_fund_concept_heatmap(self,fig_width,fig_height,asofdate):

        plot = functionality.Plot(fig_width=fig_width, fig_height=fig_height)

        sql="select * from mutual_fund_highlighthld_concept where asofdate='{}'"\
            .format(asofdate)
        raw_df=pd.read_sql(sql,con=dben.PrvFunDB().engine)

        col_list=list(set([x.split('_')[-1] for x in  raw_df.columns]))
        item_list=list(set([x.split('_')[0] for x in  raw_df.columns]))
        item_list=list(set(item_list).difference(set(col_list)))
        item_list.sort()
        col_list.remove('asofdate')
        col_list.sort()

        f = lambda x: '%.4f%%' % x

        for col in col_list:
            new_list=[x+'_'+col for x in item_list]
            tempdf = raw_df[raw_df[col].notnull()][[col] + new_list]
            if(len(tempdf)>=9):
                width=3
            elif(len(tempdf)>=4):
                width=2
            tempdf=tempdf.iloc[0:width*width]
            tempdf.sort_values(new_list[0], ascending=False,inplace=True)
            z=tempdf[new_list[0]].astype(float).values.reshape(width,width)
            z_per=tempdf[new_list[0]].astype(float).apply(f).values.reshape(width,width)
            z_text=tempdf[col].values.reshape(width,width)
            z_text=z_text + '： ' +z_per
            plot.ploty_heatmap(z, z_text, col+"_权重")

            tempdf.sort_values(new_list[1], ascending=False,inplace=True)
            z=tempdf[new_list[1]].astype(float).values.reshape(width,width)
            z_per = tempdf[new_list[1]].astype(float).apply(f).values.reshape(width, width)
            z_text=tempdf[col].values.reshape(width,width)
            z_text=z_text + '： ' + z_per
            plot.ploty_heatmap(z,z_text,col+"_增长率")

    def mutual_industry_allocation_analysis(self):

        df1=pd.read_excel(r"E:\基金分类\历次持仓汇总.xlsx")[['代码', '名称', '持股市值占基金净值比(%)','报告期']]
        df1=df1[df1['报告期']>='2010q1']

        hbdb=dben.HBDB()
        sql="select a.zqdm,b.yjxymc,b.xxfbrq from st_ashare.t_st_ag_zqzb a left join st_ashare.t_st_ag_gshyhfb b on a.gsdm=b.gsdm where  b.xyhfbz={0} and a.zqlb=1 "\
            .format(24)
        ind_map=hbdb.db2df(sql,db='alluser')
        ind_map.reset_index(drop=True,inplace=True)
        ind_map.sort_values(['zqdm','xxfbrq'],inplace=True)
        temp=ind_map['zqdm']
        temp.drop_duplicates(keep='last', inplace=True)
        ind_map = ind_map.loc[temp.index][['zqdm', 'yjxymc']]

        df1['zqdm'] = [x[0:6] for x in df1['代码']]
        df1=pd.merge(df1,ind_map,how='left',on='zqdm')
        df1.drop('zqdm',axis=1,inplace=True)
        df1.rename(columns={'yjxymc': '所属行业'}, inplace=True)

        df2=pd.DataFrame()
        for year in range(2010,2021):
            temp1=pd.read_excel(r"E:\基金分类\{0}Q1重仓持股(汇总).xlsx".format(year))
            temp1.columns = temp1.iloc[0]
            temp1=temp1.iloc[1:-2][['代码', '名称', '持股市值占基金净值比(%)']]
            temp1['zqdm']=[x[0:6] for x in temp1['代码']]
            temp1['报告期']=str(year)+'q1'
            temp1=pd.merge(temp1,ind_map,how='left',on='zqdm')
            temp1.rename(columns={'yjxymc':'所属行业'},inplace=True)
            temp1.drop('zqdm',axis=1,inplace=True)

            temp2 = pd.read_excel(r"E:\基金分类\{0}Q3重仓持股(汇总).xlsx".format(year))
            temp2.columns = temp2.iloc[0]
            temp2=temp2.iloc[1:-2][['代码', '名称', '持股市值占基金净值比(%)']]
            temp2['zqdm'] = [x[0:6] for x in temp2['代码']]
            temp2['报告期']=str(year)+'q3'
            temp2=pd.merge(temp2,ind_map,how='left',on='zqdm')
            temp2.rename(columns={'yjxymc':'所属行业'},inplace=True)
            temp2.drop('zqdm', axis=1, inplace=True)

            df2=pd.concat([df2,temp1],axis=0)
            df2 = pd.concat([df2, temp2], axis=0)


        df=pd.concat([df1,df2],axis=0)
        del df1,df2,temp1,temp2
        df=df.sort_values(['报告期', '所属行业'], ascending=False)
        df['hk']=[x.split('.')[1] for x in df['代码']]
        #remove hk stock
        df=df[df['hk']!='HK']
        df1=df.groupby(['所属行业','报告期']).sum()['持股市值占基金净值比(%)']
        df2 = df.groupby(['报告期']).sum()['持股市值占基金净值比(%)']
        df=pd.merge(df1,df2,how='left',left_index=True,right_index=True)
        df['行业占比%'] = df['持股市值占基金净值比(%)_x'] / df['持股市值占基金净值比(%)_y'] * 100
        df = df.sort_index(level=[0, 1])

        inddf=pd.read_excel(r"E:\基金分类\行业统计.xlsx")
        inddf=inddf.iloc[0:-2]
        inddf['日期']=[str(x)[0:10].replace("-","") for x in inddf['日期'] ]
        inddf['月']=[x[4:6] for x in inddf['日期']]
        inddf['年'] = [x[0:4] for x in inddf['日期']]
        inddf.loc[inddf['月']=='03','月']='q1'
        inddf.loc[inddf['月'] == '06', '月'] = 'q2'
        inddf.loc[inddf['月'] == '09', '月'] = 'q3'
        inddf.loc[inddf['月'] == '12', '月'] = 'q4'
        inddf['日期']=inddf['年']+inddf['月']
        inddf=inddf[inddf['日期'].str.contains('q')]
        # inddf.set_index('日期',drop=True,inplace=True)


        zszcol=['总市值(合计)采掘', '总市值(合计)化工', '总市值(合计)钢铁', '总市值(合计)有色金属',
       '总市值(合计)建筑材料', '总市值(合计)建筑装饰', '总市值(合计)电气设备', '总市值(合计)机械设备',
       '总市值(合计)国防军工', '总市值(合计)汽车', '总市值(合计)家用电器', '总市值(合计)纺织服装', '总市值(合计)轻工制造',
       '总市值(合计)商业贸易', '总市值(合计)农林牧渔', '总市值(合计)食品饮料', '总市值(合计)休闲服务',
       '总市值(合计)医药生物', '总市值(合计)公用事业', '总市值(合计)交通运输', '总市值(合计)房地产', '总市值(合计)电子',
       '总市值(合计)计算机', '总市值(合计)传媒', '总市值(合计)通信', '总市值(合计)银行', '总市值(合计)非银金融',
       '总市值(合计)综合']
        pecol=['市盈率(TTM,算术平均)采掘', '市盈率(TTM,算术平均)化工', '市盈率(TTM,算术平均)钢铁',
       '市盈率(TTM,算术平均)有色金属', '市盈率(TTM,算术平均)建筑材料', '市盈率(TTM,算术平均)建筑装饰',
       '市盈率(TTM,算术平均)电气设备', '市盈率(TTM,算术平均)机械设备', '市盈率(TTM,算术平均)国防军工',
       '市盈率(TTM,算术平均)汽车', '市盈率(TTM,算术平均)家用电器', '市盈率(TTM,算术平均)纺织服装',
       '市盈率(TTM,算术平均)轻工制造', '市盈率(TTM,算术平均)商业贸易', '市盈率(TTM,算术平均)农林牧渔',
       '市盈率(TTM,算术平均)食品饮料', '市盈率(TTM,算术平均)休闲服务', '市盈率(TTM,算术平均)医药生物',
       '市盈率(TTM,算术平均)公用事业', '市盈率(TTM,算术平均)交通运输', '市盈率(TTM,算术平均)房地产',
       '市盈率(TTM,算术平均)电子', '市盈率(TTM,算术平均)计算机', '市盈率(TTM,算术平均)传媒',
       '市盈率(TTM,算术平均)通信', '市盈率(TTM,算术平均)银行', '市盈率(TTM,算术平均)非银金融',
       '市盈率(TTM,算术平均)综合']
        pbcol=['市净率(算术平均)采掘', '市净率(算术平均)化工', '市净率(算术平均)钢铁',
       '市净率(算术平均)有色金属', '市净率(算术平均)建筑材料', '市净率(算术平均)建筑装饰', '市净率(算术平均)电气设备',
       '市净率(算术平均)机械设备', '市净率(算术平均)国防军工', '市净率(算术平均)汽车', '市净率(算术平均)家用电器',
       '市净率(算术平均)纺织服装', '市净率(算术平均)轻工制造', '市净率(算术平均)商业贸易', '市净率(算术平均)农林牧渔',
       '市净率(算术平均)食品饮料', '市净率(算术平均)休闲服务', '市净率(算术平均)医药生物', '市净率(算术平均)公用事业',
       '市净率(算术平均)交通运输', '市净率(算术平均)房地产', '市净率(算术平均)电子', '市净率(算术平均)计算机',
       '市净率(算术平均)传媒', '市净率(算术平均)通信', '市净率(算术平均)银行', '市净率(算术平均)非银金融',
       '市净率(算术平均)综合']

        item_name_list=['mkt_w%','pe','pb']
        col_lists=[zszcol,pecol,pbcol]

        for i in range(3):
            col_list=col_lists[i]
            item_name=item_name_list[i]
            temp=inddf[['日期']+col_list]
            values=[]
            name=[]
            date=[]
            if(item_name=='mkt_w%'):
                for i in range(len(temp)):
                    values+=(temp.iloc[i][col_list]/temp.iloc[i][col_list].sum()*100).values.tolist()
                    name+=col_list
                    date+=[temp.iloc[i]['日期']]*len(col_list)
            else:
                for i in range(len(temp)):
                    values+=temp.iloc[i][col_list].values.tolist()
                    name+=col_list
                    date+=[temp.iloc[i]['日期']]*len(col_list)

            tempdf=pd.DataFrame()
            tempdf[item_name]=values
            tempdf['所属行业']=[x.split(')')[1] for x in name]
            tempdf['报告期']=date
            tempdf = tempdf.sort_values(['报告期', '所属行业'], ascending=False)
            tempdf=tempdf.groupby(['所属行业','报告期']).sum()
            tempdf=tempdf.sort_index(level=[0,1])
            df=pd.merge(df,tempdf,how='left',left_index=True,right_index=True)


        df.rename(columns={'持股市值占基金净值比(%)_x':'持股市值占基金净值比(%)',
                           '持股市值占基金净值比(%)_y':'全行业持股市值占基金净值比(%)',
                           'mkt_w%':'全市场占比%','行业占比%':'公募重仓占比%'},inplace=True)

        df['配置系数'] = df['公募重仓占比%'] / df['全市场占比%']
        df.loc[df['配置系数']==np.inf,'配置系数']=np.nan
        df.loc[df['pe'] == 0, 'pe'] = np.nan
        df.loc[df['pb'] == 0, 'pb'] = np.nan
        df.loc[df['全市场占比%'] == 0, '全市场占比%'] = np.nan

        quant_df=pd.DataFrame()
        for indus in df.index.get_level_values(0).unique():
            tempdf=df.loc[indus][['配置系数','公募重仓占比%','pe','pb']].rank()
            tempdf=tempdf/len(tempdf)
            tempdf['所属行业']=indus
            tempdf.reset_index(inplace=True)
            quant_df=pd.concat([quant_df,tempdf],axis=0)

        quant_df=quant_df.groupby(['所属行业', '报告期']).sum()
        for col in quant_df.columns:
            quant_df.rename(columns={col:col+"_分位数"},inplace=True)
        df=pd.merge(df,quant_df,how='left',right_index=True,left_index=True)
        df.to_csv('mutual_fund_change.csv',encoding='gbk')

        return df

    @staticmethod
    def pool_return_comparision():
        # # #read pool data from local file
        quant_pool_in = pd.read_excel(r"E:\GitFolder\基金池数据\量化基金池202304.xlsx"
                                      , sheet_name='量化池列表')[['入池时间', '基金代码','超一级/一级策略', '二级策略','子池','代表产品']]
        quant_pool_out = pd.read_excel(r"E:\GitFolder\基金池数据\量化基金池202304.xlsx"
                                       , sheet_name='出池记录')[['入池时间', '基金代码', '出池时间','超一级/一级策略', '二级策略','子池','代表产品']]
        quant_pool = pd.concat([quant_pool_out, quant_pool_in], axis=0)
        quant_pool[(~quant_pool['二级策略'].str.contains('美元'))]
        quant_pool = quant_pool[(quant_pool['二级策略'].isin(['500指数增强','300指数增强','1000指数增强','量化多头']))&(quant_pool['子池']!='代销')]
        quant_pool['入池时间'] = quant_pool['入池时间'].astype(str).str.replace('-', '').str[0:6]
        quant_pool['出池时间'] = quant_pool['出池时间'].astype(str).str.replace('-', '').str[0:6]
        quant_pool.drop_duplicates('基金代码', inplace=True)

        prv_pool_in = pd.read_excel(r"C:\Users\xuhuai.zhe\Documents\WXWork\1688858146292774\Cache\File\2023-06\私募股多池202305.xlsx"
                                    , sheet_name='主观池列表')[['入池时间', '基金代码', '一级策略','子池']]
        prv_pool_out = pd.read_excel(r"C:\Users\xuhuai.zhe\Documents\WXWork\1688858146292774\Cache\File\2023-06\私募股多池202305.xlsx"
                                     , sheet_name='一般推荐(出池)')[['入池时间', '基金代码', '出池时间', '一级策略','子池']]
        prv_pool_out = prv_pool_out[(prv_pool_out['入池时间'].notnull()) &
                                    (prv_pool_out['出池时间'].notnull())]

        prv_pool = pd.concat([prv_pool_out, prv_pool_in], axis=0).sort_values('入池时间')
        prv_pool = prv_pool[ (prv_pool['一级策略']=='股票型')&(prv_pool['子池'].str.contains('FOF'))]
        prv_pool['入池时间'] = prv_pool['入池时间'].astype(str).str.replace('-', '').str[0:6]
        prv_pool['出池时间'] = prv_pool['出池时间'].astype(str).str.replace('-', '').str[0:6]
        prv_pool.drop_duplicates('基金代码', inplace=True)

        mutual_stock_in = pd.read_excel(r"E:\GitFolder\基金池数据\公募非债核心池202304.xlsx"
                                        , sheet_name='核心池-主动股多')[['调入时间', '基金代码']]
        mutual_stock_out = pd.read_excel(r"E:\GitFolder\基金池数据\公募非债核心池202304.xlsx"
                                         , sheet_name='出池')[['调入时间', '基金代码', '调出时间']]
        mutual_stock_pool = pd.concat([mutual_stock_out, mutual_stock_in], axis=0)
        mutual_stock_pool['调入时间'] = mutual_stock_pool['调入时间'].astype(str).str.replace('-', '').str[0:6]
        mutual_stock_pool['调出时间'] = mutual_stock_pool['调出时间'].astype(str).str.replace('-', '').str[0:6]
        mutual_stock_pool['基金代码'] = mutual_stock_pool['基金代码'].str[0:6]
        mutual_stock_pool.drop_duplicates('基金代码', inplace=True)

        mutual_bond_in = pd.read_excel(r"E:\GitFolder\基金池数据\债券基金池-公&私202304.xlsx"
                                       , sheet_name='1.公募')[['入池时间', '基金代码']]
        mutual_bond_out = pd.read_excel(r"E:\GitFolder\基金池数据\债券基金池-公&私202304.xlsx"
                                        , sheet_name='3.公募债基出池记录')[['入池时间', '基金代码', '出池时间']]
        mutual_bond_pool = pd.concat([mutual_bond_out, mutual_bond_in], axis=0)
        mutual_bond_pool['入池时间'] = mutual_bond_pool['入池时间'].astype(str).str.replace('-', '').str[0:6]
        mutual_bond_pool['出池时间'] = mutual_bond_pool['出池时间'].astype(str).str.replace('-', '').str[0:6]
        mutual_bond_pool['基金代码'] = mutual_bond_pool['基金代码'].str[0:6]
        mutual_bond_pool.drop_duplicates('基金代码', inplace=True)

        prv_bond_in = pd.read_excel(r"E:\GitFolder\基金池数据\债券基金池-公&私202304.xlsx"
                                    , sheet_name='2.私募')[['入池时间', '基金代码']]
        prv_bond_out = pd.read_excel(r"E:\GitFolder\基金池数据\债券基金池-公&私202304.xlsx"
                                     , sheet_name='4.私募债基出池记录')[['入池时间', '基金代码', '出池时间']]
        prv_bond_pool = pd.concat([prv_bond_out, prv_bond_in], axis=0)
        prv_bond_pool['入池时间'] = prv_bond_pool['入池时间'].astype(str).str.replace('-', '').str[0:6]
        prv_bond_pool['出池时间'] = prv_bond_pool['出池时间'].astype(str).str.replace('-', '').str[0:6]
        prv_bond_pool['基金代码'] = prv_bond_pool['基金代码'].str[0:6]
        prv_bond_pool.drop_duplicates('基金代码', inplace=True)

        sql = "select jjdm,hb1y,tjyf from st_hedge.t_st_sm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202305' and hb1y!=99999" \
            .format(util.list_sql_condition(prv_pool['基金代码'].tolist()))
        prv_pool_nav = hbdb.db2df(sql, db='highuser')
        prv_pool_nav = pd.merge(prv_pool_nav, prv_pool, how='left'
                                , left_on='jjdm', right_on='基金代码')
        # prv_pool_nav=(prv_pool_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        prv_pool_nav = prv_pool_nav[(prv_pool_nav['入池时间'] < prv_pool_nav['tjyf'])
                                        & (prv_pool_nav['出池时间'] >= prv_pool_nav['tjyf'])]
        prv_pool_nav = prv_pool_nav.groupby(['tjyf']).mean()['hb1y'] / 100
        prv_pool_nav = (prv_pool_nav + 1).cumprod()

        # #
        sql = "select jjdm,hb1y,tjyf from st_hedge.t_st_sm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202305' and hb1y!=99999" \
            .format(util.list_sql_condition(quant_pool['基金代码'].tolist()))
        quant_pool_nav = hbdb.db2df(sql, db='highuser')
        quant_pool_nav = pd.merge(quant_pool_nav, quant_pool, how='left'
                                  , left_on='jjdm', right_on='基金代码')
        # quant_pool_nav = (quant_pool_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        quant_pool_nav = quant_pool_nav[(quant_pool_nav['入池时间'] < quant_pool_nav['tjyf'])
                                        & (quant_pool_nav['出池时间'] >= quant_pool_nav['tjyf'])]
        quant_pool_nav = quant_pool_nav.groupby(['tjyf']).mean()['hb1y'] / 100
        quant_pool_nav = (quant_pool_nav + 1).cumprod()

        sql = "select jjdm,hb1y,tjyf from st_fund.t_st_gm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202304' and hb1y!=99999" \
            .format(util.list_sql_condition(mutual_stock_pool['基金代码'].tolist()))
        mutual_pool_nav = hbdb.db2df(sql, db='funduser')
        mutual_pool_nav = pd.merge(mutual_pool_nav, mutual_stock_pool, how='left'
                                   , left_on='jjdm', right_on='基金代码')
        mutual_pool_nav['tjyf'] = mutual_pool_nav['tjyf'].astype(str)
        #mutual_pool_nav = (mutual_pool_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        mutual_pool_nav = mutual_pool_nav[(mutual_pool_nav['调入时间'] < mutual_pool_nav['tjyf'])
                                          & (mutual_pool_nav['调出时间'] >= mutual_pool_nav['tjyf'])]
        mutual_pool_nav = mutual_pool_nav.groupby(['tjyf']).mean()['hb1y'] / 100
        mutual_pool_nav = (mutual_pool_nav + 1).cumprod()

        sql = "select jjdm,hb1y,tjyf from st_hedge.t_st_sm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202304' and hb1y!=99999" \
            .format(util.list_sql_condition(prv_bond_pool['基金代码'].tolist()))
        prv_bond_nav = hbdb.db2df(sql, db='highuser')
        prv_bond_nav = pd.merge(prv_bond_nav, prv_bond_pool, how='left'
                                , left_on='jjdm', right_on='基金代码')
        #prv_bond_nav = (prv_bond_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        prv_bond_nav = prv_bond_nav[(prv_bond_nav['入池时间'] < prv_bond_nav['tjyf'])
                                    & (prv_bond_nav['出池时间'] >= prv_bond_nav['tjyf'])]
        prv_bond_nav = prv_bond_nav.groupby('tjyf').mean()['hb1y'] / 100
        prv_bond_nav = (prv_bond_nav + 1).cumprod()

        sql = "select jjdm,hb1y,tjyf from st_fund.t_st_gm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202304' and hb1y!=99999" \
            .format(util.list_sql_condition(mutual_bond_pool['基金代码'].tolist()))
        mutual_bond_nav = hbdb.db2df(sql, db='funduser')
        mutual_bond_nav = pd.merge(mutual_bond_nav, mutual_bond_pool, how='left'
                                   , left_on='jjdm', right_on='基金代码')
        mutual_bond_nav['tjyf'] = mutual_bond_nav['tjyf'].astype(str)
        #mutual_bond_nav = (mutual_bond_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        mutual_bond_nav = mutual_bond_nav[(mutual_bond_nav['入池时间'] < mutual_bond_nav['tjyf'])
                                          & (mutual_bond_nav['出池时间'] >= mutual_bond_nav['tjyf'])]
        mutual_bond_nav = mutual_bond_nav.groupby('tjyf').mean()['hb1y'] / 100
        mutual_bond_nav = (mutual_bond_nav + 1).cumprod()
        plot_name=['私募股多','量化500指增','私募债券']
        i=0
        for df in [prv_pool_nav,quant_pool_nav,prv_bond_nav]:

            summary=pd.concat([df.iloc[-1] / df.iloc[-13] - 1
                , df.iloc[-1] / df.iloc[-25] - 1
                , df.iloc[-1] - 1
                , df.iloc[-1] / df.iloc[-13] - 1
                , df.iloc[-13] / df.iloc[-25] - 1
                , df.iloc[11] - 1],axis=1)
            summary.columns=['近一年', '近两年', '近三年'
                , str(df.index[-1]) + "-" + str(df.index[-13])
                , str(df.index[-13]) + "-" + str(df.index[-25])
                , str(df.index[11]) + "-" + '202204']

            name_map=hbdb.db2df("select jjdm,jjjc from st_hedge.t_st_jjxx where jjdm in ({})".format(util.list_sql_condition(df.columns.tolist()))
                                ,db='highuser')
            name_map=dict(zip(name_map['jjdm'].tolist(),name_map['jjjc'].tolist()))
            summary.index=[name_map[x] for x in summary.index]

            plot = functionality.Plot(1200, 600)
            plot.plotly_markers(summary.T,plot_name[i])
            summary.T.to_excel(str(plot_name[i])+'.xlsx')
            i+=1


        plot_name=['公募偏股','公募债券']
        i=0
        for df in [mutual_pool_nav,mutual_bond_nav]:

            summary=pd.concat([df.iloc[-1] / df.iloc[-13] - 1
                , df.iloc[-1] / df.iloc[-25] - 1
                , df.iloc[-1] - 1
                , df.iloc[-1] / df.iloc[-13] - 1
                , df.iloc[-13] / df.iloc[-25] - 1
                , df.iloc[11] - 1],axis=1)
            summary.columns=['近一年', '近两年', '近三年'
                , str(df.index[-1]) + "-" + str(df.index[-13])
                , str(df.index[-13]) + "-" + str(df.index[-25])
                , str(df.index[11]) + "-" + '202204']

            name_map=hbdb.db2df("select jjdm,jjjc from st_fund.t_st_gm_jjxx where jjdm in ({})".format(util.list_sql_condition(df.columns.tolist()))
                                ,db='funduser')
            name_map=dict(zip(name_map['jjdm'].tolist(),name_map['jjjc'].tolist()))
            summary.index=[name_map[x] for x in summary.index]

            plot = functionality.Plot(1200, 600)
            plot.plotly_markers(summary.T,plot_name[i])
            summary.T.to_excel(str(plot_name[i]) + '.xlsx')
            i+=1


        summary = pd.DataFrame(index=['近一年', '近两年', '近三年'
            , str(prv_pool_nav.index[-1]) + "-" + str(prv_pool_nav.index[-13])
            , str(prv_pool_nav.index[-13]) + "-" + str(prv_pool_nav.index[-25])
            , str(prv_pool_nav.index[11]) + "-" + '202204'],
                               columns=['私募股多', '量化', '公募偏股', '私募债券', '公募债券'])
        summary['私募股多'] = [prv_pool_nav.iloc[-1] / prv_pool_nav.iloc[-13] - 1
            , prv_pool_nav.iloc[-1] / prv_pool_nav.iloc[-25] - 1
            , prv_pool_nav.iloc[-1] - 1
            , prv_pool_nav.iloc[-1] / prv_pool_nav.iloc[-13] - 1
            , prv_pool_nav.iloc[-13] / prv_pool_nav.iloc[-25] - 1
            , prv_pool_nav.iloc[11] - 1]

        summary['量化'] = [quant_pool_nav.iloc[-1] / quant_pool_nav.iloc[-13] - 1
            , quant_pool_nav.iloc[-1] / quant_pool_nav.iloc[-25] - 1
            , quant_pool_nav.iloc[-1] - 1
            , quant_pool_nav.iloc[-1] / quant_pool_nav.iloc[-13] - 1
            , quant_pool_nav.iloc[-13] / quant_pool_nav.iloc[-25] - 1
            , quant_pool_nav.iloc[11] - 1]

        summary['公募偏股'] = [mutual_pool_nav.iloc[-1] / mutual_pool_nav.iloc[-13] - 1
            , mutual_pool_nav.iloc[-1] / mutual_pool_nav.iloc[-25] - 1
            , mutual_pool_nav.iloc[-1] - 1
            , mutual_pool_nav.iloc[-1] / mutual_pool_nav.iloc[-13] - 1
            , mutual_pool_nav.iloc[-13] / mutual_pool_nav.iloc[-25] - 1
            , mutual_pool_nav.iloc[11] - 1]

        summary['私募债券'] = [prv_bond_nav.iloc[-1] / prv_bond_nav.iloc[-13] - 1
            , prv_bond_nav.iloc[-1] / prv_bond_nav.iloc[-25] - 1
            , prv_bond_nav.iloc[-1] - 1
            , prv_bond_nav.iloc[-1] / prv_bond_nav.iloc[-13] - 1
            , prv_bond_nav.iloc[-13] / prv_bond_nav.iloc[-25] - 1
            , prv_bond_nav.iloc[11] - 1]

        summary['公募债券'] = [mutual_bond_nav.iloc[-1] / mutual_bond_nav.iloc[-13] - 1
            , mutual_bond_nav.iloc[-1] / mutual_bond_nav.iloc[-25] - 1
            , mutual_bond_nav.iloc[-1] - 1
            , mutual_bond_nav.iloc[-1] / mutual_bond_nav.iloc[-13] - 1
            , mutual_bond_nav.iloc[-13] / mutual_bond_nav.iloc[-25] - 1
            , mutual_bond_nav.iloc[11] - 1]
        summary.to_excel('pool_summary.xlsx')
        plot = functionality.Plot(1200, 600)
        # plot.plotly_markers(summary.iloc[0:3], '基金池累计收益')
        # plot.plotly_markers(summary.iloc[3:], '基金池区间收益')
        # cols = summary.columns.tolist()
        # a = int(np.floor(len(cols) / 3))
        # b = len(cols) % 3
        #
        # color_list = plot.ams_color_lista[0:a + int(b >= 1)] + \
        #              plot.ams_color_listb[0:a + int(b == 2)] + \
        #              plot.ams_color_listc[0:a]
        # count = 0
        # for col in cols:
        #     plot.plotly_markers(summary.iloc[0:3][[col]], col, color=color_list[count])
        #     plot.plotly_markers(summary.iloc[3:][[col]], col, color=color_list[count])
        #     count += 1

    @staticmethod
    def bmk_index_adjust():

        sql = "select zsdm,jyrq,jjsl,hb1z,spjg from st_hedge.t_st_sm_zhmzs where zsdm in ('HB0011','HB1002','HB1001','HB0018','HB0015','HB0017') and hb1z!=99999 and jyrq>='20131201'"
        prv_ret = hbdb.db2df(sql, db='highuser').pivot_table('hb1z', 'jyrq', 'zsdm').fillna(0)


        # cta=pd.read_excel(r"E:\GitFolder\hbshare\fe\XZ\whigh_0.5 _vol_20191223_20230424.xlsx")
        # cta['t_date']=[str(x).replace('-','')[0:8] for x in cta['时间']]
        # cta.set_index('t_date',inplace=True)
        # cta=cta.pct_change()*100
        # prv_ret = pd.merge(prv_ret, cta[['1_0.5_26']]*100, how='left'
        #                    , left_index=True, right_index=True).fillna(0)
        # prv_ret['HB0018']=prv_ret['1_0.5_26']
        # prv_ret.drop('1_0.5_26',inplace=True,axis=1)

        prv_ret.loc['20131206'] = [1, 1, 1, 1,1,1]


        index_list=prv_ret.index.to_list()
        prv_ret['week_count']=[index_list.index(x) for x in prv_ret.index]
        prv_ret['week_count']=prv_ret['week_count'] % 13
        fee_rule = pd.DataFrame(index=['HB0011', 'HB0015', 'HB0017', 'HB0018', 'HB1001', 'HB1002'], data=[0.88, 0.8, 0.8, 0.8,0.88,0.8],
                                columns=['p_rule'])
        fee_rule['n_rule'] = [1, 1, 1, 1,1,1.2]
        for i in  range(1,len(prv_ret)):

            jyrq=prv_ret.index[i]
            last_week=prv_ret.index[i-1]
            count = prv_ret.loc[jyrq]['week_count']

            prv_ret.loc[jyrq] = ((prv_ret.loc[jyrq][['HB0011', 'HB0015', 'HB0017', 'HB0018', 'HB1001', 'HB1002']] / 100 + 1) *
                                 prv_ret.loc[last_week][
                                     ['HB0011', 'HB0015', 'HB0017', 'HB0018', 'HB1001', 'HB1002']]).tolist() + [count]

            if (count==0):
                last_3month = prv_ret.index[i - 13]
                for code in ['HB0011', 'HB0015', 'HB0017', 'HB0018', 'HB1001', 'HB1002']:
                    q_ret = prv_ret.loc[jyrq][code] / prv_ret.loc[last_3month][code] - 1
                    if (q_ret > 0):
                        prv_ret.loc[jyrq, code] = prv_ret.loc[last_3month][code] * (
                                    1 + q_ret * fee_rule.loc[code]['p_rule'])
                    elif (q_ret < 0):
                        prv_ret.loc[jyrq, code] = prv_ret.loc[last_3month][code] * (
                                1 + q_ret * fee_rule.loc[code]['n_rule'])
        prv_ret.to_excel('调整后净值.xlsx')
        print('')

    @staticmethod
    def bmk_ret_summary():

        adjusted_bmk=pd.read_excel(r"E:\GitFolder\hbshare\fe\XZ\调整后净值.xlsx")
        FOF_date=\
            pd.read_excel(r"C:\Users\xuhuai.zhe\Documents\WXWork\1688858146292774\Cache\File\2023-06\新方程FOF-list.xlsx").set_index('基金代码')


        sql="select jyrq,spjg from st_market.t_st_zs_hq where jyrq in ({}) and zqdm='H11001'"\
            .format(util.list_sql_condition(adjusted_bmk['jyrq'].astype(str).tolist()))
        bond_ind=hbdb.db2df(sql,db='alluser')
        bond_ind['spjg'] = bond_ind['spjg'] / bond_ind['spjg'].iloc[0]
        adjusted_bmk=pd.merge(adjusted_bmk,bond_ind,on='jyrq',how='left')


        index_list=['HB0011', 'HB0015', 'HB0017', 'HB0018', 'HB1001', 'HB1002','spjg']
        jjdm_list=FOF_date.index.tolist()
        clyl_mat=pd.DataFrame(index=jjdm_list,columns=index_list)


        for jjdm in jjdm_list:

            start_date=FOF_date.loc[jjdm]['成立日期']
            adjusted_bmk['day_laps']=\
                [abs((datetime.datetime.strptime(str(x), '%Y%m%d')-datetime.datetime.strptime(str(start_date), '%Y%m%d')).days) for x in adjusted_bmk['jyrq']]

            adjusted_bmk[adjusted_bmk['day_laps'] == adjusted_bmk['day_laps'].min()].iloc[-1][index_list]

            clyl_mat.loc[jjdm] = adjusted_bmk.iloc[-1][index_list] / (
                adjusted_bmk[adjusted_bmk['day_laps'] == adjusted_bmk['day_laps'].min()].iloc[-1][index_list]) - 1

        clyl_mat.to_excel('基准成立以来.xlsx')

    @staticmethod
    def save_financial_left2db():

        data = pd.read_excel(
            r"C:\Users\xuhuai.zhe\Documents\WeChat Files\wxid_xvk2piiub53y12\FileStorage\File\2023-07\左右侧.xlsx")
        data['datetime'] = data['datetime'].astype(str).str.replace('-', '')
        data = pd.melt(data, id_vars=['datetime'], var_name='jjdm', value_name='基本面左右侧标签').rename(
            columns={'datetime': 'asofdate'})
        data[data['asofdate'] >= '20100101'].to_sql('financial_left_ticker', con=localdb, if_exists='append',
                                                    index=False)

    @staticmethod
    def save_stock_price_data2localfile():

        for i in range(10):

            start_date=str(2023-i)+'0101'
            end_date = str(2024 - i) + '0101'
            sql="""
            select SYMBOL as ZQDM,TDATE as JYRQ,TCLOSE as SPJG from finchina.CHDQUOTE where TDATE>={0} and TDATE<={1} and TCLOSE!=99999 and TCLOSE!=0
             """.format(start_date,end_date)
            stock_price=hbdb.db2df(sql,db='readonly')
            stock_price.to_pickle('stock_pirce_data'+"_"+start_date)
            print('date {} done'.format(start_date))

    @staticmethod
    def calculate_style_transform_mat():

        sql = "SELECT jjdm,`基金简称`,`风格偏好`,asofdate from jjpic_value_p_hbs"
        value = pd.read_sql(sql, con=localdb)
        sql = "SELECT jjdm,`规模偏好`,asofdate from jjpic_size_p_hbs"
        size = pd.read_sql(sql, con=localdb)
        data = pd.merge(value, size, how='inner', on=['jjdm', 'asofdate'])
        data['风格标签'] = data['规模偏好'] + data['风格偏好']
        date_list = data['asofdate'].unique().tolist()
        date_list.sort()
        transform_mat = pd.DataFrame(columns=['stats']).set_index('stats')
        for i in range(1, len(date_list)):
            d1 = date_list[i - 1]
            d2 = date_list[i]
            temp = data[data['asofdate'].isin([d1, d2])]
            temp_size = temp.pivot('jjdm', 'asofdate', '规模偏好')
            temp_value = temp.pivot('jjdm', 'asofdate', '风格偏好')
            temp_style = temp.pivot('jjdm', 'asofdate', '风格标签')

            temp_list = []

            for df in [temp_size, temp_value, temp_style]:
                df['stats'] = df[d1] + "->" + df[d2]
                temp_list.append(df.groupby('stats').count()[d1].to_frame(d2))

            transform_mat = pd.merge(transform_mat, pd.concat(temp_list, axis=0), how='outer', on='stats')

        transform_mat.reset_index(drop=False).drop_duplicates('stats').to_excel('风格转移矩阵.xlsx')

    @staticmethod
    def file_read(filename):
        """
        使用 pickle 读取文件
        """
        import pickle
        try:
            fid = open(filename, 'rb')
        except FileNotFoundError:
            print(filename + ' 文件不存在，请检查文件名是否正确')
            return None

        data = pickle.load(fid)
        fid.close()
        return data

    @staticmethod
    def get_industry_style():

        data=pd.read_excel(r"C:\Users\xuhuai.zhe\Downloads\行业成长.xlsx")
        import  sklearn.preprocessing as pp
        for col in ['营业收入(同比增长率)','净利润(同比增长率)']:
            max=data[col].quantile(0.1)
            min=data[col].quantile(0.9)
            data.loc[data[col]>=max,col]=max
            data.loc[data[col] <= min, col] = min

        data[['营业收入(同比增长率)', '净利润(同比增长率)', 'ROE', 'PCF', 'PE ', '股息率',
        'PB']] =pp.scale(data[['营业收入(同比增长率)', '净利润(同比增长率)', 'ROE', 'PCF', 'PE ', '股息率',
        'PB']])
        data['成长'] = data[['营业收入(同比增长率)', '净利润(同比增长率)', 'ROE']].mean(axis=1)
        data['价值'] = data[['PCF', 'PE ', '股息率',
                     'PB']].mean(axis=1)
        data['成长rank'] = data.rank(ascending=False)['成长']
        data['价值rank'] = data.rank(ascending=False)['价值']
        data['成长-价值'] = data['成长'] - data['价值']
        data['score']=data['成长-价值'].rank() / len(data)

    @staticmethod
    def funds_hk_holding_ratio_calculation(jjdm_list,asofdate):

        data=[]
        unit=int(np.ceil(len(jjdm_list)/800))
        for i in range(unit):

            sql = "select InnerCode ,SecurityCode from hsjy_gg.MF_FundArchives where SecurityCode in {} "\
                .format(tuple(jjdm_list[800*i:800*(1+i)]))
            innercode_list = \
                hbdb.db2df(sql, db='readonly').drop_duplicates('SECURITYCODE')

            sql = "SELECT innercode,enddate,RINOfHKConnect FROM ac_hsjyjj.t_ac_hsjy_jj_mf_assetallocationall " \
                  "WHERE innercode in {0} and enddate='{1}' and reporttype in (5,6)"\
                .format(tuple(innercode_list['INNERCODE'].to_list()),asofdate)

            data.append(pd.merge(hbdb.db2df(sql, db='acuser').fillna(0),innercode_list,
                                 how='left',left_on='innercode',right_on='INNERCODE'))

        data=pd.concat(data,axis=0)

        return data[['RINOfHKConnect','SECURITYCODE']]

    @staticmethod
    def get_xfc_fof_return_sumarry(date,date2,dir):

        fofdm_list=pd.read_excel(dir)['基金代码'].tolist()

        sql="select jjdm,jjjz from st_hedge.t_st_jjjz where jjdm in {0} and jzrq='{1}'"\
            .format(tuple(fofdm_list),date)
        jjjz=hbdb.db2df(sql,db='highuser')

        sql="select jjdm,zbnp,zblb,jzrq from st_hedge.t_st_sm_rqjhb where jjdm in {0} and jzrq='{1}' and zblb in ('2101','2103','2106','2998') and zbnp!=99999"\
            .format(tuple(fofdm_list),date)
        ret1=hbdb.db2df(sql,db='highuser').pivot_table('zbnp','jjdm','zblb')

        sql="select jjdm,hb1n,tjnf from st_hedge.t_st_sm_nhb where jjdm in {0}  and tjnf in ('2020','2021','2022') and hb1n<=10000".format(tuple(fofdm_list))
        year_ret=hbdb.db2df(sql,db='highuser').pivot_table('hb1n','jjdm','tjnf')


        sql="select jjdm,zbnp as 成立以来年化收益率,jzrq from st_hedge.t_st_sm_rqjnhhb  where jjdm in {0} and jzrq='{1}' and zblb ='2999' and zbnp!=99999"\
            .format(tuple(fofdm_list),date)
        ret2 = hbdb.db2df(sql, db='highuser')

        sql="select jjdm,zbnp as 成立以来最大回测,jzrq from st_hedge.t_st_sm_qjzdhc  where jjdm in {0} and jzrq='{1}' and zblb ='2999' and zbnp!=99999"\
            .format(tuple(fofdm_list),date)
        max_draw = hbdb.db2df(sql, db='highuser')

        # date2=util.str_date_shift(date,3,'+')

        sql="select jjdm,zbnp as 成立以来年化波动率,tjrq as jzrq from st_hedge.t_st_sm_zqjbdl  where jjdm in {0} and tjrq='{1}' and zblb ='2999' and zbnp!=99999"\
            .format(tuple(fofdm_list),date2)
        std = hbdb.db2df(sql, db='highuser')

        sql="select jjdm,zbnp as 成立以来年化夏普,tjrq as jzrq  from st_hedge.t_st_sm_zqjxpbl  where jjdm in {0} and tjrq='{1}' and zblb ='2999' and zbnp!=99999"\
            .format(tuple(fofdm_list),date2)
        sharp = hbdb.db2df(sql, db='highuser')


        output=jjjz.copy()
        for df in [ret1,year_ret,ret2,max_draw,std,sharp]:
            output=pd.merge(output,df,how='left',on='jjdm')

        pd.merge(pd.read_excel(dir),output,how='left',left_on='基金代码',right_on='jjdm').to_excel('新方程FOF业绩.xlsx')

class Industry_track:

    @staticmethod
    def industry_rotation_test(pool_size=5):

        data1 = pd.read_excel(r"E:\学习资料\行业研究\行业跟踪\行业轮动指示器.xlsx", sheet_name='Sheet2')
        data2 = pd.read_excel(r"E:\学习资料\行业研究\行业跟踪\行业轮动指示器.xlsx", sheet_name='Sheet3')
        data1.reset_index(drop=False, inplace=True)
        data2.reset_index(drop=False, inplace=True)
        data1['index'] = data1['index'] + 1

        col_list = data1.columns.tolist()[2:]
        col_list.remove('801230.SI')

        data1 = pd.merge(data1, data2, how='left', on='index')

        result = data1[['index', '日期_y']].copy()
        result['bmk_ret'] = data1[[x + '_y' for x in col_list]].mean(axis=1)
        ic = []

        for i in data1['index'].tolist():
            factor = data1.loc[i - 1][[x + '_x' for x in col_list]].to_frame('factor')
            factor['ret'] = data1.loc[i - 1][[x + '_y' for x in col_list]].values.tolist()
            ic.append(factor.rank().corr()['ret'].iloc[0])

            result.loc[i - 1, 'port_ret'] = \
                data1.loc[i - 1][[x[0:10] + 'y' for x in
                                  (data1.loc[i - 1][[x + '_x' for x in col_list]].to_frame('port_ret')).sort_values(
                                      'port_ret')[-pool_size:].index]].mean()


        print('ic is {0} and ir is {1} '.format(np.mean(ic[0:-2]), np.mean(ic[0:-2]) / np.std(ic[0:-2])))
        print("port annually return is {}".format(
            np.power((result['port_ret'] / 100 + 1).cumprod().iloc[86], 1 / (87 / 36)) - 1))
        print("bmk annually return is {} ".format(
            np.power((result['bmk_ret'] / 100 + 1).cumprod().iloc[86], 1 / (87 / 36)) - 1))
        print('winning pro is {}'.format((result['port_ret']>result['bmk_ret']).sum()/(result['port_ret'].notnull()).sum()))

    @staticmethod
    def update_elec_car_data(latest_date=str(datetime.datetime.today())[0:10]):

        from WindPy import w
        w.start()
        #宏观数据
        macro_data=\
            w.edb("M0012939,M0001384,M0001385,M5650805,M0000612,M0001227,M0039354,M0012989",
                  "2015-12-01", latest_date,"Fill=Previous",usedf=True)[1].reset_index(drop=False).iloc[-88:]
        macro_data.columns=\
            ['日期','总人口','M2','M2:同比','城镇调查失业率','CPI:当月同比','PPI:全部工业品:当月同比','GDP:不变价:当季同比','城镇居民人均可支配收入:累计同比']


        #汽车数据
        car_data=w.edb("S0105523,S0105710,S0105526,S0105711,S6139215,S6139212,S6131302,S6131314,S6100156,S6136813", "2015-12-01",
              latest_date, "Fill=Previous;Period=M",usedf=True)[1].reset_index(drop=False).iloc[-88:]
        car_data.columns=\
            ['日期','产量:汽车:当月值','销量:汽车:当月值','产量:乘用车:当月值','销量:乘用车:当月值','产量:新能源汽车:当月值','销量:新能源汽车:当月值','产量:新能源乘用车:当月值','销量:新能源乘用车:当月值','保有量:机动车:汽车','保有量:新能源汽车']


        #电池数据
        battery_data=\
            w.edb("C4115560,P6334924,J3277829,S6136713,M6422131,S6137439,S6137442,S6137438,S6137468",
                  "2015-12-01", latest_date,"Fill=Previous;Period=M",usedf=True)[1].reset_index(drop=False).iloc[-83:]
        battery_data.columns=\
            ['日期','销量:动力电池:磷酸铁锂:当月值','销量:动力电池:合计:当月值','销量:动力电池:三元材料:当月值','产量:新能源汽车:燃料电池:当月值','产量:太阳能电池(光伏电池):当月值','产量:动力电池:磷酸铁锂:当月值','产量:动力电池:合计:当月值','产量:动力电池:三元材料:当月值','装车量:动力电池:合计:当月值']

        # #有色数据
        metal_data=w.edb("S5801794,Q3709948,Z4436784,S0029771,S6949763", "2015-12-01",
                         latest_date,"Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False).iloc[-132:]
        metal_data.columns=['日期','中国:价格:铝合金:A356:国产','中国:出口平均单价:无衬背精炼铜箔,厚≤0.15mm(74101100):当月值',
                            '中国:进口平均单价:无衬背精炼铜箔,厚≤0.15mm(74101100):当月值','现货结算价:LME镍','安科泰:电池级碳酸锂平均价']

        # 汽车品牌数据
        car_data_by_brand=w.edb(
            "S0105876,S0105874,S0105863,S0105861,S0105868,S0105865,S0105870,S0105862,F0115834,C8884813,D1383397,H0102187,O5155240,P1489161,F5984846,L1728724,K7069600,Y7877017,Q3128968",
            "2015-12-01", latest_date, "Fill=Previous;Period=M",usedf=True)[1].reset_index(drop=False).iloc[-89:]
        car_data_by_brand.columns=\
            ['日期','比亚迪汽车','长城汽车','上汽集团','第一汽车集团','广汽集团','长安汽车集团','奇瑞汽车','东风汽车集团','小鹏汽车','江淮汽车','几何汽车','岚图汽车','东风汽车',
             '合众汽车','吉利汽车','零跑汽车','江铃汽车','蔚来','理想']


        elec=w.wsd("801730.SI", "yoy_or,yoynetprofit",
              "2015-12-01", latest_date, "Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False).iloc[-90:]

        elec.columns=['日期','营收增速','归母增速']

        car=w.wsd("801880.SI", "yoy_or,yoynetprofit",
              "2015-12-01", latest_date, "Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False).iloc[-90:]

        car.columns=['日期','营收增速','归母增速']

        metal=w.wsd("801050.SI", "yoy_or,yoynetprofit",
              "2015-12-01", latest_date, "Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False).iloc[-90:]

        metal.columns=['日期','营收增速','归母增速']


        w.stop()

        import xlwings as xw

        filename = r"E:\学习资料\行业研究\行业跟踪\新能源汽车.xlsx"
        app = xw.App(visible=False)
        wb = app.books.open(filename)

        ws = wb.sheets['宏观数据']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =macro_data.iloc[-86:]
        print('{} done'.format('宏观数据'))

        ws = wb.sheets['汽车数据']
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =car_data.iloc[-88:]
        print('{} done'.format('汽车数据'))

        ws = wb.sheets['电池数据']
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =battery_data.iloc[-83:]
        print('{} done'.format('电池数据'))

        ws = wb.sheets['汽车品牌数据']
        ws["A2"].options(pd.DataFrame, header=1, index=False, expand='table').value =car_data_by_brand.iloc[-89:]
        print('{} done'.format('汽车品牌数据'))

        ws = wb.sheets['有色数据']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =metal_data.iloc[-132:]
        print('{} done'.format('汽车品牌数据'))

        ws = wb.sheets['财务数据']
        ws["AB2"].options(pd.DataFrame, header=1, index=False, expand='table').value =elec[['营收增速','归母增速']].iloc[-90:]
        ws["AD2"].options(pd.DataFrame, header=1, index=False, expand='table').value =car[['营收增速','归母增速']].iloc[-90:]
        ws["AF2"].options(pd.DataFrame, header=1, index=False, expand='table').value =metal[['营收增速','归母增速']].iloc[-90:]
        print('{} done'.format('财务数据'))

        wb.save(filename)
        wb.close()
        app.quit()
        print('all done ')

    @staticmethod
    def update_metal_data(latest_date=str(datetime.datetime.today())[0:10]):

        from WindPy import w
        w.start()
        #价格与库存
        price_storage_data=\
            w.edb("S0029751,S0029752,S0029756,S0029755,S0029760,S0029759,S0029772,S0029771", "2015-12-01",
                  latest_date,"Fill=Previous;Period=W",usedf=True)[1].reset_index(drop=False).iloc[-386:]
        price_storage_data.columns=\
            ['日期','现货结算价:LME铜','总库存:LME铜','总库存:LME铝','现货结算价:LME铝','总库存:LME锌','现货结算价:LME锌','总库存:LME镍','现货结算价:LME镍']

        #上游需求
        demand=\
            w.edb("S2707396,S2707395,S0105711,S0105526,S0116282,S0116252,S0106273,S0106267,S0066451,S5712463",
                  "2015-12-01", latest_date,"Fill=Previous;Period=M",usedf=True)[1].reset_index(drop=False).iloc[-89:]
        demand.columns=['日期','30大中城市:商品房成交面积:当月值:','30大中城市:商品房成交套数:当月值:','销量:乘用车:当月值','产量:乘用车:当月值',
                                    '出口数量:铝合金:当月值','进口数量:铝合金:当月值','出口数量:未锻轧铝及铝材:当月值','进口数量:未锻轧铝及铝材:当月值','销售量:重点企业:镀锌板(带):累计值',
                                    '产量:重点优特钢企业:钢材:不锈钢:累计值']


        #指数财务数据
        index_fin_data=w.wsd("801050.SI", "close,pe_ttm,pb_lf,roe_avg,grossprofitmargin,netprofitmargin,yoy_or,yoynetprofit",
              "2015-12-01", latest_date, "Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False).iloc[-91:]

        index_fin_data.columns=['日期','收盘价','PETTM','PB','ROE','毛利率','净利率','营收增速','归母增速']

        w.stop()



        import xlwings as xw

        filename = r"E:\学习资料\行业研究\行业跟踪\有色金属.xlsx"
        app = xw.App(visible=False)
        wb = app.books.open(filename)

        ws = wb.sheets['价格与库存']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =price_storage_data
        print('{} done'.format('价格与库存'))

        ws = wb.sheets['上游需求']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =demand.iloc[-89:]
        print('{} done'.format('上游需求'))

        ws = wb.sheets['财务数据']
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =index_fin_data
        print('{} done'.format('财务数据'))

        wb.save(filename)
        wb.close()
        app.quit()
        print('all done ')

    @staticmethod
    def update_housing_data(start_date='2015-12-01',latest_date=str(datetime.datetime.today())[0:10]):

        from WindPy import w
        w.start()
        w.isconnected()
        #房地产供需
        demand_supply_data=\
            w.edb("X1054318,S2733019,S2733021,O2818154,S2733004,S2733006,R2770284,S2733025,S2733027,S0029674,S2707368,S2707372,S0049582,M5716876,M5716877",
                  start_date, latest_date,"Fill=Previous",usedf=True)[1].reset_index(drop=False)

        demand_supply_data.columns=['日期','成交土地规划建筑面积:住宅类用地:住宅用地','100大中城市:成交土地规划建筑面积:住宅类用地:一线城市','100大中城市:成交土地规划建筑面积:住宅类用地:三线城市',
                                    '供应土地占地面积:住宅类用地:住宅用地','100大中城市:供应土地占地面积:住宅类用地:一线城市','100大中城市:供应土地占地面积:住宅类用地:三线城市',
                                    '成交土地楼面均价:住宅类用地','100大中城市:成交土地楼面均价:住宅类用地:一线城市','100大中城市:成交土地楼面均价:住宅类用地:三线城市','商品房待售面积:住宅:累计值',
                                    '十大城市:商品房可售面积:一线城市','十大城市:商品房可售面积:二线城市','房屋新开工面积:住宅：累计值','出生人数','死亡人数']

        demand_supply_data.loc[demand_supply_data['100大中城市:成交土地规划建筑面积:住宅类用地:一线城市']==0,'100大中城市:成交土地规划建筑面积:住宅类用地:一线城市']=None
        demand_supply_data['100大中城市:成交土地规划建筑面积:住宅类用地:一线城市']=\
            util.cubic_interpolation(demand_supply_data['100大中城市:成交土地规划建筑面积:住宅类用地:一线城市'])

        demand_supply_data['全国土地供需比_MA12']= \
            (demand_supply_data['供应土地占地面积:住宅类用地:住宅用地']/demand_supply_data['成交土地规划建筑面积:住宅类用地:住宅用地']).rolling(12).mean()
        demand_supply_data['一线城市土地供需比_MA12']=\
            (demand_supply_data['100大中城市:供应土地占地面积:住宅类用地:一线城市']/demand_supply_data['100大中城市:成交土地规划建筑面积:住宅类用地:一线城市']).rolling(12).mean()
        demand_supply_data['三线城市土地供需比_MA12']=\
            (demand_supply_data['100大中城市:供应土地占地面积:住宅类用地:三线城市']/demand_supply_data['100大中城市:成交土地规划建筑面积:住宅类用地:三线城市']).rolling(12).mean()

        #房地产产业数据
        industry_data=\
            w.edb("S0073306,S0073294,S0073301,S0049593,S2707398,S2707400,S2707402,S2707411,S2707413,S2707415,S2707425,S2707427,S2707429",
                  start_date, latest_date,"Fill=Previous",usedf=True)[1].reset_index(drop=False)
        industry_data.columns=['日期','房屋施工面积:住宅:累计同比','房屋新开工面积:住宅:累计同比','商品房销售面积:住宅:累计同比','商品房销售额:住宅:累计同比','30大中城市:商品房成交面积:一线城市:当月值','30大中城市:商品房成交面积:二线城市:当月值','30大中城市:商品房成交面积:三线城市:当月值','70个大中城市新建商品住宅价格指数:当月同比','70个大中城市新建商品住宅价格指数:一线城市:当月同比','70个大中城市新建商品住宅价格指数:三线城市:当月同比','70个大中城市二手住宅价格指数:当月同比','70个大中城市二手住宅价格指数:一线城市:当月同比','70个大中城市二手住宅价格指数:三线城市:当月同比']


        #房地产金融数据
        financial_data=\
            w.edb("S0073245,B3036123,S0073254,S0073253,M0009976,M0057875,S0000020,S0000021,M5201579,M0043818,M0331299,M0043820",
                  start_date,latest_date,"Fill=Previous;Period=M",usedf=True)[1].reset_index(drop=False)
        financial_data.columns=['日期','房地产开发资金来源:国内贷款:累计同比','房地产开发资金来源:本年实际到位资金合计:累计同比','房地产开发资金来源:其他资金:个人按揭贷款:累计同比','房地产开发资金来源:其他资金:定金及预收款:累计同比','中国:金融机构:新增人民币贷款:居民户:当月值','中国:金融机构:新增人民币贷款:居民户:中长期:当月值','中国:个人住房贷款余额','中国:个人住房贷款余额:同比增长','中国:金融机构:人民币:新增贷款:房地产贷款:累计值','中国:中长期贷款利率:5年以上(月)','中国:贷款市场报价利率(LPR):5年','中国:个人住房公积金贷款利率:5年以上(月)']


        #指数财务数据
        index_fin_data=w.wsd("801180.SI", "close,pe_ttm,pb_lf,roe_avg,grossprofitmargin,netprofitmargin,yoy_or,yoynetprofit",
              start_date, latest_date, "Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False)

        index_fin_data.columns=['日期','收盘价','PETTM','PB','ROE','毛利率','净利率','营收增速','归母增速']

        w.stop()

        import xlwings as xw

        filename = r"E:\学习资料\行业研究\行业跟踪\房地产.xlsx"
        app = xw.App(visible=False)
        wb = app.books.open(filename)

        ws = wb.sheets['房地产供需']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =demand_supply_data.iloc[-127:]
        print('{} done'.format('房地产供需'))

        ws = wb.sheets['房地产数据']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =industry_data.iloc[-127:]
        print('{} done'.format('房地产数据'))

        ws = wb.sheets['房地产金融']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =financial_data.iloc[-174:]
        print('{} done'.format('房地产金融'))


        ws = wb.sheets['指数数据']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =index_fin_data.iloc[-127:]
        print('{} done'.format('指数数据'))

        wb.save(filename)
        wb.close()
        app.quit()
        print('all done ')

    @staticmethod
    def update_power_generation_data(latest_date=str(datetime.datetime.today())[0:10]):

        from WindPy import w
        w.start()
        w.isconnected()
        #煤炭产量用量与价格
        material_data=\
            w.edb("S5134471,S5101450,S5101712,S5120065,S5103920,S5103913,S0069682",
                  "2015-12-01", latest_date,"Fill=Previous",usedf=True)[1].reset_index(drop=False)

        material_data.columns=['日期','年度长协价:CCTD秦皇岛动力煤(Q5500)','宁波港:库提价(含税):动力煤(Q5500):中国产',
                                    '纽卡斯尔NEWC动力煤现货价','中国:产量:动力煤:当月值','中国:重点电厂煤耗总量:本日当月累计','中国:重点电厂煤炭库存量:总计','NYMEX 天然气 期货收盘价']


        #电力产量用量与价格
        elec_price=\
            w.edb("S5100021,S5100122,S5100023,S5100024,S5100025,S5100124,S5100125,S5100126,S5100026,S5100127,S0027012,S0027013,S0161530,S5151651,S5151652,S5151650,"
                  "S0059935,S0059938,S0059939,S0059941,S0253363,S0253261,S0253293,S0253380", "2015-12-01", latest_date,"Fill=Previous;Period=M",usedf=True)[1].reset_index(drop=False)

        elec_price.columns=['日期','中国:全社会用电量:当月值','中国:全社会用电量:当月同比','中国:全社会用电量:第一产业:当月值','中国:全社会用电量:第二产业:当月值','中国:全社会用电量:第三产业:当月值',
                               '中国:全社会用电量:第一产业:当月同比','中国:全社会用电量:第二产业:当月同比','中国:全社会用电量:第三产业:当月同比','中国:城乡居民生活用电量:当月值',
                               '中国:城乡居民生活用电量:当月同比','中国:产量:发电量:当月值','中国:产量:发电量:当月同比','中国:发电量:风电:当月值','中国:发电量:火电:当月值','中国:发电量:核电:当月值',
                               '中国:发电量:水电:当月值','中国:平均上网电价','中国:平均上网电价:风电','中国:平均上网电价:核电','中国:平均上网电价:水电','中国:平均上网电价:太阳能','中国:平均上网电价:燃煤',
                               '中国:平均上网电价:燃气','中国:平均上网电价:生物质']


        #指数财务数据
        index_fin_data=w.wsd("801160.SI", "close,pe_ttm,pb_lf,roe_avg,grossprofitmargin,netprofitmargin,yoy_or,yoynetprofit",
              "2015-12-01", latest_date, "Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False)

        index_fin_data.columns=['日期','收盘价','PETTM','PB','ROE','毛利率','净利率','营收增速','归母增速']

        w.stop()

        import xlwings as xw

        filename = r"E:\学习资料\行业研究\行业跟踪\公共事业.xlsx"
        app = xw.App(visible=False)
        wb = app.books.open(filename)

        ws = wb.sheets['煤炭产量用量与价格']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =material_data.iloc[-2060:]
        print('{} done'.format('煤炭产量用量与价格'))

        ws = wb.sheets['电力产量用量与价格']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =elec_price.iloc[-89:]
        print('{} done'.format('电力产量用量与价格'))


        ws = wb.sheets['指数数据']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =index_fin_data.iloc[-91:]
        print('{} done'.format('指数数据'))

        wb.save(filename)
        wb.close()
        app.quit()
        print('all done ')

    @staticmethod
    def update_power_resource_data(latest_date=str(datetime.datetime.today())[0:10]):

        from WindPy import w
        w.start()
        w.isconnected()


        #指数财务数据 ,.SI
        df1=w.wsd("801950.SI", "close,pe_ttm,pb_lf,roe_avg,grossprofitmargin,netprofitmargin,yoy_or,yoynetprofit,cash_pay_acq_const_fiolta,dividendyield2,tot_assets",
              "2010-01-01", latest_date, "unit=1;rptType=1;currencyType=Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False)
        df2=w.wsd("801960.SI", "close,pe_ttm,pb_lf,roe_avg,grossprofitmargin,netprofitmargin,yoy_or,yoynetprofit,cash_pay_acq_const_fiolta,dividendyield2,tot_assets",
              "2010-01-01", latest_date, "unit=1;rptType=1;currencyType=;Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False)
        df3=w.wsd("881001.WI", "close",
              "2010-01-01", latest_date, "Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False)
        df1.columns=['日期','收盘价','PETTM','PB','ROE','毛利率','净利率','营收增速','归母增速','固定资产投入占比','股息率','总资产']
        df2.columns=['日期','收盘价','PETTM','PB','ROE','毛利率','净利率','营收增速','归母增速','固定资产投入占比','股息率','总资产']
        df3.columns = ['日期', '收盘价']
        df1['固定资产投入占比']=df1['固定资产投入占比']/df1['总资产']*100
        df2['固定资产投入占比'] = df2['固定资产投入占比'] / df2['总资产']*100
        df1.drop('总资产',axis=1,inplace=True)
        df2.drop('总资产', axis=1, inplace=True)
        index_fin_data=pd.merge(df1,df2,how='outer',on='日期')
        index_fin_data=pd.merge(index_fin_data,df3,how='left',on='日期')
        index_fin_data.rename(columns={'收盘价_x':'煤炭',
                                       '收盘价_y':'石油石化',
                                       '收盘价':'万得全A'},inplace=True)
        index_fin_data.columns=[x.split('_')[0] for x in index_fin_data.columns.tolist()]
        index_fin_data['ym']=index_fin_data['日期'].astype(str).str[0:7]
        index_fin_data.drop_duplicates('ym',keep='last',inplace=True)
        index_fin_data.drop('ym',axis=1,inplace=True)

        industry_date=\
            w.edb("S0029751,M0000271,S0031525,M0000005,S5111905,S0069682,S5173578,S5173579,S5173582,L1801817,S5105044,C0900928,"
                  "S5140385,S5141701,S5123779,S7300007,S0027235,S0073064,S5105025,U0658927,V6801115,C5128614,S5134864,"
                  "S5120404,M0000185", "2010-01-01", latest_date,"Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False)
        industry_date.columns=['日期','LME铜现货','美元指数','布伦特期货','WTI原油期货','布伦特现货','NYMEX天然气期货','美国原油库存','美国原油非战略库存','美国原油战略库存','全球原油产量','欧佩克原油产量','俄罗斯原油产量',
                  '北美钻机数量','美国炼油厂产量','美国炼油厂开工率','山东地炼厂开工率','中国原油进口量','中国原油加工量','欧洲四国汽油需求','美国汽油需求','日本汽油需求','中国汽油需求'
            ,'中国汽油批发价','中国南海原油现货价','美元兑人民币中间价']
        coral_data=w.edb("S5134471,S5101450,S5101712,S5120065,S5103920,S5103913,S0069682,S0027001,S5103052,S5402619,S0027010", "2010-01-01", latest_date,"Period=M;Fill=Previous",usedf=True)[1].reset_index(drop=False)
        coral_data.columns = ['日期','年度长协价:CCTD秦皇岛动力煤(Q5500)','宁波港:库提价(含税):动力煤(Q5500):中国产','纽卡斯尔NEWC动力煤现货价',
                              '中国:产量:动力煤:当月值','中国:重点电厂煤耗总量:本日当月累计','中国:重点电厂煤炭库存量:总计','NYMEX 天然气 期货收盘价','中国进口煤数量',
                              '中国进口动力煤数量','中国进口炼焦煤数量','中国新增原煤开采产能']
        coral_data[['中国进口动力煤数量','中国进口炼焦煤数量']]=coral_data[['中国进口动力煤数量','中国进口炼焦煤数量']]/10000
        industry_date['ym']=industry_date['日期'].astype(str).str[0:7]
        industry_date.drop_duplicates('ym',keep='last',inplace=True)
        industry_date.drop('ym',axis=1,inplace=True)
        industry_date['Brent-WTI']=industry_date['布伦特期货']-industry_date['WTI原油期货']
        industry_date['Brent期现价差']=industry_date['布伦特期货']-industry_date['布伦特现货']
        industry_date['国内汽油原油价差/吨'] = industry_date['中国汽油批发价'] - industry_date['中国南海原油现货价']/0.137*industry_date['美元兑人民币中间价']
        industry_date['欧洲四国汽油需求']=industry_date['欧洲四国汽油需求']/1000


        w.stop()

        import xlwings as xw

        filename = r"E:\学习资料\行业研究\行业跟踪\能源.xlsx"
        app = xw.App(visible=False)
        wb = app.books.open(filename)

        ws = wb.sheets['财务数据']
        # ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =index_fin_data.iloc[-165:]
        print('{} done'.format('财务数据'))

        ws = wb.sheets['商品数据']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =industry_date.iloc[-165:]
        print('{} done'.format('商品数据'))

        ws = wb.sheets['煤炭数据']
        ws.clear()
        ws["A1"].options(pd.DataFrame, header=1, index=False, expand='table').value =coral_data.iloc[-165:]
        print('{} done'.format('煤炭数据'))

        wb.save(filename)
        wb.close()
        app.quit()
        print('all done ')

class Shanghui_fund_info:

    def __init__(self,jjdm_list):

        sql="select jjdm,jjjc from st_fund.t_st_gm_jjxx where jjdm in ({})"\
            .format(util.list_sql_condition(jjdm_list))
        jjjc=hbdb.db2df(sql,db='funduser')


        self.jjjc=dict(zip(jjjc['jjdm'].tolist()
                      ,jjjc['jjjc'].tolist()))

    @staticmethod
    def get_shanghui_funds_style_info(style,size,asofdate):
        sql="""select * from 
        (SELECT jjdm,`成长绝对暴露(持仓)`,`价值绝对暴露(持仓)`,`集中度排名(持仓)`,`换手率排名(持仓)` from jjpic_value_p_hbs where asofdate='{2}' and `风格偏好`='{0}') a 
        inner join 
        (SELECT jjdm as jjdm2,`大盘绝对暴露(持仓)`,`中小盘绝对暴露(持仓)`,`集中度排名(持仓)` as `集中度排名(持仓)_size` ,`换手率排名(持仓)` as `换手率排名(持仓)_size`
         from jjpic_size_p_hbs where asofdate='{2}' and `规模偏好`='{1}')b on a.jjdm=b.jjdm2"""\
            .format(style,size,asofdate)

        funds_info=pd.read_sql(sql,con=localdb)
        return  funds_info

    @staticmethod
    def return_summary(jjdm_list,bkm_list,jjjc,start_date,end_date):


        time_length=\
            (datetime.datetime.strptime(end_date, '%Y%m%d')-datetime.datetime.strptime(start_date, '%Y%m%d')).days

        #get fund daily return

        sql="select jzrq,avg(hbdr)/100 as `同策略` from st_fund.t_st_gm_rhb where jjdm in ({0}) and hbdr!=99999 and hbdr!=0 and jzrq>'{1}' and jzrq<='{2}' group by jzrq  "\
            .format(util.list_sql_condition(bkm_list),start_date,end_date)
        bmk_daily_ret=hbdb.db2df(sql, db='funduser')
        bmk_daily_ret['同策略']=(bmk_daily_ret['同策略']+1).cumprod()

        sql="select jzrq,fqdwjz ,jjdm from st_fund.t_st_gm_rhb where jjdm in ({0}) and hbdr!=99999 and hbdr!=0 and jzrq>='{1}' and jzrq<='{2}'   "\
            .format(util.list_sql_condition(jjdm_list),start_date,end_date)
        funds_daily_ret=hbdb.db2df(sql, db='funduser').pivot_table('fqdwjz','jzrq','jjdm')
        for jjdm in jjdm_list:
            funds_daily_ret[jjdm]=funds_daily_ret[jjdm].fillna(method='bfill')/funds_daily_ret[jjdm].iloc[0]

        sql="select jyrq,spjg as `中证偏股基金指数` from st_market.t_st_zs_hq where zqdm='930950' and spjg!=99999 and jyrq>='{0}' and jyrq<='{1}'   "\
            .format(start_date,end_date)
        index_daily_ret=hbdb.db2df(sql, db='alluser')
        index_daily_ret['中证偏股基金指数'] =\
            index_daily_ret['中证偏股基金指数'] / index_daily_ret['中证偏股基金指数'].iloc[0]

        funds_daily_ret=pd.merge(funds_daily_ret,bmk_daily_ret,
                                 how='left',on='jzrq').fillna(1)
        funds_daily_ret=pd.merge(funds_daily_ret,index_daily_ret,
                                 how='left',left_on='jzrq',right_on='jyrq').set_index('jzrq').drop('jyrq',axis=1)

        winning_pro=funds_daily_ret.copy()
        winning_pro['ym'] = winning_pro.index.astype(str).str[0:6]
        winning_pro=pd.concat([winning_pro.iloc[[0]]
                                  ,winning_pro.drop_duplicates('ym', keep='last')]
                              ,axis=0).drop_duplicates('ym',keep='last')

        winning_pro['month'] = winning_pro['ym'].str[4:]
        winning_pro=\
            winning_pro[winning_pro['month'].isin(['03', '06', '09', '12'])].drop(['ym','month'],axis=1)
        winning_pro=winning_pro.pct_change()
        for col in jjdm_list :
            winning_pro[col]=\
                winning_pro[col]-winning_pro['同策略']
        winning_pro=winning_pro[jjdm_list]
        winning_pro.index=winning_pro.index.astype(str)

        #get period return
        sql="select avg(zbnp)/100 as `同策略`,zblb  from st_fund.t_st_gm_rqjhb where jjdm in ({0}) and zbnp!=99999  and jzrq='{1}' and zblb in ('2101','2103','2106','2201','2202','2998') group by zblb"\
            .format(util.list_sql_condition(bkm_list),end_date)
        bmk_summary_ret=hbdb.db2df(sql, db='funduser')

        sql="select zbnp/100 as zbnp,zblb,jjdm from st_fund.t_st_gm_rqjhb where jjdm in ({0}) and zbnp!=99999  and jzrq='{1}' and zblb in ('2101','2103','2106','2201','2202','2998') "\
            .format(util.list_sql_condition(jjdm_list),end_date)
        funds_summary_ret=hbdb.db2df(sql, db='funduser').pivot_table('zbnp','zblb','jjdm')


        sql="select zbnp/100 as `中证偏股基金指数`,zblb from st_market.t_st_zs_rqjhb where  zqdm='930950' and zbnp!=99999 and jyrq='{0}' and zblb in ('2101','2103','2106','2201','2202','2998') "\
            .format(end_date)
        index_summary_ret=hbdb.db2df(sql, db='alluser')

        funds_summary_ret=pd.merge(funds_summary_ret,bmk_summary_ret,how='left',on='zblb')
        funds_summary_ret=pd.merge(funds_summary_ret,index_summary_ret,how='left',on='zblb').set_index('zblb')
        funds_summary_ret.index=['近1月','近3月','近6月','近1年','近2年','今年以来']

        for col in funds_daily_ret.columns:
            funds_summary_ret.loc['最大回撤',col]=\
                (funds_daily_ret[col]/funds_daily_ret[col].rolling(len(funds_daily_ret),0).max()-1).min()*-1
            funds_summary_ret.loc['年化收益率',col]=\
                np.power(funds_daily_ret[col].iloc[-1], 365 / time_length) - 1
            funds_summary_ret.loc['年化波动率',col]=\
                funds_daily_ret[col].pct_change().std()*np.sqrt(365)
            funds_summary_ret.loc['夏普',col]=\
                funds_summary_ret.loc['年化收益率',col]/funds_summary_ret.loc['年化波动率',col]
            funds_summary_ret.loc['卡尔马',col]=\
                funds_summary_ret.loc['年化收益率',col]/funds_summary_ret.loc['最大回撤',col]


        funds_daily_ret.rename(columns=jjjc,inplace=True)
        funds_summary_ret.rename(columns=jjjc, inplace=True)
        winning_pro.rename(columns=jjjc, inplace=True)
        funds_daily_ret.index=funds_daily_ret.index.astype(str)
        funds_summary_ret=funds_summary_ret.T


        for col in funds_summary_ret.columns[0:-2]:
            funds_summary_ret[col]=funds_summary_ret[col].map("{:.2%}".format)
        for col in funds_summary_ret.columns[-2:]:
            funds_summary_ret[col] = funds_summary_ret[col].map("{:.2}".format)


        return  funds_daily_ret,\
            funds_summary_ret.T.reset_index(drop=False).rename(columns={'index':''}),\
            winning_pro,jjjc


    def ret_comparison(self,type,jjdm_list,start_date,end_date):


        if('成长' in type
                or '价值' in type
                or '大小盘' in type):

            asofdate=pd.read_sql("select max(asofdate) as asofdate from jjpic_value_p_hbs where asofdate<='{}'"
                                 .format(end_date),con=localdb)['asofdate'].iloc[0]

            sql = """select jjdm from (select a.jjdm, CONCAT_WS(b.`规模偏好`,'',a.`风格偏好`) as type,a.asofdate  from 
            (SELECT jjdm,`风格偏好`,asofdate from jjpic_value_p_hbs where asofdate='{0}' ) a 
            inner join 
            (SELECT jjdm as jjdm2,`规模偏好`
             from jjpic_size_p_hbs where asofdate='{0}' )b on a.jjdm=b.jjdm2 ) c where c.type='{1}' """ \
                .format(asofdate,type)
            funds_pool=pd.read_sql(sql,con=localdb)

        else:
            asofdate=pd.read_sql("select max(asofdate) as asofdate from public_theme_pool_history where asofdate<='{}'"
                                 .format(end_date),con=localdb)['asofdate'].iloc[0]
            sql="select jjdm from public_theme_pool_history where asofdate='{0}'"\
                .format(asofdate)
            funds_pool = pd.read_sql(sql, con=localdb)


        last_nyears=(datetime.datetime.strptime(asofdate, '%Y%m%d')-datetime.timedelta(days=365*3))\
            .strftime('%Y%m%d')
        start_date=max([start_date,last_nyears])

        funds_daily_ret, funds_summary_ret,quart_extra,jjjc\
            =self.return_summary(jjdm_list,funds_pool['jjdm'].tolist(),self.jjjc,start_date,end_date)


        #customize part
        asofdate=pd.read_sql("select max(asofdate) as asofdate from jjpic_stock_tp where asofdate<='{}'"
                             .format(end_date),con=localdb)['asofdate'].iloc[0]
        customize_condition="`PB-ROE选股` is not null and `PEG选股` is null and `博弈基本面拐点` ='' and `博弈估值修复`='' "
        sql="select jjdm from jjpic_stock_tp where asofdate='{0}' and jjdm in ({1}) and {2}"\
            .format(asofdate,util.list_sql_condition(funds_pool['jjdm'].tolist()),customize_condition)
        bmk_list=pd.read_sql(sql,con=localdb)['jjdm'].tolist()
        funds_daily_ret2, funds_summary_ret2,quart_extra2,jjjc_2\
            =self.return_summary(jjdm_list,bmk_list,self.jjjc,start_date,end_date)


        customize_condition="`PB-ROE选股` is null and `PEG选股` is not  null and `博弈基本面拐点` ='博弈基本面拐点' and `博弈估值修复`='' "
        sql="select jjdm from jjpic_stock_tp where asofdate='{0}' and jjdm in ({1}) and {2}"\
            .format(asofdate,util.list_sql_condition(funds_pool['jjdm'].tolist()),customize_condition)
        bmk_list=pd.read_sql(sql,con=localdb)['jjdm'].tolist()
        funds_daily_ret3, funds_summary_ret3,quart_extra3,jjjc_2\
            =self.return_summary(jjdm_list,bmk_list,self.jjjc,start_date,end_date)

        funds_daily_ret=pd.merge(funds_daily_ret,funds_daily_ret2['同策略'].to_frame('PB-ROE策略'),how='left',on='jzrq')
        funds_daily_ret = pd.merge(funds_daily_ret, funds_daily_ret3['同策略'].to_frame('PEG+基本面博弈'), how='left',
                                   on='jzrq')

        funds_summary_ret=pd.merge(funds_summary_ret,funds_summary_ret2.set_index('')['同策略'].to_frame('PB-ROE策略'),how='left',on='')
        funds_summary_ret = pd.merge(funds_summary_ret, funds_summary_ret3.set_index('')['同策略'].to_frame('PEG+基本面博弈'), how='left',
                                     on='')


        market_date=self.market_stats(start_date,end_date)
        market_date['穿过50日均线次数'] = (market_date['ma5'] - market_date['ma50']) > 0
        market_date['穿过50日均线次数'] = market_date['穿过50日均线次数'].diff()

        market_date2 = \
            market_date[market_date['jyrq'].isin(quart_extra.index)]
        market_date2['spjg'] = market_date2['spjg'].pct_change()*100
        market_date2['国证成长季度涨跌幅(%)'] = market_date2['国证成长'].pct_change() * 100
        market_date2['国证价值季度涨跌幅(%)'] = market_date2['国证价值'].pct_change() * 100

        quart_list = market_date2['jyrq'].tolist()
        market_date2.set_index('jyrq', inplace=True)
        for i in range(1, len(quart_list)):
            market_date2.loc[quart_list[i], 'cjsl'] = market_date[(market_date['jyrq'] <= quart_list[i])
                                                                  & (market_date['jyrq'] > quart_list[i - 1])][
                                                          'cjsl'].sum() / 1000000000000
            market_date2.loc[quart_list[i], '穿过50日均线次数'] = market_date[(market_date['jyrq'] <= quart_list[i])
                                                                               & (market_date['jyrq'] > quart_list[
                i - 1])]['穿过50日均线次数'].sum()

            market_date2.loc[quart_list[i], '行业排名稳定性'] = abs(market_date[(market_date['jyrq'] <= quart_list[i])
                                                                               & (market_date['jyrq'] > quart_list[
                i - 1])]['IC'].mean()*10)


            sql="select zqdm,spjg,jyrq from st_market.t_st_zs_hq where zqdm in ({0}) and jyrq in ({1})"\
                .format(util.list_sql_condition(['801010','801030','801040','801050','801080','801110',
                              '801120','801130','801140','801150','801160','801170',
                              '801180','801200','801210','801230','801710','801720',
                              '801730','801740','801750','801760','801770','801780',
                              '801790','801880','801890','801950','801960','801970','801980']),
                        util.list_sql_condition([quart_list[i-1],quart_list[i]]))
            ind_quart_ret=hbdb.db2df(sql,db='alluser')
            ind_quart_ret['spjg'] = ind_quart_ret.groupby('zqdm').pct_change()['spjg']
            market_date2.loc[quart_list[i], '行业分化度']=ind_quart_ret[ind_quart_ret['jyrq'] == int(quart_list[i])]['spjg'].skew()

        market_date.rename(columns={'spjg':'万得全A',
                                    'cjsl':'成交量',
                                    'ma5': '5日均线',
                                    'ma50':'50日均线'},inplace=True)
        market_date2.rename(columns={'spjg':'wind全A季度涨跌幅(%)',
                                    'cjsl':'季度累计成交量(万亿)'},inplace=True)

        plot = functionality.Plot(1200, 1200)
        plot.plotly_table(funds_summary_ret,1200,'test')

        plot = functionality.Plot(1200, 600)
        plot.plotly_line_style(funds_daily_ret,'最大同期净值走势')
        plot.plotly_style_bar(quart_extra.iloc[1:],'相对同策略季度超额')
        data,layout=plot.plotly_line_and_area(market_date.set_index('jyrq'),['万得全A','5日均线','50日均线'],['成交量'],'万得全A走势','指数','成交量')
        plot.plot_render(data,layout)
        plot.plotly_style_bar(market_date2.iloc[1:][['wind全A季度涨跌幅(%)','国证成长季度涨跌幅(%)','国证价值季度涨跌幅(%)',
                                                     '季度累计成交量(万亿)','穿过50日均线次数','行业排名稳定性','行业分化度']], '市场统计')


        brison_ret,brison_极值_data = self.get_brison_ret(jjdm_list, start_date, end_date)
        brison_ret.index=[jjjc[x] for x in brison_ret.index]

        plot = functionality.Plot(900, 800)
        for jjdm in jjdm_list:
            plot_date = brison_极值_data.loc[[jjdm]]
            plot.ploty_polar(plot_date,jjjc[jjdm]+'_Brison收益得分')

        plot = functionality.Plot(900, 200*len(jjdm_list))
        plot.plotly_table(brison_ret.reset_index(),600,'')


    @staticmethod
    def market_stats(start_date,end_date):

        start_date_laps100=util.str_date_shift(start_date,150,'-')

        sql="select jyrq,spjg,cjsl from st_market.t_st_zs_hq where zqdm='881001' and jyrq>='{0}' and jyrq<='{1}'"\
            .format(start_date_laps100,end_date)
        trade_data=hbdb.db2df(sql,db='alluser')
        trade_data['jyrq']=trade_data['jyrq'].astype(str)
        trade_data['ma5']=trade_data['spjg'].rolling(5).mean()
        trade_data['ma50'] = trade_data['spjg'].rolling(50).mean()
        trade_data=trade_data[trade_data['jyrq']>=start_date]


        #get style index ret
        sql="select jyrq,spjg,zqdm from st_market.t_st_zs_hq where zqdm in('399370','399371') and jyrq>='{0}' and jyrq<='{1}'"\
            .format(start_date,end_date)
        style_data=hbdb.db2df(sql,db='alluser').pivot_table('spjg','jyrq','zqdm').rename(columns={'399370':'国证成长',
                                                                                                  '399371':'国证价值'})
        style_data.index=style_data.index.astype(str)



        sql=" select zqdm,rqzh,hb1z from st_market.t_st_zs_zhb where zqdm in ({0}) and rqzh>='{1}' and rqzh<='{2}' "\
            .format(util.list_sql_condition(['801010','801030','801040','801050','801080','801110',
                              '801120','801130','801140','801150','801160','801170',
                              '801180','801200','801210','801230','801710','801720',
                              '801730','801740','801750','801760','801770','801780',
                              '801790','801880','801890','801950','801960','801970','801980']),start_date,end_date)
        industry_ret=hbdb.db2df(sql,db='alluser')
        industry_ret['rank'] = industry_ret.groupby('rqzh')['hb1z'].rank()
        industry_ret=industry_ret.pivot_table('rank','zqdm','rqzh')
        col_list=industry_ret.columns.tolist()
        for i in range(1,len(col_list)):
            trade_data.loc[trade_data['jyrq'] ==str(col_list[i]), 'IC']=\
                industry_ret[[col_list[i-1],col_list[i]]].corr().iloc[0,1]

        trade_data=pd.merge(trade_data, style_data, how='left', on='jyrq')

        return  trade_data

    @staticmethod
    def get_brison_ret(jjdm_list,start_date,end_date):


        from hbshare.fe.brinson_attr import equity_brinson_attribution as eba

        brison_ret=[]
        for jjdm in jjdm_list:
            attr_result =eba.EquityBrinsonAttribution(
                fund_id=jjdm, benchmark_id='000905', start_date=start_date,
                end_date=end_date).get_attribution_result()['realized_period_attr_df'][['trade_date','fund_id', 'asset_allo',
       'sector_allo', 'equity_selection', 'trading']]

            brison_ret.append(attr_result)

        brison_ret=pd.concat(brison_ret,axis=0)
        max_date=brison_ret.groupby('fund_id')['trade_date'].max().min()
        min_date=brison_ret.groupby('fund_id')['trade_date'].min().max()

        sql="select jjdm,count(tjrq) as count from st_fund.r_st_hold_excess_attr_df where tjrq >='{0}' and tjrq<='{1}' group by jjdm "\
            .format(min_date,max_date)
        count_info=hbdb.db2df(sql,db='funduser')
        count_info=count_info[count_info['count'] == count_info['count'].max()]

        sql="select jjdm,avg(asset_allo) as asset_allo,avg(sector_allo) as sector_allo,avg(equity_selection) as equity_selection,avg(trading) as trading from st_fund.r_st_hold_excess_attr_df where tjrq in ({0}) and jjdm in ({1}) group by jjdm "\
            .format(util.list_sql_condition(brison_ret['trade_date'].tolist())
                    ,util.list_sql_condition(count_info['jjdm'].tolist()))
        rank_bmk=hbdb.db2df(sql,db='funduser')

        brison_ret=brison_ret[(brison_ret['trade_date'] >= min_date) & (brison_ret['trade_date'] <= max_date)&(~brison_ret['fund_id'].isin(count_info['jjdm'].tolist()))].groupby(
            'fund_id').mean().drop('trade_date', axis=1).reset_index().rename(columns={'fund_id':'jjdm'})
        rank_bmk=pd.concat([rank_bmk,brison_ret],axis=0)

        rank_bmk=rank_bmk.set_index('jjdm')
        rank_bmk.rename(columns=dict(zip(['asset_allo', 'sector_allo', 'equity_selection', 'trading'],
                                 ['大类配置收益', '行业配置收益', '个股选择收益', '交易收益'])),inplace=True)
        rank_bmk_极值_date=rank_bmk.rank()/len(rank_bmk)*10
        for col in rank_bmk.columns:
            rank_bmk[col]=rank_bmk[col].map("{:.2%}".format)

        return  rank_bmk.loc[jjdm_list],rank_bmk_极值_date.loc[jjdm_list]

    def industry_comparison(self,jjdm_list,end_date,start_date):


        sql="select max(jsrq) as jsrq from st_fund.t_st_gm_jjhyzhyszb where jsrq<='{}' and hyhfbz='2' and zclb='2' "\
            .format(end_date)
        last_date=hbdb.db2df(sql,db='funduser')['jsrq'].iloc[0]

        bmk_list=util.get_stock_funds_pool(end_date,2)

        # sql = "select jsrq,jjdm,flmc,zgpbl from st_fund.t_st_gm_jjhyzhyszb where jjdm in ({0}) and jsrq='{1}' and hyhfbz='2' and zclb='2' " \
        #     .format(util.list_sql_condition(bmk_list), last_date)
        # ind_dis = hbdb.db2df(sql, db='funduser')

        ind_dis=pd.read_pickle(r"E:\GitFolder\hbshare\fe\mutual_analysis\行业数据")
        date_list=ind_dis[(ind_dis['jsrq']<=int(last_date))
                          &(ind_dis['jsrq']>=int(start_date))]['jsrq'].unique().tolist()

        ind_dis_latest=ind_dis[(ind_dis['jjdm'].isin(bmk_list))&(ind_dis['jsrq']==int(last_date))]

        ind_dis_latest=pd.merge((ind_dis_latest.groupby('flmc').sum()['zgpbl']/len(bmk_list)).to_frame('偏股基金')
                         ,ind_dis_latest[ind_dis_latest['jjdm'].isin(jjdm_list)].pivot_table('zgpbl', 'flmc', 'jjdm').fillna(0),how='left',on='flmc').fillna(0).sort_values('偏股基金')

        ind_dis_3years = ind_dis[(ind_dis['jjdm'].isin(bmk_list)) & (ind_dis['jsrq'].isin(date_list))]
        temp = pd.merge(ind_dis_3years.groupby(['jsrq', 'flmc']).sum().reset_index(),
                        ind_dis_3years.groupby('jsrq').nunique()[['jjdm']], how='left', on='jsrq')
        temp['zgpbl']=temp['zgpbl'] / temp['jjdm']

        ind_dis_3years=pd.merge((temp.groupby('flmc').sum()['zgpbl']/6).to_frame('偏股基金')
                         ,ind_dis_3years[ind_dis_3years['jjdm'].isin(jjdm_list)].pivot_table('zgpbl', 'flmc', 'jjdm').fillna(0),how='left',on='flmc').fillna(0).sort_values('偏股基金')


        for jjdm in jjdm_list:
            ind_dis_latest[jjdm]=ind_dis_latest[jjdm]-ind_dis_latest['偏股基金']
            ind_dis_3years[jjdm] = ind_dis_3years[jjdm] - ind_dis_latest['偏股基金']

        plot=functionality.Plot(1200,600)
        plot.plotly_style_bar(ind_dis_latest[jjdm_list].rename(columns=self.jjjc),'最新期行业超低配情况')
        plot.plotly_style_bar(ind_dis_3years[jjdm_list].rename(columns=self.jjjc), '最大同期行业超低配情况')

    def stock_comparison(self,jjdm_list,end_date,start_date):


        sql="select max(jsrq) as jsrq from st_fund.t_st_gm_zcpz where jsrq<='{}' "\
            .format(end_date)
        last_date=hbdb.db2df(sql,db='funduser')['jsrq'].iloc[0]

        bmk_list=util.get_stock_funds_pool(end_date,2)

        # sql = "select jsrq,jjdm,flmc,zgpbl from st_fund.t_st_gm_jjhyzhyszb where jjdm in ({0}) and jsrq='{1}' and hyhfbz='2' and zclb='2' " \
        #     .format(util.list_sql_condition(bmk_list), last_date)
        # ind_dis = hbdb.db2df(sql, db='funduser')

        funds_holding=pd.read_pickle(r"C:\Users\xuhuai.zhe\Documents\WXWork\1688858146292774\Cache\File\2023-07\fund_holds")[['jsrq','jjdm','zqmc','zjbl','ccsl']]
        date_list=funds_holding[(funds_holding['jsrq']<=int(last_date))
                                &(funds_holding['jsrq']>=int(start_date))]['jsrq'].unique().tolist()
        funds_holding=funds_holding[funds_holding['jsrq'].isin(date_list)]

        holding_summary=funds_holding.groupby('zqmc')['zjbl'].mean().to_frame('zjbl').describe()
        print('偏股基金个股配置过去三年平均权重中位数 {0}%,75分位数{1}%'
              .format(holding_summary.loc['50%']['zjbl'],holding_summary.loc['75%']['zjbl']))
        holding_summary = funds_holding[funds_holding['jsrq']==last_date].groupby('zqmc')['zjbl'].mean().to_frame('zjbl').describe()
        print('偏股基金个股配置当期权重中位数 {0},75分位数{1}'
              .format(holding_summary.loc['50%']['zjbl'],holding_summary.loc['75%']['zjbl']))

        target_fund_holding=funds_holding[(funds_holding['jjdm'].isin(jjdm_list))]
        stock_list=target_fund_holding.groupby(['jjdm', 'zqmc'])['zjbl'].sum().to_frame('zjbl').reset_index()
        stock_list['rank'] = stock_list.groupby('jjdm')['zjbl'].rank(ascending=False)
        stock_list=stock_list[stock_list['rank']<=5][['jjdm','zqmc']]


        stock_dis_latest=funds_holding[(funds_holding['jjdm'].isin(bmk_list))
                                       &(funds_holding['jsrq']==int(last_date))
                                       &(funds_holding['zqmc'].isin(stock_list['zqmc'].unique()).tolist())]
        stock_dis_latest=pd.merge((stock_dis_latest.groupby('zqmc').sum()['zjbl']/len(bmk_list)).to_frame('偏股基金')
                         ,stock_dis_latest[stock_dis_latest['jjdm'].isin(jjdm_list)].pivot_table('zjbl', 'zqmc', 'jjdm').fillna(0),how='left',on='zqmc').fillna(0)

        stock_dis_3years = funds_holding[(funds_holding['jjdm'].isin(bmk_list))
                                         & (funds_holding['jsrq'].isin(date_list))
                                         &(funds_holding['zqmc'].isin(stock_list['zqmc'].unique()).tolist())]
        temp = pd.merge(stock_dis_3years.groupby(['jsrq', 'zqmc']).sum().reset_index(),
                        stock_dis_3years.groupby('jsrq').nunique()[['jjdm']], how='left', on='jsrq')
        temp['zjbl']=temp['zjbl'] / temp['jjdm']

        stock_dis_3years=pd.merge((temp.groupby('zqmc').sum()['zjbl']/6).to_frame('偏股基金')
                         ,stock_dis_3years[stock_dis_3years['jjdm'].isin(jjdm_list)].pivot_table('zjbl', 'zqmc', 'jjdm').fillna(0),how='left',on='zqmc').fillna(0)



        plot=functionality.Plot(1200,600)
        for jjdm in jjdm_list:

            plot.plotly_style_bar(stock_dis_latest.loc[stock_list[stock_list['jjdm']==jjdm]['zqmc'].tolist()][['偏股基金']+[jjdm]].rename(columns=self.jjjc),'前五大个股最新期配置情况')
            plot.plotly_style_bar(stock_dis_3years.loc[stock_list[stock_list['jjdm']==jjdm]['zqmc'].tolist()][['偏股基金']+[jjdm]].rename(columns=self.jjjc), '前五大个股最大同期平均配置情况')

class secondary_stratage_classify():

    @staticmethod
    def get_pic_from_localdb_simple_version(jjdm, asofdate='20220831'):

        latest_date = pd.read_sql(
            "select max(asofdate) as asofdate from jjpic_value_p_hbs where asofdate<='{}'"
            .format(asofdate), con=localdb)['asofdate'][0]
        sql = "SELECT * from jjpic_value_p_hbs where {0} and asofdate='{1}' " \
            .format(jjdm, latest_date)
        value_p_hbs = pd.read_sql(sql, con=localdb)[['jjdm', '集中度(持仓)', '换手率(持仓)', '成长绝对暴露(持仓)',
       '价值绝对暴露(持仓)', '集中度排名(持仓)', '换手率排名(持仓)', '成长暴露排名(持仓)', '价值暴露排名(持仓)']]

        latest_date = pd.read_sql(
            "select max(asofdate) as asofdate from jjpic_size_p_hbs where asofdate<='{}'"
            .format(asofdate), con=localdb)['asofdate'][0]
        sql = "SELECT * from jjpic_size_p_hbs where {0} and asofdate='{1}' " \
            .format(jjdm, latest_date)
        size_p_hbs = pd.read_sql(sql, con=localdb)[['jjdm', '集中度(持仓)', '换手率(持仓)', '大盘绝对暴露(持仓)',
       '中小盘绝对暴露(持仓)', '集中度排名(持仓)', '换手率排名(持仓)', '大盘暴露排名(持仓)', '中小盘暴露排名(持仓)']]

        latest_date = pd.read_sql(
            "select max(asofdate) as asofdate from jjpic_industry_p where asofdate<='{}'"
            .format(asofdate), con=localdb)['asofdate'][0]
        sql = "SELECT * from jjpic_industry_p where {0} and asofdate='{1}' " \
            .format(jjdm, latest_date)
        industry_p = pd.read_sql(sql, con=localdb)[['jjdm', '一级行业集中度', '一级行业换手率','龙头占比(时序均值)', '龙头占比(时序中位数)', '龙头占比(时序均值)排名',
       '龙头占比(时序中位数)排名',  '二级行业集中度', '二级行业换手率', '三级行业集中度',
       '三级行业换手率']]


        latest_date = pd.read_sql(
            "select max(asofdate) as asofdate from jjpic_theme_p where asofdate<='{}'"
            .format(asofdate), con=localdb)['asofdate'][0]
        sql = "SELECT * from jjpic_theme_p where {0} and asofdate='{1}' " \
            .format(jjdm, latest_date)
        theme_p = pd.read_sql(sql, con=localdb)[['jjdm', '主题集中度', '主题换手率', '大金融', '消费', 'TMT', '周期',
       '制造']]



        industry_level = ['yjxymc', 'ejxymc', 'sjxymc']

        for i in range(1):

            # get the industry contribution
            latest_date = pd.read_sql(
                "select max(asofdate) as asofdate from hbs_industry_contribution",
                con=localdb)['asofdate'][0]
            sql = "SELECT * from hbs_industry_contribution where  {0} and industry_lv='{2}' and asofdate='{1}' " \
                .format(jjdm, latest_date, industry_level[i])
            industry_con = pd.read_sql(sql, con=localdb)
            industry_con_temp = industry_con.pivot_table('contribution',  'jjdm','industry_name')


        hold_date_list=hbdb.db2df("select distinct(jsrq) as jsrq from st_fund.t_st_gm_jjhyzhyszb  where jsrq<='{0}' and zclb='2' order by jsrq "
                                  .format(asofdate), db='funduser')[-4:]
        sql = "select jjdm,flmc, avg(zzjbl) as zjbl from st_fund.t_st_gm_jjhyzhyszb where {0} and jsrq in ({1}) and hyhfbz='2' and zclb='2' group by jjdm,flmc" \
            .format(jjdm, util.list_sql_condition(hold_date_list['jsrq'].astype(str).tolist()))
        industry_w = hbdb.db2df(sql, db='funduser').pivot_table('zjbl','jjdm','flmc')


        latest_date = pd.read_sql(
            "select max(asofdate) as asofdate from jjpic_stock_p where asofdate<='{}'"
            .format(asofdate), con=localdb)['asofdate'][0]
        sql = "SELECT * from jjpic_stock_p where {0} and asofdate='{1}' " \
            .format(jjdm, latest_date)
        stock_p = pd.read_sql(sql, con=localdb)[['jjdm','个股集中度', 'hhi',
       '持股数量', '前三大', '前五大', '前十大', '平均仓位', '仓位换手率', 'PE_rank', 'PB_rank',
       'ROE_rank', '股息率_rank', 'PE_中位数_rank', 'PB_中位数_rank', 'ROE_中位数_rank',
       '股息率_中位数_rank', 'PE', 'PB', 'ROE', '股息率', 'PE_中位数', 'PB_中位数', 'ROE_中位数',
       '股息率_中位数']]


        latest_date = pd.read_sql(
            "select max(asofdate) as asofdate from jjpic_stock_tp where asofdate<='{}'"
            .format(asofdate), con=localdb)['asofdate'][0]
        sql = "SELECT * from jjpic_stock_tp where {0} and asofdate='{1}' " \
            .format(jjdm, latest_date)
        stock_tp = pd.read_sql(sql, con=localdb)[['jjdm','左侧概率(出重仓前,半年线)_rank',
       '左侧概率(出持仓前,半年线)_rank', '左侧概率(出重仓前,年线)_rank', '左侧概率(出持仓前,年线)_rank',
       '换手率_rank', '平均持有时间(出重仓前)_rank', '平均持有时间(出持仓前)_rank', '出重仓前平均收益率_rank',
       '出全仓前平均收益率_rank', '新股概率(出重仓前)_rank', '新股概率(出持仓前)_rank',
       '次新股概率(出重仓前)_rank', '次新股概率(出持仓前)_rank', '平均持有时间(出重仓前)', '平均持有时间(出持仓前)',
       '出重仓前平均收益率', '出全仓前平均收益率', '换手率', '左侧概率(出重仓前,半年线)', '左侧概率(出持仓前,半年线)',
       '左侧概率(出重仓前,年线)', '左侧概率(出持仓前,年线)', '左侧程度(出重仓前,半年线)', '左侧程度(出持仓前,半年线)',
       '左侧程度(出重仓前,年线)', '左侧程度(出持仓前,年线)', '新股概率(出重仓前)', '新股概率(出持仓前)',
       '次新股概率(出重仓前)', '次新股概率(出持仓前)']]


        jj_features=pd.merge(value_p_hbs,size_p_hbs,how='left',on='jjdm')
        for df in [industry_p,theme_p,industry_con_temp,industry_w,stock_p,stock_tp]:
            jj_features=pd.merge(jj_features,df,how='left',on='jjdm')

        return jj_features


    def classification(self,type,asofdate1,asofdate2):

        sql="select jjdm from jjpic_value_p_hbs where asofdate='{0}' and `风格偏好`='{1}'".format(asofdate1,type)
        jjdm_list=pd.read_sql(sql,con=localdb)['jjdm'].tolist()
        jjdm_con='jjdm in ({})'.format(util.list_sql_condition(jjdm_list))
        jj_features=self.get_pic_from_localdb_simple_version(jjdm_con,asofdate2)


        from sklearn.cluster import KMeans
        from sklearn.decomposition import  PCA
        import sklearn.preprocessing as pp
        # from sklearn import metrics
        n_clusters = 4
        feature_list=jj_features.columns.tolist()[1:]
        result_list=[]
        seed_num=100
        sacle_data=pp.StandardScaler().fit_transform(jj_features[feature_list].fillna(0).values)
        pca = PCA(.95)
        sacle_data=pca.fit_transform(sacle_data)
        for i in range(seed_num):
            model=KMeans(n_clusters=n_clusters,init='k-means++',
                         random_state=i).fit(sacle_data)
            jj_features['子类型'+str(i)] = \
                model.predict(sacle_data)
            result_list.append('子类型'+str(i))

        jj_features=jj_features.set_index('jjdm')[result_list].T
        answer_summary=pd.DataFrame()
        for i in range(n_clusters):
            answer_summary[str(i)]=(jj_features==i).sum(axis=0)

        answer_summary=answer_summary/seed_num
        answer_summary=\
            answer_summary.unstack().reset_index().sort_values(['jjdm', 0]).drop_duplicates('jjdm', keep='last')

        answer_summary.to_excel(type+'基金分类结果.xlsx')

        print('')

class fund_lables_summary():


    def __init__(self):

        self.asofdate_list1=\
            pd.read_sql("select distinct(asofdate) as asofdate from jjpic_size_p_hbs order by asofdate",con=localdb)['asofdate'].tolist()


    def get_funds_num_and_size(self):

        fund_num=[]
        fund_size=[]
        for asofdate in self.asofdate_list1:

            jjdm_list=util.get_stock_funds_pool(asofdate,2,if_fund_type=True)
            fund_num.append(jjdm_list.groupby('ejfl')['jjdm'].count().to_frame(asofdate[0:6]).T)
            temp_size=hbdb.db2df("select jjdm,jjzzc/100000000000 as jjzzc from st_fund.t_st_gm_zcpz where jjdm in ({0}) and left(jsrq,6)='{1}' "
                                 .format(util.list_sql_condition(jjdm_list['jjdm'].unique().tolist())
                                         ,asofdate[0:6]),db='funduser')
            fund_size.append(pd.merge(jjdm_list,temp_size,how='left',on='jjdm').groupby('ejfl')['jjzzc'].sum().to_frame(asofdate[0:6]).T)

        fund_num=pd.concat(fund_num,axis=0).rename(columns=dict(zip(['13','35','37']
                                                                    ,['普通股票型','灵活配置型','偏股混合型'])))
        fund_size=pd.concat(fund_size,axis=0).rename(columns=dict(zip(['13','35','37']
                                                                    ,['普通股票型','灵活配置型','偏股混合型'])))

        for col in fund_num.columns:
            fund_num[col+'环比增速']=fund_num[col].pct_change()
            fund_size[col+'环比增速']=fund_size[col].pct_change()

        plot=functionality.Plot(1200,600)
        data,layout=plot.plotly_line_and_bar(fund_num[fund_num.columns[3:]],fund_num[fund_num.columns[0:3]],'偏股基金数量时序',
                                 left_axis_name='环比增速',right_axis_name='数量')
        plot.plot_render(data,layout)
        data,layout=plot.plotly_line_and_bar(fund_size[fund_size.columns[3:]],fund_size[fund_size.columns[0:3]],'偏股基金规模时序',
                                 left_axis_name='环比增速',right_axis_name='规模(千亿)')
        plot.plot_render(data,layout)

    @staticmethod
    def get_portfolio_stratage_distribution(lable_info,stratage_name):

        plot = functionality.Plot(1200, 600)

        for stratage in lable_info[stratage_name].unique():

            temp = lable_info[lable_info[stratage_name] == stratage]
            combined_ratio = []
            combined_ret=[]

            for col in ['博弈基本面拐点', 'PB-ROE选股', 'PEG选股', '博弈估值修复']:
                tempp=(temp[temp[col] == col].groupby(['asofdate']).count()['jjdm'] / \
                                       temp.groupby(['asofdate']).count()['jjdm']-
                       lable_info[lable_info[col] == col].groupby(['asofdate']).count()['jjdm'] / lable_info.groupby(['asofdate']).count()['jjdm']).to_frame(col)
                tempp.loc['均值'] = tempp.mean(axis=0).values.tolist()
                combined_ratio.append(tempp)
                tempp2=tempp.copy()
                if(tempp2.isnull().sum().iloc[0]==0):
                    tempp2[col] = [1] + (temp[temp[col] == col].groupby('asofdate')[
                                            'halfyearret'].mean() + 1).cumprod().tolist()[0:-1]+[1]
                    combined_ret.append(tempp2.iloc[0:-1])


            for col in ['行业精选个股策略', '是否抱团']:
                tempp = pd.merge(temp.groupby(['asofdate', col]).count()['jjdm'].reset_index(),
                                 temp.groupby(['asofdate']).count()['jjdm']
                                 , how='left', on='asofdate')
                tempp['jjdm_x'] = tempp['jjdm_x'] / tempp['jjdm_y']

                bmk = pd.merge(lable_info.groupby(['asofdate', col]).count()['jjdm'].reset_index(),
                                 lable_info.groupby(['asofdate']).count()['jjdm']
                                 , how='left', on='asofdate')
                bmk['jjdm_x'] = bmk['jjdm_x'] / bmk['jjdm_y']
                tempp['jjdm_x']=tempp['jjdm_x']-bmk['jjdm_x']

                tempp=tempp.pivot_table('jjdm_x', 'asofdate', col)
                tempp.loc['均值'] = tempp.mean(axis=0).values.tolist()
                combined_ratio.append(tempp)

                temppp=(temp.groupby(['asofdate', col]).mean()[['halfyearret']].reset_index().pivot_table('halfyearret',
                                                                                                  'asofdate',
                                                                                                  col)+1).cumprod()

                temppp.index = tempp.index.tolist()[1:-1]
                temppp.loc[tempp.index[0]] = [1]*len(tempp.columns)
                temppp = temppp.sort_index()
                combined_ret.append(temppp)



            combined_ratio = pd.concat(combined_ratio, axis=1).rename(columns={'价值': '行业内精选价值个股',
                                                                               '成长': '行业内精选成长个股',
                                                                               }).drop(['无','其他'], axis=1)
            combined_ret = pd.concat(combined_ret, axis=1).rename(columns={'价值': '行业内精选价值个股',
                                                                               '成长': '行业内精选成长个股',
                                                                               }).drop(['无','其他'], axis=1)


            combined_ratio = combined_ratio.T.sort_values('均值', ascending=False).T
            for col in combined_ratio.columns:

                combined_ratio[col] = \
                    combined_ratio[col].map("{:.2%}".format)

            combined_ratio.index.name =stratage + "型基金个股策略超低配程度"
            plot.plotly_table(combined_ratio.reset_index(),1500,'')
            plot.plotly_line_style(combined_ret,stratage + "型基金个股策略净值")

    @staticmethod
    def get_funds_label():

        def change_asofdate(industry_p):

            industry_p.loc[industry_p['asofdate'].str.contains('06'), 'asofdate'] = \
                industry_p[industry_p['asofdate'].str.contains('06')]['asofdate'].str[0:4] + '09'
            industry_p.loc[industry_p['asofdate'].str.contains('12'), 'asofdate'] = \
                ((industry_p[industry_p['asofdate'].str.contains('12')]['asofdate'].str[0:4]).astype(int) + 1).astype(
                    str) + '03'

            return  industry_p



        out_side_data=\
            pd.read_pickle(r"E:\GitFolder\docs\基金画像更新数据\基金持仓数据\factor_center_ori").reset_index()
        out_side_data['datetime_q']=out_side_data['datetime_q'].astype(str).str.replace('-','').str[0:6]

        out_side_data.loc[out_side_data['stk_cap2_pct'] >= 1, 'stk_cap2_pct'] = \
        out_side_data[out_side_data['stk_cap2_pct'] >= 1]['stk_cap2_pct'] / 100000
        out_side_data.loc[out_side_data['stk_cap2_pct'] >= 100, 'stk_cap2_pct'] = 0

        out_side_data['m'] = out_side_data['datetime_q'].str[-2:]
        out_side_data = change_asofdate(out_side_data[out_side_data['m'].isin(['06','12'])].rename(columns={'datetime_q':'asofdate','fund_id':'jjdm'}))

        sql="select jjdm,theme as theme_type,asofdate from public_theme_pool_history "
        theme_his=pd.read_sql(sql,con=localdb)
        theme_his['asofdate']=theme_his['asofdate'].astype(str).str[0:6]
        theme_his=change_asofdate(theme_his)
        theme_his.loc[theme_his['theme_type'].astype(str).str.contains("[+]"), 'theme_type'] = '主题+'


        sql = "SELECT * from jjpic_value_p_hbs  "
        value_p_hbs = pd.read_sql(sql, con=localdb)
        value_p_hbs['asofdate']=value_p_hbs['asofdate'].astype(str).str[0:6]
        value_p_hbs=change_asofdate(value_p_hbs)

        sql = "SELECT * from jjpic_size_p_hbs "
        size_p_hbs = pd.read_sql(sql, con=localdb)
        size_p_hbs['asofdate']=size_p_hbs['asofdate'].astype(str).str[0:6]
        size_p_hbs = change_asofdate(size_p_hbs)

        sql = "SELECT * from jjpic_industry_p  "
        industry_p = pd.read_sql(sql, con=localdb)
        industry_p['asofdate']=industry_p['asofdate'].astype(str).str[0:6]
        industry_p.loc[industry_p['asofdate'].str.contains('08'), 'asofdate'] = \
            industry_p[industry_p['asofdate'].str.contains('08')]['asofdate'].str[0:4] + '09'


        sql = "SELECT * from hbs_industry_property_new  "
        industry_raw_p = pd.read_sql(sql, con=localdb)
        industry_raw_p['asofdate']=industry_raw_p['asofdate'].astype(str).str[0:6]
        industry_raw_p.loc[industry_raw_p['asofdate'].str.contains('08'), 'asofdate'] = \
            industry_raw_p[industry_raw_p['asofdate'].str.contains('08')]['asofdate'].str[0:4] + '09'


        sql = "SELECT * from jjpic_theme_p  "
        theme_p = pd.read_sql(sql, con=localdb)
        theme_p['asofdate']=theme_p['asofdate'].astype(str).str[0:6]
        theme_p.loc[theme_p['asofdate'].str.contains('08'), 'asofdate'] = \
            theme_p[theme_p['asofdate'].str.contains('08')]['asofdate'].str[0:4] + '09'


        sql = "SELECT * from jjpic_stock_p  "
        stock_p = pd.read_sql(sql, con=localdb)
        stock_p['asofdate']=stock_p['asofdate'].astype(str).str[0:6]
        stock_p = change_asofdate(stock_p)

        sql = "SELECT * from jjpic_stock_tp  "
        stock_tp = pd.read_sql(sql, con=localdb)
        stock_tp['asofdate']=stock_tp['asofdate'].astype(str).str[0:6]
        stock_tp = change_asofdate(stock_tp)

        # update the industry label by ticker shift ratio
        industry_p = pd.merge(industry_p, stock_tp[['jjdm', '换手率_rank','asofdate']], how='left', on=['jjdm','asofdate'])
        # industry_p.loc[(industry_p['一级行业类型'] == '博弈')
        #                & (industry_p['换手率_rank'] < 0.5), '一级行业类型'] = '博弈(被动)'
        # industry_p.loc[(industry_p['一级行业类型'] == '轮动')
        #                & (industry_p['换手率_rank'] < 0.5), '一级行业类型'] = '轮动(被动)'
        industry_p.drop('换手率_rank', axis=1, inplace=True)

        # theme histroy data

        sql = "SELECT * from hbs_theme_exp"
        theme_exp = pd.read_sql(sql, con=localdb).sort_values('jsrq')
        theme_exp['jjdm'] = [("000000" + x)[-6:] for x in theme_exp['jjdm']]
        theme_exp['asofdate']=theme_exp['jsrq'].astype(str).str[0:6]
        theme_exp = change_asofdate(theme_exp)

        # get the value and growth  exp

        sql = "SELECT * from hbs_style_exp "
        style_exp = pd.read_sql(sql, con=localdb)
        style_exp['asofdate']=style_exp['jsrq'].astype(str).str[0:6]
        style_exp = change_asofdate(style_exp)

        sql = "SELECT * from hbs_size_exp  "
        size_exp = pd.read_sql(sql, con=localdb)
        size_exp['asofdate']=size_exp['jsrq'].astype(str).str[0:6]
        size_exp = change_asofdate(size_exp)

        jjpic=pd.merge(value_p_hbs,size_p_hbs.drop('基金简称',axis=1)
                       ,how='inner',on=['asofdate','jjdm'])
        for df in [industry_p.drop('基金简称',axis=1), industry_raw_p,theme_p.drop('基金简称',axis=1), stock_p.drop('基金简称',axis=1),
                   stock_tp]:
            jjpic=pd.merge(jjpic,df,how='inner',on=['asofdate','jjdm'])

        jjpic=pd.merge(jjpic,theme_his,how='left',on=['asofdate','jjdm'])
        jjpic['theme_type']=jjpic['theme_type'].fillna('全市场')
        jjpic = pd.merge(jjpic, out_side_data, how='left', on=['asofdate', 'jjdm'])

        style_exp_new=[]
        size_exp_new=[]
        for date in jjpic['asofdate'].unique():
            style_exp_new.append(style_exp[(style_exp['asofdate']==date)&(style_exp['jjdm'].isin(jjpic[jjpic['asofdate']==date]['jjdm'].tolist()))])
            size_exp_new.append(size_exp[(size_exp['asofdate']==date)&(size_exp['jjdm'].isin(jjpic[jjpic['asofdate']==date]['jjdm'].tolist()))])




        return jjpic, theme_exp ,\
            pd.concat(style_exp_new,axis=0), pd.concat(size_exp_new,axis=0)

    @staticmethod
    def get_funds_ret(jjdm_list,date_list):

        if(date_list[-1]>=datetime.datetime.today().strftime('%Y%m%d')):
            orgin_date=date_list[-1]
            date_list[-1]=util.str_date_shift(datetime.datetime.today().strftime('%Y%m%d'),1,'-')

        sql="select jjdm,jzrq,fqdwjz from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ({1})"\
            .format(util.list_sql_condition(jjdm_list),util.list_sql_condition(date_list))
        fund_nav=hbdb.db2df(sql,db='funduser')
        fund_nav['halfyearret']=(fund_nav.groupby('jjdm')['fqdwjz'].pct_change().iloc[1:]).tolist()+[np.nan]

        fund_nav['asofdate']=fund_nav['jzrq'].astype(str).str[0:6]

        return  fund_nav[['jjdm','halfyearret','asofdate']]

    def lable_summary(self):

        # lable_info, theme_exp , style_exp, size_exp=self.get_funds_label()
        # trade_date_list=[util._shift_date(x+'30') for x in lable_info['asofdate'].unique().tolist()]
        # trade_date_list.sort()
        # fund_ret=self.get_funds_ret(lable_info['jjdm'].unique().tolist(),trade_date_list)
        # lable_info=pd.merge(lable_info,fund_ret,how='left',on=['jjdm','asofdate'])
        # lable_info.to_pickle('lable_info')
        # theme_exp.to_pickle('theme_exp')
        # style_exp.to_pickle('style_exp')
        # size_exp.to_pickle('size_exp')

        #
        lable_info=pd.read_pickle('lable_info').drop_duplicates(['jjdm','asofdate'])
        style_exp=pd.read_pickle('style_exp').drop_duplicates(['jjdm','asofdate'])
        size_exp=pd.read_pickle('size_exp').drop_duplicates(['jjdm','asofdate'])

        # lable_info=lable_info[lable_info['asofdate']>='201803']
        # size_exp=size_exp[size_exp['asofdate']>='201803']
        # style_exp=style_exp[style_exp['asofdate']>='201803']

        lable_info.loc[lable_info['换手率'] > 8, '换手率']=np.nan
        lable_info.loc[lable_info['换手率'] < 0, '换手率'] = np.nan

        style_exp=\
            style_exp.groupby(['jsrq', 'style_type'])['zjbl'].mean().reset_index().pivot_table('zjbl',  'style_type','jsrq')
        size_exp=\
            size_exp.groupby(['jsrq', 'size_type'])['zjbl'].mean().reset_index().pivot_table('zjbl', 'size_type', 'jsrq')


        date_list=lable_info['asofdate'].unique().tolist()
        date_list.sort()

        lable_info.rename(columns={'个股风格B':'自上而下or自下而上','theme_type':'基金主题分类'},inplace=True)
        plot=functionality.Plot(1200,600)
        # lable_info[lable_info['自上而下or自下而上'] == '自上而下'].groupby(['asofdate', '风格偏好']).count()[
        #     'jjdm'].reset_index().pivot_table('jjdm', 'asofdate', '风格偏好')
        plot.plotly_style_bar(style_exp.T,'偏股基金成长价值风格持仓权重时序%')
        plot.plotly_style_bar(size_exp.T, '偏股基金市值风格持仓权重时序%')

        lable_info['风格策略']=\
            "行业策略："+lable_info['一级行业策略']+"  个股策略："+lable_info['行业精选个股策略']
        lable_info['个股集中度'] = lable_info[['前三大', '前五大', '前十大']].sum(axis=1)
        for style in ['成长','价值']:
            temp_info=lable_info[lable_info['风格偏好']==style]
            stra_count = pd.merge(temp_info.groupby(['asofdate', '风格策略'])['jjdm'].count().reset_index(),
                                  temp_info.groupby(['asofdate'])['jjdm'].count().to_frame('count'),
                                  how='left', on='asofdate')
            stra_count['jjdm'] = stra_count['jjdm'] / stra_count['count']
            plot.plotly_style_bar(stra_count.pivot_table('jjdm','asofdate','风格策略'),'基金数量占比 按：{0}'.format('{}型基金风格策略'.format(style)))
            stra_ret=\
                (temp_info.groupby(['asofdate','风格策略'])['halfyearret'].mean().reset_index().pivot_table('halfyearret','asofdate','风格策略')+1).cumprod()
            stra_ret=pd.concat([stra_ret.iloc[[0]],stra_ret],axis=0)
            stra_ret.iloc[0]=1
            stra_ret.index=date_list

            plot.plotly_line_style(stra_ret,'基金收益率 按：{0}'.format('{}型基金风格策略'.format(style)))


        name_map=dict(zip(['cen_ind_1','cen_theme','ratio_ind_1','ratio_theme','longtou_mean','平均持有时间(出持仓前)','个股集中度','仓位换手率','换手率','stk_num', 'stk_mv_pct', 'stk_cap2_pct','逆向买入比例(出持仓前)','买入 PEG比例(出持仓前)','买入 ROE-PB比例(出持仓前)','左侧概率(出持仓前,半年线)']
                          ,['一级行业集中度','主题集中度','一级行业换手率','主题换手率','龙头占比(时序均值)','平均持有时间(天)','个股集中度','仓位换手率','换手率','同持仓基金个个数', '偏股基金平均持仓比例X10', '偏股基金资金占流通股比例','逆向买入比例','买入PEG比例','买入ROE-PB比例','左侧概率']))

        lable_info['stk_mv_pct']=lable_info['stk_mv_pct']*10
        plot.plotly_line_multi_yaxis_general(lable_info.groupby('asofdate')['stk_num', 'stk_mv_pct', 'stk_cap2_pct'].mean().rename(columns=name_map)
                              ,'市场抱团程度时序变动',['同持仓基金个个数'])

        all_the_time_jjdm_list=\
            lable_info.groupby('jjdm').count()['asofdate'][lable_info.groupby('jjdm').count()['asofdate']==lable_info.groupby('jjdm').count()['asofdate'].max()].index.tolist()

        for col in ['自上而下or自下而上','基金主题分类','PEG选股','PB-ROE选股','博弈基本面拐点','博弈估值修复','风格偏好',
                    '规模偏好','一级行业类型','左侧标签','是否抱团']:
            lable_info[col] = lable_info[col].fillna('其他')
            lable_info.loc[lable_info[col]=='',col] = '其他'
            stra_count=pd.merge(lable_info.groupby(['asofdate',col])['jjdm'].count().reset_index(),
                                lable_info.groupby(['asofdate'])['jjdm'].count().to_frame('count'),
            how='left',on='asofdate')
            stra_count['jjdm']=stra_count['jjdm']/stra_count['count']
            plot.plotly_style_bar(stra_count.pivot_table('jjdm','asofdate',col),'基金数量占比 按：{0}'.format(col))

            stra_ret=\
                (lable_info.groupby(['asofdate',col])['halfyearret'].mean().reset_index().pivot_table('halfyearret','asofdate',col)+1).cumprod()
            stra_ret=pd.concat([stra_ret.iloc[[0]],stra_ret],axis=0)
            stra_ret.iloc[0]=1
            stra_ret.index=date_list

            plot.plotly_line_style(stra_ret,'基金收益率 按：{0}'.format(col))

            temp = lable_info[lable_info['jjdm'].isin(all_the_time_jjdm_list)]
            temp=temp.groupby(['jjdm','asofdate'])[col].sum().reset_index()
            temp.rename(columns={col:'T0->T1标签转移概率'},inplace=True)
            col='T0->T1标签转移概率'
            temp['next_date'] = temp[col].iloc[1:].tolist() + [np.nan]
            temp=temp[temp['asofdate'] != temp['asofdate'].max()]
            temp = temp.groupby(['asofdate', col, 'next_date']).count()['jjdm'].reset_index()
            temp=pd.merge(temp,temp.groupby(['asofdate',col]).sum()['jjdm'],how='left',on=['asofdate',col])
            temp['ratio'] = temp['jjdm_x'] / temp['jjdm_y']
            temp=temp.groupby([col, 'next_date']).mean()['ratio'].reset_index().pivot_table('ratio',
                                                                                                        col,
                                                                                                        'next_date')
            for cols in temp.columns:
                temp[cols]=temp[cols].map("{:.2%}".format)
            plot.plotly_table(temp.reset_index(),1000,col+'标签转移矩阵')

        for col in ['cen_ind_1','cen_theme','ratio_ind_1','ratio_theme','longtou_mean']:


            plot.plotly_line_style(lable_info.groupby('asofdate')[col].mean().to_frame(name_map[col])
                                  ,name_map[col]+'时序变动')

            lable_info['分挡'] = '其他'
            lable_info.loc[lable_info[name_map[col]]>0.7,'分挡']='前30%'
            lable_info.loc[lable_info[name_map[col]]<0.3,'分挡']='后30%'

            stra_ret=\
                (lable_info.groupby(['asofdate', '分挡'])['halfyearret'].mean().reset_index().pivot_table('halfyearret','asofdate','分挡')+1).cumprod()
            stra_ret=pd.concat([stra_ret.iloc[[0]],stra_ret],axis=0)
            stra_ret.iloc[0]=1
            stra_ret.index=date_list
            plot.plotly_line_style(stra_ret, '基金收益率 按：{0}'.format(name_map[col]))

        for col in ['个股集中度','仓位换手率','平均持有时间(出持仓前)','换手率','逆向买入比例(出持仓前)','买入 PEG比例(出持仓前)','买入 ROE-PB比例(出持仓前)','左侧概率(出持仓前,半年线)']:


            plot.plotly_line_style(lable_info.groupby('asofdate')[col].mean().to_frame(name_map[col])
                                  ,name_map[col]+'时序变动')

            lable_info[name_map[col]]=\
                lable_info.groupby('asofdate')[col].rank(pct=True)
            lable_info['分挡'] = '其他'
            lable_info.loc[lable_info[name_map[col]]>0.7,'分挡']='前30%'
            lable_info.loc[lable_info[name_map[col]]<0.3,'分挡']='后30%'

            stra_ret=\
                (lable_info.groupby(['asofdate', '分挡'])['halfyearret'].mean().reset_index().pivot_table('halfyearret','asofdate','分挡')+1).cumprod()
            stra_ret=pd.concat([stra_ret.iloc[[0]],stra_ret],axis=0)
            stra_ret.iloc[0]=1
            stra_ret.index=date_list
            plot.plotly_line_style(stra_ret, '基金收益率 按：{0}'.format(name_map[col]))

        for stratage_name in ['基金主题分类','风格偏好','规模偏好','自上而下or自下而上']:

            self.get_portfolio_stratage_distribution(lable_info, stratage_name)

    @staticmethod
    def sample_funds_pic(ret_date):
        plot=functionality.Plot(1200,600)
        lable_info=pd.read_pickle('lable_info')
        lable_info=lable_info[lable_info['asofdate']==lable_info['asofdate'].max()]
        name_map=dict(zip(lable_info['jjdm'].tolist(),
                          lable_info['基金简称_x'].tolist()))


        def plot_sample_funds_ret(sample_funds,plot):
            sql = "select jjdm,zblb,zbnp from st_fund.t_st_gm_rqjhb where jjdm in ({0}) and zblb in('2103','2106','2998') and zbnp!=99999 and jzrq='{1}'" \
                .format(util.list_sql_condition(sample_funds['jjdm'].unique().tolist()), ret_date)
            sample_funds_ret = hbdb.db2df(sql, db='funduser').pivot_table('zbnp', 'jjdm', 'zblb').sort_values('2998',
                                                                                                              ascending=False).iloc[
                               0:3]
            sample_funds_ret.index = \
                [name_map[x] for x in sample_funds_ret.index]
            name_map2 = dict(zip(['index', '2103', '2106', '2998']
                                 , ['基金简称', '近3月', '近6月', '今年以来']))
            for col in sample_funds_ret.columns:
                sample_funds_ret[col] = sample_funds_ret[col].map("{:.2f}".format)

            plot.plotly_table(sample_funds_ret.reset_index().rename(columns=name_map2), 800, '')

        #top 2 down
        sample_funds=lable_info[(lable_info['个股风格B']=='自上而下')&
                                (lable_info['行业精选个股策略']=='成长')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['个股风格B']=='自上而下')&
                                (lable_info['博弈估值修复']=='博弈估值修复')&
                                (lable_info['PB-ROE选股']=='PB-ROE选股')]
        plot_sample_funds_ret(unsample_funds, plot)



        #down 2 top
        sample_funds=lable_info[(lable_info['个股风格B']=='自下而上')&(lable_info['是否抱团']=='抱团')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['个股风格B']=='自下而上')&(lable_info['是否抱团']=='逆向')]
        plot_sample_funds_ret(unsample_funds, plot)


        #value funds
        sample_funds=lable_info[(lable_info['风格偏好']=='价值')&
                                (lable_info['PB-ROE选股']=='PB-ROE选股')&
                                (lable_info['是否抱团']=='逆向')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['风格偏好']=='价值')&
                                (lable_info['是否抱团']=='抱团')]
        plot_sample_funds_ret(unsample_funds, plot)


        #growth funds
        sample_funds=lable_info[(lable_info['风格偏好']=='成长')&
                                (lable_info['行业精选个股策略']=='成长')&
                                (lable_info['是否抱团']=='抱团')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['风格偏好']=='成长')&
                                (lable_info['是否抱团']=='逆向')&
                                (lable_info['行业精选个股策略']=='价值')]
        plot_sample_funds_ret(unsample_funds, plot)


        #big funds
        sample_funds=lable_info[(lable_info['规模偏好']=='大盘')&
                                (lable_info['PB-ROE选股']=='PB-ROE选股')&
                                (lable_info['是否抱团']=='抱团')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['规模偏好']=='大盘')&
                                (lable_info['是否抱团']=='逆向')&
                                (lable_info['行业精选个股策略']=='成长')]
        plot_sample_funds_ret(unsample_funds, plot)



        #small funds
        sample_funds=lable_info[(lable_info['规模偏好']=='中小盘')&
                                (lable_info['是否抱团']=='逆向')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['规模偏好']=='中小盘')&
                                (lable_info['是否抱团']=='抱团')]
        plot_sample_funds_ret(unsample_funds, plot)


        #medic funds
        sample_funds=lable_info[(lable_info['theme_type']=='医药')&
                                (lable_info['行业精选个股策略']=='成长')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['theme_type']=='医药')&
                                (lable_info['是否抱团']=='逆向')&
                                  (lable_info['行业精选个股策略']=='价值')]
        plot_sample_funds_ret(unsample_funds, plot)

        #Big finance  funds
        sample_funds=lable_info[(lable_info['theme_type']=='大金融')&
                                (lable_info['行业精选个股策略']=='价值')&
                                (lable_info['是否抱团']=='逆向')&
                                (lable_info['PB-ROE选股']=='PB-ROE选股')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['theme_type']=='大金融')&
                                (lable_info['博弈估值修复']=='博弈估值修复')]
        plot_sample_funds_ret(unsample_funds, plot)


        #TMT  funds
        sample_funds=lable_info[(lable_info['theme_type']=='TMT')&
                                (lable_info['行业精选个股策略']=='成长')&
                                (lable_info['是否抱团']=='逆向')&
                                (lable_info['博弈基本面拐点']=='博弈基本面拐点')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['theme_type']=='TMT')&
                                  (lable_info['行业精选个股策略']=='价值')]
        plot_sample_funds_ret(unsample_funds, plot)

        #周期  funds
        sample_funds=lable_info[(lable_info['theme_type']=='周期')&
                                (lable_info['行业精选个股策略']=='价值')&
                                (lable_info['是否抱团']=='逆向')&
                                (lable_info['PB-ROE选股']=='PB-ROE选股')
                                &(lable_info['PEG选股']=='PEG选股')&
                                (lable_info['博弈基本面拐点']=='博弈基本面拐点')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['theme_type']=='周期')&
                                (lable_info['是否抱团']=='抱团')&
                                  (lable_info['博弈估值修复']=='博弈估值修复')]
        plot_sample_funds_ret(unsample_funds, plot)



        #消费  funds
        sample_funds=lable_info[(lable_info['theme_type']=='消费')&
                                (lable_info['是否抱团']=='抱团')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['theme_type']=='消费')&
                                (lable_info['是否抱团']=='逆向')]
        plot_sample_funds_ret(unsample_funds, plot)


        #manufacture  funds
        sample_funds=lable_info[(lable_info['theme_type']=='制造')&
                                (lable_info['是否抱团']=='抱团')&
                                (lable_info['博弈估值修复']=='博弈估值修复')]
        plot_sample_funds_ret(sample_funds, plot)


        unsample_funds=lable_info[(lable_info['theme_type']=='制造')&
                                (lable_info['是否抱团']=='逆向')&
                                  (lable_info['行业精选个股策略']=='价值')]
        plot_sample_funds_ret(unsample_funds, plot)

class stratage_timing():

    @staticmethod
    def cycle_detectoin(df,col_list,min_cycle=12):

        plot = functionality.Plot(1200, 600)

        from scipy.signal import argrelextrema

        for col in col_list:

            for i in argrelextrema(df[col].values,np.greater)[0].tolist():
                if(i>=min_cycle and i<len(df)-min_cycle):
                    if(df.loc[df.iloc[i].name][col]>=df[col].iloc[i-min_cycle:i].max() and
                            df.loc[df.iloc[i].name][col]>=df[col].iloc[i:i+min_cycle].max()):
                        df.loc[df.iloc[i].name,'{}_极值'.format(col)]=df.iloc[i][col]
                        # df.loc[df.iloc[i].name, '{}_flag'.format(col)] = 'max'
                elif(i<min_cycle):
                    if(df.loc[df.iloc[i].name][col]>=df[col].iloc[0:i].max() and
                            df.loc[df.iloc[i].name][col]>=df[col].iloc[i:i+min_cycle].max()):
                        df.loc[df.iloc[i].name,'{}_极值'.format(col)]=df.iloc[i][col]
                        # df.loc[df.iloc[i].name, '{}_flag'.format(col)] = 'max'
                else:
                    if(df.loc[df.iloc[i].name][col]>=df[col].iloc[0:i].max() and
                            df.loc[df.iloc[i].name][col]>=df[col].iloc[i:len(df)-1].max()):
                        df.loc[df.iloc[i].name,'{}_极值'.format(col)]=df.iloc[i][col]
                        # df.loc[df.iloc[i].name, '{}_flag'.format(col)] = 'max'



            for i in argrelextrema(df[col].values,np.less)[0].tolist():
                if(i>=min_cycle and i<len(df)-min_cycle):
                    if(df.loc[df.iloc[i].name][col]<=df[col].iloc[i-min_cycle:i].min() and
                            df.loc[df.iloc[i].name][col]<=df[col].iloc[i:i+min_cycle].min()):
                        df.loc[df.iloc[i].name,'{}_极值'.format(col)]=df.iloc[i][col]
                        # df.loc[df.iloc[i].name,'{}_flag'.format(col)]='min'
                elif(i<min_cycle):
                    if(df.loc[df.iloc[i].name][col]<=df[col].iloc[0:i].min() and
                            df.loc[df.iloc[i].name][col]<=df[col].iloc[i:i+min_cycle].min()):
                        df.loc[df.iloc[i].name,'{}_极值'.format(col)]=df.iloc[i][col]
                        # df.loc[df.iloc[i].name,'{}_flag'.format(col)]='min'
                else:
                    if(df.loc[df.iloc[i].name][col]<=df[col].iloc[i-min_cycle:i].min() and
                            df.loc[df.iloc[i].name][col]<=df[col].iloc[i:len(df)-1].min()):
                        df.loc[df.iloc[i].name,'{}_极值'.format(col)]=df.iloc[i][col]
                        # df.loc[df.iloc[i].name,'{}_flag'.format(col)]='min'



            tempdf=df[df[col+'_极值'].notnull()][[col+'_极值']].diff()
            for i in range(1,len(tempdf)):
                if(tempdf.loc[tempdf.index[i]][col+'_极值']>5):
                    df.loc[tempdf.index[i-1]:tempdf.index[i],col+'_bull']=df.loc[tempdf.index[i-1]:tempdf.index[i]][col]

                elif(tempdf.loc[tempdf.index[i]][col+'_极值']<-5):
                    df.loc[tempdf.index[i-1]:tempdf.index[i],col+'_bear']=df.loc[tempdf.index[i-1]:tempdf.index[i]][col]

                else:
                    df.loc[tempdf.index[i - 1]:tempdf.index[i], col + '_battle'] = \
                    df.loc[tempdf.index[i - 1]:tempdf.index[i]][col]

            plot.plotly_line_style(df[[col+'_bull',col+'_bear',col+'_battle']],col)

        plot.plotly_line_and_scatter(df[col_list + [x + "_极值" for x in col_list]]
                                     , 'test', line_col=col_list, scatter_col=[x + "_极值" for x in col_list])

    @staticmethod
    def hp_filter(y, lamb=10):
        def D_matrix(N):
            D = np.zeros((N - 1, N))
            D[:, 1:] = np.eye(N - 1)
            D[:, :-1] -= np.eye(N - 1)

            return D

        N = len(y)
        D1 = D_matrix(N)
        D2 = D_matrix(N - 1)
        D = D2 @ D1
        g = np.linalg.inv((np.eye(N) + lamb * D.T @ D)) @ y
        return g

    @staticmethod
    def trend_detection(df,col_list,rolling_window=12,ma1='3m',ma2='12m'):

        plot = functionality.Plot(1200, 600)


        index_list=df.index.tolist()
        for feature in col_list:

            df[ma2] = df[feature].rolling(int(ma2[:-1])).mean()
            df[ma1] = df[feature].rolling(int(ma1[:-1])).mean()
            # df[ma3] = df[feature].rolling(int(ma3[:-1])).mean()

            df[feature+'_bull'] = np.nan
            df[feature+'_bear'] = np.nan
            df.loc[((df[ma1] > df[ma2]) == True).rolling(rolling_window).sum() == rolling_window, feature+'_bull'] = \
                df[((df[ma1] > df[ma2]) == True).rolling(rolling_window).sum() == rolling_window][feature].values
            df.loc[((df[ma1] < df[ma2]) == True).rolling(rolling_window).sum() == rolling_window, feature+'_bear'] = \
                df[((df[ma1] < df[ma2]) == True).rolling(rolling_window).sum() == rolling_window][feature].values

            for col in [feature+'_bull',feature+'_bear']:
                temp_index_list=\
                    df[(df[col].diff().isnull())&(df[col].notnull())].index.to_list()+\
                    df[(df[col].diff(-1).isnull())&(df[col].notnull())].index.to_list()
                temp_index_list.sort()
                for i in range(int(len(temp_index_list)/2)):


                    index_med=index_list.index(temp_index_list[i*2])
                    index_start=index_list[index_med-rolling_window]
                    if("bull" in col):
                        if(df.loc[index_start:temp_index_list[i*2+1]][feature].max()-df.loc[index_start][feature]>df[feature].diff(rolling_window).abs().quantile(0.75)):
                            df.loc[index_start:temp_index_list[i*2+1],col] = \
                            df.loc[index_start:temp_index_list[i*2+1]][feature]
                        else:
                            df.loc[index_start:temp_index_list[i * 2 + 1], col]=np.nan
                    else:
                        if(df.loc[index_start:temp_index_list[i*2+1]][feature].min()-df.loc[index_start][feature]<-df[feature].diff(rolling_window).abs().quantile(0.75)):
                            df.loc[index_start:temp_index_list[i*2+1],col] = \
                            df.loc[index_start:temp_index_list[i*2+1]][feature]
                        else:
                            df.loc[index_start:temp_index_list[i * 2 + 1], col] = np.nan



            plot.plotly_line_style(df[[feature, feature+'_bull', feature+'_bear']], feature)

        return df

    @staticmethod
    def extram_points_detection(eco_data,col_list,min_cycle,if_remove_continue=False,draw_pic=True):

        from scipy.signal import argrelextrema

        for col in col_list:

            eco_data.loc[
                eco_data.iloc[argrelextrema(eco_data[col].values, np.greater)[
                    0].tolist()].index, col+'_flag'] = 'max'
            eco_data.loc[
                eco_data.iloc[argrelextrema(eco_data[col].values, np.less)[
                    0].tolist()].index, col+'_flag'] = 'min'

        for col in col_list:

            for i in argrelextrema(eco_data[col].values, np.greater)[0].tolist():
                if (i >= min_cycle and i < len(eco_data) - min_cycle):
                    if (eco_data.loc[eco_data.iloc[i].name][col] >= eco_data[col].iloc[i - min_cycle:i].max() and
                            eco_data.loc[eco_data.iloc[i].name][col] >= eco_data[col].iloc[i:i + min_cycle].max()):
                        eco_data.loc[eco_data.iloc[i].name, '{}_极值'.format(col)] = eco_data.iloc[i][col]
                        eco_data.loc[eco_data.iloc[i].name, '{}_flag'.format(col)] = 'max'
                elif (i < min_cycle):
                    if (eco_data.loc[eco_data.iloc[i].name][col] >= eco_data[col].iloc[0:i].max() and
                            eco_data.loc[eco_data.iloc[i].name][col] >= eco_data[col].iloc[i:i + min_cycle].max()):
                        eco_data.loc[eco_data.iloc[i].name, '{}_极值'.format(col)] = eco_data.iloc[i][col]
                        eco_data.loc[eco_data.iloc[i].name, '{}_flag'.format(col)] = 'max'
                else:
                    if (eco_data.loc[eco_data.iloc[i].name][col] >= eco_data[col].iloc[0:i].max() and
                            eco_data.loc[eco_data.iloc[i].name][col] >= eco_data[col].iloc[i:len(eco_data) - 1].max()):
                        eco_data.loc[eco_data.iloc[i].name, '{}_极值'.format(col)] = eco_data.iloc[i][col]
                        eco_data.loc[eco_data.iloc[i].name, '{}_flag'.format(col)] = 'max'

            for i in argrelextrema(eco_data[col].values, np.less)[0].tolist():
                if (i >= min_cycle and i < len(eco_data) - min_cycle):
                    if (eco_data.loc[eco_data.iloc[i].name][col] <= eco_data[col].iloc[i - min_cycle:i].min() and
                            eco_data.loc[eco_data.iloc[i].name][col] <= eco_data[col].iloc[i:i + min_cycle].min()):
                        eco_data.loc[eco_data.iloc[i].name, '{}_极值'.format(col)] = eco_data.iloc[i][col]
                        eco_data.loc[eco_data.iloc[i].name, '{}_flag'.format(col)] = 'min'
                elif (i < min_cycle):
                    if (eco_data.loc[eco_data.iloc[i].name][col] <= eco_data[col].iloc[0:i].min() and
                            eco_data.loc[eco_data.iloc[i].name][col] <= eco_data[col].iloc[i:i + min_cycle].min()):
                        eco_data.loc[eco_data.iloc[i].name, '{}_极值'.format(col)] = eco_data.iloc[i][col]
                        eco_data.loc[eco_data.iloc[i].name, '{}_flag'.format(col)] = 'min'
                else:
                    if (eco_data.loc[eco_data.iloc[i].name][col] <= eco_data[col].iloc[i - min_cycle:i].min() and
                            eco_data.loc[eco_data.iloc[i].name][col] <= eco_data[col].iloc[i:len(eco_data) - 1].min()):
                        eco_data.loc[eco_data.iloc[i].name, '{}_极值'.format(col)] = eco_data.iloc[i][col]
                        eco_data.loc[eco_data.iloc[i].name, '{}_flag'.format(col)] = 'min'
            if(if_remove_continue):
                #remove continuing max or min points
                temp=eco_data[eco_data[ '{}_极值'.format(col)].notnull()][[ '{}_极值'.format(col),'{}_flag'.format(col)]]
                temp[col+'_极值_lag1']=temp[ '{}_极值'.format(col)].iloc[1:].tolist()+[np.nan]
                temp[col+'_flag_lag1']=temp['{}_flag'.format(col)].iloc[1:].tolist()+[np.nan]
                temp=temp[temp['{}_flag'.format(col)] == temp[col+'_flag_lag1']]
                for index in temp.index.tolist():
                    if(temp.loc[index]['{}_flag'.format(col)]=='min'):
                        change_value=temp.loc[index][[ '{}_极值'.format(col),col+'_极值_lag1']].max()
                        eco_data.loc[(eco_data[ '{}_极值'.format(col)]==change_value)
                                           &(eco_data['{}_flag'.format(col)]=='min'),
                         '{}_极值'.format(col)]=np.nan
                    else:
                        change_value=temp.loc[index][[ '{}_极值'.format(col),col+'_极值_lag1']].min()
                        eco_data.loc[(eco_data[ '{}_极值'.format(col)]==change_value)
                                           &(eco_data['{}_flag'.format(col)]=='max'),
                         '{}_极值'.format(col)]=np.nan


        index_name=eco_data.index.name
        if(index_name is None):
            index_name='index'
        eco_data.reset_index(inplace=True)
        for col in col_list:
            print(col)
            print(eco_data[eco_data[col+'_flag'].notnull()].index.to_frame('test').diff().describe())
        eco_data.set_index(index_name,inplace=True)

        if(draw_pic):
            plot = functionality.Plot(1000, 500)
            plot.plotly_line_and_scatter(
                eco_data[col_list+[x+"_极值" for x in col_list]]
                , '周期变动', line_col=col_list,
                scatter_col=[x+"_极值" for x in col_list])
        return  eco_data

    def marco_eco_states_distinguish(self,start_date,end_date):


        def eco_advance_index(start_date,end_date):

            lamda=10
            min_cycle=18

            from sklearn import preprocessing as pp

            #get wind data
            from WindPy import w


            w.start()
            eco_data=w.edb("S0073293,S0073300,S0030326,M0000076,S0027013,S0027100,S0027908,S0028203,S6001313,M0001633",
                  start_date, end_date, "Period=M;Fill=Previous",usedf=True)[1]
            eco_data.columns=\
                ['房屋新开工面积累计同比','商品房销售面积累计同比','全国主要港口货物吞吐量累计同比','工业增加值同比','发电量当月同比','产量氢氧化钠同比',
                 '产量汽车同比','产量空调同比','销量挖掘机同比','中长期消费贷款']
            eco_data['中长期消费贷款']=eco_data['中长期消费贷款'].pct_change()*100
            eco_data=eco_data.iloc[1:].fillna(method='bfill')


            for col in eco_data.columns:
                eco_data[col]=self.hp_filter(eco_data[col],lamda)
                eco_data[col]=eco_data[col].diff()/eco_data[col].diff()[eco_data[col].diff().abs()<95].abs().mean()
                eco_data[col]=pp.StandardScaler().fit_transform(eco_data[col].values.reshape(-1,1))


            eco_data['advance_index']=eco_data.fillna(0).mean(axis=1).cumsum()

            temp=w.edb("M0000612, M0001227",
                  start_date, end_date, "Period=M;Fill=Previous",usedf=True)[1]
            w.stop()
            eco_data['inflation_index']=0.8*self.hp_filter(temp['M0000612'],lamda)[1:]+0.3*self.hp_filter(temp['M0001227'],lamda)[1:]

            eco_data=\
                self.extram_points_detection(eco_data, ['advance_index','inflation_index'], min_cycle,draw_pic=False)

            advance_index=eco_data[eco_data['advance_index_极值'].notnull()]['advance_index_flag']
            lag_index=eco_data[eco_data['inflation_index_极值'].notnull()]['inflation_index_flag']
            eco_cycle =pd.DataFrame()
            cycle_start=[]
            cycle_end=[]
            name=[]
            for i in  range(len(advance_index)) :


                flag=advance_index.iloc[i]

                if(i>0):

                    if(flag=='max' and last_lag=='min'):
                        cycle_start.append(last_lag_time)
                        cycle_end.append(advance_index.index[i])
                        name.append('过热')
                    elif(flag=='min' and last_lag=='max'):
                        name.append('衰退')
                        cycle_start.append(last_lag_time)
                        cycle_end.append(advance_index.index[i])
                    else:
                        cycle_start.append(advance_index.index[i-1])
                        cycle_end.append(advance_index.index[i])
                        if(flag=='max'):
                            name.append('过热')
                        else:
                            name.append('衰退')



                if(i<len(advance_index)-1):
                    lag_info=lag_index.loc[advance_index.index[i]:advance_index.index[i+1]]
                    if(len(lag_info)>0):
                        cycle_start.append(advance_index.index[i])
                        if(flag=='max' and lag_info.values[0]=='max'):
                            cycle_end.append(lag_info.index[0])
                            name.append('滞胀')
                            last_lag_time=lag_info.index[0]
                            last_lag='max'
                        elif(flag=='min' and lag_info.values[0]=='min'):
                            cycle_end.append(lag_info.index[0])
                            name.append('复苏')
                            last_lag_time=lag_info.index[0]
                            last_lag='min'


            eco_cycle['start_date']=cycle_start
            eco_cycle['end_date'] = cycle_end
            eco_cycle['scenario'] = name

            eco_cycle['start_date'] =[util._shift_date(str(x)) for x in eco_cycle['start_date'].astype(str).str.replace('-','')]
            eco_cycle['end_date'] = [util._shift_date(str(x)) for x in eco_cycle['end_date'].astype(str).str.replace('-','')]


            sql="select zqdm,spjg,jyrq from st_market.t_st_zs_hq where zqdm in ('000906','CI0077','H11001') and jyrq in ({})"\
                .format(util.list_sql_condition(list(set(eco_cycle['start_date'].tolist()+eco_cycle['end_date'].tolist()))))
            asset_ret=hbdb.db2df(sql,db='alluser').pivot_table('spjg','jyrq','zqdm')
            asset_ret.index=asset_ret.index.astype(str)
            eco_cycle=pd.merge(eco_cycle,asset_ret,how='left',
                               left_on='start_date',right_on='jyrq')
            eco_cycle=pd.merge(eco_cycle,asset_ret,how='left',
                               left_on='end_date',right_on='jyrq')
            for col in ['000906','CI0077','H11001']:
                eco_cycle[col]=eco_cycle[col+'_y']/eco_cycle[col+'_x']-1

            eco_cycle['cash']=0


            plot_data=eco_data[['advance_index', 'inflation_index']]
            upper_bound=eco_data['inflation_index'].max()
            for sc in eco_cycle['scenario'].unique():
                plot_data[sc]=np.nan
                temp_scen=eco_cycle[eco_cycle['scenario']==sc]
                for i in range(len(temp_scen)):
                    s_date=\
                        datetime.datetime.strptime(temp_scen.iloc[i]['start_date'], '%Y%m%d')
                    s_date=datetime.date(s_date.year, s_date.month, s_date.day)

                    e_date=\
                        datetime.datetime.strptime(temp_scen.iloc[i]['end_date'], '%Y%m%d')
                    e_date=datetime.date(e_date.year, e_date.month, e_date.day)

                    plot_data.loc[s_date:plot_data.index[plot_data.index<e_date][-1],sc]=upper_bound


            plot=functionality.Plot(1200,600)
            plot_data.rename(columns={'advance_index':'经济领先指标','inflation_index':'经济滞后指标'},inplace=True)
            data, layout=plot.plotly_line_and_area(plot_data,line_col=['经济领先指标', '经济滞后指标'],
                                      area_col=eco_cycle['scenario'].unique().tolist(),title_text='宏观经济周期',left_axis_name='',right_axis_name='')
            plot.plot_render(data, layout)

            return  eco_cycle[['start_date', 'end_date', 'scenario','000906', 'CI0077',
       'H11001']]


        eco_data=eco_advance_index(start_date, end_date)

    def currency_states_distinguish(self,start_date,end_date):

        from WindPy import w
        from scipy.signal import argrelextrema
        w.start()
        eco_data = w.edb("M0001381,M0001383,M0001385,M5525763,M0041371,M0010075,M0325687",
                         start_date, end_date, "Period=M;Fill=Previous", usedf=True)[1]
        eco_data.columns = \
            ['M0同比', 'M1同比', 'M2同比', '社融同比','OMO7D','R007','10年期国债到期收益率']
        eco_data['ym'] = [str(x.year) + str(x.month) for x in eco_data.index.to_list()]
        eco_data=eco_data.drop_duplicates('ym', keep='last').drop('ym',axis=1)

        eco_data['社融-M2']=self.hp_filter(eco_data['社融同比']-eco_data['M2同比'],lamb=0.1)
        eco_data['M2-M1'] = self.hp_filter(eco_data['M2同比'] - eco_data['M1同比'],lamb =1)
        # eco_data['社融-M2']=eco_data['社融同比']-eco_data['M2同比']
        # eco_data['M2-M1'] = eco_data['M2同比'] - eco_data['M1同比']
        eco_data['流动性溢价'] = self.hp_filter(eco_data['R007'] - eco_data['OMO7D'])
        eco_data['M2同比']=self.hp_filter(eco_data['M2同比'] )
        eco_data['10年期国债到期收益率']=self.hp_filter(eco_data['10年期国债到期收益率'].fillna(method='bfill'))

        eco_data=self.trend_detection(eco_data,col_list=['社融-M2','M2-M1'],ma1='3m',ma2='12m',rolling_window=6)

        plot=functionality.Plot(1200,600)
        plot.plotly_line_style(eco_data[['社融-M2','M2-M1']+[x+'_bull' for x in ['社融-M2','M2-M1']]+[x+'_bear' for x in ['社融-M2','M2-M1']]],'流动性')


        sql="select tjyf,hb1y from st_market.t_st_zs_yhb where zqdm='881001' and tjyf>='{0}' and tjyf<='{1}'"\
            .format(eco_data.index.astype(str)[int('12m'[:-1])].replace('-','')[0:6],end_date.replace('-',''))
        market_ret=hbdb.db2df(sql,db='alluser')
        market_ret['tjyf']=market_ret['tjyf'].astype(str)

        summary=pd.DataFrame()
        scenario=[]
        mean=[]
        count=[]

        eco_data.loc[(eco_data['社融-M2_bull'].notnull())
                         |(eco_data['社融-M2_bear'].notnull()),'社融-M2']=np.nan
        eco_data.loc[(eco_data['M2-M1_bull'].notnull())
                     | (eco_data['M2-M1_bear'].notnull()), 'M2-M1'] = np.nan

        for stats1 in ['社融-M2','社融-M2_bull', '社融-M2_bear']:
            for stats2 in ['M2-M1', 'M2-M1_bull', 'M2-M1_bear']:

                count.append(len(eco_data[(eco_data[stats1].notnull())
                         &(eco_data[stats2].notnull())&(eco_data.index>=eco_data.index[12])]))
                scenario.append(stats1+'+'+stats2)
                mean.append( ((market_ret[market_ret['tjyf'].isin(eco_data[(eco_data[stats1].notnull())
                                                 & (eco_data[stats2].notnull())].index.astype(str).str.replace('-','').str[0:6].tolist())]['hb1y']/100).mean()))
        summary['scenario']=scenario
        summary['mean'] = mean
        summary['count'] = count
        summary.sort_values('mean',inplace=True,ascending=False)

        plot.plotly_table(summary,table_width=1200,title_text='')

        # plot.plotly_line_style(eco_data[['10年期国债到期收益率']],'利率')
        # plot.plotly_line_style(eco_data[['流动性溢价']],'流动性溢价')

    def market_states_distinguish(self,start_date,end_date,market_index='881001'):

        sql="select jyrq,spjg as `万得全A` from st_market.t_st_zs_hq where zqdm='{2}' and jyrq>={0} and jyrq<={1}"\
            .format(start_date,end_date,market_index)
        market_data=hbdb.db2df(sql,db='alluser').set_index('jyrq')
        market_data.index=market_data.index.astype(str)
        market_data['ym']=market_data.index.str[0:6]
        market_data.drop_duplicates('ym',keep='last',inplace=True)

        market_data=self.trend_detection(market_data, ['万得全A'], rolling_window=6, ma1='6m', ma2='12m')

        market_data['market_trend']=0
        market_data.loc[market_data['万得全A_bull'].notnull(),'market_trend']=1
        market_data.loc[market_data['万得全A_bear'].notnull(), 'market_trend'] = -1


        tempdf=market_data[market_data['market_trend'].diff()!=0]
        market_cycle=pd.DataFrame()
        market_cycle['start_date']=tempdf.index[1:]
        market_cycle['end_date']=tempdf.index[2:].tolist()+[market_data.index[-1]]

        market_cycle.loc[0,'states']='牛尾熊始'
        market_cycle.loc[0, 'states2'] = '熊'
        for i in range(1,len(market_cycle)):
            date=market_cycle['start_date'][i]
            if(market_cycle.loc[i-1]['states2']=='熊'):
                if(tempdf.loc[date]['market_trend']==0 and market_cycle.loc[i-1]['states']!='大熊市'):
                    market_cycle.loc[i,'states']='熊中震荡'
                    market_cycle.loc[i, 'states2'] = '熊'
                elif(tempdf.loc[date]['market_trend']==-1 and market_cycle.loc[i-1]['states']!='大熊市'):
                    market_cycle.loc[i,'states']='大熊市'
                    market_cycle.loc[i, 'states2'] = '熊'
                elif (tempdf.loc[date]['market_trend'] == 1 and market_cycle.loc[i - 1]['states'] != '大熊市'):
                    market_cycle.loc[i, 'states'] = '熊中反弹'
                    market_cycle.loc[i, 'states2'] = '熊'
                elif (tempdf.loc[date]['market_trend'] == 1 and market_cycle.loc[i - 1]['states'] == '大熊市'):
                    market_cycle.loc[i, 'states'] = '牛市高潮'
                    market_cycle.loc[i, 'states2'] = '牛'
                elif (tempdf.loc[date]['market_trend'] == 0 and market_cycle.loc[i - 1]['states'] == '大熊市'):
                    market_cycle.loc[i, 'states'] = '熊牛转折'
                    market_cycle.loc[i, 'states2'] = '牛'
            else:
                if(tempdf.loc[date]['market_trend']==1 ):
                    market_cycle.loc[i,'states']='牛市高潮'
                    market_cycle.loc[i, 'states2'] = '牛'
                elif(tempdf.loc[date]['market_trend']==-1 ):
                    market_cycle.loc[i,'states']='牛尾熊始'
                    market_cycle.loc[i, 'states2'] = '熊'

        upper_bound = market_data['万得全A'].max()
        for sc in market_cycle['states'].unique():
            market_data[sc]=np.nan
            temp_scen=market_cycle[market_cycle['states']==sc]
            for i in range(len(temp_scen)):
                s_date=temp_scen.iloc[i]['start_date']
                e_date=temp_scen.iloc[i]['end_date']
                market_data.loc[s_date:market_data.index[market_data.index<e_date][-1],sc]=upper_bound

        plot = functionality.Plot(1200, 600)
        data, layout = plot.plotly_line_and_area(market_data[['万得全A', '万得全A_bull', '万得全A_bear',
                                                              '牛尾熊始', '熊中反弹', '熊中震荡', '大熊市', '熊牛转折', '牛市高潮']], line_col=['万得全A', '万得全A_bull', '万得全A_bear'],
                                                 area_col=market_cycle['states'].unique().tolist(),
                                                 title_text='A股周期', left_axis_name='', right_axis_name='')
        plot.plot_render(data, layout)

    def market_style_distinguish(self,start_date,end_date):

        sql="select jyrq,spjg,zqdm from st_market.t_st_zs_hq where zqdm in ('399370','399371','399314','399315','399316') and jyrq>={0} and jyrq<={1}"\
            .format(start_date,end_date)
        market_data=hbdb.db2df(sql,db='alluser').pivot_table('spjg','jyrq','zqdm')
        market_data.index=market_data.index.astype(str)

        market_data['ym']=market_data.index.str[0:6]
        market_data.drop_duplicates('ym',keep='last',inplace=True)
        market_data.drop('ym',axis=1,inplace=True)

        # make the initial point to be 1
        for col in market_data.columns:
            market_data[col]=market_data[col]/market_data[col].iloc[0]

        market_data['成长-价值']=market_data['399370']-market_data['399371']
        market_data['大盘-小盘']=market_data['399314']-market_data['399316']

        #a small rolling window means that the resutl is more sensitive to short-term shock while has less lag
        market_data=self.trend_detection(market_data, ['成长-价值','大盘-小盘'], rolling_window=3, ma1='3m', ma2='12m')

        market_data['market_trend'] = 0
        market_data.loc[market_data['成长-价值_bull'].notnull(), 'market_trend'] = 1
        market_data.loc[market_data['成长-价值_bear'].notnull(), 'market_trend'] = -1

        tempdf = market_data[market_data['market_trend'].diff() != 0]
        market_cycle = pd.DataFrame()
        market_cycle['start_date'] = tempdf.index[1:]
        market_cycle['end_date'] = tempdf.index[2:].tolist() + [market_data.index[-1]]

        for i in range(len(market_cycle)):
            start_date=market_cycle.iloc[i]['start_date']
            if(tempdf.loc[start_date]['market_trend']==1):
                market_cycle.loc[i,'states']='成长占优'
            elif(tempdf.loc[start_date]['market_trend']==-1):
                market_cycle.loc[i,'states']='价值占优'
            else:
                market_cycle.loc[i, 'states'] = '风格均势'

        upper_bound = market_data['成长-价值'].max()
        for sc in market_cycle['states'].unique():
            market_data[sc]=np.nan
            temp_scen=market_cycle[market_cycle['states']==sc]
            for i in range(len(temp_scen)):
                s_date=temp_scen.iloc[i]['start_date']
                e_date=temp_scen.iloc[i]['end_date']
                market_data.loc[s_date:market_data.index[market_data.index<e_date][-1],sc]=upper_bound

        plot = functionality.Plot(1200, 600)
        data, layout = plot.plotly_line_and_area(market_data[['成长-价值', '成长-价值_bull', '成长-价值_bear',
                                                              '成长占优', '价值占优', '风格均势']], line_col=['成长-价值', '成长-价值_bull', '成长-价值_bear'],
                                                 area_col=market_cycle['states'].unique().tolist(),
                                                 title_text='A股成长价值风格周期', left_axis_name='', right_axis_name='')
        plot.plot_render(data, layout)




        market_data['market_trend'] = 0
        market_data.loc[market_data['大盘-小盘_bull'].notnull(), 'market_trend'] = 1
        market_data.loc[market_data['大盘-小盘_bear'].notnull(), 'market_trend'] = -1

        tempdf = market_data[market_data['market_trend'].diff() != 0]
        market_cycle = pd.DataFrame()
        market_cycle['start_date'] = tempdf.index[1:]
        market_cycle['end_date'] = tempdf.index[2:].tolist() + [market_data.index[-1]]

        for i in range(len(market_cycle)):
            start_date=market_cycle.iloc[i]['start_date']
            if(tempdf.loc[start_date]['market_trend']==1):
                market_cycle.loc[i,'states']='大盘占优'
            elif(tempdf.loc[start_date]['market_trend']==-1):
                market_cycle.loc[i,'states']='中小盘占优'
            else:
                market_cycle.loc[i, 'states'] = '风格均势'

        upper_bound = market_data['大盘-小盘'].max()
        for sc in market_cycle['states'].unique():
            market_data[sc]=np.nan
            temp_scen=market_cycle[market_cycle['states']==sc]
            for i in range(len(temp_scen)):
                s_date=temp_scen.iloc[i]['start_date']
                e_date=temp_scen.iloc[i]['end_date']
                market_data.loc[s_date:market_data.index[market_data.index<e_date][-1],sc]=upper_bound

        plot = functionality.Plot(1200, 600)
        data, layout = plot.plotly_line_and_area(market_data[['大盘-小盘', '大盘-小盘_bull', '大盘-小盘_bear',
                                                              '大盘占优', '中小盘占优', '风格均势']], line_col=['大盘-小盘', '大盘-小盘_bull', '大盘-小盘_bear'],
                                                 area_col=market_cycle['states'].unique().tolist(),
                                                 title_text='A股市值风格周期', left_axis_name='', right_axis_name='')
        plot.plot_render(data, layout)

    def market_liquidity(self,start_date,end_date):

        plot=functionality.Plot(1200,600)


        from WindPy import w
        w.start()
        liquidity_data = w.edb("M0061608,M0061613,,M0329497,M0329499,M0329501,M0329505,M0331255,M0340746,M0060433",
                         start_date, end_date,  usedf=True)[1]
        liquidity_data.columns=['沪市融资融券余额','深市融资融券余额',
                                '沪股通流入(亿元)','深股通流入(亿元)','沪市港股通(亿元)','深市港股通(亿元)',
                                '沪市成交额','深市成交额','新成立基金份额(亿)']

        liquidity_data['两市融资融券余额(亿元)']=liquidity_data['沪市融资融券余额']+liquidity_data['深市融资融券余额']
        liquidity_data['两市成交额(亿元)']=liquidity_data['沪市成交额']+liquidity_data['深市成交额']
        liquidity_data['北向净流入(亿元)']=liquidity_data['沪股通流入(亿元)']+liquidity_data['深股通流入(亿元)']
        liquidity_data['南向净流出(亿元)']=liquidity_data['沪市港股通(亿元)']+liquidity_data['深市港股通(亿元)']

        #change all unit to 亿元
        liquidity_data[['两市融资融券余额(亿元)']]=\
            liquidity_data[['两市融资融券余额(亿元)']]/10000
        w.stop()



        liquidity_data['ym']=liquidity_data.index.astype(str).str.replace('-','').str[0:6]
        liquidity_data=liquidity_data.groupby('ym').sum()


        liquidity_data = self.trend_detection(liquidity_data, ['两市融资融券余额(亿元)','两市成交额(亿元)'], rolling_window=6, ma1='3m',
                                           ma2='12m')


        liquidity_data['新成立基金份额(亿)']=self.hp_filter(liquidity_data['新成立基金份额(亿)'])

        liquidity_data = \
            self.extram_points_detection(liquidity_data, ['新成立基金份额(亿)'], 6,if_remove_continue=True)


        threshold=liquidity_data['新成立基金份额(亿)'].diff(6).abs().quantile(0.75)
        upperbound=liquidity_data['新成立基金份额(亿)'].max()
        temp=liquidity_data[liquidity_data['新成立基金份额(亿)_极值'].notnull()]
        liquidity_data[['扩张','收缩','横盘']]=np.nan
        for i in range(1,len(temp)):
            if(temp.iloc[i]['新成立基金份额(亿)_极值']-temp.iloc[i-1]['新成立基金份额(亿)_极值']
                    >=threshold):
                liquidity_data.loc[temp.index[i-1]:liquidity_data.index[liquidity_data.index<temp.index[i]][-1],'扩张']=upperbound
            elif (temp.iloc[i]['新成立基金份额(亿)_极值'] - temp.iloc[i - 1]['新成立基金份额(亿)_极值']
                    <= -threshold):
                liquidity_data.loc[
                temp.index[i - 1]:liquidity_data.index[liquidity_data.index < temp.index[i]][-1],
                '收缩'] = upperbound
            else:
                liquidity_data.loc[
                temp.index[i - 1]:liquidity_data.index[liquidity_data.index < temp.index[i]][-1],
                '横盘'] = upperbound


        data,layout=plot.plotly_line_and_area(liquidity_data[['新成立基金份额(亿)','扩张','收缩','横盘']],
                                  title_text='新发基金募资量周期',
                                  line_col=['新成立基金份额(亿)'],area_col=['扩张','收缩','横盘'],left_axis_name='',right_axis_name='')
        plot.plot_render(data,layout)

        liquidity_data=liquidity_data[liquidity_data['北向净流入(亿元)']!=0]
        liquidity_data['北向净流入(亿元)']=self.hp_filter(liquidity_data['北向净流入(亿元)'],1)

        liquidity_data = \
            self.extram_points_detection(liquidity_data, ['北向净流入(亿元)'], 3,if_remove_continue=True,draw_pic=False)


        upperbound=liquidity_data['北向净流入(亿元)'].max()
        temp=liquidity_data[liquidity_data['北向净流入(亿元)_极值'].notnull()]
        liquidity_data[['扩张','收缩']]=np.nan
        for i in range(1,len(temp)):
            if(temp.iloc[i]['北向净流入(亿元)_极值']-temp.iloc[i-1]['北向净流入(亿元)_极值']
                    >=0):
                liquidity_data.loc[temp.index[i-1]:liquidity_data.index[liquidity_data.index<temp.index[i]][-1],'扩张']=upperbound
            elif (temp.iloc[i]['北向净流入(亿元)_极值'] - temp.iloc[i - 1]['北向净流入(亿元)_极值']
                    <= 0):
                liquidity_data.loc[
                temp.index[i - 1]:liquidity_data.index[liquidity_data.index < temp.index[i]][-1],
                '收缩'] = upperbound



        data,layout=plot.plotly_line_and_area(liquidity_data[['北向净流入(亿元)','扩张','收缩']],
                                  title_text='北向资金周期',
                                  line_col=['北向净流入(亿元)'],area_col=['扩张','收缩'],left_axis_name='',right_axis_name='')
        plot.plot_render(data,layout)


        

        liquidity_data['中轨']=liquidity_data['北向净流入(亿元)'].rolling(12).mean()
        liquidity_data['上轨']=liquidity_data['中轨']+liquidity_data['北向净流入(亿元)'].rolling(12).std()*2
        liquidity_data['下轨']=liquidity_data['中轨']-liquidity_data['北向净流入(亿元)'].rolling(12).std()*2


        plot.plotly_line_and_scatter(liquidity_data[['北向净流入(亿元)', '中轨','上轨','下轨','北向净流入(亿元)_极值']]
                                     ,'北向净流入',line_col=['北向净流入(亿元)', '中轨','上轨','下轨'],scatter_col=['北向净流入(亿元)_极值'])

    def industry_states_distinguish(self,start_date,end_date):

        sql = "select zqdm,hb1y,tjyf from st_market.t_st_zs_yhb where zqdm in ({0}) and tjyf>='{1}' and tjyf<='{2}'" \
            .format(util.list_sql_condition(['801010', '801030', '801040', '801050', '801080', '801110',
                                             '801120', '801130', '801140', '801150', '801160', '801170',
                                             '801180', '801200', '801210', '801230', '801710', '801720',
                                             '801730', '801740', '801750', '801760', '801770', '801780',
                                             '801790', '801880', '801890', '801950', '801960', '801970', '801980']),
                    start_date[0:6],end_date[0:6])
        ind_month_ret = hbdb.db2df(sql, db='alluser')

        ind_states_data=ind_month_ret.groupby('tjyf').skew()['hb1y'].to_frame('行业偏度')
        ind_month_ret['rank']=ind_month_ret.groupby('tjyf')['hb1y'].rank()
        index_list=ind_month_ret['tjyf'].tolist()
        ind_month_ret=ind_month_ret.pivot_table('rank', 'zqdm', 'tjyf')
        for i in range(1,len(index_list)):
            ind_states_data.loc[index_list[i],'行业排名稳定性']=\
                ind_month_ret[[index_list[i],index_list[i-1]]].corr()[index_list[i]].iloc[1]


        plot=functionality.Plot(1200,600)
        ind_states_data.index=ind_states_data.index.astype(str)

        ind_states_data['行业偏度']=self.hp_filter(ind_states_data['行业偏度'],5)
        ind_states_data['行业排名稳定性']=self.hp_filter(ind_states_data['行业排名稳定性'],5)
        ind_states_data=self.extram_points_detection(ind_states_data,col_list=['行业偏度','行业排名稳定性'],
                                                     min_cycle=6,if_remove_continue=True,draw_pic=False)

        upperbound=ind_states_data['行业排名稳定性'].max()
        temp=ind_states_data[ind_states_data['行业排名稳定性_极值'].notnull()]
        ind_states_data[['趋势保持','趋势反转']]=np.nan
        for i in range(1,len(temp)):
            if(temp.iloc[i]['行业排名稳定性_极值']-temp.iloc[i-1]['行业排名稳定性_极值']
                    >=0):
                if(temp.iloc[i]['行业排名稳定性_极值']>0):
                    ind_states_data.loc[temp.index[i-1]:ind_states_data.index[ind_states_data.index<temp.index[i]][-1],'趋势保持']=upperbound
                else:
                    ind_states_data.loc[
                    temp.index[i - 1]:ind_states_data.index[ind_states_data.index < temp.index[i]][-1],
                    '趋势反转'] = upperbound

            elif (temp.iloc[i]['行业排名稳定性_极值'] - temp.iloc[i - 1]['行业排名稳定性_极值']
                    <= 0):
                if(temp.iloc[i]['行业排名稳定性_极值']<0):
                    ind_states_data.loc[
                    temp.index[i - 1]:ind_states_data.index[ind_states_data.index < temp.index[i]][-1],
                    '趋势反转'] = upperbound
                else:
                    ind_states_data.loc[temp.index[i-1]:ind_states_data.index[ind_states_data.index<temp.index[i]][-1],'趋势保持']=upperbound


        data, layout = plot.plotly_line_and_area(ind_states_data[['行业排名稳定性','趋势保持','趋势反转']],title_text='行业排名稳定性',
                                  line_col=['行业排名稳定性'],area_col=['趋势保持','趋势反转'],left_axis_name='',right_axis_name='')
        plot.plot_render(data, layout)

        upperbound=ind_states_data['行业偏度'].max()
        temp=ind_states_data[ind_states_data['行业偏度_极值'].notnull()]
        ind_states_data[['主线清晰化','主线模糊化']]=np.nan
        for i in range(1,len(temp)):
            if(temp.iloc[i]['行业偏度_极值']-temp.iloc[i-1]['行业偏度_极值']
                    >=0):
                ind_states_data.loc[temp.index[i-1]:ind_states_data.index[ind_states_data.index<temp.index[i]][-1],'主线清晰化']=upperbound
            elif (temp.iloc[i]['行业偏度_极值'] - temp.iloc[i - 1]['行业偏度_极值']
                    <= 0):
                ind_states_data.loc[
                temp.index[i - 1]:ind_states_data.index[ind_states_data.index < temp.index[i]][-1],
                '主线模糊化'] = upperbound

        ind_states_data['偏度显著阈值']=0.5
        data, layout = plot.plotly_line_and_area(ind_states_data[['行业偏度','主线清晰化','主线模糊化','偏度显著阈值']],title_text='行业偏度',
                                  line_col=['行业偏度','偏度显著阈值'],area_col=['主线清晰化','主线模糊化'],left_axis_name='',right_axis_name='')

        plot.plot_render(data, layout)


    def stratage_cycle_distinguish(self,today):


        lable_info=pd.read_pickle('lable_info')

        lable_info.loc[lable_info['换手率'] > 8, '换手率']=np.nan
        lable_info.loc[lable_info['换手率'] < 0, '换手率'] = np.nan

        lable_info.rename(columns={'个股风格B':'自上而下or自下而上','theme_type':'基金主题分类'},inplace=True)
        plot=functionality.Plot(1200,600)

        lable_info['风格策略']=\
            "行业策略："+lable_info['一级行业策略']+"  个股策略："+lable_info['行业精选个股策略']
        lable_info['个股集中度'] = lable_info[['前三大', '前五大', '前十大']].sum(axis=1)


        all_the_time_jjdm_list=\
            lable_info.groupby('jjdm').count()['asofdate'][lable_info.groupby('jjdm').count()['asofdate']==lable_info.groupby('jjdm').count()['asofdate'].max()].index.tolist()

        sql="select jjdm,tjyf,hb1y from st_fund.t_st_gm_yhb where jjdm in ({}) and tjyf>'201812' and hb1y!=99999"\
            .format(util.list_sql_condition(all_the_time_jjdm_list))
        fund_month_ret=hbdb.db2df(sql,db='funduser')
        ret_date_list=fund_month_ret['tjyf'].unique().tolist()
        ret_date_list.sort()

        lable_info.loc[lable_info['asofdate'].str.contains('03'),'asofdate']= \
            (lable_info[lable_info['asofdate'].str.contains('03')]['asofdate'].str[0:4].astype(int) - 1).astype(
                str) + '12'
        lable_info.loc[lable_info['asofdate'].str.contains('09'),'asofdate']= \
            lable_info[lable_info['asofdate'].str.contains('09')]['asofdate'].str[0:4] + '06'

        date_list=lable_info['asofdate'].unique().tolist()+[today]
        date_list.sort()

        bmk=[]
        for i in range(len(date_list)-1):

            temp_jjdm_list=lable_info[lable_info['asofdate']==date_list[i]]['jjdm'].unique().tolist()
            bmk.append((fund_month_ret[(fund_month_ret['jjdm'].isin(temp_jjdm_list))
                           &(fund_month_ret['tjyf']>int(date_list[i]))&(fund_month_ret['tjyf']<=int(date_list[i+1]))]).groupby('tjyf').mean()[['hb1y']])

        bmk=pd.concat(bmk,axis=0)
        bmk=(bmk/100+1).cumprod()
        bmk.loc[int(date_list[0]),'hb1y']=1
        bmk=bmk.sort_index()

        for big_s in ['风格偏好','规模偏好','一级行业类型','自上而下or自下而上','PB-ROE选股',
                      'PEG选股', '博弈基本面拐点', '博弈估值修复', '是否抱团','一级行业策略', '行业精选个股策略']:
            for stratage in lable_info[big_s].unique():
                if(stratage is None):
                    continue
                print(stratage)
                stratage_ret = []
                for i in range(len(date_list) - 1):
                    temp_jjdm_list = lable_info[(lable_info['asofdate'] == date_list[i])
                                                &(lable_info[big_s] == stratage)]['jjdm'].unique().tolist()
                    stratage_ret.append((fund_month_ret[(fund_month_ret['jjdm'].isin(temp_jjdm_list))
                                               & (fund_month_ret['tjyf'] > int(date_list[i])) & (
                                                           fund_month_ret['tjyf'] <= int(date_list[i + 1]))]).groupby(
                        'tjyf').mean()[['hb1y']])

                stratage_ret = pd.concat(stratage_ret, axis=0)
                stratage_ret = (stratage_ret / 100 + 1).cumprod()
                stratage_ret.loc[int(date_list[0]), 'hb1y'] = 1
                stratage_ret = stratage_ret.sort_index()
                stratage_ret.index=stratage_ret.index.astype(str)
                stratage_ret=stratage_ret-bmk.values
                stratage_ret['hb1y']=self.hp_filter(stratage_ret['hb1y'],1)
                stratage_ret=self.extram_points_detection(stratage_ret, ['hb1y'], 6, if_remove_continue=True,draw_pic=False)

                stratage_ret.loc[stratage_ret.index[0],'hb1y_极值']=stratage_ret.iloc[0]['hb1y']
                stratage_ret.loc[stratage_ret.index[-1],'hb1y_极值']=stratage_ret.iloc[-1]['hb1y']
                stratage_ret['hb1y_increase']=np.nan
                stratage_ret['hb1y_decrease'] = np.nan
                stratage_ret['hb1y_increase_mellow']=np.nan
                stratage_ret['hb1y_decrease_mellow'] = np.nan
                temp=stratage_ret[stratage_ret['hb1y_极值'].notnull()]['hb1y_极值'].diff().to_frame('diff')
                for i in range(1,len(temp)):
                    if(temp.iloc[i]['diff']>0.05):
                        stratage_ret.loc[temp.index[i-1]:temp.index[i],'hb1y_increase']=\
                            stratage_ret[temp.index[i-1]:temp.index[i]]['hb1y']
                        stratage_ret.loc[temp.index[i-1]:temp.index[i],'hb1y']=np.nan
                    elif((temp.iloc[i]['diff']<=0.05)&(temp.iloc[i]['diff']>0.03)):
                        stratage_ret.loc[temp.index[i-1]:temp.index[i],'hb1y_increase_mellow']=\
                            stratage_ret[temp.index[i-1]:temp.index[i]]['hb1y']
                        stratage_ret.loc[temp.index[i-1]:temp.index[i],'hb1y']=np.nan
                    elif(temp.iloc[i]['diff']<-0.05):
                        stratage_ret.loc[temp.index[i-1]:temp.index[i],'hb1y_decrease']=\
                            stratage_ret[temp.index[i-1]:temp.index[i]]['hb1y']
                        stratage_ret.loc[temp.index[i-1]:temp.index[i],'hb1y']=np.nan
                    elif((temp.iloc[i]['diff']<-0.03)&(temp.iloc[i]['diff']>=-0.05)):
                        stratage_ret.loc[temp.index[i-1]:temp.index[i],'hb1y_decrease_mellow']=\
                            stratage_ret[temp.index[i-1]:temp.index[i]]['hb1y']
                        stratage_ret.loc[temp.index[i-1]:temp.index[i],'hb1y']=np.nan

                plot.plotly_line_style(stratage_ret[['hb1y_increase','hb1y_increase_mellow','hb1y_decrease','hb1y_decrease_mellow','hb1y']],big_s+":"+stratage)
                # plot.plotly_line_and_scatter(stratage_ret,big_s+":"+stratage,line_col=['hb1y'],scatter_col=['hb1y_极值'])


        name_map=dict(zip(['cen_ind_1','cen_theme','ratio_ind_1','ratio_theme','longtou_mean','平均持有时间(出持仓前)','个股集中度','仓位换手率','换手率','stk_num', 'stk_mv_pct', 'stk_cap2_pct','逆向买入比例(出持仓前)','买入 PEG比例(出持仓前)','买入 ROE-PB比例(出持仓前)','左侧概率(出持仓前,半年线)']
                          ,['一级行业集中度','主题集中度','一级行业换手率','主题换手率','龙头占比(时序均值)','平均持有时间(天)','个股集中度','仓位换手率','换手率','同持仓基金个个数', '偏股基金平均持仓比例X10', '偏股基金资金占流通股比例','逆向买入比例','买入PEG比例','买入ROE-PB比例','左侧概率']))


        # lable_info['stk_mv_pct']=lable_info['stk_mv_pct']*10
        # plot.plotly_line_multi_yaxis_general(lable_info.groupby('asofdate')['stk_num', 'stk_mv_pct', 'stk_cap2_pct'].mean().rename(columns=name_map)
        #                       ,'市场抱团程度时序变动',['同持仓基金个个数'])

def moring_report():

    from hbshare.fe.return_analysis import  pool_return_analysis as pra
    pra.mutual_pool_history_reasoning('20200201','20231031','hld')

    output=[]

    sql="SELECT jjdm,`风格偏好` from jjpic_value_p_hbs where asofdate='20230630'"
    style_fund_data=pd.read_sql(sql,con=localdb)

    sql="SELECT jjdm,`规模偏好` from jjpic_size_p_hbs where asofdate='20230630'"
    size_fund_data=pd.read_sql(sql,con=localdb)

    sql="SELECT jjdm,`个股风格B` from jjpic_stock_p where asofdate='20230630' and `个股风格B`!='无'"
    stock_fund_data=pd.read_sql(sql,con=localdb)

    sql="SELECT jjdm,`是否抱团` from jjpic_stock_tp where asofdate='20230630' and `是否抱团` is not null "
    stocktp_fund_data=pd.read_sql(sql,con=localdb)

    sql="SELECT jjdm,theme from public_theme_pool_history where asofdate='20230630'"
    theme_fund_data=pd.read_sql(sql,con=localdb)
    theme_fund_data.loc[theme_fund_data['theme'].str[-1]=='+','theme']='主题+'

    for style in style_fund_data['风格偏好'].unique():
        jjdm_list=style_fund_data[style_fund_data['风格偏好']==style]['jjdm'].tolist()
        sql="select tjyf,avg(hb1y) as hb1y from st_fund.t_st_gm_yhb where jjdm in {0} and  tjyf in ('202310','202311') group by tjyf".format(tuple(jjdm_list))
        ret_data=hbdb.db2df(sql,db='funduser')
        ret_data['style']=style
        output.append(ret_data)

    for style in size_fund_data['规模偏好'].unique():
        jjdm_list=size_fund_data[size_fund_data['规模偏好']==style]['jjdm'].tolist()
        sql="select tjyf,avg(hb1y) as hb1y from st_fund.t_st_gm_yhb where jjdm in {0} and  tjyf in ('202310','202311') group by tjyf".format(tuple(jjdm_list))
        ret_data=hbdb.db2df(sql,db='funduser')
        ret_data['style']=style
        output.append(ret_data)

    for style in stock_fund_data['个股风格B'].unique():
        jjdm_list=stock_fund_data[stock_fund_data['个股风格B']==style]['jjdm'].tolist()
        sql="select tjyf,avg(hb1y) as hb1y from st_fund.t_st_gm_yhb where jjdm in {0} and  tjyf in ('202310','202311') group by tjyf".format(tuple(jjdm_list))
        ret_data=hbdb.db2df(sql,db='funduser')
        ret_data['style']=style
        output.append(ret_data)

    for style in stocktp_fund_data['是否抱团'].unique():
        jjdm_list=stocktp_fund_data[stocktp_fund_data['是否抱团']==style]['jjdm'].tolist()
        sql="select tjyf,avg(hb1y) as hb1y from st_fund.t_st_gm_yhb where jjdm in {0} and  tjyf in ('202310','202311') group by tjyf".format(tuple(jjdm_list))
        ret_data=hbdb.db2df(sql,db='funduser')
        ret_data['style']=style
        output.append(ret_data)

    for style in theme_fund_data['theme'].unique():
        jjdm_list=theme_fund_data[theme_fund_data['theme']==style]['jjdm'].tolist()
        sql="select tjyf,avg(hb1y) as hb1y from st_fund.t_st_gm_yhb where jjdm in {0} and  tjyf in ('202310','202311') group by tjyf".format(tuple(jjdm_list))
        ret_data=hbdb.db2df(sql,db='funduser')
        ret_data['style']=style
        output.append(ret_data)

    pd.concat(output,axis=0).to_excel('收益总结.xlsx')
    print('done')

def compare_full_holding_and_artifiacl_on_second_industry():

    sql = "SELECT jsrq,jjdm,zjbl from hbs_industry_class2_exp where ejxymc='光伏设备' and jsrq>='20170630' "
    full_hld = pd.read_sql(sql, con=localdb)

    zjbl=[]
    date_list=[]
    count=[]
    for date in full_hld['jsrq'].unique().tolist():

        jjdm_list=util.get_stock_funds_pool(date)
        zjbl.append(full_hld[(full_hld['jsrq']==date)&(full_hld['jjdm'].isin(jjdm_list))]['zjbl'].sum()/len(jjdm_list))
        date_list.append(date)
        count.append(len(set(jjdm_list).intersection(set(full_hld[full_hld['zjbl']>=5]['jjdm']))))
    final_df=pd.DataFrame(index=date_list)
    final_df['zjbl']=zjbl
    final_df['持有数量']=count
    final_df.to_excel('全仓光伏.xlsx')


    sql="select * from artificial_quartly_full_hld"
    data=pd.read_sql(sql,con=localdb)

    sql="select zqdm,flmc from st_fund.t_st_gm_zqhyflb where zqdm in {} and hyhfbz=2 and fljb=2 "\
        .format(tuple(data['zqdm'].unique().tolist()))
    ind_map=hbdb.db2df(sql,db='funduser').drop_duplicates('zqdm',keep='last')

    data = pd.merge(data, ind_map, how='left', on='zqdm')

    ind_quart=data.groupby(['jsrq','flmc'])['zjbl'].sum()
    ind_count=(data.groupby(['jsrq','jjdm','flmc'])['zjbl'].sum()).reset_index()
    ind_count=(ind_count[ind_count['zjbl'] >= 0.05].groupby(['jsrq', 'flmc'])['jjdm'].count()).reset_index()
    fund_count=data.drop_duplicates(['jsrq','jjdm']).groupby('jsrq')['jjdm'].count()
    ind_quart = pd.merge(ind_quart.reset_index(), fund_count, how='left', on='jsrq')
    ind_quart['zjbl']=ind_quart['zjbl']/ind_quart['jjdm']
    ind_quart = pd.merge(ind_quart, ind_count, how='left', on=['jsrq','flmc'])
    ind_quart.rename(columns={'jjdm_x':'基金总数','jjdm_y':'权重5%基金数量'}).to_excel('季度拟合持仓二级行业.xlsx')

if __name__ == '__main__':


    trade_info=pd.read_excel(r"C:\Users\xuhuai.zhe\Documents\WXWork\1688858146292774\Cache\File\2024-01\公募持仓.xlsx",sheet_name='Sheet2')
    trade_info['jjdm']=trade_info['jjdm'].str.replace("'",'')

    hld_cb=[]
    hld_mv=pd.DataFrame(columns=['20191230'])
    hld_quant=pd.DataFrame(columns=['jjdm','20191230'])

    sql="select jjdm,jjjz,jzrq from st_fund.t_st_gm_jjjz where jzrq>='20191231' and jjdm in {}"\
        .format(tuple(trade_info['jjdm'].tolist()))
    fund_nav=hbdb.db2df(sql,db='funduser')
    last_date='20191230'
    for date in fund_nav['jzrq'].unique().tolist():

        quant=trade_info[(trade_info['开始日期']<=date)&(trade_info['结束日期']>date)]
        quant=pd.merge(quant,fund_nav[fund_nav['jzrq']==date],how='left',on='jjdm')
        hld_cb.append(quant['买入金额'].sum())
        quant['quant']=quant['买入金额']/quant['jjjz']

        hld_quant=pd.merge(hld_quant,quant[['jjdm','quant','jjjz']],how='outer',on='jjdm').fillna(0)

        hld_quant[date]=hld_quant['quant']+hld_quant[last_date]
        hld_quant['mv']=hld_quant['jjjz']*hld_quant[date]
        hld_quant.drop(['quant','jjjz'],axis=1,inplace=True)

        hld_mv=pd.concat([hld_mv,hld_quant[['jjdm','mv']].set_index('jjdm')],axis=1).fillna(0).rename(columns={'mv':date})
        last_date=date
    # asofdate_list=['20230630','20220630','20210630']
    # start_date_list=['20221216','20211231','20201231']
    # end_date_list=['20231201','20221216','20211231']
    # for i in range(3):
    #
    #     print(i)
    #
    #     asofdate=asofdate_list[i]
    #     start_date=start_date_list[i]
    #     end_date=end_date_list[i]


        # sql="SELECT jjdm from extra_table_funds where asofdate='{}' ".format(asofdate)
        # jjdm_list=pd.read_sql(sql,con=localdb)
        #
        # sql="select jjdm,fqdwjz,jzrq from st_fund.t_st_gm_rhb where jjdm in {0} and jzrq in ('{1}','{2}')"\
        #     .format(tuple(jjdm_list['jjdm'].tolist()),start_date,end_date)
        # jj_nav=hbdb.db2df(sql,db='funduser')
        # print(jj_nav.groupby('jjdm')['fqdwjz'].pct_change().mean())

        # sql="SELECT jjdm,theme from public_theme_pool_history where asofdate='{}' "\
        #     .format(asofdate)
        # jjdm_list=pd.read_sql(sql,con=localdb)
        #
        # sql = "select jjdm,fqdwjz,jzrq from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ('{1}','{2}')" \
        #     .format(util.list_sql_condition(jjdm_list['jjdm'].tolist()), start_date, end_date)
        # jj_nav = hbdb.db2df(sql, db='funduser')
        # print(jj_nav.groupby('jjdm')['fqdwjz'].pct_change().mean())

        # for theme in jjdm_list['theme'].unique():
        #     temp_jjdm_list=jjdm_list[jjdm_list['theme']==theme]['jjdm'].tolist()
        #     sql="select jjdm,fqdwjz,jzrq from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ('{1}','{2}')"\
        #         .format(util.list_sql_condition(temp_jjdm_list),start_date,end_date)
        #     jj_nav=hbdb.db2df(sql,db='funduser')
            # print(theme)
            # print(jj_nav.groupby('jjdm')['fqdwjz'].pct_change().mean())

        # sql="SELECT jjdm,`风格偏好` from jjpic_value_p_hbs where asofdate={0} "\
        #     .format(asofdate)
        # jjdm_list = pd.read_sql(sql, con=localdb)
        #
        # for theme in jjdm_list['风格偏好'].unique():
        #     temp_jjdm_list=jjdm_list[jjdm_list['风格偏好']==theme]['jjdm'].tolist()
        #     sql="select jjdm,fqdwjz,jzrq from st_fund.t_st_gm_rhb where jjdm in ({0}) and jzrq in ('{1}','{2}')"\
        #         .format(util.list_sql_condition(temp_jjdm_list),start_date,end_date)
        #     jj_nav=hbdb.db2df(sql,db='funduser')
            # print(theme)
            # print(jj_nav.groupby('jjdm')['fqdwjz'].pct_change().mean())

    hld_quant=hld_quant.set_index('jjdm').drop('mv', axis=1).T
    hld_mv=hld_mv.T
    hld_mv['cb']=[0]+hld_cb
    hld_mv['cb']=hld_mv['cb'].cumsum()
    hld_mv['mv']=hld_mv[['000619', '001691', '040018', '001410', '000751', '163406', '000991',
            '002621', '070002', '260104', '004997', '007119']].sum(axis=1)


    print('')



    #
    # from hbshare.fe.return_analysis import  pool_return_analysis as pra
    # pra.mutual_pool_history_reasoning('20200201','20231201','nav')
    #
    #
    #
    # data=pd.read_excel(r"E:\GitFolder\docs\基金池业绩归因\公募偏股基金池归因数据\个基归因总结_nav.xlsx")
    # data['jjdm']=[('000000'+str(x))[-6:] for x in data['jjdm']]
    #
    # plot=functionality.Plot(1200,600)
    #
    # plot.plotly_hist(data[data['date']==2021][['alpha']],'2021风格alpha分布情况')
    # plot.plotly_hist(data[data['date']==2022][['alpha']],'2022风格alpha分布情况')
    # plot.plotly_hist(data[data['date']==2023][['alpha']],'2023风格alpha分布情况')
    #
    #
    # plot.plotly_hist(data[data['date']==2021][['alpha_主题']],'2021主题alpha分布情况')
    # plot.plotly_hist(data[data['date']==2022][['alpha_主题']],'2022主题alpha分布情况')
    # plot.plotly_hist(data[data['date']==2023][['alpha_主题']],'2023主题alpha分布情况')



    print('')

    # Projects.get_xfc_fof_return_sumarry('20230928','20231002',
    #                                     r"C:\Users\xuhuai.zhe\Documents\WXWork\1688858146292774\Cache\File\2023-10\FOF存量-按月.xlsx")


    # sql="SELECT jjdm,asofdate from jjpic_stock_p where `个股风格B`='自上而下' and asofdate in ('20221230','20230630')"
    # data=pd.read_sql(sql,con=localdb)
    # jjdm_list=\
    #     data.groupby('jjdm')['asofdate'].count()[data.groupby('jjdm')['asofdate'].count()==2].index.to_list()


    # sql="select jjsl,spjg,tjyf from st_hedge.t_st_sm_hmzs where zsdm='HB0011' and tjyf='202308' "
    # data=hbdb.db2df(sql,db='highuser')

    #
    # sql="select distinct(jjdm) from public_theme_pool_history where jjdm in ({}) and asofdate in ('20221231','20230630')"\
    #     .format(util.list_sql_condition(jjdm_list))
    # remove_list=pd.read_sql(sql,con=localdb)['jjdm'].tolist()
    # jjdm_list=list(set(jjdm_list).difference(set(remove_list)))

    # sql="select jjdm,zbnp from st_fund.t_st_gm_rqjhb where jjdm in ({}) and jzrq='20230913' and zblb='2998'"\
    #     .format(util.list_sql_condition(jjdm_list))
    # ret=hbdb.db2df(sql,db='funduser')

    # data=[]
    # for asofdate in pd.read_sql("select distinct(asofdate)as asofdate from public_negative_index_theme_pool_history ",con=localdb)['asofdate'].tolist():
    #     jjdm_list=pd.read_sql("select jjdm from public_negative_index_theme_pool_history where theme='周期' and asofdate ='{}'".format(asofdate),con=localdb)['jjdm'].tolist()
    #     sql="select jjdm,zzjbl,flmc from st_fund.t_st_gm_jjhyzhyszb where jjdm in ({0}) and hyhfbz='2' and zclb=2 and jsrq<='{1}' and jsrq>='{2}' and flmc in ('有色金属','煤炭','石油石化') "\
    #         .format(util.list_sql_condition(jjdm_list),asofdate,str(int(asofdate)-20000))
    #     temp=hbdb.db2df(sql,db='funduser').pivot_table('zzjbl','jjdm','flmc')
    #     temp['asofdate']=str(asofdate)
    #     data.append(temp.reset_index())
    # data=pd.concat(data,axis=0)

    st=stratage_timing()
    # st.market_liquidity('20070101','20231031')
    # st.market_style_distinguish('20070101','20231130')
    # st.market_states_distinguish('20070101','20231130')
    # st.marco_eco_states_distinguish('2007-01-01','2023-11-30')
    # st.currency_states_distinguish('2007-12-01', '2023-11-28')
    # st.industry_states_distinguish('20070101','20231228')
    # st.stratage_cycle_distinguish('20230831')


    #
    # fls=fund_lables_summary()
    # fls.get_funds_num_and_size()
    # fls.lable_summary()
    # fls.sample_funds_pic('20230831')

    # sfi= Shanghui_fund_info(['003165','001743'])
    # sfi.stock_comparison(['003165', '001743'], end_date='20221231',start_date='20200930')
    # sfi.industry_comparison(['003165','001743'],end_date='20221231',start_date='20200930')
    # sfi.ret_comparison('中小盘成长',jjdm_list=['003165','001743','270028','002446','007346'],
    #                                   start_date='20200930',end_date='20230724')
    # style_info=\
    #     sfi.get_shanghui_funds_style_info('成长','中小盘','20221230')
    # style_info.drop(['jjdm','jjdm2'],axis=1).mean(axis=0).to_frame('均值')
    # sql="select * from jjpic_stock_tp where jjdm in ({}) and asofdate='20221231'"\
    #     .format(util.list_sql_condition(style_info['jjdm'].tolist()))
    # stock_trading=pd.read_sql(sql,con=localdb)
    #
    # sql="SELECT PE,PB,ROE,PEG,PCF,`股息率`,`毛利率`,`净利率`,`净利增速`,`市值` from jjpic_stock_p where jjdm in ({}) and asofdate='20221230'"\
    #     .format(util.list_sql_condition(style_info['jjdm'].tolist()))
    # stock_holding = pd.read_sql(sql, con=localdb)
    # for col in stock_holding.columns.tolist():
    #     print(col+":{}".format(        stock_holding[(stock_holding[col]>stock_holding[col].quantile(0.05))
    #                   &(stock_holding[col]<stock_holding[col].quantile(0.95))][col].mean()))



    print('')


    # ssc=secondary_stratage_classify()
    # ssc.classification('价值','20221230','20230301')
    # test=\
    #     pd.read_pickle(r"C:\Users\xuhuai.zhe\Documents\WXWork\1688858146292774\Cache\File\2023-07\fund_holds")
    # Industry_track.update_power_resource_data(latest_date=str(datetime.datetime.today())[0:10])
    # Industry_track.update_housing_data(start_date='2012-12-01')
    # Industry_track.update_metal_data()
    # Industry_track.update_power_generation_data()
    # Industry_track.update_elec_car_data(latest_date='2023-10-31')



    #Projects.update_power_generation_data()
    #Projects.update_elec_car_data('20230531')
    #Projects.bmk_ret_summary()
    #Projects.bmk_index_adjust()
    #Projects.get_shanghui_fund_holding_info(['008245','001667','005596'], '20181225','20230530','HB医药') '001667','005596'
    #Projects.get_all_market_shanghui_fund_holding_info(['240004'], '20150101','20230530')
    #

    pj=Projects()
    # df=pj.mutual_industry_allocation_analysis()
    #pj.prv_product_style2manager_style('20230630')
    #pj.pool_return_comparision()
    #pj.bmk_index_adjust()
    # pj.fund_alpha_analysis(['001476'])

    # summary.to_excel('池业绩汇总.xlsx')

    # data=pd.read_excel(r"E:\GitFolder\docs\公募基金行业动态模拟\summary_20141231.xlsx")
    # data['jjdm']=[("000000"+str(x))[-6:] for x in data['jjdm'].tolist()]
    # jjdm_list=data['jjdm'].tolist()
    #
    # data2=pd.read_sql("select * from hbs_industry_class1_exp where jjdm in ({}) and jsrq='20141231' "
    #                   .format(util.list_sql_condition(jjdm_list)),con=localdb).pivot_table('zjbl','jjdm','yjxymc').fillna(0)
    # data2=data2/100
    # ind_col=data2.columns.tolist()
    # overlap_summary=pd.DataFrame(index=data2.index,columns=['overlap'])
    # for jjdm in data2.index:
    #     tempdf=pd.concat([data2.loc[[jjdm]],data[data['jjdm']==jjdm][ind_col]],axis=0)
    #     overlap_summary.loc[jjdm,'overlap']=(tempdf.min(axis=0)).sum()/data2.loc[[jjdm]].sum(axis=1).values[0]


    # df1=pd.read_excel(r"E:\GitFolder\docs\公募基金行业动态模拟\持仓数据补全\补全持仓数据_20230331.xlsx")
    # df2=pd.read_excel(r"E:\GitFolder\docs\公募基金行业动态模拟\净值方法\summary_20230331.xlsx")
    #
    #
    #
    # import os
    # file_list = []
    # path = r"E:\GitFolder\docs\公募基金行业动态模拟\持仓数据补全\\"
    # for i, j, k in os.walk(path):
    #     if (len(file_list) == 0):
    #         file_list = k
    # daily_div_df=[]
    #
    # for file in file_list:
    #     print(file)
    #
    #     asofdate=file.split('_')[1][0:8]
    #     if(asofdate[4:6]=='03'):
    #         start_date=asofdate[0:4]+"0331"
    #         end_date=asofdate[0:4]+"0630"
    #     elif(asofdate[4:6]=='06'):
    #         start_date=asofdate[0:4]+"0630"
    #         end_date=asofdate[0:4]+"0930"
    #     elif (asofdate[4:6] == '09'):
    #         start_date=asofdate[0:4]+"0930"
    #         end_date=asofdate[0:4]+"1231"
    #     else:
    #         start_date = asofdate[0:4] + "1231"
    #         end_date = str(int(asofdate[0:4])+1) + "0331"
    #
    #     hld=\
    #         pd.read_excel(r"E:\GitFolder\docs\公募基金行业动态模拟\持仓数据补全\{0}".format(file)).drop('Unnamed: 0',axis=1)
    #     hld['zqdm']=[str(x).replace('of','') for x in hld['zqdm']]
    #     hld['jjdm'] = [("000000" + str(x))[-6:] for x in hld['jjdm']]
    #     hld['hk_flag']=[len(x) for x in hld['zqdm']]
    #     zqdm_list=hld[hld['hk_flag']==6]['zqdm'].unique().tolist()
    #     hk_zqdm_list=hld[hld['hk_flag']==5]['zqdm'].unique().tolist()
    #     hld.drop('hk_flag',axis=1,inplace=True)
    #
    #     trunk_size = 1000
    #     stock_price = []
    #     for i in range(0, int(np.floor(len(zqdm_list) / trunk_size) + 1)):
    #         temp_jjdm_list = zqdm_list[i * trunk_size:(i + 1) * trunk_size]
    #
    #         sql = """
    #         select zqdm,jyrq,spjg from st_ashare.t_st_ag_gpjy where zqdm in ({0}) and jyrq>='{1}' and jyrq<='{2}' and spjg!=99999 and spjg!=0 and scdm in ('CNSESZ','CNSESH','CNSEBJ')
    #          """.format(util.list_sql_condition(temp_jjdm_list),start_date,end_date)
    #
    #         stock_price.append(hbdb.db2df(sql, db='alluser'))
    #
    #     stock_price = pd.concat(stock_price, axis=0)
    #
    #     if(len(hk_zqdm_list)>0):
    #         sql="select b.SecuCode as zqdm,a.TradingDay as jyrq, a.ClosePrice as spjg from hsjy_gg.QT_HKDailyQuoteIndex a left join  hsjy_gg.HK_SecuCodeTable b on a.InnerCode=b.InnerCode where b.SecuCode in ({0}) and TradingDay>=to_date('{1}','yyyymmdd') and TradingDay<=to_date('{2}','yyyymmdd') "\
    #             .format(util.list_sql_condition(hk_zqdm_list),start_date,end_date)
    #         hk_price=hbdb.db2df(sql,db='readonly').drop('ROW_ID',axis=1)
    #         hk_price.columns=['zqdm','jyrq','spjg']
    #         hk_price['jyrq']=((hk_price['jyrq'].astype(str).str[0:10]).str.replace('-','')).astype(int)
    #         hk_price=hk_price[hk_price['jyrq'].isin(stock_price['jyrq'].unique().tolist())]
    #         stock_price=stock_price[stock_price['jyrq'].isin(hk_price['jyrq'].unique().tolist())]
    #         stock_price = pd.concat([stock_price,hk_price], axis=0)
    #
    #     date_list=stock_price['jyrq'].unique().tolist()
    #     stock_price=pd.merge(stock_price,stock_price.drop_duplicates('zqdm',keep='first')[['zqdm','spjg']],how='left',on='zqdm')
    #     stock_price['ret']=stock_price['spjg_x']/stock_price['spjg_y']
    #     stock_price=stock_price.pivot_table('ret','zqdm','jyrq')
    #
    #
    #     hld=pd.merge(hld,stock_price,how='left',on='zqdm')
    #     for col in date_list:
    #         hld[col]=hld[col]*hld['zjbl']
    #     hld=hld.groupby('jjdm').sum()
    #     for col in date_list:
    #         hld[col]=hld[col]+1-hld['zjbl']
    #     hld=hld[date_list]
    #
    #     #get jj nav
    #     sql="select jjdm,ljjz,jzrq from st_fund.t_st_gm_jjjz where jjdm in ({0}) and  jzrq in ({1}) "\
    #         .format(util.list_sql_condition(hld.index.astype(str).tolist()),
    #                 util.list_sql_condition(hld.columns.astype(str).tolist()))
    #     jj_nav=hbdb.db2df(sql,db='funduser').pivot_table('ljjz','jjdm','jzrq')
    #     dividen=jj_nav[date_list[0]]
    #     for col in date_list:
    #         jj_nav[col]=jj_nav[col]/dividen
    #
    #     entire_daily_div=pd.merge(hld.mean(axis=0).to_frame('mimic'),jj_nav.mean(axis=0).to_frame('real')
    #                               ,how='left',left_index=True,right_index=True)
    #     entire_daily_div['daily_ret_div']=entire_daily_div['mimic'].pct_change()-entire_daily_div['real'].pct_change()
    #
    #     fund_daily_div=hld.pct_change(axis=1).fillna(0)-jj_nav.pct_change(axis=1).fillna(0)
    #
    #
    #
    # entire_daily_div.to_excel('{}_整体日度偏离.xlsx'.format(asofdate))
    # fund_daily_div.to_excel('{}_个基金日度偏离.xlsx'.format(asofdate))





    print('')







