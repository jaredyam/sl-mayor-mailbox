from pathlib import Path
import re

import requests
from bs4 import BeautifulSoup


LATEST_DATA = 'latest.csv'
LETTER_PATH = Path('category') / 'letters'
AGENCY_PATH = Path('category') / 'agencies'


def get_soup(url):
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        raise requests.exceptions.ConnectionError(
            'please check your network connection') from e

    return BeautifulSoup(response.text, 'html.parser')


def get_letter_id_from_url(url):
    return re.findall(r'leadermailid=(\d+)', url)[0]


def format_date(date):
    if date is None:
        return None

    return '-'.join(re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date)[0])


def markdown_link(text, link):
    return f'[{text}]({link})'


def html_link(text, link):
    return f'<a href=\"{link}\">{text}</a>'
