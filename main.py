"""
Gathers popular skills.

Script parses hh.ru and gathers skills-by-popular-demand.
Writes them out into popular_skills.csv
Analyzes the skills by popularity
"""
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import aiofiles
from analyze import analyze
from collections import Counter

async def get_positions():
    """
    Parse range of job offers for a language
    :return:
    """
    base_url = 'https://volgograd.hh.ru/search/vacancy?area=113&clusters=true&enable_snippets=true&ored_clusters=true&schedule=remote&text='
    language = input('What language to analyze?\n')  # ← Set your programming language. e.g. 'python'
    request_first_page = base_url + language
    pages = await get_page_range(request_first_page)

    async with aiohttp.ClientSession() as session:
        async for i in async_range(pages):
            try:
                url = request_first_page + '&page=' + str(i)
                async with session.get(url) as response:
                    found_data = []
                    cont = await response.text()
                    soup = BeautifulSoup(cont, 'html.parser')
                    links = soup.select('.vacancy-serp-item .resume-search-item__name .g-user-content .bloko-link')
                    for link in links:
                        found_data.append(await get_details(link.attrs['href']))
                    async with aiofiles.open('popular_skills.csv', mode='a', encoding='utf-8') as out_file:
                        for data in found_data:
                            await out_file.write(','.join(data) + '\n')
            except:
                pass
        print('Done. (salary, url, skills) are saved into "popular_skills.csv".')
        print('Skills by popularity:')
        analyze()


async def async_range(count):
    """
    Async range
    :param count:
    :return:
    """
    for i in range(count):
        yield i


async def get_page_range(request_first_page):
    """
    Detects last page number
    :param request_first_page:
    :return:
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(request_first_page) as response:
            cont = await response.text()
            soup_first = BeautifulSoup(cont,'html.parser')
            next_button = soup_first.find(lambda tag: get_last_page(tag))
            last_page = next_button.previous_sibling.contents[3].text
            last_page = int(last_page)
            return last_page


async def get_details(inner_url):
    """
    Perform parsing of detail page
    :param inner_url:
    :return:
    """
    async with aiohttp.ClientSession() as inner_session:
        async with inner_session.get(inner_url) as inner_response:
            try:
                inner_content = await inner_response.text()
                inner_soup = BeautifulSoup(inner_content, "html.parser")

                relevant = inner_soup.find(lambda tag: get_key_points(tag))
                if relevant is not None:
                    tags = relevant.parent.find_all('span')
                else:
                    tags = ['<unknown>']

                salary = inner_soup.find(attrs={"data-qa": "vacancy-salary-compensation-type-net"})
                if salary is not None:
                    salary = salary.text
                else:
                    salary = '<unknown>'

                return [salary] + [inner_url] + [x.text for x in tags if type(x) is not str]
            except:
                return ['<unknown>'] + ['<unknown>'] + ['<unknown>']


def get_last_page(tag):
    if tag.text != '' and tag.text != ' ' and tag.text == 'дальше':
        return True
    # $('.pager .bloko-form-spacer .bloko-button')


def get_key_points(tag):
    """
    Searches for an html tag with 'key skills'
    :param tag:
    :return:
    """
    if tag.text != '' and tag.text != ' ' and tag.text in 'Ключевые навыки' and tag.attrs['class'][0] == 'bloko-header-2':
        return True


def get_salary(tag):
    """
    Searches for an html tag with 'salary'
    :param tag:
    :return:
    """
    if tag.text != '' and tag.text != ' ' and 'data-qa' in tag.attrs and tag.attrs['data-qa'][0] == 'vacancy-salary-compensation-type-net':
        return True


if __name__ == '__main__':
    # Reinitialize outfile
    with open('popular_skills.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write('')
    # Asyncio run
    loop = asyncio.get_event_loop()
    task = loop.create_task(get_positions())
    loop.run_until_complete(task)
