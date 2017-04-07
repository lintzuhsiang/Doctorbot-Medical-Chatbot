import tensorflow as tf
import data_helper
import numpy as np
import jieba
import os
import re
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

    def get_slot(self, sentence):
        # Dictionaries
        w2id_sentence, id2w_sentence = data_helper.initialize_vocabulary(self.vocab_sentence)
        w2id_slot, id2w_slot = data_helper.initialize_vocabulary(self.vocab_slot)

        jieba.load_userdict("../data_resource/doctor_dict.txt")
        jieba.load_userdict("../data_resource/disease_dict.txt")
        jieba.load_userdict("../data_resource/division_dict.txt")
        jieba.load_userdict("../data_resource/week_dict.txt")
        jieba.load_userdict("../data_resource/other_dict.txt")

        model = load_model(model_file)

        _WORD_FILTER = re.compile("([.,!?\"':;)(])")
        sentence = _WORD_FILTER.sub('', sentence)
        if not sentence.isalpha():
            return ("sentence should be words!")
        seg_gen = list(jieba.cut(sentence, cut_all=False))
        _sentence = " ".join(seg_gen)
        # Get token-ids for the input sentence.
        token_ids = data_helper.sentence_to_token_ids(tf.compat.as_bytes(_sentence), w2id_sentence)
        # Add GO symbol at the end of sentence
        if data_helper.GO_ID not in token_ids:
            token_ids.append(data_helper.GO_ID)
        pred = model.predict_on_batch(np.array(token_ids)[np.newaxis, :])
        _pred = np.argmax(pred,-1)[0].tolist()
        # If there is an EOS symbol in outputs, cut them at that point.
        if data_helper.EOS_ID in _pred:
            _pred = _pred[:_pred.index(data_helper.EOS_ID)]
        slot_list = [tf.compat.as_str(id2w_slot[slot_pred]) for slot_pred in _pred]

        slot_dictionary = {'disease': '', 'division': '', 'doctor': '', 'time': ''}
        for index, item in enumerate(slot_list):
            if item == 'b-disease':
                slot_dictionary['disease'] = seg_gen[index]
            elif item == 'b-division':
                slot_dictionary['division'] = seg_gen[index]
            elif item == 'b-doctor':
                slot_dictionary['doctor'] = seg_gen[index]
            elif item == 'b-time':
                slot_dictionary['time'] = seg_gen[index]
        return slot_dictionary


def main():
    while True:
        sentence = input('your sentence: ')
        slot_dictionary = SlotFilling().get_slot(sentence)
        for slot, value in slot_dictionary.items():
            print(slot, ": ", value)

if __name__ == '__main__':
    main()
