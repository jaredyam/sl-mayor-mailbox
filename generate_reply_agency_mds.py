from pathlib import Path

import numpy as np
import pandas as pd

from utils import (LATEST_DATA, AGENCY_PATH, LETTER_PATH,
                   get_letter_id_from_url, markdown_link)


def generate_reply_agency_mds():
    df = pd.read_csv(LATEST_DATA)
    df = df_expand_list_to_rows(
        df.assign(**{'reply_agency': df['reply_agency'].str.split()}),
        'reply_agency')
    agencies = list(dict.fromkeys(df['reply_agency']))

    AGENCY_PATH.mkdir(parents=True, exist_ok=True)
    with open(AGENCY_PATH / 'README.md', 'w') as md:
        md.write(f'# 👮‍♀️ Agencies\n')
        md.write(f'__TOTAL AGENCIES : {len(agencies)}__\n')
        for a in agencies:
            md.write(f'- {markdown_link(a, f"{a}.md")}\n')

    for agency in agencies:
        group_rows = df.loc[df.reply_agency == agency][['title', 'url']]
        with open(AGENCY_PATH / f'{agency}.md', 'w') as md:
            md.write(f'# {agency}\n')

            items = []
            for i, row in group_rows.iterrows():
                items.append(f'- [{row["title"]}]({Path(f"../../{LETTER_PATH}")}/'
                             f'{get_letter_id_from_url(row["url"])}.md)')

            md.write(f'__TOTAL MAILS : {len(items)}__\n')
            md.write('\n'.join(items))


def df_expand_list_to_rows(df, column):
    return pd.DataFrame({c: np.repeat(df[c].values,
                                      df[column].str.len())
                         for c in df.columns.difference([column])}
                        ).assign(**{column: np.concatenate(
                            df[column].values)})[df.columns.tolist()]


if __name__ == '__main__':
    generate_reply_agency_mds()
