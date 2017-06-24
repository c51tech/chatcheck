import numpy as np
import datetime
import sys
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
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


def load(count, dir_path='.'):

    comments_pgr = comment_loader.load_comments(count=count//2, dir_path=dir_path, file_filter=r'.+pgr.+\.txt', count_per_file=count//16)
    comments_ilbe = comment_loader.load_comments(count=count//2, dir_path=dir_path, file_filter=r'.+ilbe.+\.txt', count_per_file=count//16)

    comments = np.concatenate((comments_pgr, comments_ilbe), axis=0)

    y_pgr = np.ones(comments_pgr.shape)
    y_ilbe = np.zeros(comments_ilbe.shape)

    y = np.concatenate((y_pgr, y_ilbe))

    idx_shuffle = np.random.permutation(count)

    comments = comments[idx_shuffle]
    y = y[idx_shuffle]

    return comments, y


def preprocess_comments(comments, max_review_length=100):
    x = comment_loader.convert_comments_to_charidx(comments, char2idx)
    x = comment_loader.convert_charidx_to_onehot(x)
    x = sequence.pad_sequences(x, maxlen=max_review_length)

    return x


def learn(train_dir='.', test_dir='.', count=1024, test_count=1024, epochs=10, max_review_length=100):

    model = Sequential()
    model.add(LSTM(128, input_shape=(max_review_length, len(char2idx) + 1)))
    model.add(Dense(1, activation='linear'))

    learning_rate = 0.001
    adam = Adam(lr=learning_rate)
    model.compile(loss='mean_squared_error', optimizer=adam, metrics=['mae'])

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    model_json = model.to_json()
    with open('model_%s.json' % timestamp, 'w') as json_file:
        json_file.write(model_json)

    weight_file = './weights_%s.h5' % timestamp
    checkpoint = ModelCheckpoint(weight_file, monitor='loss', verbose=1, save_best_only=True, mode='min')
    callback_list = [checkpoint]

    for i in range(200):
        print('################# Iteration: %d' % i)

        comments_train, y_train = load(count, dir_path=train_dir)
        comments_test, y_test = load(test_count, dir_path=test_dir)

        x_train = preprocess_comments(comments_train, max_review_length)
        x_test = preprocess_comments(comments_test, max_review_length)

        # y_train = np_utils.to_categorical(y_train)
        # y_test = np_utils.to_categorical(y_test)

        model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=epochs, batch_size=16, callbacks=callback_list, verbose=2)

        # model.save_weights('model_%s.h5' % timestamp)
        K.set_value(adam.lr, learning_rate / (epochs * (i + 1)))

    scores = model.evaluate(x_test, y_test, verbose=0)
    print('Accuracy %f' % scores[1])


def test(model_file_path, weight_file_path, x_test, y_test, threshold=0.5):
    json_file = open(model_file_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    loaded_model.load_weights(weight_file_path)

    loaded_model.summary()

    loaded_model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['mae'])

    # score = loaded_model.evaluate(x_test, y_test)
    # print('\n%s: %.2f%%' % (loaded_model.metrics_names[1], score[1] * 100))

    prediction = loaded_model.predict(x_test, verbose=1)
    print(prediction.shape)
    print(prediction[:5, :])
    print(prediction[0, 0])
    diff = np.sum(np.abs(prediction - y_test.reshape(prediction.shape)), axis=1)
    wrong = diff >= threshold
    print(wrong.shape)
    return wrong, prediction


def play(model_file_path, weight_file_path):
    json_file = open(model_file_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    loaded_model.load_weights(weight_file_path)

    loaded_model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['mae'])
    loaded_model.summary()

    while True:
        comment = input('메시지를 입력하세요.\n')
        if comment == 'quit':
            break

        x = preprocess_comments(np.array([comment]))

        prediction = loaded_model.predict(x, verbose=0)

        print('%.2f%%' % (prediction[0][0] * 100))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('python comment_learner learn [options]')
        print('python comment_learner test [options]')
        exit()

    if sys.argv[1] == 'learn':
        learn(train_dir='/media/kikim/Data/data/chatcheck', test_dir='/media/kikim/Data/data/chatcheck',
              count=1024, test_count=128, epochs=5, max_review_length=128)

    elif sys.argv[1] == 'test':
        count_test = 1024
        max_review_length = 128
        comments, y_test,  = load(count=count_test, dir_path='/media/kikim/Data/data/chatcheck/test')
        x_test = preprocess_comments(comments, max_review_length=max_review_length)

        is_wrong, pred = test('./model_20170624_193321.json', 'weights-20170624_193321.h5', x_test, y_test, threshold=0.5)

        print('Accuracy: %.2f%%' % (100 - np.sum(is_wrong) / count_test * 100))
        for i in enumerate(is_wrong):
            if is_wrong[i]:
                print('%f %f %s' % (y_test[i][0], pred[i][0], comments[i][0]))

    elif sys.argv[1] == 'play':
        play('./model_20170624_193321.json', './weights-20170624_193321.h5')