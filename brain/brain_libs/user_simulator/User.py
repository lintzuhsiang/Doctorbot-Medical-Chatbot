#User Simulation
from random import shuffle
from random import choice
from random import uniform

def weighted_choice(option):
    option = list(option)
    total = sum(w for c, w in option)
    print(total)
    print(option)
    r = uniform(0, total)
    print("r = ",r)
    upto = 0
    for c, w in option:
        if upto + w >= r:
            return c
        upto += w
        print("upto = ",upto)
    assert False, "Shouldn't get here"

class User(object):
    SUCCESS_CHECK = [lambda x: x["disease"] != None, 
                     lambda x: x["disease"] != None,
                     lambda x: x["disease"] != None or x["division"] != None,
                     lambda x: x["doctor"] != None,
                     lambda x: x["doctor"] != None and x["time"] != None]
    ERROR_RATE = {"intent":0, "disease":0, "division":0, "doctor": 0.8, "time":0 }
    WRONG_DOCTOR_LIST = ["李琳山", "李宏毅", "陳縕儂", "廖世文", "楊佳玲"]
    def __init__(self, intent = None, slot = None):
        # default:  randomly pick up an intent if intent == None
        if intent != None and slot != None:
            self.intent = intent
            self.slot   = slot
        else:
            self.intent = 5
            self.slot   = { "disease": "過敏性鼻炎", "division": "耳鼻喉科", "doctor": "林怡岑", "time": "星期五" }
        self.state = {"disease": False, "division": False, "doctor": False, "time": False}
        self.observation = None
        self.reward_per_response = -1
        self.reward_repeat = -3
        self.reward_success = 20
        self.reward_fail = -100
        self.reward_accumalation = 0

    
    # for NLG
    def nlg_intent_1(self,response_slot):
        pattern_dic = {
        "disease":[self.slot["disease"]+"會怎樣",self.slot["disease"],"我想問"+self.slot["disease"],
        self.slot["disease"]+"會有什麼症狀"]
        }
        return choice(pattern_dic[response_slot])
    def nlg_intent_2(self,response_slot):
        pattern_dic = {
        "disease":[self.slot["disease"]+"要看什麼科",self.slot["disease"],"我想問"+self.slot["disease"],
        self.slot["disease"]+"屬於哪科",
        ]
        }
        return choice(pattern_dic[response_slot])
    def nlg_intent_3(self,response_slot):
        pattern_dic = {
        "disease":[self.slot["disease"]+"要看什麼科",self.slot["disease"],"我想問"+self.slot["disease"],
        self.slot["disease"]+"要看哪科"
        ],
        "time":[self.slot["time"]+"有誰可以",self.slot["time"],self.slot["time"]+"哪些醫生可以",
        self.slot["time"]+"有哪些醫生可以","我"+self.slot["time"]+"可以","我"+self.slot["time"]+"有空"
        ]
        }
        return choice(pattern_dic[response_slot])
    def nlg_intent_4(self,response_slot):
        if weighted_choice(zip([True, False],[User.ERROR_RATE["doctor"], 1 - User.ERROR_RATE["doctor"]])):
            doctor = choice(User.WRONG_DOCTOR_LIST)
        else:
            doctor = self.slot["doctor"]
        pattern_dic = {
        "disease":[self.slot["disease"]+"的",self.slot["disease"],self.slot["disease"]],
        "doctor":[doctor + "的" + "門診時間表" ],
        "time":[self.slot["time"]+"的",self.slot["time"],self.slot["time"]+"的時刻表"],
        "division":[self.slot["division"]+"的",self.slot["division"]
        ]
        }
        return choice(pattern_dic[response_slot])
    def nlg_intent_5(self,response_slot):
        if weighted_choice(zip([True, False],[User.ERROR_RATE["doctor"], 1 - User.ERROR_RATE["doctor"]])):
            doctor = choice(User.WRONG_DOCTOR_LIST)
        else:
            doctor = self.slot["doctor"]
        pattern_dic = {
        "disease":["我得了"+self.slot["disease"],self.slot["disease"],"我有"+self.slot["disease"],
        self.slot["disease"]
        ],
        "time":[self.slot["time"]+"的",self.slot["time"],"我"+self.slot["time"]+"可以","我"+self.slot["time"]+"有空"
        ],
        "doctor":["我要掛"+doctor,doctor]
        }        
        return choice(pattern_dic[response_slot])

    #  def nlg_time(self):
    #      pattern_list = [
    #      "我要掛"+self.slot["time"]+"的診",
    #      self.slot["time"],
    #      self.slot["time"]+"的"
    #      ]
    #      return choice(pattern_list)
    #
    #  def nlg_disease(self):
    #      pattern_list =
    #      [
    #      "我得了"+self.slot["disease"],
    #      self.slot["disease"],
    #      "好像是"+self.slot["disease"],
    #      "應該是"+self.slot["disease"]
    #      ]
    #      return choice(pattern_list)
    #
    #  def nlg_division(self):
    #      pattern_list =
    #      [
    #      "我要看"+self.slot["division"],
    #      self.slot["division"],
    #      "好像是"+self.slot["division"],
    #      "應該是"+self.slot["division"]
    #      ]
    #      return choice(pattern_list)
    #
    #  def nlg_doctor(self):
    #      #this part should generate some typo
    #      pattern_list =
    #      [
    #      "我要掛"+self.slot["doctor"],
    #      "我要掛"+self.slot["doctor"],
    #      self.slot["doctor"]+"醫生",
    #      self.slot["doctor"][0]+"醫生" # 林醫生
    #      ]
    #      return choice(pattern_list)

    def check_if_something_wrong(self):
        # check if observation is consistent with users intent and slots
        wrong = False
        reward = self.reward_per_response
        response = ""
        for key in self.slot:
            if (self.state[key] == True 
            and self.observation['state'][key] != None):
                if self.slot[key] != self.observation['state'][key]:
                    wrong = True
                    response = "我是說" + self.slot[key]
                    break
        return wrong, response, reward;

    def say_intent_again(self):
        if self.intent == 1:
            self.state["disease"] = True
            response, reward = "我是說請問得"+self.slot["disease"]+"會怎樣", -1
        if self.intent == 2:
            self.state["disease"] = True
            response, reward = "我是說請問"+self.slot["disease"]+"要看哪一科", -1
        if self.intent == 3:
            self.state["time"] = True
            response, reward = "我是說請問"+self.slot["time"]+"有哪些醫生可以", -1
        if self.intent == 4:
            response, reward = "我要問時間", -1
        if self.intent == 5:
            response, reward = "我想要掛號", -1
        return response, reward
 


    def response_dm_request(self):
        # if the slot request by DM is provided before, more punishment will be sent.
        # intent 3 and 5 are basically the same, only different in booking action.
        slot_to_respond = []
        if self.intent == 1:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_1(slot_to_respond[0]), self.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_1(slot_to_respond[0]), -1
                
        elif self.intent == 2:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_2(slot_to_respond[0]), self.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_2(slot_to_respond[0]), -1
                
        elif self.intent == 3:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_3(slot_to_respond[0]), self.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_3(slot_to_respond[0]), -1
                
        elif self.intent == 4:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_4(slot_to_respond[0]), self.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_4(slot_to_respond[0]), -1    
        elif self.intent == 5:
            for slot in self.observation["slot"]:
                if self.slot[slot] != None:
                    slot_to_respond.append(slot)
            shuffle(slot_to_respond)
            if(self.state[slot_to_respond[0]]==True):
                return self.nlg_intent_5(slot_to_respond[0]), self.reward_repeat
            else:
                self.state[slot_to_respond[0]] = True
            return self.nlg_intent_5(slot_to_respond[0]), -1
        # def response_dm_confirm(self):
        # def response_dm_inform(self):
    # def response_dm_choose(self):
        #choosing principle?
        #1. random
        #2. base on other slot(flexible)?
    def response_dm_confirm(self):
        correct = True
        check_slots = self.observation["slot"]
        print(check_slots)
        for s in check_slots:
            if self.observation['state'][s] != self.slot[s]:
                return choice(["我是說","不，我是說"]) + self.slot[s] + " 不是" + self.observation['state'][s], self.reward_per_response
        if correct:
            return choice(["對","是的","沒錯","就是這樣"]), self.reward_per_response
            
    def response_dm_end(self):
        #check if mission complete 
        #1. intent compare
        #2. slot compare
        #INTENT CHANGING? 問到醫生之後再問時間? 
        #answer checking
        self.success = True
        if(self.intent == self.observation["intent"]):
            if User.SUCCESS_CHECK[self.intent-1](self.observation["state"]):
                for key in self.slot:
                    if ((self.state[key] == True and self.observation['state'][key] != None)
                        or (self.state[key] == False and self.observation['state'][key] == None)):
                        if self.slot[key] != self.observation['state'][key]:
                            self.success = False
                            break
                    else:
                        self.success = False
                        break
        else:
            self.success = False
        #######
        if(self.success):
            return "謝謝", self.reward_success
        else:
            return "我病得更嚴重了", self.reward_fail

    def respond(self,observation):
        reward = -1                
        self.observation = observation
        wrong, response, reward = self.check_if_something_wrong()
        if wrong and self.observation["intent"] != 'end':
            return response, reward
        if self.observation == None:
            if self.intent == 1:
                self.state["disease"] = True
                response, reward = "請問得"+self.slot["disease"]+"會怎樣", -1
            elif self.intent == 2:
                self.state["disease"] = True
                response, reward = "請問"+self.slot["disease"]+"要看哪一科", -1
            elif self.intent == 3:
                self.state["time"] = True
                response, reward = "我想看"+self.slot["disease"]+"有哪些醫生可以", -1
            elif self.intent == 4:
                response, reward = "我要問時間", -1
            elif self.intent == 5:
                response, reward = "我想要掛號", -1
        elif self.observation["intent"] != self.intent:
            response, reward = self.say_intent_again()
        elif self.observation["request"] == "info": # request
            response, reward = self.response_dm_request()
        elif self.observation["request"] == "choose":
            response, reward = self.response_dm_choose()
        elif self.observation["request"] == "confirm":
            response, reward = self.response_dm_confirm()
        elif self.observation["request"] == "end":
            response, reward = self.response_dm_end()
        return response, reward
                # respond DM's confirm, inform, or request
