import os, sys, random
import numpy as np

import keras


# %%
class DataGenerator(object):
    def __init__(self, param):
        self.index_path = param['index']
        self.test_rate = param['test']
        self.number_classes = param['num_classes']
        index_file = open(self.index_path)
        lines = index_file.readlines()
        index_file.close()

        self.labels = []
        self.feature_paths = []

        for line in lines:
            label = int(line[:4])
            data_pos = line[4:-1]

            self.labels.append(label)
            self.feature_paths.append(data_pos)
            print(label, data_pos)

        self.labels = np.asarray(self.labels)
        self.labels = keras.utils.np_utils.to_categorical(self.labels, self.number_classes)

        self.number_train = int(len(self.labels) * (1 - self.test_rate))
        index = [n for n in range(len(self.labels))]
        random.shuffle(index)
        self.train_index, self.test_index = index[:self.number_train], index[self.number_train:]

        self.train_labels, self.train_features = [], []
        for index in self.train_index:
            self.train_labels.append(self.labels[index])
            self.train_features.append(np.load(self.feature_paths[index]))

        self.test_labels, self.test_features = [], []
        for index in self.test_index:
            self.test_labels.append(self.labels[index])
            self.test_features.append(np.load(self.feature_paths[index]))

        self.feature_shape = self.test_features[0].shape

        self.train_labels, self.train_features = np.asarray(self.train_labels), np.asarray(self.train_features)
        self.test_labels, self.test_features = np.asarray(self.test_labels), np.asarray(self.test_features)

    def genTrainBatch(self, batch_size):
        while True:
            batch_index = [n for n in range(len(self.train_features))]
            random.shuffle(batch_index)
            batch_index = batch_index[:batch_size]

            shape = (batch_size, *self.feature_shape)
            batch = np.zeros(shape, dtype='float32')

            label_batch = np.zeros((batch_size, self.number_classes), np.int)
            for i in range(batch_size):
                batch[i][:][:][:][:] = self.train_features[batch_index[i]]
                label_batch[i][:] = self.train_labels[batch_index[i]]

            yield batch, label_batch

    def genTestBatch(self, batch_size):
        while True:
            batch_index = [n for n in range(len(self.test_features))]
            random.shuffle(batch_index)
            batch_index = batch_index[:batch_size]

            shape = (batch_size, *self.feature_shape)
            batch = np.zeros(shape, dtype='float32')

            label_batch = np.zeros((batch_size, self.number_classes), np.int)
            for i in range(batch_size):
                batch[i][:][:][:][:] = self.test_features[batch_index[i]]
                label_batch[i][:] = self.test_labels[batch_index[i]]

            yield batch, label_batch
