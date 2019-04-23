import numpy as np
import pandas as pd

from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.project.multi_factor.alpha_model.exposure.alpha_factor import AlphaFactor


class AlphaEBIT2IncomeQoQ(AlphaFactor):

    """
    因子说明：息税前利润_TTM /营业总收入_TTM 环比增长率
    """

    def __init__(self):

        AlphaFactor.__init__(self)
        self.exposure_path = self.data_path
        self.raw_factor_name = 'alpha_raw_ebit2income_qoq'

    def cal_factor_exposure(self, beg_date, end_date):

        """ 计算因子暴露 """

        # param
        ebit = Stock().read_factor_h5("EBIT") / 100000000
        ebit_ttm = Stock().change_cum_quarter_to_ttm_quarter(ebit, type="quarter")
        income = Stock().read_factor_h5("OperatingIncomeTotal")
        income_ttm = Stock().change_single_quarter_to_ttm_quarter(income)
        income_ttm[income_ttm == 0] = np.nan

        ebit2income = ebit_ttm.div(income_ttm)
        e2i_qoq = ebit2income.T.diff().T

        report_data = Stock().read_factor_h5("ReportDateDaily")
        e2i_qoq = Stock().change_quarter_to_daily_with_disclosure_date(e2i_qoq, report_data, beg_date, end_date)

        res = e2i_qoq.T.dropna(how='all').T
        self.save_alpha_factor_exposure(res, self.raw_factor_name)


if __name__ == "__main__":

    from datetime import datetime
    beg_date = '20040101'
    end_date = datetime.today()

    self = AlphaEBIT2IncomeQoQ()
    self.cal_factor_exposure(beg_date, end_date)
