import sys
import random
sys.path.append('../LU_model')
import db
sys.path.pop()
sys.path.append('../data_resource')
import CrawlerTimeTable

DB_IP = "104.199.131.158"  # doctorbot GCP ip
DB_PORT = 27017  # default MongoDB port
DB_NAME = "doctorbot"  # use the collection

class intent_slot_generator(object):
    def __init__(self):
        client = db.MongoClient(DB_IP, DB_PORT)
        collection_division = client[DB_NAME]["division"]
        collection_disease = client[DB_NAME]["disease"]

        disease_list = [line.rstrip('\n') for line in open("../data_resource/disease_dict.txt", "r")]
        #print(disease_list)

        notfind = True
        while notfind :
            notfind = False

            disease = disease_list[random.randint(0, len(disease_list)-1)]
            #print(disease)
            while collection_division.find({"disease": disease}).count() < 1:
                disease = disease_list[random.randint(0, len(disease_list) - 1)]

            #print(disease)
            for collection in collection_disease.find({"disease_c": disease}):
                division = collection['department'][0]

            doctor_list = []
            for collection in collection_division.find({"disease": disease}):
                doctor_list.extend(collection['doctor'])

            #print(doctor_list)
            if len(doctor_list) is 0:
                notfind = True
            elif len(doctor_list) > 1:
                name = doctor_list[random.randint(0, len(doctor_list)-1)]
            else:
                name = doctor_list[0]

            if not notfind:
                time_list = CrawlerTimeTable.Timetable(name).get_time()
                #print(time_list)
                if len(time_list) is 0:
                    notfind = True
                elif len(time_list) > 1:
                    time = time_list[random.randint(0, len(time_list)-1)]
                else:
                    time = time_list[0]

        self.goal = {'intent': random.randint(1, 5),
                     'slot': {'disease': disease, 'division': division, 'doctor': name, 'time': time}}


#def main():
    #print(intent_slot_generator().goal)

#if __name__ == '__main__':
#   main()
