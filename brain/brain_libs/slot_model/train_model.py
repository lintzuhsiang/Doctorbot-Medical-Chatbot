import sys
import tensorflow as tf
import data_helper
import numpy as np
import progressbar
import gc
import jieba
import os
import re

from keras.models import Sequential
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import SimpleRNN, GRU, LSTM
from keras.layers.core import Dense, Dropout
from keras.layers.wrappers import TimeDistributed
from keras.layers import Convolution1D
from keras.models import load_model

from metrics.accuracy import conlleval

if not os.path.exists("data"):
    os.makedirs("data")

sentence_file = "data/training_sentence.txt"
slot_file = "data/training_slot.txt"
sentence_training_file = "data/sentence_training.txt"
sentence_developing_file = "data/sentence_developing.txt"
slot_training_file = "data/slot_training.txt"
slot_developing_file = "data/slot_developing.txt"

model_file = 'model/GRU_model_1.h5'

class SlotFilling(object):
    def __init__(self):
        # Prepare data
        (self.sentence_train,
        self.slot_train,
        self.sentence_dev,
        self.slot_dev,
        self.vocab_sentence,
        self.vocab_slot) = data_helper.prepare_data(
            "data",
            sentence_training_file,
            slot_training_file,
            sentence_developing_file,
            slot_developing_file,
            from_vocabulary_size=2000,
            to_vocabulary_size=2000,
            tokenizer=None)


    def decode(self, sentence=None):
        # Dictionaries
        w2id_sentence, id2w_sentence = data_helper.initialize_vocabulary(self.vocab_sentence)
        w2id_slot, id2w_slot = data_helper.initialize_vocabulary(self.vocab_slot)

        jieba.load_userdict("../data_resource/doctor_dict.txt")
        jieba.load_userdict("../data_resource/disease_dict.txt")
        jieba.load_userdict("../data_resource/division_dict.txt")
        jieba.load_userdict("../data_resource/week_dict.txt")
        jieba.load_userdict("../data_resource/other_dict.txt")

        model = load_model(model_file)

        if sentence == None:
            # Decode from standard input.
            sys.stdout.write("> ")
            sys.stdout.flush()
            sentence = sys.stdin.readline()
            while sentence:
                seg_gen = jieba.cut(sentence, cut_all=False)
                _sentence = " ".join(seg_gen)
                # Get token-ids for the input sentence.
                token_ids = data_helper.sentence_to_token_ids(
                    tf.compat.as_bytes(_sentence), w2id_sentence)
                print(token_ids)
                # Add GO symbol at the end of sentence
                if data_helper.GO_ID not in token_ids:
                    token_ids.append(data_helper.GO_ID)
                pred = model.predict_on_batch(np.array(token_ids)[np.newaxis,:])
                _pred = np.argmax(pred,-1)[0].tolist()
                # If there is an EOS symbol in outputs, cut them at that point.
                if data_helper.EOS_ID in _pred:
                    _pred = _pred[:_pred.index(data_helper.EOS_ID)]
                print(" ".join([tf.compat.as_str(id2w_slot[slot_pred]) for slot_pred in _pred]))
                print("> ", end="")
                sys.stdout.flush()
                sentence = sys.stdin.readline()

        else:
            _WORD_FILTER = re.compile("([.,!?\"':;)(])")
            sentence = _WORD_FILTER.sub('', sentence)
            if not sentence.isalpha():
                return ("sentence should be words!")
            seg_gen = jieba.cut(sentence, cut_all=False)
            _sentence = " ".join(seg_gen)
            # Get token-ids for the input sentence.
            token_ids = data_helper.sentence_to_token_ids(
            tf.compat.as_bytes(_sentence), w2id_sentence)
            # Add GO symbol at the end of sentence
            if data_helper.GO_ID not in token_ids:
                token_ids.append(data_helper.GO_ID)
            pred = model.predict_on_batch(np.array(token_ids)[np.newaxis,:])
            _pred = np.argmax(pred,-1)[0].tolist()
            # If there is an EOS symbol in outputs, cut them at that point.
            if data_helper.EOS_ID in _pred:
                _pred = _pred[:_pred.index(data_helper.EOS_ID)]
            return " ".join([tf.compat.as_str(id2w_slot[slot_pred]) for slot_pred in _pred])


    def train(self):
        sentence_developing, slot_devloping = data_helper.read_data(
            self.sentence_dev, self.slot_dev, max_size=None)
        sentence_training, slot_training = data_helper.read_data(
            self.sentence_train, self.slot_train, max_size=None)

        # Make toy data; comment this block to train on the full dataset
        #n_toy = 1000
        #sentence_training, slot_training = sentence_training[:n_toy],\
        #    slot_training[:n_toy]
        #sentence_developing, slot_devloping = sentence_developing[:round(n_toy/2)],\
        #    slot_devloping[:round(n_toy/2)]

        # Dictionaries
        w2id_sentence, id2w_sentence = data_helper.initialize_vocabulary(self.vocab_sentence)
        w2id_slot, id2w_slot = data_helper.initialize_vocabulary(self.vocab_slot)

        # For conlleval script
        words_train = [list(map(lambda x: id2w_sentence[x].decode('utf8'), w)) for w in sentence_training]
        labels_train = [list(map(lambda x: id2w_slot[x].decode('utf8'), y)) for y in slot_training]
        words_val = [list(map(lambda x: id2w_sentence[x].decode('utf8'), w)) for w in sentence_developing]
        labels_val = [list(map(lambda x: id2w_slot[x].decode('utf8'), y)) for y in slot_devloping]

        # Define model
        n_vocab = len(w2id_sentence)
        n_classes = len(w2id_slot)

        model = Sequential()
        model.add(Embedding(n_vocab,100))
        model.add(Convolution1D(128, 5, border_mode='same', activation='relu'))
        model.add(Dropout(0.25))
        model.add(GRU(100,return_sequences=True))
        model.add(TimeDistributed(Dense(n_classes, activation='softmax')))
        model.compile('rmsprop', 'categorical_crossentropy')

        # Training
        #n_epochs = 30
        n_epochs = 1

        train_f_scores = []
        val_f_scores = []
        best_val_f1 = 0

        print("Training =>")
        train_pred_label = []
        avgLoss = 0

        for i in range(n_epochs):
            print("Training epoch {}".format(i))

            bar = progressbar.ProgressBar(max_value=len(sentence_training))
            for n_batch, sent in bar(enumerate(sentence_training)):
                label = slot_training[n_batch]
                # Make labels one hot
                label = np.eye(n_classes)[label][np.newaxis, :]
                # View each sentence as a batch
                sent = sent[np.newaxis, :]

                if sent.shape[1] > 1: #ignore 1 word sentences
                    loss = model.train_on_batch(sent, label)
                    avgLoss += loss

                pred = model.predict_on_batch(sent)
                pred = np.argmax(pred, -1)[0]
                train_pred_label.append(pred)

            avgLoss = avgLoss/n_batch

            predword_train = [list(map(lambda x: id2w_slot[x].decode('utf8'), y))
                              for y in train_pred_label]
            con_dict = conlleval(predword_train, labels_train,
                                 words_train, 'measure.txt')
            train_f_scores.append(con_dict['f1'])
            print('Loss = {}, Precision = {}, Recall = {}, F1 = {}'.format(
                avgLoss, con_dict['r'], con_dict['p'], con_dict['f1']))
            # Save model
            model.save(model_file)

            print("Validating =>")

            labels_pred_val = []
            avgLoss = 0

            bar = progressbar.ProgressBar(max_value=len(sentence_developing))
            for n_batch, sent in bar(enumerate(sentence_developing)):
                label = slot_devloping[n_batch]
                label = np.eye(n_classes)[label][np.newaxis, :]
                sent = sent[np.newaxis, :]

                if sent.shape[1] > 1: #some bug in keras
                    loss = model.test_on_batch(sent, label)
                    avgLoss += loss

                pred = model.predict_on_batch(sent)
                pred = np.argmax(pred, -1)[0]
                labels_pred_val.append(pred)

            avgLoss = avgLoss/n_batch

            predword_val = [list(map(lambda x: id2w_slot[x].decode('utf8'), y))
                            for y in labels_pred_val]
            con_dict = conlleval(predword_val, labels_val,
                                 words_val, 'measure.txt')
            val_f_scores.append(con_dict['f1'])
            print('Loss = {}, Precision = {}, Recall = {}, F1 = {}'.format(
                avgLoss, con_dict['r'], con_dict['p'], con_dict['f1']))

            if con_dict['f1'] > best_val_f1:
                best_val_f1 = con_dict['f1']
                with open('model_architecture.json', 'w') as outf:
                    outf.write(model.to_json())
                model.save_weights('best_model_weights.h5', overwrite=True)
                print("Best validation F1 score = {}".format(best_val_f1))
            print()

            # Prevent from tensorflow bugs: BaseSession.__del__
            gc.collect()


def main():
    sf = SlotFilling()
    #sf.train()
    sf.decode()


if __name__ == '__main__':
    main()
