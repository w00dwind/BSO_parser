from pathlib import Path

CONFIG = {
    'base_url': 'https://bso.ru',
    'home_concert_class': 'abon-descr scroll-pane',
    'tour_concert_class': 'abon-descr scroll-pane gastrol-descr',
    # Select season
    'start_year': 2022,
    'end_year': 2023,
    # Paths to dataframes
    'sync_df': 'gs_df_sync.csv',
    'parsed_df': 'parsed_df.csv',

    'stop_sentences': ['купить билет онлайн'],

    # 'df_columns': [
    #     'title',
    #     'place',
    #     'dt',
    #     'program',
    #     'n_rehersals',
    #     'principal',
    #     'co-principal',
    #     'second',
    #     'contra',
    #     'russia_tour',
    #     'international_tour'
    #               ]

    # gs_sync config
    'secret_json': 'secrets/parser-369321-949b6976533c.json',
    'table_name': 'parser_experiment',
    'sheet_name': 'upload',
    'gs_df_file': 'sync.csv'

}
