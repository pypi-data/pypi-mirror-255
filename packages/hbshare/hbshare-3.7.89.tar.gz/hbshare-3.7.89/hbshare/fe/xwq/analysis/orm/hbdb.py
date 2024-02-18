# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
import hbshare as hbs
import warnings
warnings.filterwarnings('ignore', category=pymysql.Warning)


class HBDB:
    def __init__(self):
        pass

    def get_df(self, sql, db, page_size=2000):
        data = hbs.db_data_query(db, sql, page_size=page_size, timeout=120)
        pages = data['pages']
        data = pd.DataFrame(data['data'])
        if pages > 1:
            for page in range(2, pages + 1):
                temp_data = hbs.db_data_query(db, sql, page_size=page_size, page_num=page, timeout=120)
                data = pd.concat([data, pd.DataFrame(temp_data['data'])], axis=0)
        return data

    def read_report_date(self):
        sql = "select distinct(jsrq) as REPORT_DATE FROM st_fund.t_st_gm_gpzh"
        df = self.get_df(sql, db='funduser')
        return df

    def read_cal_nodate(self):
        sql = "SELECT jyrq, sfjj, sfzm, sfym FROM st_main.t_st_gg_jyrl"
        df = self.get_df(sql, db='alluser')
        return df

    def read_cal(self, start, end):
        sql = "SELECT jyrq, sfjj, sfzm, sfym FROM st_main.t_st_gg_jyrl WHERE jyrq>={0} and jyrq<={1}".format(start, end)
        df = self.get_df(sql, db='alluser')
        return df

    def read_fund_info(self):
        sql = "select jjdm, jjmc, jjjc, clrq, zzrq, cpfl, jjfl, ejfl, kffb from st_fund.t_st_gm_jjxx where cpfl='2' and m_opt_type<>'03'"
        df = self.get_df(sql, db='funduser')
        return df

    def read_stock_fund_info(self):
        sql = "select jjdm, jjmc, jjjc, clrq, zzrq, ejfl, kffb from st_fund.t_st_gm_jjxx where jjzt='0' and cpfl='2' and ejfl in ('13', '35', '37') and m_opt_type<>'03'"
        df = self.get_df(sql, db='funduser')
        return df

    def read_company_fund_given_code(self, code):
        sql = "select b.jgdm, b.jgmc, a.jjdm from st_fund.t_st_gm_jjxx a JOIN broadcast.t_st_gg_jgxx b ON a.glrm = b.jgdm where a.m_opt_type <> '03' AND b.m_opt_type <> '03' AND b.jgdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_company_given_code(self, code):
        sql = "select a.jjdm, b.jgdm, b.jgmc from st_fund.t_st_gm_jjxx a JOIN broadcast.t_st_gg_jgxx b ON a.glrm = b.jgdm where a.m_opt_type <> '03' AND b.m_opt_type <> '03' AND a.jjdm ='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_manager_given_code(self, code):
        sql = "select jjdm, rydm, ryxm, ryzw, ryzt, bdrq, rzrq, lrrq, lryy from st_fund.t_st_gm_jjjl where jjdm='{0}' and m_opt_type <> '03'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_manager(self):
        sql = "select jjdm, rydm, ryxm, ryzw, ryzt, bdrq, rzrq, lrrq, lryy from st_fund.t_st_gm_jjjl where m_opt_type <> '03'"
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_given_manager_code(self, manager_code):
        sql = "select jjdm, rydm, ryxm, ryzw, ryzt, bdrq, rzrq, lrrq, lryy from st_fund.t_st_gm_jjjl where rydm='{0}' and m_opt_type <> '03'".format(manager_code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_manager_info_given_manager_code(self, manager_code):
        sql = "select rydm, ryxm, ryxb, ryxl, ryjj from st_main.t_st_gg_ryjl where rydm='{0}' and m_opt_type <> '03'".format(manager_code)
        df = self.get_df(sql, db='alluser')
        return df

    def read_fund_target_given_code(self, code):
        sql = "select jjdm, tzmb from st_fund.t_st_gm_fjxx where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_scale_given_code(self, code):
        sql = "select jjdm, bblb, jsrq, ggrq, zcjz from st_fund.t_st_gm_cwzb where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_scale_given_date(self, date):
        sql = "select jjdm, bblb, jsrq, ggrq, zcjz from st_fund.t_st_gm_cwzb where jsrq='{0}'".format(date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_share_given_code(self, code):
        sql = "select jjdm, bblb, jsrq, plrq, qsrq, qcfe, qjsgfe, cfzjfe, wjshfe, qmfe from st_fund.t_st_gm_febd where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_share_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, bblb, jsrq, plrq, qsrq, qcfe, qjsgfe, cfzjfe, wjshfe, qmfe from st_fund.t_st_gm_febd where jjdm in ({0}) and m_opt_type<>'03'".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_holder_given_code(self, code):
        sql = "select jjdm, jsrq, ggrq, jgcyfe, jgcybl, grcyfe, grcybl from st_fund.t_st_gm_fecyrbd where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_holder_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, ggrq, grcyfe, grcybl, jgcyfe, jgcybl, ygcyfe, ygcybl from st_fund.t_st_gm_fecyrbd where jjdm in ({0}) and m_opt_type<>'03'".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_manager_product_given_code(self, manager_code):
        sql = "select rydm, jsrq, zgcpsl, zgcpgm, dbjj from st_fund.t_st_gm_jlzgcptj where rydm='{0}'".format(manager_code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_manager_achievement_given_code(self, manager_code, code):
        sql = "select rydm, jjdm, qsrq, jsrq, rqts, hbrq, rqnhhb, zdyl, zdhc, nhxpbl, kmbl from st_fund.t_st_gm_jlrqhb where rydm='{0}' and jjdm='{1}'".format(manager_code, code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_position_given_code(self, code):
        sql = "select jjdm, jsrq, jjzzc, gptzsz, zqzsz, jjtzszhj, hbzjsz from st_fund.t_st_gm_zcpz where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_position_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, jjzzc, jjjzc, gptzsz, gptzzjb, zqzsz, zqzszzjb, jjtzszhj, jjtzhjzjb, hbzjsz, hbzjzjb from st_fund.t_st_gm_zcpz where jjdm in ({0}) and m_opt_type<>'03'".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_position_given_date(self, date):
        sql = "select jjdm, jsrq, jjzzc, gptzsz, zqzsz, jjtzszhj, hbzjsz from st_fund.t_st_gm_zcpz where jsrq='{0}'".format(date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_cr_given_code(self, code):
        sql = "select jjdm, jsrq, qsdzb, qsdzbtlpj, qwdzb, qwdzbtlpj from st_fund.t_st_gm_cgjzd where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_turnover_given_code(self, code):
        sql = "select jjdm, jsrq, tjqj, hsl from st_fund.t_st_gm_jjhsl where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_turnover_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, tjqj, hsl from st_fund.t_st_gm_jjhsl where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_turnover_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, tjqj, hsl from st_fund.t_st_gm_jjhsl where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_nav_given_code(self, code):
        sql = "select jjdm, jzrq, jjjz, ljjz from st_fund.t_st_gm_jjjz where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_benchmark_nav_given_code(self, code):
        sql = "select jjdm, jzrq, jzhbdr from st_fund.t_st_gm_jzrhb where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_benchmark_given_code(self, code):
        sql = "select jjdm, jsrq, bjjz, syzt from st_fund.t_st_gm_bjjz where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_wind_size_given_code(self, code):
        sql = "select jjdm, wdszsx from st_fund.t_st_gm_jjxx where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_return_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, rqnp, zbnp, zbnhnp from st_fund.t_st_gm_rqjhb where jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_return_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, rqnp, zbnp, zbnhnp from st_fund.t_st_gm_rqjhb where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_return_period_given_codes_and_date(self, codes, date):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jzrq, zblb, rqnp, zbnp, zbnhnp from st_fund.t_st_gm_rqjhb where m_opt_type <> '03' and jjdm in ({0}) and jzrq = '{1}'".format(codes, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_private_fund_return_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, rqnp, zbnp, nhzbnp from st_hedge.t_st_sm_qjhb_zx where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='highuser')
        return df

    def read_fund_volatility_period_given_code_and_date(self, code, date):
        sql = "select jjdm, tjrq, zblb, zbnp, nhzbnp from st_fund.t_st_gm_zqjbdl where m_opt_type <> '03' and jjdm='{0}' and tjrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_private_fund_volatility_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, zbnp, nhzbnp from st_hedge.t_st_sm_qjbdlzp_zx where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='highuser')
        return df

    def read_fund_maxdrawdown_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, zbnp, zdhchfts, zdhccxts from st_fund.t_st_gm_rqjzdhc where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_maxdrawdown_period_given_codes_and_date(self, codes, date):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jzrq, zblb, zbnp, zdhchfts, zdhccxts from st_fund.t_st_gm_rqjzdhc where m_opt_type <> '03' and jjdm in ({0}) and jzrq = '{1}'".format(codes, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_private_fund_maxdrawdown_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, zbnp, hfts from st_hedge.t_st_sm_qjzdhc_zx where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='highuser')
        return df

    def read_fund_sharpe_period_given_code_and_date(self, code, date):
        sql = "select jjdm, tjrq, zblb, zbnp, nhzbnp from st_fund.t_st_gm_zqjxpbl where m_opt_type <> '03' and jjdm='{0}' and tjrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_private_fund_sharpe_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, zbnp, nhzbnp from st_hedge.t_st_sm_qjxpblzp_zx where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='highuser')
        return df

    def read_fund_sortino_period_given_code_and_date(self, code, date):
        sql = "select jjdm, tjrq, zblb, zbnp, nhzbnp from st_fund.t_st_gm_zqjstn where m_opt_type <> '03' and jjdm='{0}' and tjrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_calmar_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, zbnp from st_fund.t_st_gm_rqjkmbl where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_private_fund_calmar_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, zbnp from st_hedge.t_st_sm_qjkmbl_zx where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='highuser')
        return df

    def read_fund_winratio_period_given_code_and_date(self, code, date):
        sql = "select jjdm, tjyf, zblb, zbnp from st_fund.t_st_gm_yqjtzsl where m_opt_type <> '03' and jjdm='{0}' and tjyf >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_private_fund_winratio_period_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, zbnp from st_hedge.t_st_sm_qjtzslyp_zx where m_opt_type <> '03' and jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='highuser')
        return df

    def read_fund_gl_period_given_code_and_date(self, code, date):
        sql = "select jjdm, tjyf, zblb, zbnp, zsypj, fsypj from st_fund.t_st_gm_yqjpjsyb where m_opt_type <> '03' and jjdm='{0}' and tjyf >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_return_year_given_code(self, code):
        sql = "select jjdm, tjnf, rqzh, rq1n, hb1n from st_fund.t_st_gm_nhb where m_opt_type <> '03' and jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_return_year_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, tjnf, rqzh, rq1n, hb1n from st_fund.t_st_gm_nhb where m_opt_type <> '03' and jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_maxdrawdown_year_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, tjnf, zbnp1n, zdhchfts1n, zdhccxts1n from st_fund.t_st_gm_nzdhc_ls where m_opt_type <> '03' and jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_volatility_year_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, tjnf, zzbnp1n, znhzbnp1n from st_fund.t_st_gm_nbdl_ls where m_opt_type <> '03' and jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_sharpe_year_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, tjnf, zzbnp1n, znhzbnp1n from st_fund.t_st_gm_nxpbl_ls where m_opt_type <> '03' and jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_calmer_year_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, tjnf, zbnp1n from st_fund.t_st_gm_nkmbl_ls where m_opt_type <> '03' and jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_winratio_year_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, tjnf, zbnp1n from st_fund.t_st_gm_ntzsl_ls where m_opt_type <> '03' and jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_pl_year_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, tjnf, zsypj1n, fsypj1n, pjsyb1n from st_fund.t_st_gm_npjsyb_ls where m_opt_type <> '03' and jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_private_fund_return_year_given_code(self, code):
        sql = "select jjdm, tjnf, hblb, rqzh, rq1n, hb1n, nhhb1n from st_hedge.t_st_sm_nhb_ls where m_opt_type <> '03' and jjdm='{0}'".format(code)
        df = self.get_df(sql, db='highuser')
        return df

    def read_fund_return_month_given_code(self, code):
        sql = "select jjdm, tjyf, rqzh, rq1y, hb1y from st_fund.t_st_gm_yhb where m_opt_type <> '03' and jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_private_fund_return_month_given_code(self, code):
        sql = "select jjdm, tjyf, rqzh, rq1y, hb1y from st_hedge.t_st_sm_yhb where m_opt_type <> '03' and jjdm='{0}'".format(code)
        df = self.get_df(sql, db='highuser')
        return df

    def read_fund_samekind_return_given_code_and_date(self, code, date):
        sql = "select jjdm, jzrq, zblb, pmnpyj, slnpyj, zbnpyj, pmnpej, slnpej, zbnpej, zbnhnpyj, zbnhnpej from st_fund.t_st_gm_rqjhbpm where jjdm='{0}' and jzrq >= '{1}'".format(code, date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_year_return_given_code(self, code):
        sql = "select a.jjdm, a.tjnf, a.hb1n, b.hb1npmyj, b.hb1npmej, b.hb1npmslyj, b.hb1npmslej, b.pjhb1nyj, b.pjhb1nej from st_fund.t_st_gm_nhb a left join st_fund.t_st_gm_nhbpm b on a.jjdm=b.jjdm and a.tjnf=b.tjnf where a.jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_year_volatility_given_code(self, code):
        sql = "select a.jjdm, a.tjnf, a.zzbnp1n, a.znhzbnp1n, b.zbdpm1nyj, b.tlzbdsl1nyj, b.zbdpm1nej, b.tlzbdsl1nej, b.pjzbd1nyj, b.pjnhzbd1nyj, b.pjzbd1nej, b.pjnhzbd1nej from st_fund.t_st_gm_nbdl a left join st_fund.t_st_gm_nbdlpm b on a.jjdm=b.jjdm and a.tjnf=b.tjnf where a.jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_year_sharpratio_given_code(self, code):
        sql = "select a.jjdm, a.tjnf, a.zzbnp1n, a.znhzbnp1n, b.zxppm1nyj, b.tlzxpsl1nyj, b.zxppm1nej, b.tlzxpsl1nej, b.pjzxp1nyj, b.pjznhxp1nyj, b.pjzxp1nej, b.pjznhxp1nej from st_fund.t_st_gm_nxpbl a left join st_fund.t_st_gm_nxpblpm b on a.jjdm=b.jjdm and a.tjnf=b.tjnf where a.jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_year_maxdrawdown_given_code(self, code):
        sql = "select a.jjdm, a.tjnf, a.zbnp1n, a.zdhchfts1n, a.zdhccxts1n, b.hczdpm1nyj, b.tlhczdsl1nyj, b.hczdpm1nej, b.tlhczdsl1nej, b.pjhczd1nyj, b.pjhczd1nej from st_fund.t_st_gm_nzdhc a left join st_fund.t_st_gm_nzdhcpm b on a.jjdm=b.jjdm and a.tjnf=b.tjnf where a.jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_brinson_attribution_given_code(self, code):
        sql = "select jjdm, tjrq, portfolio_return, benchmark_return, asset_allo, sector_allo, equity_selection, trading, portfolio_weight, benchmark_weight from st_fund.r_st_hold_excess_attr_df where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_brinson_attribution_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, tjrq, portfolio_return, benchmark_return, asset_allo, sector_allo, equity_selection, trading, portfolio_weight, benchmark_weight from st_fund.r_st_hold_excess_attr_df where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_barra_attribution_given_code(self, code):
        sql = "select jjdm, tjrq, attr_type, style_factor, data_type, data_value from st_fund.r_st_nav_attr_df where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_gptzzjb_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, gptzzjb from st_fund.t_st_gm_zcpz where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_gptzzjb_given_date(self, date):
        sql = "select jjdm, jsrq, gptzzjb from st_fund.t_st_gm_zcpz where jsrq='{0}'".format(date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_holding_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zqdm, zqmc, ccsz, ccsl, zjbl from st_fund.t_st_gm_gpzh where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_holding_given_date(self, date):
        sql = "select jjdm, jsrq, zqdm, zqmc, ccsz, ccsl, zjbl from st_fund.t_st_gm_gpzh where jsrq='{0}'".format(date)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_holding_diff_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zqdm, zqmc, zclb, zgblbd, sfsqzcg from st_fund.t_st_gm_jjcgbd where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_holding_semi_diff_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zqdm, zqmc, zzjbl, zjblpm, ggzjzbjbd from st_fund.t_st_gm_gpzhggtj where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_valuation_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zclb, pe, pb, roe, dividend from st_fund.t_st_gm_jjggfg where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=2000)
        return df

    def read_stock_market_value_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE from hsjy_gg.LC_DIndicesForValuation a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_star_stock_market_value_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE from hsjy_gg.LC_STIBDIndiForValue a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_valuation_given_date(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE, a.PE AS PE_TTM, a.PB AS PB_LF, a.PEG, a.DividendRatio AS DIVIDEND_RATIO_TTM, a.ForwardPEHR AS FORWARD_PEHR from hsjy_gg.LC_DIndicesForValuation a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly')
        return df

    def read_star_stock_valuation_given_date(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE, a.PETTM AS PE_TTM, a.PB AS PB_LF, a.PEG, a.DividendRatioTTM AS DIVIDEND_RATIO_TTM, a.ForwardPEHR AS FORWARD_PEHR from hsjy_gg.LC_STIBDIndiForValue a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly')
        return df

    def read_stock_valuation_given_code(self, code):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE, a.PE AS PE_TTM, a.PB AS PB_LF, a.PEG, a.DividendRatio AS DIVIDEND_RATIO_TTM, a.ForwardPEHR AS FORWARD_PEHR from hsjy_gg.LC_DIndicesForValuation a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where b.SECUCODE='{0}'".format(code)
        df = self.get_df(sql, db='readonly')
        return df

    def read_star_stock_valuation_given_code(self, code):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE, a.PETTM AS PE_TTM, a.PB AS PB_LF, a.PEG, a.DividendRatioTTM AS DIVIDEND_RATIO_TTM, a.ForwardPEHR AS FORWARD_PEHR from hsjy_gg.LC_STIBDIndiForValue a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where b.SECUCODE='{0}'".format(code)
        df = self.get_df(sql, db='readonly')
        return df

    def read_stock_finance_given_date(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, a.NetProfit AS NET_PROFIT, a.MainIncomePS AS MAIN_INCOME_PS, a.ROETTM AS ROE_TTM, a.GrossIncomeRatioTTM AS GROSS_INCOME_RATIO_TTM, a.NetProfitRatioTTM AS NET_PROFIT_RATIO_TTM, a.EPSTTM AS EPS_TTM, a.OperCashFlowPSTTM AS OPER_CASH_FLOW_PS_TTM, a.NetAssetPS AS NET_ASSET_PS from hsjy_gg.LC_MainIndexNew a left join hsjy_gg.SecuMain b on a.CompanyCode=b.CompanyCode where to_char(a.EndDate, 'yyyyMMdd')='{0}' and substr(b.SECUCODE, 0, 1) in ('0', '3', '6', '8') and length(b.SECUCODE) = 6".format(date)
        df = self.get_df(sql, db='readonly')
        return df

    def read_star_stock_finance_given_date(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, a.NPParentCompanyOwners AS NET_PROFIT, a.MainIncomePS AS MAIN_INCOME_PS, a.ROETTM AS ROE_TTM, a.GrossIncomeRatioTTM AS GROSS_INCOME_RATIO_TTM, a.NetProfitRatioTTM AS NET_PROFIT_RATIO_TTM, a.EPSTTM AS EPS_TTM, a.OperCashFlowPSTTM AS OPER_CASH_FLOW_PS_TTM, a.NetAssetPS AS NET_ASSET_PS from hsjy_gg.LC_STIBMainIndex a left join hsjy_gg.SecuMain b on a.CompanyCode=b.CompanyCode where to_char(a.EndDate, 'yyyyMMdd')='{0}' and substr(b.SECUCODE, 0, 1) in ('0', '3', '6', '8') and length(b.SECUCODE) = 6 and a.IfMerged=1 and a.IfAdjusted=2".format(date)
        df = self.get_df(sql, db='readonly')
        return df

    def read_stock_daily_k_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.ClosePrice AS CLOSE_PRICE from hsjy_gg.QT_PerformanceData a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_star_stock_daily_k_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.ClosePrice AS CLOSE_PRICE from hsjy_gg.LC_STIBPerformanceData a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_daily_k_given_code(self, code):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.ClosePrice AS CLOSE_PRICE from hsjy_gg.QT_PerformanceData a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where b.SecuCode='{0}'".format(code)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_star_stock_daily_k_given_code(self, code):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.ClosePrice AS CLOSE_PRICE from hsjy_gg.LC_STIBPerformanceData a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where b.SecuCode='{0}'".format(code)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    # def read_stock_industry(self):
    #     sql = "select gsdm, xxfbrq, xxly, xyhfbz, ssxy, sfzx, qxrq, yjxydm, yjxymc, ejxydm, ejxymc from st_ashare.t_st_ag_gshyhfb"
    #     df = self.get_df(sql, db='alluser')
    #     return df

    def read_stock_industry(self):
        sql = "select zqdm, flmc, fldm, fljb, hyhfbz, qsrq, jsrq, sfyx, credt_etl from st_fund.t_st_gm_zqhyflb where m_opt_type <> '03'"
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_industry_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zclb, hyhfbz, fldm, flmc, zzjbl, hyzjzbjbd, hyzjzbltlpj, zgpbl, hyzgpbjbd, hyzgpbltlpj, zltgbl, hyzltgbjbd, hyzltgbltlpj from st_fund.t_st_gm_jjhyzhyszb where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_industry_theme(self):
        sql = "select hybh, hyzt, fldm, qsrq, jsrq from st_fund.t_st_gm_hyztpzb"
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_theme_given_codes(self, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jsrq, zblx, zclb, zgpszb, jsqbd, tlpj from st_fund.t_st_gm_ztcgbd where jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_industry_info(self):
        sql = "select hyhfbz, fldm, flmc, zsdm, qsrq, jsrq, fljb, sfyx from st_market.t_st_zs_hyzsdmdyb"
        df = self.get_df(sql, db='alluser')
        return df

    def read_index_info(self):
        sql = "select a.IndexCode, b.SecuCode, b.ChiName, b.ChiNameAbbr from hsjy_gg.LC_IndexBasicInfo a left join hsjy_gg.SecuMain b on a.IndexCode=b.InnerCode"
        df = self.get_df(sql, db='readonly')
        return df

    def read_index_cons(self, index):
        sql = "select a.IndexCode, b.SecuCode, a.InfoSource, a.EndDate, a.Weight from hsjy_gg.LC_IndexComponentsWeight a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.IndexCode='{0}'".format(index)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_fund_style(self):
        sql = "select fund_id, trade_date, type, cap_score, vcg_score, category from st_fund.r_st_gm_equity_score"
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_stock_style(self):
        sql = "select ticker, trade_date, type, cap_score, vcg_score, category from st_fund.r_st_gp_equity_score"
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_barra_style_exposure_given_dates(self, dates):
        dates = '"' + '","'.join(dates) + '"'
        sql = "select ticker, trade_date, size, beta, momentum, resvol, btop, sizenl, liquidity, earnyield, growth, leverage from st_ashare.r_st_barra_style_factor where trade_date in ({0})".format(dates)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_index_daily_k_given_date_and_indexs(self, date, indexs):
        indexs = '"' + '","'.join(indexs) + '"'
        sql = "select scdm, zqdm, zqmc, jyrq, qspj, kpjg, spjg, zgjg, zdjg, zdsl, zdfd, bdfd, cjsl, cjjs, cjbs, ltsz, zsz, pe, pb, roe, gxl from st_market.t_st_zs_hqql where jyrq>='{0}' and zqdm in ({1}) ".format(date, indexs)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_index_daily_k_given_date(self, date, indexs):
        indexs = '"' + '","'.join(indexs) + '"'
        sql = "select scdm, zqdm, zqmc, jyrq, qspj, kpjg, spjg, zgjg, zdjg, zdsl, zdfd, bdfd, cjsl, cjjs, cjbs, ltsz, zsz, pe, pb, roe, gxl from st_market.t_st_zs_hqql where jyrq='{0}' and zqdm in ({1}) ".format(date, indexs)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_industry_index_given_date_and_names(self, date, names):
        names = '"' + '","'.join(names) + '"'
        sql = "select zqmc, zqdm from st_market.t_st_zs_hqql where jyrq='{0}' and zqmc in ({1}) and left(zqdm, 1)='8' and length(zqdm)=6".format(date, names)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_index_valuation_given_date_and_indexs(self, date, indexs):
        indexs = '"' + '","'.join(indexs) + '"'
        sql = "select scdm, zqdm, zqmc, jyrq, pe, pb, roe, gxl from st_market.t_st_zs_hqql where jyrq>='{0}' and zqdm in ({1}) ".format(date, indexs)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_fund_nav_given_date_and_codes(self, date, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jzrq, jjjz, ljjz from st_fund.t_st_gm_jjjz where jzrq>='{0}' and jjdm in ({1}) ".format(date, codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_nav_adj_given_date_and_codes(self, date, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jzrq, fqdwjz, hbfh, hbcl, hbdr from st_fund.t_st_gm_rhb where jzrq>='{0}' and jjdm in ({1}) ".format(date, codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_nav_given_date(self, date, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jzrq, jjjz, ljjz from st_fund.t_st_gm_jjjz where jzrq='{0}' and jjdm in ({1}) ".format(date, codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_fund_nav_adj_given_date(self, date, codes):
        codes = '"' + '","'.join(codes) + '"'
        sql = "select jjdm, jzrq, fqdwjz, hbfh, hbcl, hbdr from st_fund.t_st_gm_rhb where jzrq='{0}' and jjdm in ({1}) ".format(date, codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_finance_data_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, ROETTM AS ROE_TTM, ROATTM AS ROA_TTM, ROICTTM AS ROIC_TTM, NetProfitRatioTTM AS NET_PROFIT_RATIO_TTM, GrossIncomeRatioTTM AS GROSS_INCOME_RATIO_TTM, EBITToToAssetsTTM AS EBIT_ASSET_RATIO_TTM, a.NetProfit AS NET_PROFIT, a.MainIncomePS AS INCOME_PS from hsjy_gg.LC_MainIndexNew a left join hsjy_gg.SecuMain b on a.CompanyCode=b.CompanyCode where to_char(a.EndDate, 'yyyyMMdd')='{0}'".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_bond_fund_info(self):
        sql = "select jjdm, jjmc, jjjc, clrq, zzrq, ejfl, kffb from st_fund.t_st_gm_jjxx where cpfl = '2' and jjzt not in ('3', 'c') and m_opt_type <> '03' and ejfl in ('21', '22', '23', '24', '25', '27', '28', '34', '35', '38')"
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_private_bond_fund_info(self):
        sql = "select jjdm, jjmc, jjjc, clrq, zzrq, jjfl from st_hedge.t_st_jjxx where cpfl = '4' and jjzt not in ('3') and m_opt_type <> '03' and jjfl in ('2')"
        df = self.get_df(sql, db='highuser', page_size=200000)
        return df

    def read_bond_fund_position_given_code(self, code):
        sql = "select jjdm, jsrq, gptzsz, kzzsz from st_fund.t_st_gm_zcpz where jjdm='{0}'".format(code)
        df = self.get_df(sql, db='funduser')
        return df

    def read_fund_cumret_given_code(self, code, start, end):
        sql = "SELECT a.jjdm AS FUND_CODE, b.jzrq AS TRADE_DATE, b.hbcl AS CUM_RET FROM st_fund.t_st_gm_jjxx a, st_fund.t_st_gm_rhb b WHERE a.cpfl = '2' AND a.jjdm = b.jjdm AND a.jjzt not in ('3', 'c') AND a.m_opt_type <> '03' AND a.jjdm = '{0}' AND b.jzrq >= {1} AND b.jzrq <= {2} order by b.jzrq".format(code, start, end)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_private_fund_cumret_given_code(self, code, start, end):
        sql = "SELECT a.jjdm AS FUND_CODE, b.jzrq AS TRADE_DATE, b.fqdwjz AS ADJ_NAV FROM st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b WHERE a.cpfl = '4' AND a.jjdm = b.jjdm AND a.jjzt not in ('3') AND a.m_opt_type <> '03' AND a.jjdm = '{0}' AND b.jzrq >= {1} AND b.jzrq <= {2} order by b.jzrq".format(code, start, end)
        df = self.get_df(sql, db='highuser', page_size=200000)
        return df

    def read_private_fund_ret_given_codes(self, codes):
        codes = "'" + "','".join(codes) + "'"
        sql = "SELECT jjdm, jzrq, hbdr, hbcl, hbfh, fqdwjz FROM st_hedge.t_st_rhb WHERE m_opt_type <> '03' AND jjdm in ({0})".format(codes)
        df = self.get_df(sql, db='highuser', page_size=200000)
        return df

    def read_fund_cumret_given_date(self, date):
        sql = "SELECT jjdm, jzrq, hbcl FROM st_fund.t_st_gm_rhb WHERE jzrq = '{0}'".format(date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_mutual_fund_nav_adj_given_date(self, date):
        sql = "SELECT jjdm, jzrq, hbfh, hbcl, hbdr, fqdwjz FROM st_fund.t_st_gm_rhb WHERE jzrq='{0}' and m_opt_type <> '03'".format(date)
        df = self.get_df(sql, db='funduser')
        return df

    def read_stock_info(self):
        sql = "SELECT zqdm, zqjc, ssrq FROM st_ashare.t_st_ag_zqzb where zqlb=1 and sszt=1"
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_consensus_given_date(self, date, type):
        sql = "SELECT S_INFO_WINDCODE AS TICKER_SYMBOL, EST_DT, ROLLING_TYPE, EST_PE, EST_PB, EST_PEG, EST_DPS, NET_PROFIT AS EST_NET_PROFIT, EST_OPER_REVENUE, EST_ROE, EST_EPS, EST_CFPS, EST_BPS FROM wind.AShareConsensusRollingData where EST_DT='{0}' AND ROLLING_TYPE='{1}'".format(date, type)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_heightest_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.ClosePrice AS CLOSE_PRICE, a.HighestPrice, a.HighestPriceRW, a.HighestPriceTW, a.HighestPriceRM, a.HighestPriceTM, a.HighestPriceR3M AS HighestPriceRMThree, a.HighestPriceR6M AS HighestPriceRMSix, a.HighestPriceR12M AS HighestPriceRY, a.HighestPriceYTD from hsjy_gg.QT_PerformanceData a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_star_stock_heightest_given_date(self, date):
        sql = "select b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.ClosePrice AS CLOSE_PRICE, a.HighestPrice, a.HighestPriceRW, a.HighestPriceTW, a.HighestPriceRM, a.HighestPriceTM, a.HighestPriceRMThree, a.HighestPriceRMSix, a.HighestPriceRY, a.HighestPriceYTD from hsjy_gg.LC_STIBPerformanceData a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_fund_stock_change_given_date(self, date):
        sql = "select b.SecuCode AS FUND_CODE, date_format(a.EndDate, '%Y%m%d') AS END_DATE, date_format(a.InfoPublDate, '%Y%m%d') AS PUBLISH_DATE, a.ReportType AS REPORT_TYPE, a.ChangeType AS CHANGE_TYPE, a.SecuCode AS TICKER_SYMBOL, a.SecuName AS SEC_SHORT_NAME, a.TradeSum AS TRADE_SUM, a.RatioInNVAtBegin AS TS_IN_BNAV, a.RatioInNVAtEnd AS TS_IN_ENAV from hsjy_jj.MF_StockChangeAll a left join hsjy_jj.SecuMain b on a.InnerCode=b.InnerCode where date_format(a.EndDate, '%Y%m%d')='{0}'".format(date)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_industry_symbol(self):
        sql = "select hyhfbz, fldm, flmc, zsdm, qsrq, jsrq, fljb, sfyx from st_market.t_st_zs_hyzsdmdyb where m_opt_type <> '03'"
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_stock_daily_k_ch(self, date):
        sql = "SELECT TDATE, SYMBOL, SNAME, TCLOSE, PCHG, VATURNOVER, TURNOVER, MCAP, TCAP FROM finchina.CHDQUOTE WHERE TDATE = {0}".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_daily_k_ch_mkt(self, date):
        sql = "SELECT TDATE, SYMBOL, SNAME, TCLOSE, PCHG, VOTURNOVER, VATURNOVER, TURNOVER, MCAP, TCAP FROM finchina.CHDQUOTE WHERE TDATE = {0}".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_index_daily_k_ch(self, date):
        sql = "SELECT TDATE, SYMBOL, SNAME, TCLOSE, PCHG, VATURNOVER FROM finchina.CIHDQUOTE WHERE TDATE = {0}".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_valuation_jy(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE, a.PE AS PE_TTM, a.PB AS PB_LF, a.PCFTTM AS PCF_TTM, a.DividendRatio AS DIVIDEND_RATIO_TTM from hsjy_gg.LC_DIndicesForValuation a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_star_stock_valuation_jy(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.TradingDay, 'yyyyMMdd') AS TRADE_DATE, a.TotalMV AS MARKET_VALUE, a.PETTM AS PE_TTM, a.PB AS PB_LF, a.PCFTTM AS PCF_TTM, a.DividendRatioTTM AS DIVIDEND_RATIO_TTM from hsjy_gg.LC_STIBDIndiForValue a left join hsjy_gg.SecuMain b on a.InnerCode=b.InnerCode where a.TradingDay=to_date('{0}', 'yyyymmdd')".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_finance_jy(self, date):
        sql = "SELECT b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, OperatingRevenueGrowRate AS OPER_REVENUE_YOY, NetProfitGrowRate AS NET_PROFIT_YOY, ROETTM AS ROE_TTM, EPSTTM AS EPS_TTM, NetAssetPS AS NAPS, OperCashFlowPSTTM AS OCF_TTM, DividendTTM AS DIVIDEND_TTM FROM hsjy_gg.LC_MainIndexNew a LEFT JOIN hsjy_gg.SecuMain b ON a.CompanyCode=b.CompanyCode WHERE to_char(a.EndDate, 'yyyyMMdd')='{0}' and substr(b.SECUCODE, 0, 1) in ('0', '3', '6', '8') and length(b.SECUCODE) = 6".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_star_stock_finance_jy(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, OperatingRevenueYOY AS OPER_REVENUE_YOY, NetProfitYOY AS NET_PROFIT_YOY, ROETTM AS ROE_TTM, EPSTTM AS EPS_TTM, NetAssetPS AS NAPS, OperCashFlowPSTTM AS OCF_TTM, DividendTTM AS DIVIDEND_TTM from hsjy_gg.LC_STIBMainIndex a left join hsjy_gg.SecuMain b on a.CompanyCode=b.CompanyCode where to_char(a.EndDate, 'yyyyMMdd')='{0}' and substr(b.SECUCODE, 0, 1) in ('0', '3', '6', '8') and length(b.SECUCODE) = 6 and a.IfMerged=1 and a.IfAdjusted=2".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_mutual_index_daily_k_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zsdm AS INDEX_SYMBOL, jzrq AS TRADE_DATE, spjg AS CLOSE_INDEX FROM st_fund.t_st_gm_clzs WHERE zsdm in ({0}) AND jzrq >= {1} AND jzrq <= {2} AND m_opt_type <> '03'".format(indexs, start, end)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_private_index_daily_k_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zsdm AS INDEX_SYMBOL, jyrq AS TRADE_DATE, spjg AS CLOSE_INDEX FROM st_hedge.t_st_sm_zhmzs WHERE zsdm in ({0}) AND jyrq >= {1} AND jyrq <= {2} AND m_opt_type <> '03'".format(indexs, start, end)
        df = self.get_df(sql, db='highuser', page_size=200000)
        return df

    def read_fof_holding_given_codes(self, codes):
        codes = "'" + "','".join(codes) + "'"
        sql = "SELECT jjdm, jsrq, gbrq, cyjjdm, cyjjjc, cyjz, cyfe, zjbl FROM st_fund.t_st_gm_jjzh WHERE jjdm in ({0}) AND m_opt_type <> '03'".format(codes)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_overseas_nav_given_codes(self, codes):
        codes = "'" + "','".join(codes) + "'"
        sql = "SELECT jjdm, jzrq, hbdr, hbcl, hbfh, fqdwjz FROM st_hedge.t_st_rhb WHERE jjdm in ({0}) AND m_opt_type <> '03'".format(codes)
        df = self.get_df(sql, db='highuser', page_size=200000)
        return df

    def read_stock_finance_jy2(self, date):
        sql = "SELECT b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, OperatingRevenueGrowRate AS OPER_REVENUE_YOY, NetProfitGrowRate AS NET_PROFIT_YOY, ROETTM AS ROE_TTM, EPSTTM AS EPS_TTM, NetAssetPS AS NAPS, OperCashFlowPSTTM AS OCF_TTM, DividendTTM AS DIVIDEND_TTM, ROATTM AS ROA_TTM, ROICTTM AS ROIC_TTM, GrossIncomeRatio, NetProfitRatio, NPParentCompanyYOY, NPParentCompanyCutYOY, OperProfitGrowRate, TotalAssetGrowRate, CashRateOfSalesTTM from hsjy_gg.LC_MainIndexNew a LEFT JOIN hsjy_gg.SecuMain b ON a.CompanyCode=b.CompanyCode WHERE to_char(a.EndDate, 'yyyyMMdd')='{0}' and substr(b.SECUCODE, 0, 1) in ('0', '3', '6', '8') and length(b.SECUCODE) = 6".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_star_stock_finance_jy2(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, OperatingRevenueYOY AS OPER_REVENUE_YOY, NetProfitYOY AS NET_PROFIT_YOY, ROETTM AS ROE_TTM, EPSTTM AS EPS_TTM, NetAssetPS AS NAPS, OperCashFlowPSTTM AS OCF_TTM, DividendTTM AS DIVIDEND_TTM, ROATTM AS ROA_TTM, ROICTTM AS ROIC_TTM, GrossIncomeRatio, NetProfitRatio, NPParentCompanyYOY, NPParentCompanyCutYOY, OperProfitGrowRate, TotalAssetGrowRate, CashRateOfSalesTTM from hsjy_gg.LC_STIBMainIndex a left join hsjy_gg.SecuMain b on a.CompanyCode=b.CompanyCode where to_char(a.EndDate, 'yyyyMMdd')='{0}' and substr(b.SECUCODE, 0, 1) in ('0', '3', '6', '8') and length(b.SECUCODE) = 6 and a.IfMerged=1 and a.IfAdjusted=2".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_finance_jy3(self, date):
        sql = "SELECT b.SecuCode AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, \
               EPSTTM, NetAssetPS, OperatingRevenuePSTTM, CashFlowPSTTM, \
               ROATTM, ROETTM, ROICTTM, GrossIncomeRatioTTM, NetProfitRatioTTM, \
               CurrentRatio, QuickRatio, InterestCover, DebtAssetsRatio, \
               OperatingRevenueGrowRate,  NPParentCompanyYOY, NetOperateCashFlowYOY, NetAssetGrowRate, FAExpansionRate, \
               InventoryTRate, ARTRate, TotalAssetTRate, WorkingCaitalTRate, \
               CashRateOfSalesTTM , CapitalExpenditureToDM, OperCashInToAsset, \
               DividendPaidRatio, RetainedEarningRatio \
               from hsjy_gg.LC_MainIndexNew a LEFT JOIN hsjy_gg.SecuMain b ON a.CompanyCode=b.CompanyCode WHERE to_char(a.EndDate, 'yyyyMMdd')='{0}' and substr(b.SECUCODE, 0, 1) in ('0', '3', '6', '8') and length(b.SECUCODE)=6".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_star_stock_finance_jy3(self, date):
        sql = "select b.SECUCODE AS TICKER_SYMBOL, b.ChiNameAbbr AS SEC_SHORT_NAME, to_char(a.EndDate, 'yyyyMMdd') AS END_DATE, to_char(a.InfoPublDate, 'yyyyMMdd') AS PUBLISH_DATE, \
               EPSTTM, NetAssetPS, OperatingRevenuePSTTM, CashFlowPSTTM, \
               ROATTM, ROETTM, ROICTTM, GrossIncomeRatioTTM, NetProfitRatioTTM, \
               CurrentRatio, QuickRatio, InterestCover, DebtAssetsRatio, \
               OperatingRevenueYOY AS OperatingRevenueGrowRate,  NPParentCompanyYOY, NetOperateCashFlowYOY, NetAssetGrowRate, FAExpansionRate, \
               InventoryTRate, ARTRate, TotalAssetTRate, WorkingCaitalTRate, \
               CashRateOfSalesTTM , CapitalExpenditureToDM, OperCashInToAsset, \
               DividendPaidRatio, RetainedEarningRatio \
               from hsjy_gg.LC_STIBMainIndex a left join hsjy_gg.SecuMain b on a.CompanyCode=b.CompanyCode where to_char(a.EndDate, 'yyyyMMdd')='{0}' and substr(b.SECUCODE, 0, 1) in ('0', '3', '6', '8') and length(b.SECUCODE)=6 and a.IfMerged=1 and a.IfAdjusted=2".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    # def read_stock_cb_ch_given_date(self, date):
    #     sql = "SELECT CompanyCode AS COMPANY_CODE, to_char(ReportDate, 'yyyyMMdd') AS END_DATE, to_char(PublishDate, 'yyyyMMdd') AS PUBLISH_DATE, ReportStyle AS REPORT_STYLE, \
    #            CBSheet14 AS INVENTORY, CBSheet7 AS ACCOUNTS_RECEIVABLE, CBSheet11 AS ADVANCE_PAYMENT, CBSheet29 AS FIXED_ASSETS_GROSS_VALUE, CBSheet30 AS ACCUMULATED_DEPRECIATION \
    #            FROM finchina.CBSheet_New WHERE to_char(ReportDate, 'yyyyMMdd')='{0}'".format(date)
    #     df = self.get_df(sql, db='readonly', page_size=200000)
    #     return df
    #
    # def read_stock_ci_ch_given_date(self, date):
    #     sql = "SELECT CompanyCode AS COMPANY_CODE, to_char(ReportDate, 'yyyyMMdd') AS END_DATE, to_char(PublishDate, 'yyyyMMdd') AS PUBLISH_DATE, ReportStyle AS REPORT_STYLE, \
    #            CINST1 AS OPERATING_INCOME, CINST3 AS OPERATING_COST, CINST12 AS OPERATING_PROFIT, CINST24 AS NET_INCOME, CINST58 AS NET_INCOME_TP \
    #            FROM finchina.CINST_New WHERE to_char(ReportDate, 'yyyyMMdd')='{0}'".format(date)
    #     df = self.get_df(sql, db='readonly', page_size=200000)
    #     return df
    #
    # def read_stock_cf_ch_given_date(self, date):
    #     sql = "SELECT CompanyCode AS COMPANY_CODE, to_char(ReportDate, 'yyyyMMdd') AS END_DATE, to_char(PublishDate, 'yyyyMMdd') AS PUBLISH_DATE, ReportStyle AS REPORT_STYLE, \
    #            CFST4 AS CFO_IN, CFST9 AS CFO_OUT, CFST15 AS CFI_IN, CFST19 AS CFI_OUT, CFST24 AS CFF_IN, CFST29 AS CFF_OUT, CFST16 AS CF_FA \
    #            FROM finchina.CFST_New WHERE to_char(ReportDate, 'yyyyMMdd')='{0}'".format(date)
    #     df = self.get_df(sql, db='readonly', page_size=200000)
    #     return df

    def read_stock_ci_ch_given_date(self, date):
        sql = "SELECT CompanyCode AS COMPANY_CODE, to_char(ReportDate, 'yyyyMMdd') AS END_DATE, to_char(PublishDate, 'yyyyMMdd') AS PUBLISH_DATE, CINST1 AS REVENUE FROM finchina.CINST_New WHERE ReportStyle='11' AND to_char(ReportDate, 'yyyyMMdd')='{0}'".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_cf_ch_given_date(self, date):
        sql = "SELECT CompanyCode AS COMPANY_CODE, to_char(ReportDate, 'yyyyMMdd') AS END_DATE, to_char(PublishDate, 'yyyyMMdd') AS PUBLISH_DATE, CFST16 AS CAPEX FROM finchina.CFST_New WHERE ReportStyle='11' AND to_char(ReportDate, 'yyyyMMdd')='{0}'".format(date)
        df = self.get_df(sql, db='readonly', page_size=200000)
        return df

    def read_stock_info_ch(self):
        sql = "SELECT scdm, zqdm, zqmc, zqlx, gsdm FROM st_ashare.t_st_ag_zqdm WHERE zqlx IN ('EQA', 'EQB', 'HKE', 'SBA', 'SBB')"
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_fund_cumret_given_codes(self, mutual_codes, private_codes, start, end):
        df = hbs.commonQuery('ALL_JJJZ', gmdm=mutual_codes, smdm=private_codes, startDate=start, endDate=end, fields=['jjdm', 'jzrq', 'fqdwjz'])
        df = df.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': 'ADJ_NAV'})
        return df

    def get_stock_info(self, start, end):
        sql = "select TDATE, SYMBOL, SNAME, TOPEN, TCLOSE, HIGH, LOW, VOTURNOVER, VATURNOVER, NDEALS, AVGPRICE, AVGVOLPD, PCHG, MCAP, TCAP, TURNOVER from finchina.CHDQUOTE where TDATE >= '{0}' and TDATE <= '{1}'".format(start, end)
        df = self.get_df(sql, db='readonly', page_size=2000000)
        return df

    def get_bloomberg_symbol(self):
        sql = "SELECT a.jjdm 基金代码, c.mbz 彭博代码 FROM st_hedge.t_st_rhb a JOIN st_hedge.t_st_jjjz b ON a.jjdm=b.jjdm AND a.jzrq=b.jzrq JOIN broadcast.t_st_gg_zm c ON c.zhbh='092' AND c.dxz=a.jjdm WHERE a.m_opt_type<>'03' ORDER BY a.jjdm"
        df = self.get_df(sql, db='highuser', page_size=2000000)
        return df

    def read_overseas_index_daily_k_given_indexs(self, indexs):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT bzzsdm, jyrq, px_last, cur_mkt_cap, free_float_market_cap, turnover, px_volume, indx_traded_val, pe_ratio, indx_px_sales, eqy_dvd_yld_12m, dvd_sh_12m FROM st_market.t_st_zs_bbzshq WHERE bzzsdm in ({0}) and m_opt_type<>'03'".format(indexs)
        df = self.get_df(sql, db='alluser', page_size=2000000)
        return df

    def read_overseas_index_finance_given_indexs(self, indexs):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT bzzsdm, jyrq, px_to_book_ratio, px_to_cash_flow, trail_12m_eps_bef_xo_item, book_val_per_sh, trail_12m_net_sales, trail_12m_sales_per_sh, return_com_eqy, return_on_cap, trail_12m_gross_margin, trail_12m_prof_margin, trail_12m_cap_expend, cf_cash_from_fnc_act, return_on_asset FROM st_market.t_st_zs_bbzscwzb WHERE bzzsdm in ({0}) and m_opt_type<>'03'".format(indexs)
        df = self.get_df(sql, db='alluser', page_size=2000000)
        return df

    def read_overseas_index_best_given_indexs(self, indexs):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT bzzsdm, jyrq, best_pe_ratio, best_px_bps_ratio, best_px_sales_ratio, best_px_cps_ratio, best_div_yld, best_eps, best_cps, best_dps, best_roe, best_roa, best_sales, best_net_income, best_gross_margin, best_ni_adj_to_sales, best_capex FROM st_market.t_st_zs_bbzsyg WHERE bzzsdm in ({0}) and m_opt_type<>'03'".format(indexs)
        df = self.get_df(sql, db='alluser', page_size=2000000)
        return df

    def read_overseas_cal(self, market_id):
        sql = "select scdm, rq, sfjy, sfzm, sfym, sfnm from st_main.t_st_gg_hwjyrl where scdm='{0}' and m_opt_type <> '03'".format(market_id)
        df = self.get_df(sql, "alluser", page_size=2000000)
        return df

if __name__ == '__main__':
    dates = HBDB().read_fund_barra_attribution_given_code('450004')
    barra_style_exposure = HBDB().read_barra_style_exposure_given_dates(fund_zc_wmv['RECENT_TRADE_DATE'].unique().tolist())
    barra_style_exposure.to_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/barra_style_exposure.hdf', key='table', mode='w')

    stock_info = HBDB().get_stock_info('20230928', '20231013')
    stock_info = stock_info[['TDATE', 'SYMBOL', 'SNAME', 'TOPEN', 'TCLOSE', 'HIGH', 'LOW', 'VOTURNOVER', 'VATURNOVER', 'NDEALS', 'AVGPRICE', 'AVGVOLPD', 'PCHG', 'MCAP', 'TCAP', 'TURNOVER']]
    stock_info.to_csv('E:/周5_市场数据跟踪/code/stk.new.csv', index=None)