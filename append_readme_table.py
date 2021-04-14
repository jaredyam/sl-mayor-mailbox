from datetime import datetime
import pandas as pd

from utils import (LATEST_DATA, LETTER_PATH, AGENCY_PATH,
                   get_letter_id_from_url, html_link)


def create_readme_table():
    df = pd.read_csv(LATEST_DATA)

    df['title'] = '<a href=\"' + str(LETTER_PATH) + '/' + \
        df['url'].apply(get_letter_id_from_url) + '.md' + \
        '\">' + df['title'] + '</a>'
    df['reply_agency'] = df['reply_agency'
                            ].apply(_convert_reply_agency_to_html_link)

    df = df[['query_date', 'reply_date',  'title', 'reply_agency']]

    with open('README.md', 'a') as md:
        md.write(f'<pre><b>LAST UPDATE : {datetime.today():%Y-%m-%d}</b><br/>'
                 f'<b>TOTAL MAILS : {len(df):>10}</b></pre>\n<pre>\n')
        for i, row in df.iterrows():
            md.write(f'- {row["title"]}<br/>')
            md.write(f'  Query Date : {"<b>"+str(row["query_date"])+"</b>":<17} - '
                     f'Reply Date : {"<b>"+str(row["reply_date"])+"</b>":<17} - '
                     f'Reply Agency : {row["reply_agency"]}\n')

        md.write('</pre>')


def _convert_reply_agency_to_html_link(agency):
    return r' '.join([html_link(a, f'{AGENCY_PATH / a}.md')
                      for a in agency.split()])


if __name__ == '__main__':
    create_readme_table()
