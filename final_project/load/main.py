import argparse
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import pandas as pd

from article import Article
from base import Base, engine,Session

def main(filename):
    Base.metadata.create_all(engine)
    session = Session()
    articles = pd.read_csv(filename)

    for index,row in articles.iterrows():
        logger.info(f"Loading article with uid {row['uid']} into DB")
        article = Article(row['uid'],
                        row['body'],
                        row['host'],
                        row['newspaper'],
                        row['n_tokens_body'],
                        row['n_tokens_title'],
                        row['title'],
                        row['url']
                        )
        session.add(article)
    session.commit()
    session.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help = "File you want to load into the db, type=str")
    
    args = parser.parse_args()

    main(args.filename)