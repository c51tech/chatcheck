import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
from keras.preprocessing import sequence

import comment_loader

np.random.seed(7)

char2idx = comment_loader.get_char2idx(comment_loader.std_char_list)


def load(count, dir_path='.'):

    comments_pgr = comment_loader.load_comments(count=count//2, dir_path=dir_path, file_filter=r'.+pgr.+\.txt')
    comments_ilbe = comment_loader.load_comments(count=count//2, dir_path=dir_path, file_filter=r'.+ilbe.+\.txt')

    x_pgr = comment_loader.convert_comments_to_charidx(comments_pgr, char2idx)
    x_ilbe = comment_loader.convert_comments_to_charidx(comments_ilbe, char2idx)

    x = np.concatenate((x_pgr, x_ilbe), axis=0)

    y_pgr = np.ones(x_pgr.shape)
    y_ilbe = np.zeros(x_ilbe.shape)

    y = np.concatenate((y_pgr, y_ilbe))

    idx_suffle = np.random.permutation(count)

    x = x[idx_suffle]
    y = y[idx_suffle]

    # print(x.shape)
    # print(y.shape)
    #
    # print(x[:5])
    # print(y[:5])

    comments = np.concatenate((comments_pgr, comments_ilbe), axis=0)
    comments = comments[idx_suffle]

    # print(comments[:5])

    return x, y, comments


def learn():
    # x_train, y_train, _ = load(1024, dir_path='/media/kikim/Data/data/chatcheck')
    x_train, y_train, _ = load(1024, dir_path='.')
    x_test, y_test, _ = load(1024, dir_path='.')

    x_train = comment_loader.convert_charidx_to_onehot(x_train)
    x_test = comment_loader.convert_charidx_to_onehot(x_test)
    # print(x_train.shape)
    # print(y_train.shape)
    #
    # print(x_train[:5])
    # print(y_train[:5])

    max_review_length = 1000

    x_train = sequence.pad_sequences(x_train, maxlen=max_review_length)
    x_test = sequence.pad_sequences(x_test, maxlen=max_review_length)

    # print(x_train.shape)
    # print(x_test.shape)

    y_train = np_utils.to_categorical(y_train)
    y_test = np_utils.to_categorical(y_test)

    # print(y_train.shape)
    # print(y_train[:3, :])

    model = Sequential()
    model.add(LSTM(16, input_shape=(x_train.shape[1], x_train.shape[2])))
    model.add(Dense(y_train.shape[1], activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=10, batch_size=16)
    scores = model.evaluate(x_test, y_test)
    print('Accuracy %f' % scores[1])


if __name__ == "__main__":
    learn()
