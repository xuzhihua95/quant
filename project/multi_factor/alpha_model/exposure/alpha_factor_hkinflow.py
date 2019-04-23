import numpy as np
from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.project.multi_factor.alpha_model.exposure.alpha_factor import AlphaFactor


class AlphaHKInflow(AlphaFactor):

    """
    因子说明: 北向资金净流入(6月), 持股数变动*日均成交价
    """

    def __init__(self):

        AlphaFactor.__init__(self)
        self.exposure_path = self.data_path
        self.raw_factor_name = 'alpha_raw_hk_inflow'

    def cal_factor_exposure(self, beg_date, end_date):

        """ 计算因子暴露 """

        term = 120

        # read data
        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)
        share = Stock().read_factor_h5("HK2CHoldShare")
        price = Stock().read_factor_h5("Price_Unadjust")

        vol = price.mul(share) / 1000000
        vol = vol.T.dropna(how='all')
        vol = vol.loc[beg_date:end_date, :]
        vol = vol.fillna(0.0)

        vol_bias = vol.diff(periods=term)
        vol_bias = vol_bias.T
        vol_bias = vol_bias.replace(0, np.nan)

        # save data
        vol_bias = vol_bias.T.dropna(how='all').T
        self.save_alpha_factor_exposure(vol_bias, self.raw_factor_name)

if __name__ == "__main__":

    from datetime import datetime
    beg_date = '20040101'
    end_date = datetime.today()

    self = AlphaHKInflow()
    self.cal_factor_exposure(beg_date, end_date)
