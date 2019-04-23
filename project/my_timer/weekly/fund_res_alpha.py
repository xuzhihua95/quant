import os
import numpy as np
import pandas as pd
from datetime import datetime

from quant.data.data import Data
from quant.fund.fund import Fund
from quant.stock.date import Date
from quant.stock.index import Index
from quant.stock.barra import Barra
from quant.stock.stock import Stock
from quant.mfc.mfc_data import MfcData
from quant.utility.write_excel import WriteExcel
from quant.utility.code_format import CodeFormat
from quant.project.multi_factor.alpha_model.sample.alpha_split import AlphaSplit
from quant.project.multi_factor.alpha_model.exposure.alpha_factor_update import AlphaFactorUpdate


class ResAlphaExposure(Data):

    """ 计算泰达基金在Barra风格和行业，已经在Alpha残差因子上的暴露 """

    def __init__(self):

        Data.__init__(self)
        self.sub_data_path = r'mfcteda_data\alpha_expsore'
        self.data_path = os.path.join(self.primary_data_path, self.sub_data_path)

    def update_data(self, beg_date, end_date):

        """ 更新数据 """

        print(beg_date, end_date)
        AlphaFactorUpdate().update_alpha_factor(beg_date, end_date)

    def get_fund_file(self, fund_pool):

        """ 得到基金列表 """

        file = os.path.join(self.data_path, "fund.xlsx")
        data = pd.read_excel(file, index_col=[0], sheetname=fund_pool)
        return data

    def get_alpha_file(self):

        """ Alpha 参数表 """

        file = os.path.join(self.data_path, "res_alpha.xlsx")
        data = pd.read_excel(file)
        data = data.dropna(subset=['mFactorName'])
        data.index = data['mFactorName'].map(lambda x: str(x) + '_res')
        return data

    def res_alpha_exposure(self, fund_pool, report_date, index_code, type="halfyear"):

        """ 生成基金持仓及指数 在残差Alpha上的暴露 """

        fund_info = self.get_fund_file(fund_pool)
        fund_holder = Fund().get_fund_holding_stock_all()
        fund_holder = fund_holder[fund_holder.ReportDate == report_date]
        fund_holder = fund_holder.reset_index(drop=True)
        alpha_list = self.get_alpha_file()
        trade_date = Date().get_trade_date_offset(report_date, 0)

        result = pd.DataFrame([], index=fund_info.index)

        # alpha 暴露
        for i_alpha in range(0, len(alpha_list)):

            alpha_name_en = alpha_list.index[i_alpha]
            alpha_name_ch = alpha_list.loc[alpha_name_en, "名称"]
            alpha_data = Stock().read_factor_h5(alpha_name_en, path=os.path.join(self.data_path, "MatlabAlphaRes"))
            try:
                trade_date = alpha_data.columns[alpha_data.columns <= trade_date][-1]
            except Exception as e:
                print(e)
                trade_date = alpha_data.columns[0]

            for i_fund in range(0, len(fund_info)):

                fund_code = fund_info.index[i_fund]
                fund_name = fund_info.loc[fund_code, "基金名称"]

                if type == "halfyear":
                    holder = fund_holder[fund_holder.FundCode == fund_code]
                    holder = holder.reset_index(drop=True)
                    holder.index = holder.StockCode
                    weight = pd.DataFrame(holder.Weight)
                else:
                    weight = MfcData().get_fund_security(report_date)
                    weight = weight[weight['基金名称'] == fund_name]
                    weight.index = weight['证券代码']
                    weight = pd.DataFrame(weight['市值比净值(%)'])
                    weight.index = weight.index.map(CodeFormat().stock_code_add_postfix)
                    weight.columns = ['Weight']
                    weight['Weight'] /= weight['Weight'].sum()

                if (len(weight) > 0) and (trade_date in alpha_data.columns):
                    weight = weight.sort_values(by=['Weight'], ascending=False)
                    alpha = pd.DataFrame(alpha_data[trade_date])
                    alpha.columns = [alpha_name_ch]
                    concat_data = pd.concat([weight, alpha], axis=1)
                    concat_data = concat_data.dropna()
                    concat_data['WeightAlpha'] = concat_data['Weight'] * concat_data[alpha_name_ch]
                    if len(concat_data) > 0:
                        weight_alpha = concat_data['WeightAlpha'].sum() / concat_data['Weight'].sum()
                        result.loc[fund_code, alpha_name_ch] = weight_alpha

                    print(fund_name, fund_code, alpha_name_ch, alpha_name_en)
                else:
                    print(fund_name, fund_code, alpha_name_ch, alpha_name_en, "is Null")

            result.loc["基金平均", alpha_name_ch] = result[alpha_name_ch].median()

            # 指数暴露
            weight = Index().get_weight_date(index_code, trade_date)
            weight.columns = ['Weight']
            if (len(weight) > 0) and (trade_date in alpha_data.columns):
                weight = weight.sort_values(by=['Weight'], ascending=False)
                alpha = pd.DataFrame(alpha_data[trade_date])
                alpha.columns = [alpha_name_ch]
                concat_data = pd.concat([weight, alpha], axis=1)
                concat_data = concat_data.dropna()
                concat_data['WeightAlpha'] = concat_data['Weight'] * concat_data[alpha_name_ch]
                if len(concat_data) > 0:
                    weight_alpha = concat_data['WeightAlpha'].sum() / concat_data['Weight'].sum()
                    result.loc[index_code, alpha_name_ch] = weight_alpha

        result = result.dropna(how="all")
        result_abs = result
        result = result.sub(result.loc[index_code, :])
        return result, result_abs

    def barra_exposure(self, fund_pool, report_date, index_code, type="halfyear"):

        """ 生成基金持仓及指数 在Barra上的暴露 """

        fund_info = self.get_fund_file(fund_pool)
        fund_holder = Fund().get_fund_holding_stock_all()
        fund_holder = fund_holder[fund_holder.ReportDate == report_date]
        fund_holder = fund_holder.reset_index(drop=True)
        trade_date = Date().get_trade_date_offset(report_date, 0)
        barra_data = Barra().get_factor_exposure_date(trade_date, type_list=["STYLE", "INDUSTRY"])
        result = pd.DataFrame([], index=fund_info.index)

        # 风格行业因子暴露
        for i_alpha in range(0, len(barra_data.columns)):

            barra_name = barra_data.columns[i_alpha]

            for i_fund in range(0, len(fund_info)):

                fund_code = fund_info.index[i_fund]
                fund_name = fund_info.loc[fund_code, "基金名称"]
                if type == "halfyear":
                    holder = fund_holder[fund_holder.FundCode == fund_code]
                    holder = holder.reset_index(drop=True)
                    holder.index = holder.StockCode
                    weight = pd.DataFrame(holder.Weight)
                else:
                    weight = MfcData().get_fund_security(report_date)
                    weight = weight[weight['基金名称'] == fund_name]
                    weight.index = weight['证券代码']
                    weight = pd.DataFrame(weight['市值比净值(%)'])
                    weight.index = weight.index.map(CodeFormat().stock_code_add_postfix)
                    weight.columns = ['Weight']
                    weight['Weight'] /= weight['Weight'].sum()

                if (len(weight) > 0) and (barra_name in barra_data.columns):
                    weight = weight.sort_values(by=['Weight'], ascending=False)
                    barra = pd.DataFrame(barra_data[barra_name])
                    barra.columns = [barra_name]
                    concat_data = pd.concat([weight, barra], axis=1)
                    concat_data = concat_data.dropna()
                    concat_data['WeightAlpha'] = concat_data['Weight'] * concat_data[barra_name]
                    if len(concat_data) > 0:
                        weight_alpha = concat_data['WeightAlpha'].sum() / concat_data['Weight'].sum()
                        result.loc[fund_code, barra_name] = weight_alpha
                    print(fund_name, fund_code, barra_name)
                else:
                    print(fund_name, fund_code, barra_name, "is Null")

            result.loc["基金平均", barra_name] = result[barra_name].median()

            # 指数暴露
            weight = Index().get_weight_date(index_code, trade_date)
            weight.columns = ['Weight']
            if (len(weight) > 0) and (barra_name in barra_data.columns):
                weight = weight.sort_values(by=['Weight'], ascending=False)
                barra = pd.DataFrame(barra_data[barra_name])
                barra.columns = [barra_name]
                concat_data = pd.concat([weight, barra], axis=1)
                concat_data = concat_data.dropna()
                concat_data['WeightAlpha'] = concat_data['Weight'] * concat_data[barra_name]
                if len(concat_data) > 0:
                    weight_alpha = concat_data['WeightAlpha'].sum() / concat_data['Weight'].sum()
                    result.loc[index_code, barra_name] = weight_alpha

        result = result.dropna(how="all")
        result_abs = result
        result = result.sub(result.loc[index_code, :])
        return result, result_abs

    def generate_file(self, fund_pool, report_date, index_code, type="halfyear"):

        """ 生成暴露的文件 """

        fund_info = self.get_fund_file(fund_pool)
        result, result_abs = self.res_alpha_exposure(fund_pool, report_date, index_code, type)
        result = result.drop(index_code)
        barra, barra_abs = self.barra_exposure(fund_pool, report_date, index_code, type)

        industry_abs = barra_abs.loc[:, list(Barra().get_factor_name(type_list=['INDUSTRY']).NAME_EN)]
        industry_abs['IndustryBias'] = industry_abs.abs().sum(axis=1)
        style_abs = barra_abs.loc[:, list(Barra().get_factor_name(type_list=['STYLE']).NAME_EN)]

        industry = barra.loc[:, list(Barra().get_factor_name(type_list=['INDUSTRY']).NAME_EN)]
        industry['IndustryBias'] = industry.abs().sum(axis=1)
        style = barra.loc[:, list(Barra().get_factor_name(type_list=['STYLE']).NAME_EN)]

        res = pd.concat([fund_info[['基金名称', '类型', '成立日期']],
                         style, industry['IndustryBias'], result, industry], axis=1)
        res = res.loc[result.index, :]

        res_abs = pd.concat([fund_info[['基金名称', '类型', '成立日期']],
                             style_abs, industry_abs['IndustryBias'], result_abs, industry_abs], axis=1)
        res_abs = res_abs.loc[result_abs.index, :]

        num_format_pd = pd.DataFrame([], columns=res.columns, index=['format'])
        num_format_pd.ix['format', :] = '0.00'

        sheet_name = fund_pool
        file = os.path.join(self.data_path, "风险及残差Alpha暴露_%s_%s.xlsx" % (fund_pool, report_date))
        excel = WriteExcel(file)
        worksheet = excel.add_worksheet(sheet_name)
        excel.write_pandas(res, worksheet, begin_row_number=0, begin_col_number=1,
                           num_format_pd=num_format_pd, color="orange", fillna=True)
        excel.conditional_format(worksheet, 1, 0 + 5, 1 + len(res), len(res.columns) + 5, None)

        excel.close()

        num_format_pd = pd.DataFrame([], columns=res_abs.columns, index=['format'])
        num_format_pd.ix['format', :] = '0.00'

        sheet_name = fund_pool
        file = os.path.join(self.data_path, "风险及残差Alpha绝对暴露_%s_%s.xlsx" % (fund_pool, report_date))
        excel = WriteExcel(file)
        worksheet = excel.add_worksheet(sheet_name)
        excel.write_pandas(res_abs, worksheet, begin_row_number=0, begin_col_number=1,
                           num_format_pd=num_format_pd, color="orange", fillna=True)
        excel.conditional_format(worksheet, 1, 0 + 5, 1 + len(res), len(res.columns) + 5, None)

        excel.close()

    def fund_alpha_exposure_all(self, beg_date, end_date, fund_pool, index_code, period="S", type="halfyear"):

        """ 所有时期 """

        date_series = Date().get_normal_date_series(beg_date, end_date, period)
        print(date_series)

        for report_date in date_series:
            self.generate_file(fund_pool, report_date, index_code, type)


if __name__ == '__main__':

    """ 参数 """

    today = datetime.today().strftime("%Y%m%d")
    end_date = Date().get_trade_date_offset(today, -1)
    beg_date = Date().get_trade_date_offset(today, -220)
    report_date = "20181231"
    index_code = "000300.SH"
    fund_pool = "部门沪深300"
    report_date = "20190417"

    self = ResAlphaExposure()
    # self.update_data(beg_date, end_date)
    # self.fund_alpha_exposure_all("20170701", "20190401", "中证500", "000905.SH")
    # self.fund_alpha_exposure_all("20170701", "20190401", "沪深300", "000300.SH")
    # self.fund_alpha_exposure_all("20170701", "20190401", "主动股票基金", "基金持仓基准基金池_等权季报满仓_季报日")
    self.generate_file(fund_pool="部门中证500", report_date="20190418", index_code="000905.SH", type="mfcteda")
    self.generate_file(fund_pool="部门沪深300", report_date="20190418", index_code="000300.SH", type="mfcteda")