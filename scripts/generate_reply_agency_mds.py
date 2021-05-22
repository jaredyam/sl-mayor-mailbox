import importlib
from pathlib import Path

import numpy as np
import pandas as pd

from utils import (LATEST_DATA, AGENCY_PATH, MAIL_PATH, PROJECT_PATH,
                   get_mail_id_from_url, markdown_link)
csv_converter = importlib.import_module('csv-converter.csv_converter')


def generate_reply_agency_mds():
    df = pd.read_csv(LATEST_DATA)
    df = df_expand_list_to_rows(
        df.assign(**{'reply_agency': df['reply_agency'].str.split()}),
        'reply_agency')
    count_agency_mails = dict.fromkeys(df['reply_agency'])

    AGENCY_PATH.mkdir(parents=True, exist_ok=True)
    for agency in count_agency_mails.keys():
        group_rows = df.loc[df.reply_agency == agency][['title', 'url']]
        with open(AGENCY_PATH / f'{agency}.md', 'w') as md:
            md.write(f'# {agency}\n')

            mails = []
            for i, row in group_rows.iterrows():
                filepath = Path('{path}/{file}'.format(
                    path=f'../../{MAIL_PATH.relative_to(PROJECT_PATH)}',
                    file=f'{get_mail_id_from_url(row["url"])}.md'))
                mails.append(f'- {markdown_link(row["title"], filepath)}')

            count_agency_mails[agency] = len(mails)
            md.write(f'__TOTAL MAILS : {len(mails)}__\n')
            md.write('\n'.join(mails))

    with open(AGENCY_PATH / 'README.md', 'w') as md:
        md.write(f'# 👮‍♀️ Agencies\n')
        md.write(f'__TOTAL AGENCIES : {len(count_agency_mails.keys())}__\n')
        count_agency_mails = {markdown_link(k, f'{k}.md'): v
                              for k, v in count_agency_mails.items()}
        agencies_df = pd.DataFrame.from_dict(
            count_agency_mails,
            orient='index',
            columns=['Number of Replied Mails']).sort_values(
            by='Number of Replied Mails',
            ascending=False)
        csv_string = agencies_df.to_csv(header=['Number of Replied Mails'],
                                        index_label='Agency')
        table = csv_converter.csv2markdown(csv_string,
                                           raw_string=True,
                                           pretty=False,
                                           alignment='cr')
        md.write(table)


def df_expand_list_to_rows(df, column):
    """Expand dataframe cells of list type to multiple rows."""
    return pd.DataFrame({c: np.repeat(df[c].values,
                                      df[column].str.len())
                         for c in df.columns.difference([column])}
                        ).assign(**{column: np.concatenate(
                            df[column].values)})[df.columns.tolist()]


if __name__ == '__main__':
    generate_reply_agency_mds()
