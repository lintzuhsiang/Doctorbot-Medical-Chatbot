import sys
import os
import json
import re
sys.path.append('../LU_model')
import LU
import db
sys.path.pop()
sys.path.append('../data_resource')
import CrawlerTimeTable

DB_IP = "104.199.131.158"  # doctorbot GCP ip
DB_PORT = 27017  # default MongoDB port
DB_NAME = "doctorbot"  # use the collection

def initialize():
    state = {"intent": None, "disease": None, "division": None, "doctor": None, "time": None}
    DM = {"Request": None, "Intent": None, "Slot": None, "State": state}
    if os.path.exists("DM.json"):
        os.remove("DM.json")
    return DM
#################################################################################################
#                   search for division or doctor from database                                 #
#################################################################################################
def get_dbinfo(slot1,slot2, choose):
    client = db.MongoClient(DB_IP, DB_PORT)

    collection_division = client[DB_NAME]["division"]
    collection_disease = client[DB_NAME]["disease"]
    #use disease to find division
    if slot2 == "department":
        for data in collection_disease.find({"disease_c": {"$regex": slot1}}):
            return  data['department']
    #use disease to find doctors
    elif slot2 == "doctor" and choose == 0:
        for data in collection_division.find({"$and": [{"disease": {"$regex": slot1}},
                                                       {"department": {"$regex": ""}}]}):
            return data['doctor']
    #use division to find doctors
    elif slot2 == "doctor" and choose == 1:
        for data in collection_division.find({"$and": [{"disease": {"$regex": ''}},
                                                       {"department": {"$regex": slot1}}]}):
            return data['doctor']
#################################################################################################
#                   decide a request                                                            #
#################################################################################################
def DM_request(DM):
    DM["Request"] = None
    DM["Slot"] = None

    if DM["Intent"] == 1 or DM["Intent"] == 2:
        if DM["State"]["disease"]!=None:
            DM["Request"] = "end"
        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease"]
    elif DM["Intent"] == 3:
        if DM["State"]["division"] != None and DM["State"]["disease"] != None:
            DM["Request"] = "end"
        elif DM["State"]["disease"] == None:
            DM["Request"] = "info"
            DM["Slot"] = ["disease"]
        else:
            DM["Request"] = "end"
            DM["State"]["division"] = get_dbinfo(DM["State"]["disease"], "department",0)
    elif DM["Intent"] == 4:
        if DM["State"]["doctor"] != None:
            DM["Request"] = "end"
        elif DM["State"]["disease"] != None:
            DM["State"]["doctor"] = get_dbinfo(DM["State"]["disease"], "doctor",0)
            DM["Request"] = "choose"
            DM["Slot"] = ["doctor"]
        elif DM["State"]["division"] != None:
            DM["State"]["doctor"] = get_dbinfo(DM["State"]["division"], "doctor", 1)
            DM["Request"] = "choose"
            DM["Slot"] = ["doctor"]
        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease", "division", "doctor"]
    elif DM["Intent"] == 5:
        if DM["State"]["doctor"] != None and DM["State"]["time"] != None:
            DM["Request"] = "end"
        elif DM["State"]["doctor"] == None:
            if DM["State"]["disease"] != None:
                DM["State"]["doctor"] = get_dbinfo(DM["State"]["disease"], "doctor",0)
                DM["Request"] = "choose"
                DM["Slot"] = ["doctor"]
            elif DM["State"]["division"] != None:
                DM["State"]["doctor"] = get_dbinfo(DM["State"]["division"], "doctor",1)
                DM["Request"] = "choose"
                DM["Slot"] = ["doctor"]
            else:
                DM["Request"] = "info"
                DM["Slot"] = ["disease", "division", "doctor"]
        elif DM["State"]["time"] == None:
            if DM["State"]["doctor"] != None:
                DM["State"]["time"] = CrawlerTimeTable.Timetable(DM["State"]["doctor"]).get_time()
                DM["Request"] = "choose"
                DM["Slot"] = ["time"]

        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease", "division", "doctor"]
    else:
        pass

    return DM

def main():

    sys.stdout.flush()
    DM = initialize()
    disease = []
    week = []
    division = []
    doctor = []
    with open('../data_resource/disease_dict.txt', 'r', encoding='utf-8') as r_disease:
        for line in r_disease:
            disease.append(line.replace('\n',''))
    with open('../data_resource/week_dict.txt', 'r', encoding='utf-8') as r_week:
        for line in r_week:
            week.append(line.replace('\n',''))
    with open('../data_resource/division_dict.txt', 'r', encoding='utf-8') as r_division:
        for line in r_division:
            division.append(line.replace('\n',''))
    # with open('../data_resource/doctor_dict.txt','r') as r_doctor:
    #     for line in r_doctor:
    #         doctor.append(line)

    while True:
        if os.path.exists("DM.json"):
            with open("DM.json", 'r') as f:
                DM = json.load(f)
        slot_dictionary = {'disease': '', 'division': '', 'doctor': '', 'time': ''}

        sentence = input('U: ')
        pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+")
        match = pattern.match(sentence)
        if match:
            DM["State"]["time"] = sentence
        elif sentence in week:
            DM["State"]["time"] = sentence
        # elif sentence in doctor:
        #     DM["State"]["doctor"] = sentence
        elif sentence in division:
            DM["State"]["division"] = sentence
        elif sentence in disease:
            DM["State"]["disease"] = sentence
        else:
            slot_dictionary = LU.SlotFilling().decode(sentence)

        print("[ Slot ]")
        for slot, value in slot_dictionary.items():
            print(slot, ": ", value)
        for slot in slot_dictionary:
            if slot_dictionary[slot] != '' and (DM["State"][slot] == None or (type(DM["State"][slot]) == list and len(DM["State"][slot]) > 1)):
                DM["State"][slot] = slot_dictionary[slot]

        if type(DM["State"]["time"]) == str and DM["State"]["time"] not in week and not match:
            DM["State"]["time"] = None

        if DM["Intent"] == None:
            intent = LU.IntentPredict().get_intent(sentence)
            intent_index= intent.index(max(intent))
            DM["Intent"] = intent_index

        DM = DM_request(DM)
        print ("[ DM ]")
        for i in DM:
            print (i, DM[i])
        with open("DM.json", 'w') as fp:
            json.dump(DM, fp)
        if DM["Request"] == "end":
            sys.exit()


if __name__ == '__main__':
    main()
