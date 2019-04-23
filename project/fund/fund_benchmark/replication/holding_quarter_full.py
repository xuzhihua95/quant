import os
import pandas as pd
from datetime import datetime

from quant.data.data import Data
from quant.stock.date import Date
from quant.stock.index import Index
from quant.stock.stock import Stock
from quant.fund.fund_pool import FundPool
from quant.fund.fund_holder import FundHolder
from quant.fund.fund_factor import FundFactor
from quant.source.backtest import BackTest
from quant.source.wind_portfolio import WindPortUpLoad


class HoldingQuarter(Data):

    """
    每个季度末得到公募主动股票基金的平均持仓 满仓股票
    """

    def __init__(self):

        Data.__init__(self)

        self.port_name = "基金持仓基准基金池_等权季报满仓_季报日"
        self.wind_port_path = WindPortUpLoad().path
        self.data_weight_path = Index().data_path_weight
        self.data_factor_path = Index().data_data_factor

        self.stock_ratio = None

    def cal_weight_date(self, quarter_date):

        """ 单个季度公募主动股票基金平均权重 每个基金的权都为1 """

        fund_pool = FundPool().get_fund_pool_code(name="基金持仓基准基金池", date="20181231")

        for i_fund in range(len(fund_pool)):
            fund = fund_pool[i_fund]
            try:
                fund_holding = FundHolder().get_fund_stock_weight_quarter(fund=fund)
                fund_holding_date = pd.DataFrame(fund_holding[quarter_date])
                fund_holding_date = fund_holding_date.dropna()
                fund_holding_date *= 1.0
                fund_holding_date.columns = [fund]
            except Exception as e:
                fund_holding_date = pd.DataFrame([], columns=[fund])
            if i_fund == 0:
                stock_data = fund_holding_date
            else:
                stock_data = pd.concat([stock_data, fund_holding_date], axis=1)

        stock_data = stock_data.dropna(how='all')
        stock_data_weight = pd.DataFrame(stock_data.sum(axis=1))
        return stock_data_weight

    def cal_all_wind_file(self):

        """ 计算 所有季报日 公募主动股票基金 基金平均持仓 还要考虑股票仓位 并生成wind文件"""

        date_series = Date().get_normal_date_series("20060101", datetime.today(), "S")

        for i_date in range(len(date_series)):

            quarter_date = date_series[i_date]
            stock_data_weight = self.cal_weight_date(quarter_date)
            stock_data_weight.columns = ["Weight"]
            stock_data_weight /= stock_data_weight.sum()
            print(len(stock_data_weight))

            publish_date = Date().get_trade_date_offset(quarter_date, 0)
            stock_data_weight.index.name = "Code"
            stock_data_weight["CreditTrading"] = "No"
            stock_data_weight["Date"] = publish_date
            stock_data_weight["Price"] = 0.0
            stock_data_weight["Direction"] = "Long"

            sub_path = os.path.join(self.wind_port_path, self.port_name)
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)

            file = os.path.join(sub_path, '%s_%s.csv' % (self.port_name, publish_date))
            stock_data_weight.to_csv(file)

    def backtest(self):

        """ 计算 回测结果 """

        port = BackTest()
        port.set_info(self.port_name, '885000.WI')
        port.read_weight_at_all_change_date()
        port.cal_weight_at_all_daily()
        port.cal_port_return()
        port.cal_turnover()
        port.cal_summary()

    def cal_weight_data(self):

        """
        将每天权重结果 和 指数每日涨跌幅表现 写入Index数据当中
        """

        port = BackTest()
        port.set_info(self.port_name, "885000.WI")
        port.get_weight_at_all_daily()
        port.get_port_return()
        port_daily = port.port_hold_daily

        # 写入每日收益率
        data = pd.DataFrame(port.port_return['PortReturn'])
        data.columns = ['PCT']
        data["CLOSE"] = (data['PCT'] + 1.0).cumprod() * 1000
        sub_path = self.data_factor_path
        data.to_csv(os.path.join(sub_path, self.port_name + '.csv'))

        # 写入每日权重
        file = os.path.join(self.data_weight_path, '%s.csv' % self.port_name)
        port_daily.to_csv(file)

if __name__ == '__main__':

    self = HoldingQuarter()

    # self.cal_all_wind_file()
    # self.backtest()
    self.cal_weight_data()

