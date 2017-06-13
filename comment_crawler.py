#-*- coding: utf-8 -*-

import re
import urllib2
from bs4 import BeautifulSoup


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
    url = 'http://www.pgr21.com/pb/pb.php?id=%s&no=%d' % (board, article_no)
    data = urllib2.urlopen(url).read()

    soup = BeautifulSoup(data, 'html5lib')
    comments = soup.find_all('div', {"class": "cmemo"})

    return comments


def get_comments_ilbe(article_no):
    url = 'http://www.ilbe.com/index.php?document_srl=%d&cpage=1' % article_no
    data = urllib2.urlopen(url).read()
    soup = BeautifulSoup(data, 'html5lib')
    comments = soup.find_all('div', {"class": "replyContent"})

    return comments


if __name__ == "__main__":
    comments = get_comments_ilbe(9821475171)
    print(len(comments))

    # print(comments[8])
    for c in comments:
        print('<%s>' % c.text.strip())
