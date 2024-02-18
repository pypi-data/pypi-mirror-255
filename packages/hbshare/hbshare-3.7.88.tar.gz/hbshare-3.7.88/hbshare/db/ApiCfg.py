from enum import Enum
from lib2to3.pytree import Node
from hbshare.base.upass import is_prod_env

# 办公环境
DOMAINS_OFFICE = {'hbcgi': 'data.howbuy.com', 's': 's.howbuy.com',
                  'ams': 'ams-data.intelnal.howbuy.com', 
                  'ams-admin': 'ams.howbuy.com'
                #   'ams-admin': 'ams.it38.k8s.howbuy.com'
                  }

# 产线环境
DOMAINS_PROD = {'hbcgi': 'data.howbuy.com', 's': 's.howbuy.com',
                'ams': 'ams.inner.howbuy.com', 'ams-admin': 'ams.howbuy.com'}
P_TYPE = {'http': 'http://', 'ftp': 'ftp://', 'https': 'https://'}


class UrlCfg():
    def __init__(self, url, method, domain, parsePostDataFunc, parseParamsFunc, supportFields):
        self.__url__ = url
        self.method = method
        self.__domain__ = domain
        self.__parsePostDataFunc__ = parsePostDataFunc
        self.__parseParamsFunc__ = parseParamsFunc
        self.supportFields = supportFields

    def parsePostData(self, kwargs):
        return self.__parsePostDataFunc__(kwargs)

    def parseParams(self, kwargs):
        return self.__parseParamsFunc__(kwargs)

    def getUrl(self):
        if is_prod_env():
            return self.__url__ % DOMAINS_PROD.get(self.__domain__)
        return self.__url__ % DOMAINS_OFFICE.get(self.__domain__)

    def supportFields(self):
        return self.supportFields


class UrlEnum(Enum):

    @classmethod
    def getValue(self, name):
        '''根据枚举name匹配到枚举对象，并返回对应的value'''
        for k, member in self.__members__.items():
            if name == k:
                return member.value
        else:
            return None

############################### 指数 ###############################
    MARKET_SPJG = UrlCfg('http://%s/data/zs/spj', 'get', 'ams',
                       lambda x: {},
                        lambda y: {
                           'dm': y['zqdm'],
                           'startTime': y['startDate'],
                           'endTime': y['endDate']
                        },
                       supportFields=('hb1n', 'hb1y', 'hb1z', 'hb2n', "hb3n","hb3y","hb5n",
                                      "hb6y","hbcl","hbjn","jjsl","jyrq","scdm","spjg","tjrq","zqdm"
                                      )
                       )
    ''' 查询指数行情收盘价格 '''
    MARKET_SPJG_BATCH = UrlCfg('http://%s/data/zs/spj/batch', 'post', 'ams',
                        lambda x: {
                           'sczs': x.get('sczs'),
                           'gmclzs': x.get('gmclzs'),
                           'smclzs': x.get('smclzs'),
                           'startTime': x['startDate'],
                           'endTime': x['endDate'],
                           'fields': x['fields']
                        },
                        lambda y: {},
                       supportFields=('hb1n', 'hb1y', 'hb1z', 'hb2n', "hb3n","hb3y","hb5n",
                                      "hb6y","hbcl","hbjn","jjsl","jyrq","scdm","spjg","tjrq","zqdm"
                                      )
                       )
    ''' 查询指数行情收盘价格多个指数代码 '''    

