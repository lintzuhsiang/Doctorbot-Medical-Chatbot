import jieba
import numpy as np
jieba.load_userdict("data_resource/doctorbot_dict.txt")


class SyntaxAnalysis(object):
    def __init__(self):
        pass

    def segment_words(self, file_name):
        stop_words = [' ', '\n']
        sentences = []
        categories = []
        with open(file_name, 'r', encoding="utf-8") as file:
            for line in file:
                # print (line)
                line = line.split(",&")
                sentence = []
                for word in jieba.cut(line[0]):
                    if word not in stop_words:
                        sentence.append(word)
                categories.append(int(line[1]))
                sentences.append(sentence)
        # print (sentences)
        # print (categories)
        return sentences, categories

    def flat_sentences(self, sentences):
        words = [word for sentence in sentences for word in sentence]
        return words

    def generate_corpus(self, words):
        corpus_dict = {}
        corpus_list = []
        for word in words:
            if word in corpus_dict:
                corpus_dict[word] += 1
            else:
                corpus_dict[word] = 1
        # print(corpus_dict)

        for key, value in corpus_dict.items():
            corpus_list.append(key)
        # print (corpus_list)
        return corpus_list

    def one_hot_encode(self, corpus_list, sentence_words):
        one_hot_words = np.array([])
        for s_word in sentence_words:
            one_hot_word = np.zeros(len(corpus_list) + 1)
            if s_word not in corpus_list:
                one_hot_word[-1] = 1
                # print('word: {} one-hot: {}'.format(s_word, one_hot_word))
            else:
                for index, word in enumerate(corpus_list):
                    if word == s_word:
                        one_hot_word[index] = 1
                        # print('word: {} one-hot: {}'.format(s_word, one_hot_word))
            one_hot_words = np.append(one_hot_words, one_hot_word)

        return one_hot_words

    def zero_padding(self, one_hot_words, time_steps, sentence_length):
        padding_num = int(time_steps - sentence_length)
        one_hot_word = np.zeros(int(len(one_hot_words) / sentence_length))
        for i in range(padding_num):
            one_hot_words = np.append(one_hot_words, one_hot_word)
        # print (one_hot_words.shape)
        # print (one_hot_words.reshape(30, 4))
        return one_hot_words

    def generat_answer_one_hot_encode(self, sentence_category, output_size):
        one_hot_word_answer = np.zeros(output_size)
        one_hot_word_answer[sentence_category] = 1
        # print (one_hot_word_answer)
        return one_hot_word_answer


def main():
    sentence_words = ['妳好', '妳', '好', '哈']
    sentence_category = 0
    sa = SyntaxAnalysis()
    sentences, categories = sa.segment_words('dialogue.txt')
    words = sa.flat_sentences(sentences)
    corpus_list = sa.generate_corpus(words)
    one_hot_words = sa.one_hot_encode(corpus_list, sentence_words)
    sentence_x = sa.zero_padding(one_hot_words, 40, len(sentence_words))
    sentence_y = sa.generat_answer_one_hot_encode(sentence_category, 3)
    sentence_data = (sentence_x, sentence_y)
    # print (sentence_data)

    # sa = SyntaxAnalysis()
    # sa.segment_words()
    # words = ['妳好', '妳好', '妳好', '妳', '好']
    # sentence_words = ['妳好', '妳', '好', '哈']
    # corpus_list = sa.generate_corpus(words)
    # one_hot_words = sa.one_hot_encode(corpus_list, sentence_words)
    # sa.zero_padding(one_hot_words, 30, 4)


if __name__ == '__main__':
    main()
