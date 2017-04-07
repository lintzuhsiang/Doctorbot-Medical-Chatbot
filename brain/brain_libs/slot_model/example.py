"""
Usage:
python3 example.py

Sample input:
請問青光眼看哪科

Sample output:
division :
doctor :
time :
disease :  青光眼
"""
import slot_model

while True:
    sentence = input('your sentence: ')
    slot_dictionary = slot_model.SlotFilling().get_slot(sentence)
    for slot, value in slot_dictionary.items():
        print(slot, ": ", value)
