#-*- coding: utf-8 -*-

import math
import os
import random
import re
import numpy as np


def load_comments(count=1024, dir_path='.', file_filter=r'.+\.txt', count_per_file=128):
    file_names = os.listdir(dir_path)

    file_names = [f for f in file_names if re.match(file_filter, f)]

    if len(file_names) == 0:
        raise Exception('No files. dir=[%s], filter=[%s]' % (dir_path, file_filter))

    num_iter = math.ceil(count / count_per_file)

    # comments = [None] * count
    comments = np.empty([count], dtype=object)
    for i in range(num_iter):
        filename = random.choice(file_names)

        comments[i * count_per_file: (i+1) * count_per_file] = load(dir_path + '/' + filename, count=count_per_file)

    return comments


def load(file_path, count=100):
    with open(file_path, 'r') as data_file:
        lines = data_file.readlines()

        # comments = [None] * 10000
        comments = np.empty([10000], dtype=object)
        count_comments = 0
        comment = ''
        for l in lines:
            if l == '&&&&&&&&&&&&&&&\n':
                comment = comment.strip()

                if len(comment) > 0:

                    if len(comments) == count_comments:
                        # comments += [None] * 1000
                        comments = np.append(comments, np.empty([1000], dtype=object))

                    comments[count_comments] = comment
                    count_comments += 1

                comment = ''
            else:
                comment += l

    comments = comments[:count_comments]
    comments = random.choices(comments, k=count)

    return np.array(comments)


def disassemble(ch):
    cho_arr = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    jung_arr = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    jong_arr = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    n_chr = ord(ch) - 44032    # ord('가')

    if 0 <= n_chr <= 11171:     # ord('힣') - ord('가')
        jong = n_chr % 28
        jung = ((n_chr - jong) // 28) % 21
        cho = (((n_chr - jong) // 28) - jung) // 21

        jaso = cho_arr[cho] + jung_arr[jung] + jong_arr[jong]

        return jaso

    return ch


def disassemble_str(sentence):
    element = ''
    for c in sentence:
        element += disassemble(c)

    return element


def get_char2idx(chars):
    return {ch: i for i, ch in enumerate(chars)}


def convert_char_to_idx(chars, char2idx):
    idx_list = [None] * len(chars)

    for i, ch in enumerate(chars):
        if ch in char2idx:
            idx_list[i] = char2idx[ch]
        else:
            idx_list[i] = len(char2idx)

    return idx_list


std_char_list = '!\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~' \
                'ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ' \
                'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ' \
                ' \t\n'


def convert_comments_to_charidx(comments, char2idx):
    charidx_list = np.empty(comments.shape, dtype=object)

    for i, c in enumerate(comments):
        charidx_list[i] = convert_char_to_idx(disassemble_str(c), char2idx)

    return charidx_list


def convert_charidx_to_onehot(comments_charidx, num_char=146):

    data = np.empty(comments_charidx.shape, dtype=object)

    for i, c in enumerate(comments_charidx):
        comment_mat = np.zeros([len(c), num_char])

        for row, col in enumerate(c):
            comment_mat[row, col] = 1

        data[i] = comment_mat

    return data


def restore_char(x, char_list):
    # char_idx = np.where(x, axis=2)

    comments_char = np.empty([x.shape[0]], dtype=object)
    for i in range(x.shape[0]):
        c = [None] * x.shape[1]
        for j in range(x.shape[1]):
            idx = np.where(x[i, j, :])
            if len(idx) == 0 or len(idx[0]) == 0:
                continue

            if idx[0] < len(char_list):
                c[j] = char_list[idx[0][0]]
            else:
                c[j] = chr(22231)

        comments_char[i] = list(filter(None, c))

    return comments_char


if __name__ == "__main__":
    # load('comments_pgr_recommend_1-2_20170617_185152.txt')

    print(disassemble_str('asdg닭대가리ㅎ *%^##'))

    char2idx = get_char2idx(std_char_list)
    print(char2idx)

    idx_list = convert_char_to_idx(disassemble_str('asdgcABHJK가낱럌ㄷ ?.,]['), char2idx)

    print(idx_list)

    comments = load('comments_pgr_recommend_1-2_20170617_185152.txt')
    print(comments.shape)
    print(comments[0])

    comments_charidx = convert_comments_to_charidx(comments[:2], char2idx)

    print(comments_charidx.shape)
    print(comments[:2])
    print(comments_charidx)

    print(len(std_char_list))

    # data = convert_charidx_to_onehot(comments_charidx)
    #
    # print(data[0][0])
    # print(data[0].shape)
    #
    # print(data[1][0])
    # print(data[1].shape)
