import numpy as np
import pandas as pd

from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.project.multi_factor.alpha_model.exposure.alpha_factor import AlphaFactor


class AlphaTHS(AlphaFactor):

    """
    因子说明： -最近10天 同花顺点击数量 平均
    """

    def __init__(self):

        AlphaFactor.__init__(self)
        self.exposure_path = self.data_path
        self.raw_factor_name = 'alpha_raw_ths'

    def cal_factor_exposure(self, beg_date, end_date):

        """ 计算因子暴露 """

        # param
        term = 10
        effective_term = int(term / 2)

        # read data
        click_num = Stock().read_factor_h5("click_num")

        # calculate data daily
        date_series = Date().get_trade_date_series(beg_date, end_date)
        date_series = list(set(date_series) & set(click_num.columns))
        date_series.sort()
        res = pd.DataFrame()

        for i in range(0, len(date_series)):

            current_date = date_series[i]
            data_beg_date = Date().get_trade_date_offset(current_date, -(term - 1))
            data_period = click_num.loc[:, data_beg_date:current_date]
            data_period = data_period.T.dropna(how='all')

            if len(data_period) > effective_term:
                print('Calculating factor %s at date %s' % (self.raw_factor_name, current_date))
                data_date = - data_period.mean()
                effective_number = data_period.count()
                data_date[effective_number <= effective_term] = np.nan
                data_date = pd.DataFrame(data_date)
                data_date.columns = [current_date]
            else:
                print('Calculating factor %s at date %s is null' % (self.raw_factor_name, current_date))
                data_date = pd.DataFrame([], columns=[current_date], index=click_num.index)

            res = pd.concat([res, data_date], axis=1)

        res = res.T.dropna(how='all').T
        self.save_alpha_factor_exposure(res, self.raw_factor_name)


if __name__ == "__main__":

    from datetime import datetime
    beg_date = '20040101'
    end_date = datetime.today()

    self = AlphaTHS()
    self.cal_factor_exposure(beg_date, end_date)
