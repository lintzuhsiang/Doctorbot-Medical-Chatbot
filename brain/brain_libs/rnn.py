import numpy as np
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import SimpleRNN, LSTM, Activation, Dense
from keras.optimizers import Adam
import gc

TIME_STEPS = 15
INPUT_SIZE = 10
BATCH_SIZE = 50
BATCH_INDEX = 0
OUTPUT_SIZE = 10
CELL_SIZE = 50
LR = 0.001

xm = np.array([])
one_hot_x = np.zeros(10)
one_hot_x[0] = 1
for i in range(100):
    xs = np.array([])
    for j in range(15):
        xs = np.append(xs, one_hot_x)
    xm = np.append(xm, xs)
xm = xm.reshape(100, 15, 10)
X_train = xm
X_test = xm

ym = np.array([])
one_hot_y = np.zeros(10)
one_hot_y[0] = 1
for i in range(100):
    ym = np.append(ym, one_hot_y)
ym = ym.reshape(100, 10)
y_train = ym
y_test = ym

# build RNN model
model = Sequential()

# RNN cell
model.add(SimpleRNN(
    # for batch_input_shape, if using tensorflow as the backend, we have to put None for the batch_size.
    # Otherwise, model.evaluate() will get error.
    # Or: input_dim=INPUT_SIZE, input_length=TIME_STEPS,
    batch_input_shape=(None, TIME_STEPS, INPUT_SIZE),
    output_dim=CELL_SIZE,
    unroll=True,
))

# output layer
model.add(Dense(OUTPUT_SIZE))
model.add(Activation('softmax'))

# optimizer
adam = Adam(LR)
model.compile(optimizer=adam,
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# training
for step in range(4001):
    X_batch = X_train[BATCH_INDEX: BATCH_INDEX + BATCH_SIZE, :, :]
    Y_batch = y_train[BATCH_INDEX: BATCH_INDEX + BATCH_SIZE, :]
    cost = model.train_on_batch(X_batch, Y_batch)
    BATCH_INDEX += BATCH_SIZE
    BATCH_INDEX = 0 if BATCH_INDEX >= X_train.shape[0] else BATCH_INDEX

    if step % 50 == 0:
        cost, accuracy = model.evaluate(
            X_test, y_test, batch_size=y_test.shape[0], verbose=False)
        print('test cost: ', cost, 'test accuracy: ', accuracy)

gc.collect()
