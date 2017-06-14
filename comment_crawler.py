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
    c_codes = soup.find_all('div', {"class": "cmemo"})
    comments = [c.text.strip() for c in c_codes]

    return comments


def get_comments_ilbe(article_no):

    comments = []

    for page in range(1, 20):
        print('page %d' % page)

        url = 'http://www.ilbe.com/index.php?document_srl=%d&cpage=%d' % (article_no, page)
        data = urllib2.urlopen(url).read()
        soup = BeautifulSoup(data, 'html5lib')
        c_codes = soup.find_all('div', {"class": "replyContent"})

        if len(comments) > 0 and comments[-1] == c_codes[-1].text.strip():
            print('same page. break!')
            break

        c_page = [c.text.strip() for c in c_codes]

        comments += c_page

    return comments


if __name__ == "__main__":
    comments = get_comments_ilbe(9821475171)
    # comments = get_comments_pgr(2823)
    print(len(comments))

    # print(comments)

    for c in comments:
        print('<%s>' % c)
