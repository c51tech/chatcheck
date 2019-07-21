#-*- coding: utf-8 -*-

import random
import re
import time
import urllib.request as request
from bs4 import BeautifulSoup
from datetime import datetime


def get_article_no_list_pgr(board='recommend', page=1):
    return get_article_no_list(board, page,
                               board_url='http://www.pgr21.com/pb/pb.php?id=%s&page=%d',
                               pattern='&no=(\d+)')


def get_article_no_list_ilbe(board='ilbe', page=1):
    return get_article_no_list(board, page,
                               board_url='http://www.ilbe.com/index.php?mid=%s&page=%d',
                               pattern='http://www\.ilbe\.com/(\d+)')


def get_article_no_list(page, board_url, pattern, board=None, encoding='utf-8'):
    if board is None:
        url = board_url % board
    else:
        url = board_url % (board, page)

    attempts = 0
    while attempts < 3:
        try:
            data = request.urlopen(url).read().decode(encoding, 'ignore')
            break
        except Exception as e:
            print(e)
            print(url)
            attempts += 1
            time.sleep(5 * attempts)

    if attempts >= 3:
        print('Too many connection failures!')
        return []

    c = re.compile(pattern)
    m = c.findall(data)

    return m


def get_comments_pgr(article_no, board='recommend'):
    url = 'http://www.pgr21.com/pb/pb.php?id=%s&no=%s' % (board, str(article_no))

    data = request.urlopen(url).read().decode('utf-8', 'ignore')
    soup = BeautifulSoup(data, 'html5lib')
    c_codes = soup.find_all('div', {"class": "cmemo"})
    comments = [c.text.strip() for c in c_codes]

    return comments


def get_comments_ilbe(article_no, board=None):

    comments = []

    for page in range(1, 20):
        url = 'http://www.ilbe.com/index.php?document_srl=%s&cpage=%d' % (str(article_no), page)

        data = request.urlopen(url).read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(data, 'html5lib')
        c_codes = soup.find_all('div', {"class": "replyContent"})

        if len(comments) > 0 and comments[-1] == c_codes[-1].text.strip():
            break

        c_page = [c.text.strip() for c in c_codes]
        comments += c_page

    return comments


def crawl_comments(site='pgr', board='recommend', start_page=1, end_page=100, file_dir='.', time_sleep=10):

    if site == 'pgr':
        fn_article_no_list = get_article_no_list_pgr
        fn_comments = get_comments_pgr
    elif site == 'ilbe':
        fn_article_no_list = get_article_no_list_ilbe
        fn_comments = get_comments_ilbe
    else:
        raise Exception('site "%s" is not supported' % site)

    print('%s - %s' % (site, board))

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = file_dir + '/' + 'comments_%s_%s_%d-%d_%s.txt' % (site, board, start_page, end_page, timestamp)

    comment_count = 0
    with open(file_path, 'w+') as data_file:

        last_article_no = '0'
        for page in range(end_page, start_page - 1, -1):
            print('page %d' % page)

            article_no_list = fn_article_no_list(board, page)
            if last_article_no == article_no_list[-1]:
                break

            for a_no in article_no_list:
                comments_article = fn_comments(a_no, board)
                print('  article %s (count = %d)' % (a_no, len(comments_article)))

                for c in comments_article:
                    data_file.write(c)
                    data_file.write('\n&&&&&&&&&&&&&&&\n')

                comment_count += len(comments_article)
                time.sleep(random.randrange(0, time_sleep))

            print('count = %d' % comment_count)


if __name__ == "__main__":

    # step = -10
    # for end_page in range(70, 0, step):
    #     crawl_comments(site='pgr', board='recommend', start_page=end_page + step + 1, end_page=end_page,
    #                    time_sleep=5, file_dir='.')

    start = 980
    step = -2
    iter = 40
    for end_page in range(start, start + step * iter, step):
        crawl_comments(site='ilbe', board='ilbe', start_page=end_page + step + 1, end_page=end_page,
                       time_sleep=3, file_dir='/media/kikim/Data/data/chatcheck')
