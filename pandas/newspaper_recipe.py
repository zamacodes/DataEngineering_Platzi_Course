import pandas as pd
import argparse
import logging
logging.basicConfig(level=logging.INFO)
from  urllib.parse import urlparse
import re
import hashlib
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

def _fill_missing_titles(df):
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()
    missing_titles = (df[missing_titles_mask]['url']
                    .str.extract(r'(?P<missing_titles>[^/]+)$')
                    .applymap(lambda title: title.replace('-',' '))
                    .applymap(lambda title: title.replace('.html','')) 
                    )
    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:,'missing_titles']
    return df

def _generate_uids_for_rows(df):
    logger.info(f'Generating uids')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())),
                axis = 'columns')
            .apply(lambda hash_object: hash_object.hexdigest())
            ) 
    df['uid'] = uids
    return df.set_index('uid')

def _remove_new_lines_from_body(df):
    logger.info(f'Removing line breaks and tabs from body')
    stripped_body = (df
                     .apply(lambda row: row['body'], axis = 'columns')
                     .apply(lambda body: list(body))
                     .apply(lambda letters: list(map(lambda letter: letter.replace ('\n',''), letters)))
                     .apply(lambda letters_list: ''.join(letters_list))
                     
                )
    df['body'] = stripped_body
    stripped_body = (df
                    .apply(lambda row: row['body'], axis = 'columns')
                    .apply(lambda body: list(body))
                    .apply(lambda letters: list(map(lambda letter: letter.replace ('\t',''), letters)))
                    .apply(lambda letters_list: ''.join(letters_list))
                    
            )
    df['body'] = stripped_body
    return df


def main(filename):
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df,newspaper_uid)
    df = _extract_host(df)
    df = _eliminate_tags(df)
    df = _fill_missing_titles(df)
    df = _generate_uids_for_rows(df)
    df = _remove_new_lines_from_body(df)

    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Path of Dirty data', type=str)

    args = parser.parse_args()
    df = main(args.filename)
    print(df)