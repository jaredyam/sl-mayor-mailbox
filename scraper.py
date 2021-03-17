from pathlib import Path
import re
import asyncio
import csv

import requests
from bs4 import BeautifulSoup
import aiohttp


class Scraper:

    BASE_URL = 'http://www.shangluo.gov.cn'
    DEFAULT_QUERY = '/zmhd/ldxxlb.jsp'
    SAVE_DIR = Path('./history')
    INIT_FILENAME = 'first_run.csv'
    LATEST_FILENAME = 'latest.csv'

    def run(self):
        self.first_run = not (self.SAVE_DIR / self.INIT_FILENAME).exists()
        if self.first_run:
            print('first run...')
            self.create()
        elif self.need_update():
            print('start to update...')
            self.update()
        else:
            print('it\'s the latest version')

    def create(self):
        letter_urls = asyncio.run(self.collect_letter_urls())
        records = asyncio.run(self.collect_letters_content(letter_urls))
        print(f'successfully saved total {len([r for r in records if r is not None])} letters')
        self.to_csv(records)

    def update(self):
        letter_urls = self.get_new_letter_urls()
        records = asyncio.run(self.collect_letters_content(letter_urls))
        print(f'successfully saved total {len([r for r in records if r is not None])} letters')
        self.to_csv(records)

    def need_update(self):
        with open(self.LATEST_FILENAME, 'r') as f:
            _ = f.readline()
            latest_record = f.readline()
            self.latest_letter_id_of_file = self._get_letter_id_from_url(
                latest_record.split(',')[-1])

        first_page_soup = self.get_soup(self.get_page(1))
        self.latest_letter_id_of_webpage = self._get_letter_id_from_url(
            first_page_soup.find('span',
                                 class_='titlestyle1333').parent.get('href'))

        return not self.latest_letter_id_of_file == self.latest_letter_id_of_webpage

    def to_csv(self, records):
        filename = (self.INIT_FILENAME if self.first_run else
                    (self.latest_letter_id_of_file + '-'
                     + self.latest_letter_id_of_webpage + '.csv'))
        self.SAVE_DIR.mkdir(exist_ok=True)
        filepath = self.SAVE_DIR / filename
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=records[0].keys())
            writer.writeheader()
            for row in records:
                if isinstance(row, dict):
                    writer.writerow(row)

    def get_page(self,  num):
        return (self.BASE_URL + self.DEFAULT_QUERY + '?'
                + f'formname1333at=54&formname1333ap={num}&formname1333ac=15&'
                + 'urltype=tree.TreeTempUrl&wbtreeid=1112')

    @staticmethod
    def get_soup(url):
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(
                'please check your network connection')

        return BeautifulSoup(response.text, 'html.parser')

    def collect_page_urls(self):
        soup = self.get_soup(self.get_page(1))
        total_pages = soup.find(
            'a', class_='Next').parent.find_all('a')[-2].text
        return [self.get_page(i + 1) for i in range(int(total_pages))]

    def get_new_letter_urls(self):
        new_letter_urls = []
        current_page_soup = self.get_soup(self.get_page(1))

        find_latest_item_of_file = False
        while not find_latest_item_of_file:
            items = current_page_soup.find('table',
                                           class_='winstyle1333').find_all('tr')[1:]
            for item in items:
                latest_letter_href = item.find_all('td')[1].a.get('href')
                letter_id = self._get_letter_id_from_url(latest_letter_href)
                if letter_id == self.latest_letter_id_of_file:
                    find_latest_item_of_file = True
                    break
                else:
                    new_letter_urls.append(self.BASE_URL + latest_letter_href)
            else:
                next_page_href = self.first_page_soup.find(
                    'a', class_='Next').get('href')
                next_page_url = (self.BASE_URL
                                 + self.DEFAULT_QUERY + '?'
                                 + next_page_href)
                current_page_soup = self.get_soup(next_page_url)

        return new_letter_urls

    async def get_html_text(self, url, session):
        async with session.get(url) as response:
            return await response.text()

    async def get_letter_urls(self, page_url, session):
        text = await self.get_html_text(page_url, session)
        soup = BeautifulSoup(text, 'html.parser')
        main_table = soup.find('table', class_='winstyle1333')

        print(f'collecting letter urls from web page: {page_url}...')
        return [self.BASE_URL + item.a.get('href') for item in
                main_table.find_all('tr')[1:]]

    async def get_letter_content(self, letter_url, session):
        text = await self.get_html_text(letter_url, session)
        soup = BeautifulSoup(text, 'html.parser')
        avaliable_titles = soup.find_all('td', class_='titlestyle1335')
        interest_titles = ['信件编号', '来信主题', '信件内容', '来信时间',
                           '回复内容', '回复时间', '回复人']

        record_headers = ['letter_id', 'title', 'query', 'query_date',
                          'reply', 'reply_date', 'reply_agency']
        record = dict(zip(record_headers,
                          [None for _ in range(len(record_headers))]))

        for i, it in enumerate(interest_titles):
            for at in avaliable_titles:
                if at.text == it:
                    record[record_headers[i]] = at.parent.find(
                        'td', 'contentstyle1335').text
                    break

        record['url'] = letter_url
        for date in ['query_date', 'reply_date']:
            record[date] = self._format_date(record[date])

        print(f'saved letter - query date : {record["query_date"]} - '
              f'reply date : {record["reply_date"]}'
              f'\ntitle : {record["title"]}\n'
              f'url - {record["url"]}')

        return record

    async def collect_letter_urls(self):
        async with aiohttp.ClientSession() as session:
            urls_each_page = await asyncio.gather(*[self.get_letter_urls(page_url, session)
                                                    for page_url
                                                    in self.collect_page_urls()])

        return [url for letter_urls in urls_each_page for url in letter_urls]

    async def collect_letters_content(self, letter_urls):
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*[self.get_letter_content(url, session)
                                          for url in letter_urls])

    @staticmethod
    def _get_letter_id_from_url(url):
        return re.findall(r'leadermailid=(\d+)', url)[0]

    @staticmethod
    def _format_date(date):
        if date is None:
            return None

        return '-'.join(re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date)[0])


if __name__ == '__main__':
    scraper = Scraper()
    scraper.run()