################################ 公募 ################################
    # 公募基金净值
    FUND_JJJZ = UrlCfg('http://%s/data/gm/jz', 'get', 'ams',
                       lambda x: {
                           'dm': x['jjdm'],
                            'startTime': x['startDate'],
                            'endTime': x['endDate']
                       },
                       lambda y: {
                           'dm': y['jjdm'],
                            'startTime': y['startDate'],
                            'endTime': y['endDate']
                        },
                       supportFields=('jzrq', 'jjdm', 'jjjz', 'ljjz', 'hbcl','hbdr','fqdwjz')
                       )
    '''公募基金净值'''
    # 公募基金净值多基金代码

    ALL_JJJZ = UrlCfg('http://%s/data/all/jz', 'post', 'ams',
                       lambda x: {
                            'gmdm': x.get('gmdm'),
                            'smdm': x.get('smdm'),
                            'startTime': x['startDate'],
                            'endTime': x['endDate'],
                            'fields': x['fields']
                       },
                       lambda y: {},
                       supportFields=('jzrq', 'jjdm', 'jjjz', 'ljjz', 'hbcl','hbdr','fqdwjz')
                       )
    '''公募基金净值多基金代码'''

    #  私募基金回报数据
    SIMU_RHB = UrlCfg('http://%s/data/fund/jzgy/rhb', 'post', 'ams',
                      lambda x: {
                          'jjdm': x['jjdm'],
                          'jzrq': {
                              'startDate': x['startDate'],
                              'endDate': x['endDate']
                          },
                          'fields': x['fields'],
                          'page': x['page'],
                          'perPage': x['perPage']
                      },
                      lambda y: {},
                      supportFields=('jjdm', 'jzrq', 'hbdr',
                                     'hbcl', 'hbfh', 'fqdwjz',)
                      )
    ''' 私募基金回报数据 '''
    # 私募基金净值
    SIMU_JJJZ = UrlCfg('http://%s/data/sm/jz', 'get', 'ams',
                       lambda x: {
                           'dm': x['jjdm'],
                            'startTime': x['startDate'],
                            'endTime': x['endDate']
                       },
                       lambda y: {
                           'dm': y['jjdm'],
                            'startTime': y['startDate'],
                            'endTime': y['endDate']
                        },
                       supportFields=('jzrq', 'jjdm', 'jjjz', 'ljjz', 'hbcl','hbdr','fqdwjz')
                       )
    '''私募基金净值'''

################################ A股市场/科创板 ################################
    # 非标数据日净值 - 日净值分页查询
    FB_RJZ = UrlCfg('https://%s/admin/dailyNetValue/queryList', 'post', 'ams-admin',
                    lambda x: {
                        'belongDate': {
                            'startDate': x.get('startDate'),
                            'endDate': x.get('endDate')
                        },
                        'jjdm': x.get('jjdm'),
                        # 接口查询 人员下的基金代码 再拼接 参数基金代码去做查询。
                        'rydm': x.get('rydm'),
                        'sorts': [{'jjdm': 'desc', 'jzrq': 'asc'}],
                        'page': x['page'],
                        'perPage': x['perPage']
                    },
                    lambda y: {'access_token': y['access_token']},
                    supportFields=('jjdm', 'jjmc', 'netValue', 'netValueDate', 'fqdwjz', 'ljjz',
                                   'glry', 'glrymc', 'researchers', 'updateTime',
                                   'updateUsername', 'createdUser', 'createdUsername', 'createdTime')
                    )
    '''非标数据日净值 - 日净值分页查询'''
    # fof估值子基金 - 查询子基金列表
    FOF_ZJJLIST = UrlCfg('https://%s/admin/fof/gz/sf/list', 'post', 'ams-admin',
                         lambda x: {
                             'jzrq': {
                                 'startDate': x.get('startDate'),
                                 'endDate': x.get('endDate')
                             },
                             'jjdm': x.get('jjdm'),
                             'khdm': x.get('khdm'),
                             #   数据状态 1-正常 0-异常 不传为 null
                             'state': x.get('state'),
                             'sorts': [{'jjdm': 'desc', 'jzrq': 'asc'}],
                             'page': x['page'],
                             'perPage': x['perPage']
                         },
                         lambda y: {'access_token': y['access_token']},
                         supportFields=('dataSource', 'sjly', 'jjdm', 'originalJjdm', 'jjmc', 'khdm', 'originalKhdm',
                                        'khmc', 'jzrq', 'jjjz', 'ljjz', 'xnjz', 'khzcfe', 'khzcjz', 'jsrq', 'ferq',
                                        'febdrq', 'qrrq', 'fsfe', 'xnyjbc', 'yjbclx', 'jtfs', 'jtqzcjz', 'jtqzcjz2',
                                        'scjtrq', 'mrdwjz', 'mrljdwjz', 'scjtdwjz', 'scjtljdwjz', 'glr', 'tgr', 'jjzh',
                                        'jyzh', 'khlx', 'zjlx', 'zjhm', 'xsjg', 'ztfhtx', 'ztshtx', 'bz', 'state')
                         )
    '''fof估值子基金 - 查询子基金列表'''
        # fof历史净值 - 查询历史净值
    FOF_LSJZ = UrlCfg('https://%s/admin/sm/fof/sy/lsjz', 'get', 'ams-admin',
                         lambda x: {},
                         lambda y: {'access_token': y['access_token'],'dm':y['jjdm']},
                         supportFields=('jzrq', 'ljjz', 'jjjz')
                         )
    '''fof估值子基金 - 查询历史净值'''