import numpy as np
import pandas as pd

from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.project.multi_factor.alpha_model.exposure.alpha_factor import AlphaFactor


class AlphaEBIT2EV(AlphaFactor):

    """
    因子说明：息税前利润_TTM / 企业价值(剔除货币资金)
    """

    def __init__(self):

        AlphaFactor.__init__(self)
        self.exposure_path = self.data_path
        self.raw_factor_name = 'alpha_raw_ebit2ev'

    def cal_factor_exposure(self, beg_date, end_date):

        """ 计算因子暴露 """

        # param
        ebit = Stock().read_factor_h5("EBIT")  / 100000000
        ebit_ttm = Stock().change_cum_quarter_to_ttm_quarter(ebit, type="quarter")

        report_data = Stock().read_factor_h5("ReportDateDaily")
        ebit_ttm = Stock().change_quarter_to_daily_with_disclosure_date(ebit_ttm, report_data, beg_date, end_date)
        ev = Stock().read_factor_h5("Ev2") / 100000000

        # data precessing
        [ebit_ttm, ev] = Stock().make_same_index_columns([ebit_ttm, ev])
        res = ebit_ttm.div(ev)

        res = res.T.dropna(how='all').T
        self.save_alpha_factor_exposure(res, self.raw_factor_name)


if __name__ == "__main__":

    from datetime import datetime
    beg_date = '20040101'
    end_date = datetime.today()

    self = AlphaEBIT2EV()
    self.cal_factor_exposure(beg_date, end_date)
