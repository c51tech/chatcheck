# -*- coding: utf-8 -*-

import random
import re
import time
import urllib.request as request
from bs4 import BeautifulSoup
from datetime import datetime
import comment_crawler


# MBC radio
# board='kmh_world' 김동환의 세계는 우리는
# board='focus03' 신동호의 시선집중
def get_article_no_list_mbc_radio(board, page=1):
    article_no_list = comment_crawler.get_article_no_list(
        page=page, board=board, encoding='euc-kr',
        board_url='http://imbbs.imbc.com/list.mbc?bid=%s&page=%d',
        pattern="javascript\:goView\(\d+,\s*(\d+)\)")

    article_no_list = list(set(map(int, article_no_list)))
    article_no_list.sort()

    return article_no_list


def get_each_q_or_a_mbc_radio(article_no, board):
    url = 'http://imbbs.imbc.com/view.mbc?list_id=%s&bid=%s' % (str(article_no), board)

    attempts = 0
    while attempts < 3:
        try:
            data = request.urlopen(url).read().decode('euc-kr', 'ignore')
            break
        except Exception as e:
            print(e)
            print(url)
            attempts += 1
            time.sleep(5 * attempts)

    if attempts >= 3:
        print('Too many connection failures!')
        return []

    soup = BeautifulSoup(data, 'html5lib')
    qa_text = soup.find('div', {"id": "divContents"}).text.strip()
    qas = [qa.replace('\xa0', ' ').strip() for qa in qa_text.split('\n') if qa.strip() is not '']
    if len(qas) < 5:
        qas = [qa.strip() for qas_i in qas for qa in re.split('☎|⊙|◎|◉|☉|#|◆|■|\*', qas_i) if qa.strip() is not '']

    if qas[0][-1] is ':':   # 옛날 양식 1
        qa_list = [qa for qa in qas if qa[-1] is not ':']
    elif qas[0][0] is '<':   # 옛날 양식 2
        qa_list = [re.split(':\t*', qa, maxsplit=1)[1].strip() for qa in qas if len(re.split(':\t*', qa)) > 1]
    else:
        qa_list = [re.split('>|:', qa, maxsplit=1)[1].strip() for qa in qas if len(re.split('>|:', qa)) > 1]

    # return qas
    return qa_list


def crawl_interview(site='mbc', board='kmh_world', start_page=1, end_page=100, file_dir='.', time_sleep=10):

    if site == 'mbc':
        fn_article_no_list = get_article_no_list_mbc_radio
        fn_comments = get_each_q_or_a_mbc_radio
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
            if len(article_no_list) == 0 or last_article_no == article_no_list[-1]:
                break

            for a_no in article_no_list:
                comments_article = fn_comments(a_no, board)

                if len(comments_article) < 5:
                    print('  article %s (count = %d)' % (a_no, len(comments_article)))
                    continue
                # print('  article %s (count = %d)' % (a_no, len(comments_article)))

                for c in comments_article:
                    data_file.write(c)
                    data_file.write('\n&&&&&&&&&&&&&&&\n')

                comment_count += len(comments_article)
                time.sleep(random.randrange(0, time_sleep))

            print('count = %d' % comment_count)


if __name__ == "__main__":
    # print(get_article_no_list_mbc_radio('kmh_world', 259))
    # print(get_each_q_or_a_mbc_radio(6916281, 'kmh_world'))
    # print(get_each_q_or_a_mbc_radio(3265727, 'kmh_world'))
    # print(get_each_q_or_a_mbc_radio(127, 'kmh_world'))
    # print(get_each_q_or_a_mbc_radio(3, 'kmh_world'))
    #
    # print(get_article_no_list_mbc_radio('focus03', 2))
    # print(get_each_q_or_a_mbc_radio(6915085, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(6382705, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(5010805, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(2476017, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(2786, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(2682, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(2720, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(2505, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(2495, 'focus03'))
    # print(get_each_q_or_a_mbc_radio(2486, 'focus03'))

    # start = 260
    # step = -2
    # iter = 130
    #
    # for end_page in range(start, start + step * iter, step):
    #     crawl_interview(site='mbc', board='kmh_world', start_page=end_page + step + 1, end_page=end_page,
    #                     time_sleep=3, file_dir='/media/kikim/Data/data/chatcheck/interview_mbc')

    start = 522
    step = -2
    iter = 261

    for end_page in range(start, start + step * iter, step):
        crawl_interview(site='mbc', board='focus03', start_page=end_page + step + 1, end_page=end_page,
                        time_sleep=3, file_dir='/media/kikim/Data/data/chatcheck/interview_mbc')

