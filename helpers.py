import conf
from typing import List
from pymystem3 import Mystem
import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import gspread
from datetime import datetime


CONFIG = conf.CONFIG


def gs_sync(secret_json=CONFIG['secret_json'],
            table_name=CONFIG['table_name'],
            sheet_name=CONFIG['sheet_name'],
            save_path=CONFIG['gs_df_file'],
            mode='get',
            row_to_append=None
            ):
    """
    sync data with Google Sheets.
    Available modes - 'get' or 'upload'.
    """
    assert mode in ['get', 'upload'], "Wrong mode! Available modes: 'get' or 'upload'"
    gc = gspread.service_account(filename=secret_json)
    table = gc.open(table_name)
    worksheet = table.worksheet(sheet_name)
    # Check matching columns in config and google sheet
    if worksheet.row_values(1) != CONFIG['columns']:
        worksheet.update([CONFIG['columns']])
        print('>>> gs columns updated from config!')

    if mode == 'get':
        sheet_values = worksheet.get_all_values()
        sync_df = pd.DataFrame(sheet_values[1:], columns=sheet_values[0])
        if save_path is not None:
            sync_df.to_csv(save_path)
        return sync_df
    else:
        worksheet.append_rows(row_to_append)
        print(f'{len(row_to_append)} rows appended !')


def get_concert_urls(homepage: str, start_year=CONFIG['start_year'], end_year=CONFIG['end_year']):
    """
    homepage: homepage url in format https://site.com
    start_year: year of start season
    end_year: year of end season
    """
    page = requests.get(homepage)
    soup = BeautifulSoup(page.text, 'html.parser')

    raw_parsed_urls = []
    for e in soup.find_all('a'):
        raw_parsed_urls.append(str(e.get('href')))

    idx = []
    for u in raw_parsed_urls:
        try:
            year, month = int(u.split('/')[-4]), int(u.split('/')[-3])
        except:
            year, month = 0, 0
        if (year == start_year and month > 7) or (year == end_year and month < 7):
            idx.append(raw_parsed_urls.index(u))

    first_idx, last_idx = idx[0], idx[-1]
    concert_urls = [homepage + c for c in
                    tqdm(raw_parsed_urls[first_idx:last_idx], desc='making concert urls list', colour='green')]

    return concert_urls


def convert_date(date: List[str], ):
    """
    !! Important !!

    order of datetime:
    [day, month, year, hour]
    """
    # Month
    month_list = ['январь',
                  'февраль',
                  'март',
                  'апрель',
                  'май',
                  'июнь',
                  'июль',
                  'август',
                  'сентябрь',
                  'октябрь',
                  'ноябрь',
                  'декабрь',
                  ]
    numered_month: dict = {m: n for n, m in enumerate(month_list, start=1)}
    lem = Mystem()
    lemmatized_month = lem.lemmatize(date[1])[0]

    date[1] = str(numered_month[lemmatized_month])

    return datetime.strptime(' '.join(date), '%d %m %Y %H.%M')
