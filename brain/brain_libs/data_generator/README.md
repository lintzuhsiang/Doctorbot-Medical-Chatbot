"""

Usage:python3 intent_training_data.py

**Please put disease.csv and division.csv in the same folder

Output: intent_training.txt

pattern_list format:

        [[pattern], [pattern], ... , [',&N']]

***where pattern is a list of string,N is the number of the category for the intent


"""

disease 239個,division 51個,doctor 702個,time 16個（星期一-日/天，禮拜一-日/天）

1.查詢症狀 search_symptom

資料量：2*2*239*2 + 2*2*239*2 = 3,824

        [['請問', ''], ['得', ''], disease_list, ['會'], ['怎麼樣', '怎樣'], [',&1']],

        [['請問', ''], ['得', ''], disease_list, ['會有'], ['什麼症狀', '哪些症狀'], [',&1']],



2.查詢科別 search_division

資料量：2*2*239*5*2 = 49,712

	[['請問', ''], ['得', ''], disease_list, ['是', '屬於', '要看', '要掛', '要掛號'], ['哪', '什麼'], ['科'], [',&2']],



3.查詢醫生 search_doctor

資料量：2*16*2*2*2*4*239 + 2*239*2*4*2*2 = 325,040

        [['請問', ''], time_list, ['有', ''], ['什麼', '哪些'], ['醫生', '醫師'], ['可以'],['看', '掛', '掛號', '預約'], disease_list, ['的門診'], [',&3']],

        [['請問', ''], disease_list, ['要', '可以'], ['看', '掛', '掛號', '預約'], ['什麼', '哪些'], ['醫生', '醫師'], [',&3']],


4.查詢門診 search_timetable

資料量：5*16*239*2 + 5*16*51*2 + 5*16*702*2 = 120,480

        [['請給我', '給我', '請告訴我', '告訴我', '請問'], time_list, disease_list, ['的門診時刻表', '的門診時間'], [',&4']],

        [['請給我', '給我', '請告訴我', '告訴我', '請問'], time_list, division_list, ['的門診時刻表', '的門診時間'], [',&4']],

        [['請給我', '給我', '請告訴我', '告訴我', '請問'], time_list, doctor_list, ['的門診時刻表', '的門診時間'], [',&4']],


5.預約掛號 register

資料量：2*3*4*702*2 + 2*3*4*51*2 + 2*3*4*239*2 = 23,808

        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], time_list, doctor_list, ['', '的門診'], [',&5']],

        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], time_list, division_list, ['', '的門診'], [',&5']],

        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], time_list, disease_list, ['', '的門診'], [',&5']]


"""


Usage:

python3 slot_training_data.py

**Please put disease.csv and division.csv in the same folder
**Please run create_dictionary.py to get newest dictionary for Jieba

Output:

slot_training.txt


training data format:

( [], [] )



"""

Data Example:


        ([請問,得,過敏性鼻炎,會,怎麼樣,],[o,o,b-disease,o,o])
