# fix bug
# from tensorflow.compat.v1 import ConfigProto
# from tensorflow.compat.v1 import InteractiveSession

# config = ConfigProto()
# config.gpu_options.allow_growth = True
# config.gpu_options.per_process_gpu_memory_fraction = 0.8
# session = InteractiveSession(config=config)

import numpy as np
import jieba
import os
import re
import json
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Flatten, Embedding, Dense, SimpleRNN, LSTM, GRU

embedding_path = '/home/zhiyong/server/data/NLP/merge_sgns_bigram_char300.txt'

comments_path = '/home/zhiyong/server/data/DataBase_BackUp/MongoDB/comment_infos.json'

embedding_dic = {}
embedding_dim = 300
maxlen = 1000
max_words = 30000
word_index = []


def init_data(texts, labels):
    with open(comments_path, encoding='UTF-8') as f:
        index = 0
        for line in f:
            dic = json.loads(line)
            comment = dic['brief_comment']
            stars = dic['comment_rating_stars']
            comment = illegal_char(comment)
            comment = comment.replace('\n', '')
            seg_list = jieba.lcut(cleanhtml(comment))
            texts.append(seg_list)
            stars = int(stars)
            if stars >= 3:
                labels.append(1)
            else:
                labels.append(0)
            # index += 1
            # if index >= 10000:
            #     break


def preprocess_data(texts, labels):
    total_samples = len(labels)
    training_samples = int(total_samples * 0.7)
    validation_samples = int(total_samples * 0.3)

    tokenizer = Tokenizer(num_words=max_words, lower=False)
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)

    word_index = tokenizer.word_index
    print('Found %s unique tokens.' % len(word_index))

    data = pad_sequences(sequences, maxlen=maxlen)
    labels = np.asarray(labels)
    print('Shape of data tensor:', data.shape)
    print('Shape of label tensor:', labels.shape)

    indices = np.arange(data.shape[0])
    np.random.shuffle(indices)
    data = data[indices]
    labels = labels[indices]
    x_train = data[:training_samples]
    y_train = labels[:training_samples]
    x_val = data[training_samples: training_samples + validation_samples]
    y_val = labels[training_samples: training_samples + validation_samples]

    embedding_matrix = np.zeros((max_words, embedding_dim))
    for word, i in word_index.items():
        if i < max_words:
            embedding_vector = embedding_dic.get(word)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector

    return (x_train, y_train), (x_val, y_val), embedding_matrix


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


def illegal_char(s):
    s = re \
        .compile( \
        u"[^"
        u"\u4e00-\u9fa5"  # 判断 中文
        u"\u0041-\u005A"  # 判断 A-Z
        u"\u0061-\u007A"  # 判断 a-z
        # u"\u0030-\u0039"
        u"\u3002\uFF1F\uFF01"  # 中文标点符号 。？！
        u"\n"
        # u"\uFF0C\u3001\uFF1B\uFF1A\u300C\u300D\u300E\u300F\u2018\u2019\u201C\u201D\uFF08\uFF09\u3014\u3015\u3010\u3011\u2014\u2026\u2013\uFF0E\u300A\u300B\u3008\u3009"
        # u"\!\@\#\$\%\^\&\*\(\)\-\=\[\]\{\}\\\|\;\'\:\"\,\.\/\<\>\?\/\*\+"
        u"]+"
    ) \
        .sub('', s)
    s = re.compile(u"[\u3002\uFF1F\uFF01]+").sub('\n', s)  # 应该是断句用
    s = re.compile(u"\n+").sub('\n', s)
    return s


def init_embedding_dic():
    lines_num, dim = 0, 0
    with open(embedding_path, encoding='UTF-8') as f:
        first_line = True
        for line in f:
            if first_line:
                first_line = False
                dim = int(line.rstrip().split()[1])
                print(dim)
                continue
            lines_num += 1
            tokens = line.rstrip().split(' ')
            embedding_dic[tokens[0]] = np.asarray([float(x) for x in tokens[1:]])


if __name__ == '__main__':
    texts = []
    labels = []
    init_embedding_dic()
    init_data(texts, labels)
    (x_train, y_train), (x_val, y_val), embedding_matrix = preprocess_data(texts, labels)
    print('x_train.shape: ', x_train.shape)
    print('y_train.shape: ', y_train.shape)
    print('x_val.shape: ', x_val.shape)
    print('y_val.shape: ', y_val.shape)
    print('embedding_matrix.shape: ', embedding_matrix.shape)

    model = Sequential()
    model.add(Embedding(max_words, embedding_dim, input_length=maxlen))
    model.add(LSTM(16, return_sequences=True))
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(64, return_sequences=True))
    model.add(LSTM(64))
    model.add(Dense(1, activation='sigmoid'))

    model.layers[0].set_weights([embedding_matrix])
    model.layers[0].trainable = False

    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['acc'])
    history = model.fit(x_train, y_train,
                        epochs=50,
                        batch_size=64,
                        validation_data=(x_val, y_val))
    model.save_weights('3_LSTM_all_data_model_e100.h5')
