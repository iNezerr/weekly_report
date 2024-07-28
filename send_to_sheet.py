import gspread
import pandas as pd
from bd2 import main

file_path = 'raw/sheet1.xlsx'
arrival_date = "2024-07-27"

sa = gspread.service_account(filename="keys/service_json1.json")
sh = sa.open("GES_Weekly_Reports")
sheet = sh.worksheet("Sheet1")
cell_range = 'B2:J7'
df = main(file_path, arrival_date)

data = df.values.tolist()
data.insert(0, df.columns.tolist())

sheet.update(cell_range, data)
