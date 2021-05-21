from pathlib import Path
import csv
import asyncio

from bs4 import BeautifulSoup
import aiohttp

from utils import LATEST_DATA, get_soup, format_date, get_mail_id_from_url


class Scraper:

    BASE_URL = 'http://www.shangluo.gov.cn'
    DEFAULT_QUERY = '/zmhd/ldxxlb.jsp'

    def __init__(self):
        self.first_page_soup = get_soup(self.get_page_url(1))

        self.total_pages = int(self.first_page_soup.find(
            'a', class_='Next').parent.find_all('a')[-2].text)
        self.mails_per_page = len(self.get_mail_urls_from_page_soup(
            self.first_page_soup))

    def run(self):
        if not Path(LATEST_DATA).exists():
            print('first time to run...')
            self.create()
        else:
            new_mail_urls, need_recreate = self.get_new_mail_urls()
            if need_recreate:
                self.create()
            elif new_mail_urls is not None:
                print('start to update...')
                self.update(new_mail_urls)
            else:
                print('latest version')

    def create(self):
        mail_urls = asyncio.run(self.collect_mail_urls())
        records = asyncio.run(self.collect_mails_content(mail_urls))

        self.to_csv(records)

    def update(self, new_mail_urls):
        records = asyncio.run(self.collect_mails_content(new_mail_urls))

        csvfile = open(LATEST_DATA, newline='')
        history_records = [r for r in csv.DictReader(csvfile)]

        self.to_csv(records + history_records)

    def to_csv(self, records):
        with open(LATEST_DATA, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=records[0].keys())
            writer.writeheader()
            for row in records:
                writer.writerow(row)

    def get_page_url(self, num):
        return (self.BASE_URL + self.DEFAULT_QUERY + '?'
                + f'formname1333at=54&formname1333ap={num}&formname1333ac=15&'
                + 'urltype=tree.TreeTempUrl&wbtreeid=1112')

    def collect_page_urls(self):
        return [self.get_page_url(i + 1) for i in range(self.total_pages)]

    def get_new_mail_urls(self):
        with open(LATEST_DATA, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            latest_saved_id = get_mail_id_from_url(next(reader)['url'])

            saved_mails = 1
            for row in reader:
                saved_mails += 1

        total_mails = self.mails_per_page * (self.total_pages - 1) \
            + len(self.get_mail_urls_from_page_soup(
                get_soup(self.get_page_url(self.total_pages))))

        miss_mails = total_mails - saved_mails
        if not miss_mails:
            return None, False

        new_mail_urls = []
        current_page_soup = self.first_page_soup

        found_latest_saved_id = False
        while not found_latest_saved_id:
            mail_urls = self.get_mail_urls_from_page_soup(current_page_soup)
            for url in mail_urls:
                mail_id = get_mail_id_from_url(url)
                if mail_id == latest_saved_id:
                    found_latest_saved_id = True
                    break
                else:
                    new_mail_urls.append(url)
                    miss_mails -= 1
            else:
                next_page_href = self.current_page_soup.find(
                    'a', class_='Next').get('href')
                current_page_soup = get_soup(self.BASE_URL
                                             + self.DEFAULT_QUERY + '?'
                                             + next_page_href)

        # new updates before the latest saved mail
        need_recreate = miss_mails > 0

        return new_mail_urls, need_recreate

    def get_mail_urls_from_page_soup(self, page_soup):
        main_table = page_soup.find('table', class_='winstyle1333')
        return [self.BASE_URL + item.a.get('href')
                for item in main_table.find_all('tr')[1:]]

    async def get_soup_under_session(self, url, session):
        async with session.get(url) as response:
            text = await response.text()
            return BeautifulSoup(text, 'html.parser')

    async def get_mail_urls(self, page_url, session):
        soup = await self.get_soup_under_session(page_url, session)
        print(f'collecting mail urls from web page: {page_url}...')
        return self.get_mail_urls_from_page_soup(soup)

    async def get_mail_content(self, mail_url, session):
        while True:
            try:
                soup = await self.get_soup_under_session(mail_url, session)
                break
            except (aiohttp.ServerDisconnectedError,
                    aiohttp.ClientResponseError,
                    aiohttp.ClientConnectorError,
                    aiohttp.ClientOSError):
                print(f'retry: {mail_url}...')
                await asyncio.sleep(1)

        avaliable_headers = {h.text: h for h
                             in soup.find_all('td', class_='titlestyle1335')}
        target_headers = ['信件编号', '来信主题', '信件内容', '来信时间',
                          '回复内容', '回复时间', '回复人']

        record_headers = ['mail_id', 'title', 'query', 'query_date',
                          'reply', 'reply_date', 'reply_agency']
        record = dict(zip(record_headers,
                          [None for _ in range(len(record_headers))]))

        for i, th in enumerate(target_headers):
            if th in avaliable_headers:
                record[record_headers[i]] = avaliable_headers[th].parent.find(
                    'td', 'contentstyle1335').text

        record['url'] = mail_url
        for date in ['query_date', 'reply_date']:
            record[date] = format_date(record[date])

        if record['reply_agency'] is not None:
            record['reply_agency'] = record[
                'reply_agency'].strip().replace('、', ' ')

        print(f'saved mail - query date : {record["query_date"]} - '
              f'reply date : {record["reply_date"]}\n'
              f'title : {record["title"]}\n'
              f'url - {record["url"]}')

        return record

    async def collect_mail_urls(self):
        async with aiohttp.ClientSession() as session:
            urls_each_page = await asyncio.gather(
                *[self.get_mail_urls(page_url, session)
                  for page_url in self.collect_page_urls()])

        return [url for mail_urls in urls_each_page for url in mail_urls]

    async def collect_mails_content(self, mail_urls):
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*[self.get_mail_content(url, session)
                                          for url in mail_urls])


if __name__ == '__main__':
    scraper = Scraper()
    scraper.run()
