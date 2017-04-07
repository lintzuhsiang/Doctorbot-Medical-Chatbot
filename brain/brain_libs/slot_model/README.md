# train_model.SlotFilling

## Usage:
### Decoding mode:
`python3 train_model.py`

**Or**
### Run slot model example:
`python3 example.py`

#### Sample input:
請問青光眼看哪科

#### Sample output:
division :
doctor :
time :
disease :  青光眼

### Training mode:
Reverse the comment mark in line 22[3-4].
`python3 train_model.py`

### Prerequisites:
Tensorflow, Keras, jieba

### Toy data:
Uncomment line 11[1-5] in train_model.py to apply toy data
