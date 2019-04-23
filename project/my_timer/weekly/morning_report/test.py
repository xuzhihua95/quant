import os
import pandas as pd

from quant.fund.fund import Fund
from quant.mfc.mfc_data import MfcData


path = r"C:\Users\doufucheng\OneDrive\Desktop\波动率"
file = "残差波动率.xlsx"
filename = os.path.join(path, file)
data = pd.read_excel(filename, index_col=[0])

gb = data.groupby(by=['行业']).median()
gb = gb.sort_values(by=['波动率'])

file = "行业残差波动率.csv"
filename = os.path.join(path, file)
gb.to_csv(filename)

fund_list = MfcData().get_mfc_fund_info()
fund_list = fund_list[fund_list['Type'] == '公募']
fund_list = list(fund_list.Code)

report_date = "20181231"

result = pd.DataFrame([], index=fund_list, columns=['波动率'])
adata = pd.DataFrame()

for i_fund in range(len(fund_list)):

    fund = fund_list[i_fund]
    weight = Fund().get_fund_stock_weight_halfyear(fund)
    try:
        weight = pd.DataFrame(weight[report_date])
        weight.columns = ['weight']
        weight = weight.dropna()
        weight = weight.sort_values(by=['weight'])

        cdata = pd.concat([weight, data], axis=1)
        cdata = cdata.dropna()
        adata = pd.concat([adata, cdata], axis=0)

        file = "%s_残差波动率.csv" % fund
        filename = os.path.join(path, file)
        cdata.to_csv(filename)

        vol = (cdata['weight'] * cdata['波动率']).sum() / cdata['weight'].sum()
        result.loc[fund, "波动率"] = vol
    except Exception as e:
        print(e, fund)


file = "基金_残差波动率.csv"
filename = os.path.join(path, file)
result.to_csv(filename)

adata['code'] = adata.index
adata_gb = adata.groupby(by=['code'])['weight'].sum()
adata_gb = pd.concat([adata_gb, data], axis=1)
adata_gb = adata_gb.dropna()

file = "股票_残差波动率.csv"
filename = os.path.join(path, file)
adata_gb.to_csv(filename)