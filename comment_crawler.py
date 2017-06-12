import re
import urllib2
from bs4 import BeautifulSoup


def get_article_no_list_pgr(board='recommend', page=1):
    pgr_url = 'http://www.pgr21.com/pb/pb.php?id=%s&page=%d' % (board, page)
    # req = urllib.request.Request(pgr_url)
    data = urllib2.urlopen(pgr_url).read()

    article_no = '&no=(\d+)'

    c = re.compile(article_no)
    m = c.findall(data)

    return m


if __name__ == "__main__":
    print(get_article_no_list_pgr())
