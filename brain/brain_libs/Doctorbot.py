import sys
import db_management
sys.path.append('./slot_model')
import slot_model

sys.path.append('./intent_predict')
import intent_model

DB_IP = "104.199.131.158"  # doctorbot GCP ip
DB_PORT = 27017  # default MongoDB port
DB_NAME = "doctorbot"  # use the collection


def main():
    client = db_management.MongoClient(DB_IP, DB_PORT)

    collection_division = client[DB_NAME]["division"]
    collection_disease = client[DB_NAME]["disease"]
    sys.stdout.flush()
    print("您好，我是Seek Doctor Bot，如果您想要\n" +
          "1.查詢某疾病相關症狀，您可以問我：請問青光眼會怎樣\n" +
          "2.知道某疾病屬於什麼科別，您可以問我：青光眼是哪科\n" +
          "3.查詢某疾病或科別主治醫師，您可以問我：青光眼要看哪些醫生\n" +
          "4.查詢某疾病,科別或醫生的門診時間，您可以說：給我青光眼門診時刻表\n" +
          "5.預約掛號某疾病,科別或醫生的門診，您可以說：我要掛號眼科"
          )

    while True:
        sentence = input('\n\n請輸入: ')
        slot_dictionary = slot_model.SlotFilling().get_slot(sentence)
        print("[ Slot ]")
        for slot, value in slot_dictionary.items():
            print(slot, ": ", value)

        intent_index = intent_model.IntentPredict().get_intent(sentence)
        intents = ['greeting', 'search_symptom', 'search_division', 'search_doctor', 'search_timetable', 'register']
        print('[ Intent ] ' + intents[intent_index])

        print('\n\n')
        if intent_index == 1:  # search_symptom
            print("好的，您想查詢" +
                  slot_dictionary['disease'] +
                  "會有什麼症狀，以下為相關可能症狀：")
            for data in collection_disease.find({"disease_c": {"$regex": slot_dictionary['disease']}}):
                print(", ".join(data['symptom']))
        elif intent_index == 2:  # search_division
            print("好的，您想查詢" +
                  slot_dictionary['disease'] +
                  "是屬於哪一科，以下為相關科別：")
            for data in collection_disease.find({"disease_c": {"$regex": slot_dictionary['disease']}}):
                print(", ".join(data['department']))
        elif intent_index == 3:  # search_doctor
            print("好的，您想查詢" +
                  slot_dictionary['division'] + slot_dictionary['disease'] +
                  "有哪些醫生可以掛號，以下為醫生表列：")
            for data in collection_division.find({"$and": [{"disease": {"$regex": slot_dictionary['disease']}},
                                                           {"department": {"$regex": slot_dictionary['division']}}]}):
                print(data['department'] + " 醫師: " + ", ".join(data['doctor']))
        elif intent_index == 4:  # search_timetable
            print("好的，您想查詢" + slot_dictionary['division'] +
                  slot_dictionary['disease'] + slot_dictionary['doctor'] + slot_dictionary['time'] + "的門診時間")
        elif intent_index == 5:  # register
            print("好的，幫您預約掛號" + " " + slot_dictionary['division'] + " " +
                  slot_dictionary['disease'] + " " + slot_dictionary['doctor'] + " " +
                  slot_dictionary['time'] + "的門診")
        else:
            print("不好意思,我不確定您的意思")

if __name__ == '__main__':
    main()
