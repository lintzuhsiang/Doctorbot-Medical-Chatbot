"""

Usage:
python3 intent_training_data.py
**disease.csv and division.csv are in the folder ../data_resource/

Output:
intent_training.txt

pattern_list format:
[[pattern], [pattern], ... , [',&N']]
where pattern is a list of string,
(if there is an empty string'' in the pattern list, please put it in the end of the list)
N is the number of the category for the intent

"""
import csv
import ast


def dfs(sen, depth, input_list, ans):
    if depth == len(input_list):
        ans.append(sen)
        return
    for j in input_list[depth]:
        sen += j
        dfs(sen, depth+1, input_list, ans)
        sen = sen[:-len(j)]


def data_generator(pattern_list):
    output = []
    dfs("", 0, pattern_list, output)
    return output


def disease_list_generator(disease_file, disease_list, division_list):
    for row in disease_file:
        for index, col in enumerate(row):
            if index == 0:  # Generate disease_list from disease_file
                disease_list.append(col)
            elif index == 2:  # Generate division_list from disease_file
                for item in ast.literal_eval(col):
                    if division_list.count(item) == 0:
                        division_list.append(item)


def doctor_list_generator(division_file, doctor_list):
    for row in division_file:
        for index, col in enumerate(row):
            if index == 2:  # Generate doctor_list from division_file
                for item in ast.literal_eval(col):
                    if len(item) <= 3 and doctor_list.count(item) == 0:
                        doctor_list.append(item)


def main():

    div_rf = open("../data_resource/division.csv", "r")
    division_file = csv.reader(div_rf)
    dis_rf = open("../data_resource/disease.csv", "r")
    disease_file = csv.reader(dis_rf)

    disease_list = []
    division_list = []
    doctor_list = []
    time_list = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日', '星期天',
                 '禮拜一', '禮拜二', '禮拜三', '禮拜四', '禮拜五', '禮拜六', '禮拜日', '禮拜天', '']
    disease_list_generator(disease_file, disease_list, division_list)
    doctor_list_generator(division_file, doctor_list)

    pattern_list = [
        [['請問', ''], ['得', ''], disease_list, ['會'], ['怎麼樣', '怎樣'], [',&1']],
        [['請問', ''], ['得', ''], disease_list, ['會有'], ['什麼症狀', '哪些症狀'], [',&1']],

        [['請問', ''], ['得', ''], disease_list, ['是', '屬於', '要看', '要掛', '要掛號'], ['哪', '什麼'], ['科'], [',&2']],

        [['請問', ''], time_list, ['有', ''], ['什麼', '哪些'], ['醫生', '醫師'], ['可以'],
         ['看', '掛', '掛號', '預約'], disease_list, ['的門診'], [',&3']],
        [['請問', ''], disease_list, ['要', '可以'], ['看', '掛', '掛號', '預約'], ['什麼', '哪些'], ['醫生', '醫師'], [',&3']],

        [['請給我', '給我', '請告訴我', '告訴我', '請問'], time_list, disease_list, ['的門診時刻表', '的門診時間'], [',&4']],
        [['請給我', '給我', '請告訴我', '告訴我', '請問'], time_list, division_list, ['的門診時刻表', '的門診時間'], [',&4']],
        [['請給我', '給我', '請告訴我', '告訴我', '請問'], time_list, doctor_list, ['的門診時刻表', '的門診時間'], [',&4']],

        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], time_list, doctor_list, ['的門診', ''], [',&5']],
        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], time_list, division_list, ['的門診', ''], [',&5']],
        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], time_list, disease_list, ['的門診', ''], [',&5']]
    ]

    it_wf = open("intent_training.txt", "w")
    for lis in pattern_list:
        for sen in data_generator(lis):
            print(sen, file=it_wf)

    div_rf.close()
    dis_rf.close()
    it_wf.close()

if __name__ == '__main__':
    main()
