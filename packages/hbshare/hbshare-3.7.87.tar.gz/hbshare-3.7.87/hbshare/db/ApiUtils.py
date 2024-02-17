from hbshare.db.ApiCfg import UrlEnum
# from ApiCfg import UrlEnum
from hbshare.base.data_pro import hb_api
import hbshare as hbs
import pandas as pd
import time  

def commonQuery(key, pause=0.01, timeout=10, **kwargs):
    '''
        通用Api调用方法
        :param key: 指定API枚举
        :param fields: 限定查询结果列,可选,默认使用API配置的所有字段
        :return: 以fields为列的dataframe
    '''
    if key is None and kwargs['key']:
        key = kwargs['key']
    if key is None:
        raise ValueError('必须指定接口')
    if UrlEnum.getValue(key):
        return OldQuery.commonQuery(key,pause,timeout,**kwargs)
    return NewQuery.commonQuery(key,pause,timeout,**kwargs)

class OldQuery():
    @classmethod
    def fieldsCheckd(self,kwargs, supportFields: tuple):
        fields = kwargs.get('fields')
        if fields is None or len(fields) == 0:
            # 元组转list
            kwargs['fields'] = list(supportFields)
            return
        for field in fields:
            if field not in supportFields:
                raise ValueError("field %s not supported" % field)
            
    @classmethod
    def commonQuery(self,urlEnum, pause=0.01, timeout=10, **kwargs):
        if type(urlEnum) is str:
            cfg = UrlEnum.getValue(urlEnum)
        else:
            cfg = urlEnum.value
        if kwargs is None:
            kwargs = {}
        # 判断目标字段是否指定，没指定则使用接口支持字段
        self.fieldsCheckd(kwargs, cfg.supportFields)
        api = hb_api(timeout=timeout)
        pages = 1
        page = 1
        perPage = 1000
        data = []
        while page <= pages:
            kwargs['page'] = page
            kwargs['perPage'] = perPage
            try:
                # json传参
                post_data = cfg.parsePostData(kwargs)
                # url链接后拼接
                params = cfg.parseParams(kwargs)
            except KeyError as e:
                raise RuntimeError("Use commonQuery(%s) failed,parameter %s not found" % (urlEnum, e.args[0]))
            org_js = api.query(cfg.getUrl(), method=cfg.method,
                               params=params, post_data=post_data)
            status_code = str(org_js['code'])
            if status_code != '0000':
                status = str(org_js['desc'])
                raise ValueError(status)
            if 'body' not in org_js:
                status = "未查询到数据"
                raise ValueError(status)
            body = org_js['body']
            if body is None:
                break
            if type(body) is list and 'pages' not in body:
                # 接口不分页
                data += org_js['body']
                break
            if 'records' in body and 'pages' in body:
                # 总页数
                pages = body['pages']
                # 页码加1
                page += 1
                data += body['records']
                time.sleep(pause)
                continue
            # 返回的是单个对象
            data.append(body)
        prod_df = pd.DataFrame(data, columns=kwargs['fields'])
        return prod_df
    
class NewQuery():
    
    @classmethod
    def commonQuery(self,key, pause=0.01, timeout=10, **kwargs):
        if kwargs is None:
            kwargs = {}
        url = 'http://fpc-data.intelnal.howbuy.com/data/access/commonapi'
        api = hb_api(timeout=timeout)
        pageNum = 1
        pageSize = 3000
        kwargs['ifByPage'] = 1
        kwargs['key'] = key
        fields = kwargs['fields']
        if fields and type(fields) is list and len(fields) > 0:
            fieldsStr = ','.join(fields)
            kwargs['fields'] = fieldsStr
        data = []
        while pageNum <= 500:
            kwargs['pageNum'] = pageNum
            kwargs['pageSize'] = pageSize
            # json传参
            post_data = kwargs
            org_js = api.query(url=url, method='POST',params={}, post_data=post_data)
            returnCode = str(org_js['returnCode'])
            if returnCode != 'F0000000':
                returnMsg = str(org_js['returnMsg'])
                raise ValueError(returnMsg)
            if 'data' not in org_js:
                status = "未查询到数据"
                raise ValueError(status)
            tmp = org_js['data']
            if tmp is None or len(tmp) == 0:
                break
            data += tmp
            if len(tmp) < pageSize:
                break
            # 页码加1
            pageNum += 1
            time.sleep(pause)
        return pd.DataFrame(data)


if __name__ == '__main__':
    # '20211101', '20231105'
    data = hbs.commonQuery('SECTOR_FACTOR',startDate='20060104', endDate='20210112',
                           fields=['tradeDate', 'bigfinance',
                                   'consuming', 'tmt', 'cycle']
                           )
    print(data)

