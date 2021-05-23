import importlib
from pathlib import Path

import numpy as np
import pandas as pd

from utils import (
    LATEST_DATA,
    AGENCY_PATH,
    MAIL_PATH,
    PROJECT_PATH,
    get_mail_id_from_url,
    markdown_link,
    html_link,
)

csv_converter = importlib.import_module("csv-converter.csv_converter")


def generate_reply_agency_mds():
    df = pd.read_csv(LATEST_DATA)
    df = df_expand_list_to_rows(
        df.assign(**{"reply_agency": df["reply_agency"].str.split()}), "reply_agency"
    )
    count_agency_mails = dict.fromkeys(df["reply_agency"])

    AGENCY_PATH.mkdir(parents=True, exist_ok=True)
    for agency in count_agency_mails.keys():
        agency_df = df.loc[df["reply_agency"] == agency]
        agency_df = agency_df[["query_date", "reply_date", "title", "url"]]
        with open(AGENCY_PATH / f"{agency}.md", "w") as md:
            md.write(f"# {agency}\n")

            mails = []
            for i, row in agency_df.iterrows():
                filepath = Path(
                    "{path}/{file}".format(
                        path=f"../../{MAIL_PATH.relative_to(PROJECT_PATH)}",
                        file=f'{get_mail_id_from_url(row["url"])}.md',
                    )
                )
                mails.append(
                    f'- {html_link(row["title"], filepath)}<br/>'
                    f'  Query Date : {"<b>"+str(row["query_date"])+"</b>":<17} - '
                    f'Reply Date : {"<b>"+str(row["reply_date"])+"</b>"}'
                )

            count_agency_mails[agency] = len(mails)
            md.write(f"<pre><b>TOTAL MAILS : {len(mails)}</b></pre>\n<pre>\n")
            md.write("\n".join(mails))
            md.write("\n</pre>\n")

    with open(AGENCY_PATH / "README.md", "w") as md:
        md.write("# 👮‍♀️ Agencies\n")
        md.write(f"__TOTAL AGENCIES : {len(count_agency_mails.keys())}__\n")
        count_agency_mails = {
            markdown_link(k, f"{k}.md"): v for k, v in count_agency_mails.items()
        }
        agencies_df = pd.DataFrame.from_dict(
            count_agency_mails, orient="index", columns=["Number of Replied Mails"]
        ).sort_values(by="Number of Replied Mails", ascending=False)
        csv_string = agencies_df.to_csv(
            header=["Number of Replied Mails"], index_label="Agency"
        )
        table = csv_converter.csv2markdown(
            csv_string, raw_string=True, pretty=False, alignment="cr"
        )
        md.write(table + "\n")


def df_expand_list_to_rows(df, column):
    """Expand dataframe cells of list type to multiple rows."""
    return pd.DataFrame(
        {
            c: np.repeat(df[c].values, df[column].str.len())
            for c in df.columns.difference([column])
        }
    ).assign(**{column: np.concatenate(df[column].values)})[df.columns.tolist()]


if __name__ == "__main__":
    generate_reply_agency_mds()
