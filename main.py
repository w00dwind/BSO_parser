from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from tqdm.notebook import tqdm
import argparse

import re
from typing import List
from datetime import datetime
from pathlib import Path

import gspread

import conf
from helpers import *

CONFIG = conf.CONFIG

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--parsed-path', type=str, default=CONFIG['parsed_df'], help='path to parsed csv file')
    parser.add_argument('--mode', type=str, choices=['parse_to_df', 'parse_and_update'], default='parse_and_update',
                        help='parse concerts and update google sheet, or only parse to local csv file')
    parser.add_argument('--scan_range', type=int, nargs=2, default=None, help='left and right border of urls list')
    parser.add_argument('--timeout', type=float, default=0.5, help='timeout between requests')
    args = parser.parse_args()
    print(args)


def get_concert_dataframe(
        home_class=CONFIG['home_concert_class'],
        tour_class=CONFIG['tour_concert_class'],
        timeout=args.timeout,
        scan_range=args.scan_range,
        stop_sentences=CONFIG['stop_sentences'],
        verbose=False,
        save_df=True,
        # upload=True
) -> pd.DataFrame:
    mode = args.mode
    concerts_urls = get_concert_urls(CONFIG['base_url'])
    if mode == 'parse_and_update':
        sync_df = gs_sync()
        # Check is url already in database
        concert_urls = [u for u in concert_urls if u not in sync_df['url'].values]
        if len(concert_urls) == 0:
            return print('concerts sheet is up to date, nothing to add')
    if scan_range is not None:
        concert_urls = concert_urls[scan_range[0]:scan_range[1]]

    concerts_list = []

    chars_to_replace = {ord('\xa0'): None, ord('\n'): None, ord('\r'): None}

    for url in tqdm(concerts_urls, desc='parsing data', colour='green'):
        concert = {}
        concert_page = requests.get(url)
        concert_soup = BeautifulSoup(concert_page.text, 'html.parser')

        concert['title'] = concert_soup.title.text.translate(chars_to_replace)

        time_place = concert_soup.find(class_='place').text.translate(chars_to_replace)
        concert['place'] = re.sub(r'\|[^\|]*$', '', ' '.join(time_place.split()))
        # date parsing
        soup_dt = concert_soup.find(class_='active')
        # active year
        year = concert_soup.find('div', {'id': 'dates'}).find('span', class_='year').text
        # month
        month = concert_soup.find('a', class_='active').text.split()[1]
        # day
        day = concert_soup.find('a', class_='active').text.split()[0]
        # time
        hour = time_place.split()[-1]
        # fill dictionary
        concert['dt'] = str(convert_date([day, month, year, hour]))
        # Is on tour
        russia_tour, international_tour = False, False
        if 'tour' in url:
            if 'Россия' in concert['place'].split():
                russia_tour = True
            else:
                international_tour = True

        # Parse concert program
        class_mode = tour_class if (russia_tour or international_tour) else home_class
        program = [' '.join(txt.text.split()) for txt in concert_soup.find(class_=class_mode)]
        # Remove empty elements of list
        program = list(filter(None, program))
        # Remove useless sentences
        program = ' '.join([s for s in program if not s.lower() in stop_sentences])
        concert['program'] = program

        # Default employed values
        concert['n_rehearsals'] = 0
        concert['principal'] = False
        concert['co-principal'] = False
        concert['second'] = False
        concert['contra'] = False

        # Tour modes
        concert['russia_tour'] = russia_tour
        concert['international_tour'] = international_tour
        concert['url'] = url
        concerts_list.append(concert)

        if verbose:
            print(f"\n{concert['title']}\ndata parsed. timeout {timeout} sec.\n{'___' * 10}")
        time.sleep(timeout)
    print('Finished !')
    concerts_df = pd.DataFrame(concerts_list)
    # Save parsed data to file
    if save_df:
        concerts_df.to_csv(CONFIG['parsed_df'], index=False)
        print('local dataframe saved')
    if mode == 'parse_and_update':
        gs_sync(mode='upload', row_to_append=concerts_df.values.tolist())

    # return concerts_df


get_concert_dataframe()
