
#interation, 需要json之類的，才能傳~
from User import *
import UserSimulation

user_intent = None
user_slot = None

generate = UserSimulation.intent_slot_generator()
user_intent = generate.goal["intent"]
user_slot = generate.goal["slot"]
sim_user = User(intent = user_intent, slot = user_slot)
reward = 0
request_dic = {"i":"info","s":"choose","c":"confirm","e":"end"}
slot_name_dic = {"dis":"disease","div":"division","doc":"doctor","t":"time"}
intent_dic = {"1":"查症狀","2":"查科別","3":"查醫師","4":"查時間","5":"幫我掛號"}
state = {
"intent":None,
"disease":None,
"division":None,
"doctor":None,
"time":None
}
request_to_user = None
slot_to_user = None
DM = {
    "request":None,
    "intent":None,
    "slot": None,
    "state":None
}
error = True
handle_slot = ['int','dis','div','doc','t']
handle_request = ['i','s','c','e'] 
while(True):
    print("intent : ",intent_dic[str(sim_user.intent)])
    print("Slot : ", sim_user.slot)
    print("State : ",sim_user.state)
    if reward == 0:
        user_word , reward_once = sim_user.respond(None)
    else:
        user_word , reward_once = sim_user.respond(DM)
    print('\033[93m'+"U: "+user_word+'\033[0m'+" , "+str(reward_once))
    reward = reward + reward_once
    print("Reward : "+str(reward))
    if reward_once == sim_user.reward_fail or reward_once == sim_user.reward_success:
        break
    while(input('new information?(n/y)')=='y'):
        while (error):
            slot_name = input('intent(int) 疾病（dis）、科別(div)、醫生(doc)、時間(t)：')
            if not (slot_name in handle_slot):
                print("Wrong syntax")
            else:
                error = False
        error = True 
        if slot_name == 'int':
            DM["intent"] = int(input('查症狀(1), 查科別(2), 查醫師(3), 查時間(4), 幫我掛號(5) : '))
        else:
            slot = input(slot_name_dic[slot_name]+" = ")
            state[slot_name] = slot
    while(error):
        request = input('要求（i）、選擇（s）、確認(c)、結束（e）：')
        if not (request in handle_request):
            print("Wrong syntax")
        else:
            error = False
    error = True
    if request !='e':
        while(error):
            slot_name = input('疾病（dis）、科別(div)、醫生(doc)、時間(t)：')
            if not (slot_name in handle_slot):
                print("Wrong syntax")
            else:
                error = False
        error = True

    if request == 'i' or request == 'c':
        request_slot = slot_name_dic[slot_name]
        DM["slot"] = [request_slot]
    DM["state"] = state
    DM["request"] = request_dic[request]
    #DM["slot"] = slotname
    

        

