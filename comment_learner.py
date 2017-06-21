import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils

import comment_loader

np.random.seed(7)

char2idx = comment_loader.get_char2idx(comment_loader.std_char_list)


def load(count, dir_path='.'):

    comments_pgr = comment_loader.load_comments(count=count//2, dir_path='/media/kikim/Data/data/chatcheck', file_filter=r'.+pgr.+\.txt')
    comments_ilbe = comment_loader.load_comments(count=count//2, dir_path='/media/kikim/Data/data/chatcheck', file_filter=r'.+ilbe.+\.txt')

    x_pgr = comment_loader.convert_comments_to_charidx(comments_pgr, char2idx)
    x_ilbe = comment_loader.convert_comments_to_charidx(comments_ilbe, char2idx)

    x = np.concatenate((x_pgr, x_ilbe), axis=0)

    y_pgr = np.ones(x_pgr.shape)
    y_ilbe = np.zeros(x_ilbe.shape)

    y = np.concatenate((y_pgr, y_ilbe))

    idx_suffle = np.random.permutation(count)

    x = x[idx_suffle]
    y = y[idx_suffle]

    print(x.shape)
    print(y.shape)

    print(x[:5])
    print(y[:5])

    comments = np.concatenate((comments_pgr, comments_ilbe), axis=0)
    comments = comments[idx_suffle]
    print(comments[:5])

    return x, y, comments


if __name__ == "__main__":
    load(1000, dir_path='/media/kikim/Data/data/chatcheck')
