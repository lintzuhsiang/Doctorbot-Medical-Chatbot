import jieba
import numpy as np
jieba.load_userdict("../LU_model/doctorbot_dict.txt")
import multiprocessing
from collections import OrderedDict
class generate_vector(object):
    def __init__(self):
        pass

    def segment_words(self, sentence):
        stop_words = [' ', '\n']
        sentences = []

        for word in jieba.cut(sentence):
            if word not in stop_words:
                sentences.append(word)

        maxsize = 15
        return sentences, maxsize

    def one_hot_encode(self, length, sentences, maxsize, dict_one_hot_word):
        one_hot_words = np.array([])
        #for sentence_words in sentences:
        temp = np.array([])

        for s_word in sentences:
            if s_word in dict_one_hot_word.keys():
                temp = np.append(temp, np.array(dict_one_hot_word.get(s_word)))
            else:
                one_hot_word = np.zeros(length + 1)
                one_hot_word[-1] = 1
                temp = np.append(temp, one_hot_word)
        for i in range(maxsize - len(sentences)):
            one_hot_word = np.zeros(length + 1)
            temp = np.append(temp, one_hot_word)

        one_hot_words = np.append(one_hot_words, temp)

        #ne_hot_words = np.reshape(one_hot_words, (len(sentences), maxsize, (len(corpus_list)+1)))
        return one_hot_words


