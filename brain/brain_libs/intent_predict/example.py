"""
Usage:
python3 example.py

Sample input:
請問青光眼看哪科

Sample output:
intent： search_division
"""
import intent_model

while True:
    sentence = input('your sentence: ')
    intent_index = intent_model.IntentPredict().get_intent(sentence)
    intents = ['greeting', 'search_symptom', 'search_division', 'search_doctor', 'search_timetable', 'register']
    print('intent： ' + intents[intent_index])