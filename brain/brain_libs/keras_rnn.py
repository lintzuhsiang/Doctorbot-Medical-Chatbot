import numpy as np
import gc
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import SimpleRNN, LSTM, Activation, Dense
from keras.optimizers import Adam


class KerasRnn(object):
    def __init__(self, TIME_STEPS, INPUT_SIZE, BATCH_SIZE, OUTPUT_SIZE, CELL_SIZE, LR, data):
        self.TIME_STEPS = TIME_STEPS
        self.INPUT_SIZE = INPUT_SIZE
        self.BATCH_SIZE = BATCH_SIZE
        self.OUTPUT_SIZE = OUTPUT_SIZE
        self.CELL_SIZE = CELL_SIZE
        self.LR = LR
        self.BATCH_INDEX = 0
        self.data = data
        # TIME_STEPS = 15 # INPUT_SIZE = 10 # BATCH_SIZE = 50
        # OUTPUT_SIZE = 10 # CELL_SIZE = 50 # LR = 0.001
        # BATCH_INDEX = 0

    def generate_X(self, data):
        X_train = np.array([])
        for x in data:
            X_train = np.append(X_train, x[0])
        X_train = X_train.reshape(1000, 40, self.INPUT_SIZE)
        X_test = X_train
        return X_train, X_test

    def generate_y(self, data):
        y_train = np.array([])
        for y in data:
            y_train = np.append(y_train, y[1])
        y_train = y_train.reshape(1000, self.OUTPUT_SIZE)
        y_test = y_train
        return y_train, y_test

    def train_model(self):
        X_train, X_test = self.generate_X(self.data)
        y_train, y_test = self.generate_y(self.data)

        # build RNN model
        model = Sequential()

        # RNN cell
        model.add(LSTM(
            # for batch_input_shape, if using tensorflow as the backend, we have to put None for the batch_size.
            # Otherwise, model.evaluate() will get error.
            # Or: input_dim=INPUT_SIZE, input_length=TIME_STEPS,
            batch_input_shape=(None, self.TIME_STEPS, self.INPUT_SIZE),
            output_dim=self.CELL_SIZE,
            unroll=True,
        ))

        # output layer
        model.add(Dense(self.OUTPUT_SIZE))
        model.add(Activation('softmax'))

        # optimizer
        adam = Adam(self.LR)
        model.compile(optimizer=adam,
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        # training
        for step in range(4000):
            X_batch = X_train[self.BATCH_INDEX: self.BATCH_INDEX + self.BATCH_SIZE, :, :]
            Y_batch = y_train[self.BATCH_INDEX: self.BATCH_INDEX + self.BATCH_SIZE, :]
            cost = model.train_on_batch(X_batch, Y_batch)
            self.BATCH_INDEX += self.BATCH_SIZE
            self.BATCH_INDEX = 0 if self.BATCH_INDEX >= X_train.shape[0] else self.BATCH_INDEX

            if step % 50 == 0:
                cost, accuracy = model.evaluate(
                    X_test, y_test, batch_size=y_test.shape[0], verbose=False)
                print('test cost: ', cost, 'test accuracy: ', accuracy)

        gc.collect()


# def main():
#     kn = KerasRnn(15, 10, 50, 10, 50, 0.001)
#     kn.train_model()


# if __name__ == '__main__':
#     main()
