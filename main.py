import time
from tqdm.notebook import tqdm
import argparse
# from typing import List
import re

from helpers import *

CONFIG = conf.CONFIG


def get_concert_dataframe(
        base_url: str = CONFIG['base_url'],
        hdrs=CONFIG['headers'],
        home_class: str = CONFIG['home_concert_class'],
        tour_class: str = CONFIG['tour_concert_class'],
        timeout: float = 0.5,
        scan_range: list = None,
        stop_sentences: List[str] = CONFIG['stop_sentences'],
        verbose: bool = False,
        parsed_path: str = CONFIG['parsed_df'],
        mode: str = CONFIG['mode']
) -> object:
    modes = ['parse', 'parse_update']
    assert mode in modes, f'Wrong mode. Available modes is {modes}'
    concert_urls = get_concert_urls(base_url)
    if scan_range is not None:
        concert_urls = concert_urls[scan_range[0]:scan_range[1]]
    print(f">>> mode: {mode}")
    if mode == 'parse_update':
        sync_df = gs_sync()
        # Check is url already in database
        concert_urls = [u for u in concert_urls if u not in sync_df['url'].values]
        if len(concert_urls) == 0:
            return print('>>> concerts sheet is up to date, nothing to add')

    concerts_list = []

    chars_to_replace = {ord('\xa0'): None, ord('\n'): None, ord('\r'): None}

    for url in tqdm(concert_urls, desc='parsing data', colour='green'):
        concert = {}
        concert_page = requests.get(url, headers=hdrs)
        concert_soup = BeautifulSoup(concert_page.text, 'html.parser')

        concert['title'] = concert_soup.title.text.translate(chars_to_replace)

        time_place = concert_soup.find(class_='place').text.translate(chars_to_replace)
        concert['place'] = re.sub(r'\|[^\|]*$', '', ' '.join(time_place.split()))

        # active year
        year = concert_soup.find('div', {'id': 'dates'}).find('span', class_='year').text
        # month
        month = concert_soup.find('a', class_='active').text.split()[1]
        # day
        day = concert_soup.find('a', class_='active').text.split()[0]
        # time
        hour = time_place.split()[-1]

        # Is on tour
        russia_tour, international_tour = False, False
        if 'tour' in url:
            if 'Россия' in concert['place'].split():
                russia_tour = True
                year = int(year) + 1 # bugfix on the web page - years in russia tours always shows as less at one than it should be
                year = str(year) # cast to str, cause function "convert_date" accept list of strings.
                # print(year)
            else:
                international_tour = True
        # fill dictionary
        concert['dt'] = str(convert_date([day, month, year, hour]))

        # Parse concert program
        class_mode = tour_class if (russia_tour or international_tour) else home_class
        program = [' '.join(txt.text.split()) for txt in concert_soup.find(class_=class_mode)]
        # Remove empty elements of list
        program = list(filter(None, program))
        # Remove useless sentences
        program = '^^^'.join([s for s in program if not s.lower() in stop_sentences])
        concert['program'] = program
        # empty col for formatting inside google sheets
        concert['formatted_program'] = ' '
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
    if parsed_path is not None:
        concerts_df.to_csv(parsed_path, index=False)
        print('local dataframe saved')
    if mode == 'parse_update':
        gs_sync(mode='upload', row_to_append=concerts_df.values.tolist())

    return concerts_df



if __name__ == "__main__":
    CONFIG = conf.CONFIG
    parser = argparse.ArgumentParser()
    parser.add_argument('--parsed-path', type=str, default=CONFIG['parsed_df'], help='path to parsed csv file')
    parser.add_argument('--mode', type=str, choices=['parse', 'parse_update'], default=CONFIG['mode'],
                        help='parse concerts and update google sheet, or only parse to local csv file')
    parser.add_argument('--scan_range', type=int, nargs=2, default=None, help='left and right border of urls list')
    parser.add_argument('--timeout', type=float, default=0.5, help='timeout between requests')
    args = parser.parse_args()
    get_concert_dataframe(parsed_path=args.parsed_path,
                          mode=args.mode,
                          timeout=args.timeout,
                          scan_range=args.scan_range,
                          )
