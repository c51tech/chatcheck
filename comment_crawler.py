#-*- coding: utf-8 -*-

import random
import re
import time
import urllib2
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


def get_article_no_list(board, page, board_url, pattern):
    url = board_url % (board, page)
    data = urllib2.urlopen(url).read()

    c = re.compile(pattern)
    m = c.findall(data)

    return m


def get_comments_pgr(article_no, board='recommend'):
    url = 'http://www.pgr21.com/pb/pb.php?id=%s&no=%s' % (board, str(article_no))
    data = urllib2.urlopen(url).read()

    soup = BeautifulSoup(data, 'html5lib')
    c_codes = soup.find_all('div', {"class": "cmemo"})
    comments = [c.text.strip() for c in c_codes]

    return comments


def get_comments_ilbe(article_no, board=None):

    comments = []

    for page in range(1, 20):
        # print('page %d' % page)

        url = 'http://www.ilbe.com/index.php?document_srl=%s&cpage=%d' % (str(article_no), page)
        data = urllib2.urlopen(url).read()
        soup = BeautifulSoup(data, 'html5lib')
        c_codes = soup.find_all('div', {"class": "replyContent"})

        if len(comments) > 0 and comments[-1] == c_codes[-1].text.strip():
            # print('same page. break!')
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

            # comments = []
            for a_no in article_no_list:
                comments_article = fn_comments(a_no, board)
                print('  article %s (count = %d)' % (a_no, len(comments_article)))

                for c in comments_article:
                    data_file.write(c.encode('utf-8'))
                    data_file.write('\n&&&&&&&&&&&&&&&\n')

                comment_count += len(comments_article)
                time.sleep(random.randrange(0, time_sleep))

            print('count = %d' % comment_count)


if __name__ == "__main__":

    crawl_comments(site='pgr', board='recommend', end_page=10, time_sleep=5)
    # crawl_comments(site='ilbe', board='ilbe', end_page=2, time_sleep=5)

    # comments = get_comments_ilbe('9821475171')
    # # comments = get_comments_pgr(2823)
    # print(len(comments))
    #
    # # print(comments)
    #
    # for c in comments:
    #     print('<%s>' % c)


