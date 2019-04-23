import os
from datetime import datetime

from quant.stock.date import Date
from quant.stock.index import Index
from quant.project.timing.exposure.timing_factor import TimingFactor
from quant.project.multi_factor.alpha_model.exposure.alpha_factor import AlphaFactor


class TFactorROE(TimingFactor):

    """
    指数ROE
    """

    def __init__(self):

        TimingFactor.__init__(self)
        self.factor_name = "ROE"

    @staticmethod
    def score_average_diff(x):

        """ 将均线点位差转换成为仓位，在100%和-100%之间 """

        if x >= 0:
            position = 1
        else:
            position = -1

        return position

    def cal_factor_exposure(self, beg_date, end_date, index_code, index_name):

        """ 计算指标数值 """

        term = 20

        path = AlphaFactor().exposure_hdf_path
        factor_series = self.cal_factor_from_stock("alpha_raw_roe", path, index_code, self.factor_name)
        factor_series = factor_series.rolling(window=term).mean()
        factor_series = factor_series.loc[beg_date:end_date, :]
        self.factor_index_plot(factor_series, self.factor_name, index_code, index_name, 1)


if __name__ == "__main__":

    beg_date = "20050301"
    end_date = datetime.today().strftime("%Y%m%d")
    index_code = "000300.SH"
    index_name = "沪深300"
    self = TFactorROE()
    self.cal_factor_exposure(beg_date, end_date, index_code, index_name)
