"""
安值的估值表解析
"""
import datetime
import os
import pandas as pd
import datetime


def load_holding(data_path):
    filenames = os.listdir(data_path)
    for filename in filenames:
        data = pd.read_excel(
            os.path.join(data_path, filename), sheet_name=0, header=7).dropna(subset=['科目代码', '数量', '行情'])
        data = data[data['科目代码'].str.startswith('1103')]
        data['ticker'] = data['科目代码'].apply(lambda x: x.split('.')[-1])
        data['ticker'] = data['ticker'].apply(lambda x: x.replace(' ', '.'))
        data.rename(columns={"市值占比": "weight"}, inplace=True)
        weight_df = data.groupby('ticker')['weight'].sum().reset_index()
        tmp = weight_df.copy()
        # 对应正股的市值
        cb_df = pd.read_excel("D:\\可转债正股信息.xlsx", sheet_name=0)
        cb_df.rename(columns={"证券代码": "ticker"}, inplace=True)
        weight_df = weight_df.merge(cb_df, on='ticker')
        weight_df['code'] = weight_df['正股代码'].apply(lambda x: x.split('.')[0])

        trade_date = filename.split('.')[0][-8:]
        style_factor = pd.read_csv(
            "D:\\kevin\\risk_model_jy\\RiskModel\\data\\zzqz_sw\\style_factor\\{}.csv".format(trade_date))
        style_factor['ticker'] = style_factor['ticker'].apply(lambda x: str(x).zfill(6))

        idx = list(set(style_factor['ticker']).intersection(set(weight_df['code'])))

        res_df = weight_df.set_index('code').reindex(idx)[['weight']].T.dot(
            style_factor.set_index('ticker').reindex(idx)['size'])

        print("日期时点 = {}，持有{}只转债，持仓权重之和 = {}，当期市值敞口 = {}".format(
            trade_date, tmp.shape[0], tmp['weight'].sum(), res_df.loc["weight"]))


if __name__ == '__main__':
    load_holding("D:\\估值表基地\\安值福慧量化1号")