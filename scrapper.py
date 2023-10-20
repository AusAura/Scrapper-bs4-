import aiohttp
import json, logging
from bs4 import BeautifulSoup
from aiohttp import ClientSession

url = 'https://quotes.toscrape.com/'
start_url = url
login_url = 'http://quotes.toscrape.com/login'
login_data = {'username': 'admin', 'password': 'admin'}

# Настройка логгирования
logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def login(session: ClientSession) -> None:
    logging.info('TRYING TO LOG IN')
    async with session.post(login_url, data=login_data) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'lxml')
            is_logged = soup.select_one('a[href^="http://goodreads.com"]')
            logging.info(f'IF LOGIN SUCCESSFUL: {is_logged}')

async def fetch_author(session: ClientSession, url: str, meta: str) -> dict:
    logging.info(f'START FETCHING AUTHOR LINK: {url}')
    async with session.get(url) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'lxml')

            data = {'fullname': soup.find('h3', class_='author-title').text,
                    'born_date': soup.find('span', class_='author-born-date').text,
                    'born_location': soup.find('span', class_='author-born-location').text,
                    'description': soup.find('div', class_='author-description').text.strip(),
                    'goodreads_url': meta}
            
            logging.info(f'FETCHED AN AUTHOR: {data}')
            return data

async def fetch_content(session: ClientSession, url: str) -> tuple[list, list]:
        logging.info(f'START FETCHING: {url}')
        async with session.get(url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'lxml')
                logging.info(f'INITIAL FETCH: {soup}')
                quotes = soup.find_all('span', class_='text')
                authors = soup.find_all('small', class_='author')
                tags = soup.find_all('div', class_='tags')
                author_pages = soup.select('a[href^="/author/"]')
                hrefs = [result['href'] for result in author_pages]
                externals = soup.select('a[href^="http://goodreads.com"]', class_='text')
                external_urls = [result['href'] for result in externals]
                author_data = []
                quotes_data = []

                for i in range(0, len(quotes)):
                    quote = quotes[i].text
                    author = authors[i].text
                    tags_prep_quote = tags[i].find_all('a', class_='tag')
                    tags_quote = []

                    for tag in tags_prep_quote:
                        tags_quote.append(tag.text)

                    data = {
                        "tags": tags_quote,
                        "author": author,
                        "quote": quote
                    }

                    logging.info(f'FETCHED A QUOTE: {data}')

                    quotes_data.append(data)

                    href = hrefs[i]
                    logging.info(f'FETCHED THIS HREF: {href}')
                    author_url = start_url + href

                    meta = external_urls[i]
                    logging.info(f'FETCHED THIS AUTHOR LINK: {author_url}, META = {meta}')
                    author_data.append(await fetch_author(session, url=author_url, meta=meta))

                logging.info(f'GOT QUOTES: {quotes_data}')
                logging.info(f'GOT AUTHORS: {author_data}')

                return tuple(quotes_data), tuple(author_data)


async def main(url: str) -> None:
    async with aiohttp.ClientSession() as session:
        await login(session)
        logging.info(f'PAGINATION INIT')
        quotes_data = []
        author_data = []

        while True:
            quotes, authors = await fetch_content(session, url)
            if quotes:
                quotes_data.extend(quotes)
            if authors:
                author_data.extend(authors)

            response = await session.get(url)
            soup = BeautifulSoup(await response.text(), 'lxml')

            next_page = soup.find('li', class_='next')
            logging.info(f'LOOKING FOR NEXT PAGE: {next_page}')
            if not next_page:
                logging.info('NEXT PAGE NOT FOUND!')
                break
            next_url = next_page.a['href']
            url = f'{start_url}{next_url}'
            logging.info(f'TAKING NEW URL: {url}')
            print(f'TAKING NEW URL: {url}')

        logging.info(f'FINAL QUOTES: {quotes_data}')
        logging.info(f'FINAL AUTHORS: {author_data}')

        # Убираем дубликаты
        # quotes_prep_data = [dict(t) for t in {tuple(q.items()) for q in quotes_data}]
        # author_prep_data = [dict(t) for t in {tuple(a.items()) for a in author_data}]        
        quotes_prep_data = [json.loads(t) for t in {json.dumps(q, sort_keys=True) for q in quotes_data}]
        author_prep_data = [json.loads(t) for t in {json.dumps(a, sort_keys=True) for a in author_data}]

        # Запись данных в файл JSON
        with open('quotes.json', 'w', encoding='utf-8') as f:
            json.dump(quotes_prep_data, f, indent=4, ensure_ascii=False)
            logging.info('WRITING QUOTES DONE')

        with open('authors.json', 'w', encoding='utf-8') as f:
            json.dump(author_prep_data, f, indent=4, ensure_ascii=False)
            logging.info('WRITING AUTHORS DONE')


if __name__ == '__main__':
    import asyncio
    logging.info(f'BEGIN!')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url=url))
    logging.info(f'FINISHED!')
    print(f'FINISHED!')