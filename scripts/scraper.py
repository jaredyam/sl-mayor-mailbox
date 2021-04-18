from pathlib import Path
import csv
import asyncio

from bs4 import BeautifulSoup
import aiohttp

from utils import LATEST_DATA, get_soup, format_date, get_letter_id_from_url


class Scraper:

    BASE_URL = 'http://www.shangluo.gov.cn'
    DEFAULT_QUERY = '/zmhd/ldxxlb.jsp'

    def run(self):
        if not Path(LATEST_DATA).exists():
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

        print(f'successfully saved total {len(records)} letters')
        self.to_csv(records)

    def update(self):
        letter_urls = self.get_new_letter_urls()
        records = asyncio.run(self.collect_letters_content(letter_urls))

        csvfile = open(LATEST_DATA, newline='')
        history_records = [r for r in csv.DictReader(csvfile)]

        print(f'successfully added total {len(records)} letters')
        self.to_csv(records + history_records)

    def need_update(self):
        with open(LATEST_DATA, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    latest_record = row
                    break
        self.latest_id_from_file = get_letter_id_from_url(latest_record['url'])

        first_page_soup = get_soup(self.get_page(1))
        self.latest_id_from_site = get_letter_id_from_url(
            first_page_soup.find('span', class_='titlestyle1333'
                                 ).parent.get('href'))

        return not self.latest_id_from_file == self.latest_id_from_site

    def to_csv(self, records):
        with open(LATEST_DATA, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=records[0].keys())
            writer.writeheader()
            for row in records:
                writer.writerow(row)

    def get_page(self,  num):
        return (self.BASE_URL + self.DEFAULT_QUERY + '?'
                + f'formname1333at=54&formname1333ap={num}&formname1333ac=15&'
                + 'urltype=tree.TreeTempUrl&wbtreeid=1112')

    def collect_page_urls(self):
        soup = get_soup(self.get_page(1))
        total_pages = soup.find(
            'a', class_='Next').parent.find_all('a')[-2].text

        return [self.get_page(i + 1) for i in range(int(total_pages))]

    def get_new_letter_urls(self):
        new_letter_urls = []
        current_page_soup = get_soup(self.get_page(1))

        find_latest_item_of_file = False
        while not find_latest_item_of_file:
            urls = self.get_letter_urls_from_page_soup(current_page_soup)
            for url in urls:
                letter_id = get_letter_id_from_url(url)
                if letter_id == self.latest_id_from_file:
                    find_latest_item_of_file = True
                    break
                else:
                    new_letter_urls.append(url)
            else:
                next_page_href = self.current_page_soup.find(
                    'a', class_='Next').get('href')
                current_page_soup = get_soup(self.BASE_URL
                                             + self.DEFAULT_QUERY + '?'
                                             + next_page_href)

        return new_letter_urls

    def get_letter_urls_from_page_soup(self, page_soup):
        main_table = page_soup.find('table', class_='winstyle1333')
        return [self.BASE_URL + item.a.get('href')
                for item in main_table.find_all('tr')[1:]]

    async def get_html_text(self, url, session):
        async with session.get(url) as response:
            return await response.text()

    async def get_letter_urls(self, page_url, session):
        text = await self.get_html_text(page_url, session)
        soup = BeautifulSoup(text, 'html.parser')

        print(f'collecting letter urls from web page: {page_url}...')
        return self.get_letter_urls_from_page_soup(soup)

    async def get_letter_content(self, letter_url, session):
        text = await self.get_html_text(letter_url, session)
        soup = BeautifulSoup(text, 'html.parser')
        avaliable_headers = {s.text: s for s
                             in soup.find_all('td', class_='titlestyle1335')}
        target_headers = ['信件编号', '来信主题', '信件内容', '来信时间',
                          '回复内容', '回复时间', '回复人']

        record_headers = ['letter_id', 'title', 'query', 'query_date',
                          'reply', 'reply_date', 'reply_agency']
        record = dict(zip(record_headers,
                          [None for _ in range(len(record_headers))]))

        for i, th in enumerate(target_headers):
            if th in avaliable_headers:
                record[record_headers[i]] = avaliable_headers[th].parent.find(
                    'td', 'contentstyle1335').text

        record['url'] = letter_url
        for date in ['query_date', 'reply_date']:
            record[date] = format_date(record[date])

        if record['reply_agency'] is not None:
            record['reply_agency'] = record[
                'reply_agency'].strip().replace('、', ' ')

        print(f'saved letter - query date : {record["query_date"]} - '
              f'reply date : {record["reply_date"]}'
              f'\ntitle : {record["title"]}\n'
              f'url - {record["url"]}')

        return record

    async def collect_letter_urls(self):
        async with aiohttp.ClientSession() as session:
            urls_each_page = await asyncio.gather(
                *[self.get_letter_urls(page_url, session)
                  for page_url in self.collect_page_urls()])

        return [url for letter_urls in urls_each_page for url in letter_urls]

    async def collect_letters_content(self, letter_urls):
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*[self.get_letter_content(url, session)
                                          for url in letter_urls])


if __name__ == '__main__':
    scraper = Scraper()
    scraper.run()