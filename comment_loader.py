#-*- coding: utf-8 -*-


def load(file_path):
    with open(file_path, 'r') as data_file:
        lines = data_file.readlines()

        comments = [None] * 10000
        count_comments = 0
        comment = ''
        for l in lines:
            if l == '&&&&&&&&&&&&&&&\n':
                comment = comment.strip()

                if len(comment) > 0:

                    if len(comments) == count_comments:
                        comments += [None] * 1000

                    comments[count_comments] = comment
                    count_comments += 1

                comment = ''
            else:
                comment += l

    comments = comments[:count_comments]

    return comments


def disassemble(ch):
    cho_arr = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    jung_arr = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    jong_arr = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    n_chr = ord(ch) - 44032    # ord('가')

    if 0 <= n_chr <= 55203:     # ord('힣')
        jong = n_chr % 28
        jung = ((n_chr - jong) // 28) % 21
        cho = (((n_chr - jong) // 28) - jung) // 21

        return cho_arr[cho] + jung_arr[jung] + jong_arr[jong]

    return ch


def disassemble_str(sentence):
    element = ''
    for c in sentence:
        element += disassemble(c)

    return element


def get_char2idx(chars):
    return { ch:i for i,ch in enumerate(chars) }


def convert_char_to_idx(chars, char2idx):
    idx_list = [None] * len(chars)

    for i, ch in enumerate(chars):
        if ch in char2idx:
            idx_list[i] = char2idx[ch]
        else:
            idx_list[i] = -1

    return idx_list


std_char_list = '!\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~' \
                'ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ' \
                'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ' \
                ' \t\n'


def convert_comments2charidx(comments, char2idx):
    charidx_list = [None] * len(comments)
    for i, c in enumerate(comments):
        charidx_list[i] = convert_char_to_idx(disassemble_str(c), char2idx)

    return charidx_list


if __name__ == "__main__":
    # load('comments_pgr_recommend_1-2_20170617_185152.txt')

    print(disassemble_str('asdg닭대가리ㅎ *%^##'))

    char2idx = get_char2idx(std_char_list)
    print(char2idx)

    idx_list = convert_char_to_idx(disassemble_str('asdgcABHJK가낱럌ㄷ ?.,]['), char2idx)

    print(idx_list)

    comments = load('comments_pgr_recommend_1-2_20170617_185152.txt')

    comments_charidx = convert_comments2charidx(comments[:2], char2idx)

    print(comments[:2])
    print(comments_charidx)
