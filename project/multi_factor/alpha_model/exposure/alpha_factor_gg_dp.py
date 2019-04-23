import pandas as pd
from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.utility.factor_preprocess import FactorPreProcess
from quant.project.multi_factor.alpha_model.exposure.alpha_factor import AlphaFactor


class AlphaGGEP(AlphaFactor):

    """
    因子说明: wind一致预测滚动每股股利 / 未复权股价
    """

    def __init__(self):

        AlphaFactor.__init__(self)
        self.exposure_path = self.data_path
        self.raw_factor_name = 'alpha_raw_gg_ep'

    def cal_factor_exposure(self, beg_date, end_date):

        """ 计算因子暴露 """

        # read data
        long_term = 35
        short_term = 5

        # read data
        d0 = Stock().read_factor_h5("Est_Avgdps_M0")
        d1 = Stock().read_factor_h5("Est_Avgdps_1")
        price = Stock().read_factor_h5("Price_Unadjust")
        date_series = Date().get_trade_date_series(beg_date, end_date)
        date_series = list(set(date_series) & set(d0.columns) & set(d1.columns) & set(price.columns))
        date_series.sort()
        result = pd.DataFrame()

        for i in range(0, len(date_series)):

            current_date = date_series[i]
            long_beg_date = Date().get_trade_date_offset(current_date, -(long_term - 1))
            short_beg_date = Date().get_trade_date_offset(current_date, -(short_term - 1))

        # save data
        ep = ep.T.dropna(how='all').T
        self.save_alpha_factor_exposure(ep, self.raw_factor_name)

if __name__ == "__main__":

    from datetime import datetime
    beg_date = '20040101'
    end_date = datetime.today()

    self = AlphaGGEP()
    self.cal_factor_exposure(beg_date, end_date)
