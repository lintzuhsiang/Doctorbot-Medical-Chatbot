# LU_MODEL

## Usage:
### Get LU prediction in a cmd environment:
`python3 get_lu_pred.py` will get a cmd prompt for input sentence iteration.

### Get LU prediction as a object output:
	import get_lu_pred as lu
	model = lu.LuModel()
	intent, slot = model.get_lu_pred(sentence="星期四王德宏的門診時間")
	model.sess.close()  # Close tensorflow session

### Training model:
`python3 run_multi-task_rnn.py`  
Training data will be generated accordingly.

`python3 run_multi-task_rnn_test.py`  
With extremely few `max_training_steps` and applied training data for testing purpose.

Tokenized dataset will be generated if training-model scripts executed the first time.

### Prerequisites:
Tensorflow, jieba
