import gspread
import conf

CONFIG = conf.CONFIG
gc = gspread.service_account(filename=CONFIG['secret_json'])
table = gc.open(CONFIG['table_name'])
worksheet = table.worksheet(CONFIG['sheet_name'])

print(worksheet.row_values(1) == CONFIG['columns'])

