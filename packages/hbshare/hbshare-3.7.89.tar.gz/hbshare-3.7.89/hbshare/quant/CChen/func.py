import pymysql
import numpy as np
import pandas as pd
from scipy import optimize as sco


def generate_table(database, table, generate_sql, sql_ip, sql_user, sql_pass, table_comment=''):
    db = pymysql.connect(host=sql_ip, user=sql_user, password=sql_pass, database=database)

    cursor = db.cursor()

    sql = 'create table if not exists `' + table + '` ' + generate_sql + ' comment=\'' + table_comment + '\''
    cursor.execute(sql)
    db.close()


def portfolio_var(weights, cov_matrix):
    return np.dot(weights.T, np.dot(cov_matrix, weights))


def risk_contribute(weights, cov_matrix):
    std = np.sqrt(portfolio_var(weights, cov_matrix))
    mrc = np.matrix(cov_matrix) * np.matrix(weights).T
    return np.multiply(mrc, np.matrix(weights).T) / std


def portfolio_annualised_performance(weights, mean_returns, cov_matrix, freq=252):
    returns = np.sum(mean_returns * weights) * freq
    std = np.sqrt(portfolio_var(weights, cov_matrix)) * np.sqrt(freq)
    return std, returns


def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate, freq=252):
    p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix, freq=freq)
    return -(p_ret - risk_free_rate) / p_var


def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate=0.015, freq=252, single_max=0.3):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate, freq)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    # bound = (0.0, 1.0)
    # bounds = tuple(bound for asset in range(num_assets))
    bounds = sco.Bounds([0] * num_assets, [single_max] * num_assets)
    result = sco.minimize(
        negative_sharpe_ratio,
        np.array(num_assets * [1 / num_assets]),
        args=args,
        bounds=bounds,
        constraints=constraints
    )
    return pd.DataFrame(
        result.x,
        index=mean_returns.index,
        columns=['allocation']
    )


def risk_error_sum(weights, cov_matrix):
    # print(weights)
    p_vol = np.sqrt(portfolio_var(weights=weights, cov_matrix=cov_matrix))
    asset_rc = risk_contribute(weights=weights, cov_matrix=cov_matrix)
    return sum(np.abs(asset_rc - p_vol / len(weights)))[0, 0]


def total_weight_constraint(x):
    return np.sum(x) - 1.0


def long_only_constraint(x):
    return x


def risk_parity(cov_matrix, single_max=1, max_i=5000):
    w0 = [0.5] * len(cov_matrix)
    cons = (
        {'type': 'eq', 'fun': total_weight_constraint}
        # {'type': 'ineq', 'fun': long_only_constraint}
    )
    res = sco.minimize(
        risk_error_sum,
        np.array(w0),
        args=cov_matrix,
        constraints=cons,
        bounds=sco.Bounds([0] * len(cov_matrix), [single_max] * len(cov_matrix)),
        options={
            'disp': True,
            'maxiter': max_i
        },
        method='SLSQP',
    )
    return res


if __name__ == '__main__':
    from hbshare.quant.CChen.db_const import sql_write_path_work
    from hbshare.quant.CChen.cta_factor.analysis import cta_factor_line
    from datetime import datetime, timedelta

    endDate = datetime(2023, 10, 31).date()
    startDate = endDate - timedelta(days=365 * 2)

    factors = {
        'tsmom_dzq': '短时序动量',
        'tsmom_zzq': '中时序动量',
        'tsmom_czq': '长时序动量',
        'xsmom_dzq': '短截面动量',
        'xsmom_zzq': '中截面动量',
        'xsmom_czq': '长截面动量',
        'qxjg': '期现结构',
        'tsbasismom_dzq': '短基差动量',
        'tsbasismom_zzq': '长基差动量',
        'xssigma_d20_q75': '波动率',
    }

    data_table = 'cta_index'
    path = sql_write_path_work['daily']

    data = cta_factor_line(
        cta_factors=factors,
        start_date=startDate,
        end_date=endDate,
        table=data_table,
        sql_path=path,
        freq=''
    )
    lb_p = 125
    range_p = 250
    rp_df = pd.DataFrame()
    for i in range(range_p):
        data_slice = data.iloc[len(data) - range_p + 1 + i - lb_p:len(data) - range_p + 1 + i]

        returns = data_slice.pct_change()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()

        rp_w = risk_parity(cov_matrix=cov_matrix).x
        rp_df = pd.concat([rp_df, pd.DataFrame(rp_w, columns=[data_slice.index.tolist()[-1]], index=data.columns).T])
    print()
