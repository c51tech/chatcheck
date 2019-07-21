import numpy as np
import datetime
import random
import sys
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.layers import LSTM
from keras.models import model_from_json
from keras.callbacks import ModelCheckpoint
from keras.optimizers import Adam
from keras.utils import np_utils
from keras.preprocessing import sequence
from keras import backend as K

import comment_loader

# np.random.seed(7)

char2idx = comment_loader.get_char2idx(comment_loader.std_char_list)


def load_data(count, dir_path='.'):

    comments_formal = comment_loader.load_comments(count=count//2, dir_path=dir_path, file_filter=r'.+pgr.+\.txt', count_per_file=count//16)
    comments_rude= comment_loader.load_comments(count=count//2, dir_path=dir_path, file_filter=r'.+dc.+\.txt', count_per_file=count//16)

    comments = np.concatenate((comments_formal, comments_rude), axis=0)

    y_formal = np.ones(comments_formal.shape)
    y_rude= np.zeros(comments_rude.shape)

    y = np.concatenate((y_formal, y_rude))

    idx_shuffle = np.random.permutation(count)

    comments = comments[idx_shuffle]
    y = y[idx_shuffle]

    return comments, y


def preprocess_comments(comments, max_review_length=128):
    x = comment_loader.convert_comments_to_charidx(comments, char2idx)
    x = comment_loader.convert_charidx_to_onehot(x)
    x = sequence.pad_sequences(x, maxlen=max_review_length)

    return x


def load_model(model_file_path, weight_file_path):
    json_file = open(model_file_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)

    model.load_weights(weight_file_path)

    model.summary()

    return model


def learn(model=None, train_dir='.', test_dir='.', count=1024, test_count=1024, max_iter=100, epochs=10, max_review_length=128, data_modifier=None):

    if model is None:
        model = Sequential()
        model.add(LSTM(256, input_shape=(max_review_length, len(char2idx) + 1), return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(256, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dense(1, activation='relu'))

    learning_rate = 0.001
    adam = Adam(lr=learning_rate)
    model.compile(loss='mean_squared_error', optimizer=adam, metrics=['mae'])

    start_time = datetime.datetime.now()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    model_json = model.to_json()
    with open('model_%s.json' % timestamp, 'w') as json_file:
        json_file.write(model_json)

    weight_file = './weights_%s.h5' % timestamp
    # checkpoint = ModelCheckpoint(weight_file, monitor='loss', verbose=1, save_best_only=False, mode='min')
    # callback_list = [checkpoint]

    for i in range(max_iter):
        print('################# Iteration: %d' % i)

        comments_train, y_train = load_data(count, dir_path=train_dir)
        comments_test, y_test = load_data(test_count, dir_path=test_dir)

        if data_modifier is not None:
            comments_train = data_modifier(comments_train, y_train)
            comments_test = data_modifier(comments_test, y_test)

        x_train = preprocess_comments(comments_train, max_review_length)
        x_test = preprocess_comments(comments_test, max_review_length)

        model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=epochs, batch_size=16, verbose=2)

        model.save_weights(weight_file)

        K.set_value(adam.lr, learning_rate / (epochs * (i + 1)))

    print('\nLearning Time: %s' % (datetime.datetime.now() - start_time))

    comments_test, y_test, = load_data(count=test_count, dir_path='/media/kikim/Data/data/chatcheck/test')
    x_test = preprocess_comments(comments_test, max_review_length=max_review_length)

    prediction = model.predict(x_test, verbose=0)

    diff = np.sum(np.abs(prediction - y_test.reshape(prediction.shape)), axis=1)
    is_wrong = diff >= 0.5
    count_wrong = np.sum(is_wrong)
    print('Accuracy: %.2f%%' % (100 - count_wrong / test_count * 100))


def comment_modifier(comments, y):

    for idx, c in enumerate(comments):
        if y[idx] == 0:
            r = random.random()
            if r < 0.033:
                comments[idx] += ';' * random.randint(1, 50)
            elif r < 0.66:
                comments[idx] += '.' * random.randint(1, 50)
    return comments


def comment_mixer(comments, y):
    comments_pgr = comments[y == 1]

    for idx, c in enumerate(comments):
        if y[idx] == 0 and random.random() < 0.1:
            i = random.randint(0, comments_pgr.shape[0] - 1)
            len_to_add = -1 * min(len(comments_pgr[i]), 20)
            comments[idx] += ' ' + comments_pgr[i][len_to_add:]

    return comments


def test(model_file_path, weight_file_path, x_test, y_test, threshold=0.5):

    loaded_model = load_model(model_file_path, weight_file_path)
    loaded_model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['mae'])

    prediction = loaded_model.predict(x_test, verbose=1)
    diff = np.sum(np.abs(prediction - y_test.reshape(prediction.shape)), axis=1)
    wrong = diff >= threshold

    return wrong, prediction


def play(model_file_path, weight_file_path):

    loaded_model = load_model(model_file_path, weight_file_path)
    loaded_model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['mae'])
    loaded_model.summary()

    while True:
        comment = input('메시지를 입력하세요.\n')
        if comment == 'quit':
            break

        x = preprocess_comments(np.array([comment]))

        prediction = loaded_model.predict(x, verbose=0)

        print('%.2f%%' % (max(0, min(1, prediction[0][0])) * 100))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('python comment_learner learn [options]')
        print('python comment_learner test [options]')
        exit()

    if sys.argv[1] == 'learn':
        learn(train_dir='/media/kikim/Data/data/chatcheck', test_dir='/media/kikim/Data/data/chatcheck',
              count=1024, test_count=128, max_iter=1000, epochs=5, max_review_length=256)

    elif sys.argv[1] == 'test':
        count_test = 1024
        max_review_length = 128
        comments, y_test,  = load_data(count=count_test, dir_path='/media/kikim/Data/data/chatcheck/test')
        x_test = preprocess_comments(comments, max_review_length=max_review_length)

        is_wrong, pred = test('./model_20170626_005027.json', './weights_20170626_005027.h5', x_test, y_test, threshold=0.5)

        print('Accuracy: %.2f%%' % (100 - np.sum(is_wrong) / count_test * 100))
        for i in enumerate(is_wrong):
            if is_wrong[i]:
                print('%f %f %s' % (y_test[i][0], pred[i][0], comments[i][0]))

    elif sys.argv[1] == 'play':
        # play('./model_20170625_132026.json', './weights_20170625_132026.h5')
        play('./model_20170625_212948.json', './weights_20170625_212948.h5')
        # play('./model_20170626_005027.json', './weights_20170626_005027.h5')

    elif sys.argv[1] == 'transfer1':
        model = load_model('./model_20170625_132026.json', './weights_20170625_132026.h5')
        learn(model=model, train_dir='/media/kikim/Data/data/chatcheck', test_dir='/media/kikim/Data/data/chatcheck',
              count=1024, test_count=128, max_iter=20, epochs=5, max_review_length=128, data_modifier=comment_modifier)

    elif sys.argv[1] == 'transfer2':
        model = load_model('./model_20170625_212948.json', './weights_20170625_212948.h5')
        learn(model=model, train_dir='/media/kikim/Data/data/chatcheck', test_dir='/media/kikim/Data/data/chatcheck',
              count=1024, test_count=128, max_iter=20, epochs=5, max_review_length=128, data_modifier=comment_mixer)
