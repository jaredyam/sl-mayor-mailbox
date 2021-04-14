import importlib
from pathlib import Path
import pandas as pd

from utils import (LATEST_DATA, LETTER_PATH, AGENCY_PATH,
                   get_letter_id_from_url, html_link)
csv2markdown = importlib.import_module(
    'csv-converter.csv_converter.csv2markdown')


def generate_mailid_mds():
    df = pd.read_csv(LATEST_DATA)

    df['reply_agency'] = df['reply_agency'].apply(
        _convert_reply_agency_to_html_link)

    LETTER_PATH.mkdir(parents=True, exist_ok=True)
    for i, row in df.iterrows():
        title = row['title']
        url = row['url']
        letter_id = get_letter_id_from_url(url)

        row = row[['query_date', 'query',
                   'reply_date',  'reply', 'reply_agency']]
        row = row.rename({'query_date': '来信时间',
                          'query': '来信内容',
                          'reply_date': '回复时间',
                          'reply': '回复内容',
                          'reply_agency': '回复机构'})

        csvfile = row.to_csv(header=['Content'], index_label='Title')
        table = csv2markdown(csvfile)

        with open(LETTER_PATH / f'{letter_id}.md', 'w') as md:
            md.write(f'# {html_link(title, url)}\n')
            md.write(table)


def _convert_reply_agency_to_html_link(agency):
    return r' '.join([html_link(a, f'{Path(f"../../{AGENCY_PATH}") / a}.md')
                      for a in agency.split()])


if __name__ == '__main__':
    generate_mailid_mds()
