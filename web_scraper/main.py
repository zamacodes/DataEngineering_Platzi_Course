import argparse
from common import config
import logging
logging.basicConfig(level=logging.INFO)

import news_page_objects as news
import re
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
import datetime
import csv

logger = logging.getLogger(__name__)
is_well_formed_link = re.compile(r'^https?://.+/.+$') #https://mypage.com/hello-world
is_root_path = re.compile(r'^/.+$') #/my-text

def _news_scrapper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    logging.info('Starting scrapper for {}'.format(host))
    homepage = news.HomePage(news_site_uid, host)
    articles = []
    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info('Article fetched correctly.')
            articles.append(article)
           # print(article.title)
    #print(f'We got {len(articles)} articles')
    _save_articles(news_site_uid,articles)

def _save_articles(news_site_uid,articles):
    now_date = datetime.datetime.now().strftime('%Y_%m_%d')
    out_file_name = f'{news_site_uid}_{now_date}_articles.csv'

    csv_headers = list(filter(lambda property: not property.startswith('_'),dir(articles[0])))
    with open(out_file_name, mode = 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article,prop)) for prop in csv_headers]
            writer.writerow(row)
    


def _build_link(host,link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return f'{host}{link}'
    else:
        return f'{host}/{link}'

def _fetch_article(news_site_uid, host, link):
    logger.info(f'Starting to fetch article at {link}')

    article = None
    try:
        article = news.ArticlePage(news_site_uid, _build_link(host,link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching article', exc_info = False)
    if article and not article.body:
        logger.warning('Invalid article. There is no body in it')
        return None
    return article

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site',
                         help = 'News site that you want to scrape',
                        type = str,
                        choices = news_site_choices
                        )
    args = parser.parse_args()
    _news_scrapper(args.news_site)