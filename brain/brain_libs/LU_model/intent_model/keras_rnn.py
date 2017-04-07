import numpy as np
import gc
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import SimpleRNN, LSTM, Activation, Dense
from keras.optimizers import Adam
from keras.models import model_from_json
import os


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
		X_train = data[0]
		X_train = X_train.reshape([None, self.TIME_STEPS, self.INPUT_SIZE])
		X_test = X_train
		return X_train, X_test

	def generate_y(self, data):
		#y_train = np.array([])
		#for y in data:
		#	y_train = np.append(y_train, y[1])
		y_train = data[1]
		y_train = y_train.reshape([None, self.OUTPUT_SIZE])
		y_test = y_train
		return y_train, y_test

	def getData(self):
		############################################################
		#					buile shffle data set 				   #
		############################################################
		# first get data size
		DataSize = self.data[0].shape[0]
		# build shuffle index					
		ShuffleDataIndexs = np.arange(DataSize)
		np.random.shuffle(ShuffleDataIndexs)	
		# get shuffle data
		X_Data = self.data[0].copy()
		X_Data = X_Data[ShuffleDataIndexs]
		Y_Data = self.data[1].copy()
		Y_Data = Y_Data[ShuffleDataIndexs]
		
		############################################################
		#	   spilt data into training set and testing set 	   #
		############################################################
		X_Train = X_Data[0:int(DataSize*0.7)]
		Y_Train = Y_Data[0:int(DataSize*0.7)]
		X_Test = X_Data[int(DataSize*0.7):]
		Y_Test = Y_Data[int(DataSize*0.7):]
		
		return [(X_Train, Y_Train), (X_Test, Y_Test)]
		
		
	
	def train_model(self):
		#X_train, X_test = self.generate_X(self.data)
		#y_train, y_test = self.generate_y(self.data)
		(X_train, y_train) , (X_test, y_test) = self.getData()
		#print(X_train.shape)
		#print(y_train.shape)
		
		
		# build RNN model
		model = Sequential()

		# RNN cell
		'''
		model.add(LSTM(
			# for batch_input_shape, if using tensorflow as the backend, we have to put None for the batch_size.
			# Otherwise, model.evaluate() will get error.
			# Or: input_dim=INPUT_SIZE, input_length=TIME_STEPS,
			batch_input_shape=(None, self.TIME_STEPS, self.INPUT_SIZE),
			output_dim=self.CELL_SIZE,
			unroll=True,
		))'''

		#model.add(LSTM(units=100, input_shape=(None,self.TIME_STEPS, self.INPUT_SIZE), output_dim = self.CELL_SIZE,unroll=True))
		model.add(LSTM(units=self.CELL_SIZE, input_shape=(self.TIME_STEPS, self.INPUT_SIZE), unroll=True))
		# output layer
		model.add(Dense(self.OUTPUT_SIZE))
		model.add(Activation('softmax'))

		# optimizer
		adam = Adam(self.LR)
		model.compile(optimizer=adam,
					  loss='categorical_crossentropy',
					  metrics=['accuracy'])

		# training
		# for step in range(6000):
			# X_batch = X_train[self.BATCH_INDEX: self.BATCH_INDEX + self.BATCH_SIZE, :, :]
			# Y_batch = y_train[self.BATCH_INDEX: self.BATCH_INDEX + self.BATCH_SIZE, :]
			# cost = model.train_on_batch(X_batch, Y_batch)
			# self.BATCH_INDEX += self.BATCH_SIZE
			# self.BATCH_INDEX = 0 if self.BATCH_INDEX >= X_train.shape[0] else self.BATCH_INDEX

			# if step % 300 == 0:
				# cost, accuracy = model.evaluate(
					# X_test, y_test, batch_size=y_test.shape[0], verbose=False)
				# print('test cost: ', cost, 'test accuracy: ', accuracy)
		print('Strat training...')
		model.fit(X_train, y_train, batch_size=self.BATCH_SIZE, epochs=10, validation_data=(X_test, y_test), shuffle=True)
		score, acc = model.evaluate(X_test, y_test, batch_size=self.BATCH_SIZE)
		print()
		print('Test score:', score)
		print('Test accuracy:', acc)
		#model.save("intent_model.h5")
		#gc.collect()
		
		# serialize model to JSON
		model_json = model.to_json()
		with open("model.json", "w") as json_file:
			json_file.write(model_json)
		# serialize weights to HDF5
		model.save_weights("model.h5")
		print("Saved model to file \'model.json\'")
		print("Saved weight to file \'model.h5\'")
		model.save("intent_model.h5")
		print("-----------------------------------------------")
		
	def predict(self):
		print("Use Saved model to predict:")
		# load json and create model
		modelFileName = "model.json"
		print("Loaded model from file \'{}\'".format(modelFileName))
		json_file = open(modelFileName, 'r')
		loaded_model_json = json_file.read()
		json_file.close()
		loaded_model = model_from_json(loaded_model_json)
		
		# load weights into new model
		weightFileName = "model.h5"
		print("Loaded weight from file \'{}\'".format(weightFileName))
		loaded_model.load_weights(weightFileName)
		 
		# load data
		(X_train, y_train) , (X_test, y_test) = self.getData()
		 
		# evaluate loaded model on test data
		adam = Adam(self.LR)
		loaded_model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
		score = loaded_model.evaluate(X_test, y_test, verbose=0)
		print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))

		
		
		# def main():
#	kn = KerasRnn(15, 10, 50, 10, 50, 0.001)
#	kn.train_model()


# if __name__ == '__main__':
#	 main()
