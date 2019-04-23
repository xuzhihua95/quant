from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.utility.factor_preprocess import FactorPreProcess
from quant.project.multi_factor.alpha_model.exposure.alpha_factor import AlphaFactor


class AlphaHKHoldPct(AlphaFactor):

    """
    因子说明: 北向资金持仓比例
    """

    def __init__(self):

        AlphaFactor.__init__(self)
        self.exposure_path = self.data_path
        self.raw_factor_name = 'alpha_raw_hk_hold_pct'

    def cal_factor_exposure(self, beg_date, end_date):

        """ 计算因子暴露 """

        # read data
        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)
        pct = Stock().read_factor_h5("HK2CHold").T
        pct = pct.loc[beg_date:end_date, :].T

        # save data
        pct = pct.T.dropna(how='all').T
        self.save_alpha_factor_exposure(pct, self.raw_factor_name)

if __name__ == "__main__":

    from datetime import datetime
    beg_date = '20040101'
    end_date = datetime.today()

    self = AlphaHKHoldPct()
    self.cal_factor_exposure(beg_date, end_date)
