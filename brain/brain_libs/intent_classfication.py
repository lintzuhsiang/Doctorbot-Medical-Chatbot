from keras_rnn import KerasRnn
from syntax_analysis import SyntaxAnalysis


class IntentClassfication(object):
    def __init__(self):
        pass

    def generate_data(self):
        pass

    def train(self):
        sa = SyntaxAnalysis()
        sentences, categories = sa.segment_words('toy.txt')
        words = sa.flat_sentences(sentences)
        corpus_list = sa.generate_corpus(words)

        sentence_data_list = []
        for i, sentence in enumerate(sentences):
            one_hot_words = sa.one_hot_encode(corpus_list, sentence)
            sentence_x = sa.zero_padding(one_hot_words, 40, len(sentence))
            sentence_y = sa.generat_answer_one_hot_encode(categories[i], 6)
            sentence_data = (sentence_x, sentence_y)
            # print('-----')
            # print (sentence_x)
            # print (sentence_x.shape)
            # print (sentence_y)
            # print (sentence_y.shape)
            # print (sentence_data)
            sentence_data_list.append(sentence_data)

        time_steps = 40
        input_size = len(corpus_list) + 1
        batch_size = 50
        output_size = 6
        cell_size = 50
        lr = 0.01
        kr = KerasRnn(TIME_STEPS=time_steps, INPUT_SIZE=input_size, BATCH_SIZE=batch_size,
                      OUTPUT_SIZE=output_size, CELL_SIZE=cell_size, LR=lr, data=sentence_data_list)
        kr.train_model()


def main():
    ic = IntentClassfication()
    ic.train()


if __name__ == '__main__':
    main()
