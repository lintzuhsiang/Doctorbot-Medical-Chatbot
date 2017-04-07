from language_understanding import LanguageUnderstanding
from dialogue_management import DialogueManagement
from natural_language_generation import NaturalLanguageGeneration


def main():
    lu = LanguageUnderstanding()
    lu.segment_word()
    dm = DialogueManagement()
    dm.test()
    nlg = NaturalLanguageGeneration()
    nlg.test()


if __name__ == '__main__':
    main()
