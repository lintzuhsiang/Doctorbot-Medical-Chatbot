from generate_vector import generate_vector
import json
from keras.models import load_model
loaded_model = load_model('intent_predict/intent_model.h5')


class IntentPredict(object):
    def get_intent(self, sentence):
        gv = generate_vector()
        sentences, maxsize = gv.segment_words(sentence)

        with open('dict_one_hot_word.txt', 'r', encoding='utf-8') as f:
            dict_one_hot_word = json.load(f)

        one_hot_words = gv.one_hot_encode(1467, sentences, maxsize, dict_one_hot_word)
        one_hot_words = one_hot_words.reshape(-1, 15, 1468)

        return loaded_model.predict_classes(one_hot_words)[0].item()


def main():
    while True:
        sentence = input('your sentence: ')
        intent_index = IntentPredict().get_intent(sentence)
        intents = ['greeting', 'search_symptom', 'search_division', 'search_doctor', 'search_timetable', 'register']
        print('intent： ' + intents[intent_index])

if __name__ == '__main__':
    main()