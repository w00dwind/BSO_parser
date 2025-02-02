
CONFIG = {
    'base_url': 'https://bso.ru',
    'headers': {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36'},
    'home_concert_class': 'abon-descr scroll-pane',
    'tour_concert_class': 'abon-descr scroll-pane gastrol-descr',
    # Select season
    'start_year': 2024,
    'end_year': 2025,
    # Paths to dataframes
    'sync_df': 'gs_df_sync.csv',
    'parsed_df': 'parsed_df.csv',
    'mode': 'parse_update',
    'stop_sentences': ['купить билет онлайн'],
    'columns': [
        'title',
        'place',
        'dt',
        'program',
        'formatted_program',
        'n_rehersals',
        'principal',
        'co-principal',
        'second',
        'related_instrument',
        'russia_tour',
        'international_tour',
        'url'
        ],

    # gs_sync config
    'secret_json': 'secrets/parser-369321-949b6976533c.json',
    'table_name': 'BSO_23_24',
    'sheet_name': 'concerts_sheet',
    'gs_df_file': 'sync.csv'

}
