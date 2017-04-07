from keras_rnn import KerasRnn
#from syntax_analysis import SyntaxAnalysis
import numpy as np

class IntentClassfication(object):
	def __init__(self):
		pass

	def generate_data(self):
		pass

	def train(self):

		############################################################
		#						 Loading Data					   #
		############################################################


		fileName = "sentence_x.npy"
		sentence_x = np.load(fileName)
		sentence_x = sentence_x.astype('float32')
		sentence_x = sentence_x.reshape([-1, 15, 1468])
		
		print("Load finished.")
		
		############################################################
		#		 Build label (aka the answer or the intent)		   #
		############################################################

		fileName = "sentence_y.npy"
		sentence_y = np.load(fileName)
		sentence_y = sentence_y.astype('float32')
		sentence_y = sentence_y.reshape([-1, 6])
		print("X Data shape: ", sentence_x.shape)
		print("Y Data shape: ", sentence_y.shape)

		############################################################
		#			 Create model and Start training			   #
		############################################################
		sentence_data = (sentence_x, sentence_y)
		time_steps = 15
		input_size = 1467 + 1
		batch_size = 300
		output_size = 6
		cell_size = 100
		lr = 0.01
		kr = KerasRnn(TIME_STEPS=time_steps, INPUT_SIZE=input_size, BATCH_SIZE=batch_size,
					  OUTPUT_SIZE=output_size, CELL_SIZE=cell_size, LR=lr, data=sentence_data)
		kr.train_model()
		kr.predict()

def main():
	ic = IntentClassfication()
	ic.train()


if __name__ == '__main__':
	main()
