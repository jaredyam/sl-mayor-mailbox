import importlib
from pathlib import Path
import pandas as pd

from utils import (LATEST_DATA, MAIL_PATH, AGENCY_PATH, PROJECT_PATH,
                   get_mail_id_from_url, html_link)
csv_converter = importlib.import_module('csv-converter.csv_converter')


def generate_mailid_mds():
    df = pd.read_csv(LATEST_DATA)

    df['reply_agency'] = df['reply_agency'].apply(
        _convert_reply_agency_to_links)

    MAIL_PATH.mkdir(parents=True, exist_ok=True)
    for i, row in df.iterrows():
        title = row['title']
        url = row['url']
        mail_id = get_mail_id_from_url(url)

        row = row[['query_date', 'query',
                   'reply_date',  'reply', 'reply_agency']]
        row = row.rename({'query_date': '来信时间',
                          'query': '来信内容',
                          'reply_date': '回复时间',
                          'reply': '回复内容',
                          'reply_agency': '回复机构'})

        csv_string = row.to_csv(header=['Content'], index_label='Title')
        table = csv_converter.csv2markdown(csv_string,
                                           raw_string=True,
                                           pretty=False)

        with open(MAIL_PATH / f'{mail_id}.md', 'w') as md:
            md.write(f'# {html_link(title, url)}\n')
            md.write(table)


def _convert_reply_agency_to_links(agencies):
    return r' '.join([html_link(
        agency,
        f'{Path(f"../../{AGENCY_PATH.relative_to(PROJECT_PATH)}") / agency}.md')
        for agency in agencies.split()])


if __name__ == '__main__':
    generate_mailid_mds()
