from datetime import datetime
import pandas as pd

from utils import (
    LATEST_DATA,
    MAIL_PATH,
    AGENCY_PATH,
    PROJECT_PATH,
    get_mail_id_from_url,
    html_link,
)


def create_readme_table():
    df = pd.read_csv(LATEST_DATA)
    df = df.fillna("-")

    df["title"] = (
        '<a href="'
        + str(MAIL_PATH.relative_to(PROJECT_PATH))
        + "/"
        + df["url"].apply(get_mail_id_from_url)
        + ".md"
        + '">'
        + df["title"]
        + "</a>"
    )
    df["reply_agency"] = df["reply_agency"].apply(_convert_reply_agency_to_links)

    df = df[["query_date", "reply_date", "title", "reply_agency"]]

    with open("README.md", "a") as md:
        md.write(
            f"<pre><b>LAST UPDATE : {datetime.today():%Y-%m-%d}</b><br/>"
            f"<b>TOTAL MAILS : {len(df):>10}</b></pre>\n<pre>\n"
        )
        for i, row in df.iterrows():
            md.write(f'- {row["title"]}<br/>')
            md.write(
                f'  Query Date : {"<b>"+str(row["query_date"])+"</b>":<17} - '
                f'Reply Date : {"<b>"+str(row["reply_date"])+"</b>":<17} - '
                f'Reply Agency : {row["reply_agency"]}\n'
            )

        md.write("</pre>\n")


def _convert_reply_agency_to_links(agencies):
    return r" ".join(
        [
            html_link(agency, f"{AGENCY_PATH.relative_to(PROJECT_PATH) / agency}.md")
            for agency in agencies.split()
        ]
    )


if __name__ == "__main__":
    create_readme_table()
