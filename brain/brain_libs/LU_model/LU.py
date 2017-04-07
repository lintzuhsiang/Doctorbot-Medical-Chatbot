import tensorflow as tf
import data_helper
import jieba
import os

from generate_vector import generate_vector
import numpy as np
import json
from keras.models import load_model
from keras.models import model_from_json

if not os.path.exists("data"):
    os.makedirs("data")

loaded_model = load_model('intent_model.h5')

sentence_file = "data/training_sentence.txt"
slot_file = "data/training_slot.txt"
sentence_training_file = "data/sentence_training.txt"
sentence_developing_file = "data/sentence_developing.txt"
slot_training_file = "data/slot_training.txt"
slot_developing_file = "data/slot_developing.txt"

model_file = 'model/GRU_model_1.h5'


class IntentPredict(object):
    def get_intent(self, sentence):
        gv = generate_vector()
        sentences, maxsize = gv.segment_words(sentence)
        # print("senteces size: {}".format(np.shape(sentences)))

        with open('dict_one_hot_word.txt', 'r', encoding='utf-8') as f:
            dict_one_hot_word = json.load(f)

        one_hot_words = gv.one_hot_encode(1467, sentences, maxsize, dict_one_hot_word)
        # print(one_hot_words.shape)
        one_hot_words = one_hot_words.reshape(-1, 15, 1468)

        # print('intent is {}'.format(loaded_model.predict_classes(one_hot_words)))
        return loaded_model.predict_classes(one_hot_words)[0].item()


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


    def decode(self, sentence):
        # Dictionaries
        w2id_sentence, id2w_sentence = data_helper.initialize_vocabulary(self.vocab_sentence)
        w2id_slot, id2w_slot = data_helper.initialize_vocabulary(self.vocab_slot)

        jieba.load_userdict("../data_resource/doctor_dict.txt")
        jieba.load_userdict("../data_resource/disease_dict.txt")
        jieba.load_userdict("../data_resource/division_dict.txt")
        jieba.load_userdict("../data_resource/week_dict.txt")
        jieba.load_userdict("../data_resource/other_dict.txt")

        model = load_model(model_file)

        # Decode from standard input.
        seg_gen = list(jieba.cut(sentence, cut_all=False))
        # print("/".join(jieba.cut(sentence, cut_all=False)))
        _sentence = " ".join(seg_gen)
        # Get token-ids for the input sentence.
        token_ids = data_helper.sentence_to_token_ids(
        tf.compat.as_bytes(_sentence), w2id_sentence)
        # print(token_ids)
        # Add GO symbol at the end of sentence
        if data_helper.GO_ID not in token_ids:
            token_ids.append(data_helper.GO_ID)
        pred = model.predict_on_batch(np.array(token_ids)[np.newaxis, :])
        _pred = np.argmax(pred,-1)[0].tolist()
        # If there is an EOS symbol in outputs, cut them at that point.
        if data_helper.EOS_ID in _pred:
            _pred = _pred[:_pred.index(data_helper.EOS_ID)]
        slot_list = [tf.compat.as_str(id2w_slot[slot_pred]) for slot_pred in _pred]
        # print("/".join(slot_list))
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
        slot_dictionary = SlotFilling().decode(sentence)
        for slot, value in slot_dictionary.items():
            print(slot, ": ", value)
        intent_index = IntentPredict().get_intent(sentence)
        intents = ['greeting', 'search_symptom', 'search_division', 'search_doctor', 'search_timetable', 'register']
        print('intent： ' + intents[intent_index])

if __name__ == '__main__':
    main()
