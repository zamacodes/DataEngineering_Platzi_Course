import pandas as pd
import argparse
import logging
logging.basicConfig(level=logging.INFO)
from  urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

def _read_data(filename):
    logger.info(f'Reading file {filename}')
    return pd.read_csv(filename)

def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper uid')
    newspaper_uid = filename.split('_')[0]
    logger.info(f'Newspaper uid detected: {newspaper_uid}')
    return newspaper_uid

def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info(f'Filling newspaper_uid column with {newspaper_uid}')
    df['newspaper'] = newspaper_uid
    return df

def _extract_host(df):
    logger.info(f'Extracting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df

def _eliminate_tags(df):
    tag_regex = re.compile(r'^<.*>$') #/my-text

    for _ in df['body']:
        re.sub(tag_regex, '', _)
    return df


def main(filename):
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df,newspaper_uid)
    df = _extract_host(df)
    df = _eliminate_tags(df)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Path of Dirty data', type=str)

    args = parser.parse_args()
    df = main(args.filename)
    print(df)