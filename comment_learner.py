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

    comments_pgr = comment_loader.load_comments(count=count//2, dir_path=dir_path, file_filter=r'.+pgr.+\.txt')
    comments_ilbe = comment_loader.load_comments(count=count//2, dir_path=dir_path, file_filter=r'.+ilbe.+\.txt')

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
    model.add(Dense(2, activation='softmax'))

    learning_rate = 0.001
    adam = Adam(lr=learning_rate)
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    model_json = model.to_json()
    with open('model_%s.json' % timestamp, 'w') as json_file:
        json_file.write(model_json)

    weight_file = './weights-%s.h5' % timestamp
    checkpoint = ModelCheckpoint(weight_file, monitor='loss', verbose=1, save_best_only=True, mode='min')
    callback_list = [checkpoint]

    for i in range(200):
        print('################# Iteration: %d' % i)

        comments_train, y_train = load(count, dir_path=train_dir)
        comments_test, y_test = load(test_count, dir_path=test_dir)

        x_train = preprocess_comments(comments_train, max_review_length)
        x_test = preprocess_comments(comments_test, max_review_length)

        y_train = np_utils.to_categorical(y_train)
        y_test = np_utils.to_categorical(y_test)

        model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=epochs, batch_size=16, callbacks=callback_list, verbose=2)

        # model.save_weights('model_%s.h5' % timestamp)
        K.set_value(adam.lr, learning_rate / (epochs * (i + 1)))

    scores = model.evaluate(x_test, y_test, verbose=0)
    print('Accuracy %f' % scores[1])


def test(model_file_path, weight_file_path, x_test, y_test):
    json_file = open(model_file_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    loaded_model.load_weights(weight_file_path)

    loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    score = loaded_model.evaluate(x_test, y_test)
    print('\n%s: %.2f%%' % (loaded_model.metrics_names[1], score[1] * 100))

    prediction = loaded_model.predict(x_test, verbose=1)
    idx = np.argmax(prediction, axis=1)
    diff = np.sum(np.abs(prediction - y_test), axis=1)
    wrong = diff >= 1

    x_wrong = x_test[wrong]
    comments_wrong = comment_loader.restore_char(x_wrong, comment_loader.std_char_list)

    print(prediction[:5, :])
    print(y_test[:5, :])
    print(diff[:5])
    print(wrong[:5])
    print(np.mean(wrong))
    print(comments_wrong[:5])

    return wrong


def play(model_file_path, weight_file_path):
    json_file = open(model_file_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    loaded_model.load_weights(weight_file_path)

    loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    loaded_model.summary()

    while True:
        comment = input('메시지를 입력하세요.\n')
        if comment == 'quit':
            break

        x = preprocess_comments(np.array([comment]))

        prediction = loaded_model.predict(x, verbose=0)

        print('%.2f%%' % (prediction[0][1] * 100))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('python comment_learner learn [options]')
        print('python comment_learner test [options]')
        exit()

    if sys.argv[1] == 'learn':
        learn(train_dir='/media/kikim/Data/data/chatcheck', test_dir='/media/kikim/Data/data/chatcheck', count=1024, test_count=1024, epochs=5)

    elif sys.argv[1] == 'test':
        x_test, y_test, comments = load(1024, dir_path='/media/kikim/Data/data/chatcheck')

        x_test = comment_loader.convert_charidx_to_onehot(x_test)

        max_review_length = 100
        x_test = sequence.pad_sequences(x_test, maxlen=max_review_length)
        y_test = np_utils.to_categorical(y_test)
        is_wrong = test('./model_20170622_120942.json', 'model_20170622_120942.h5', x_test, y_test)

        print(comments[is_wrong])
    elif sys.argv[1] == 'play':
        play('./model_20170622_120942.json', './model_20170622_120942.h5')