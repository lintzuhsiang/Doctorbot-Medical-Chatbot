# Doctor Bot Github Page

## Final Presentation
### [Demo link](https://www.facebook.com/Seek-Doctor-392307634461738/)
### Overview
![](https://i.imgur.com/xNsWy31.png)

## Functions
### Interaction example
1. 查詢症狀: 
U：青光眼會怎樣?
D：青光眼的話,通常罹患此病會常有
眼睛痛, 發紅, 同側頭痛, 噁心, 視力模糊, 視覺範圍縮小, 嘔吐眼睛痛, 發紅, 同側頭痛, 噁心, 視力模糊, 視覺範圍縮小, 嘔吐更多資訊可以到這裡看看喔；
https://health.udn.com/disease/sole/289
謝謝您使用Seek Doctor！希望有幫助到您！Good bye~
2. 查詢科別: 
U：我想知道青光眼是哪科?
D：青光眼的科別是：
眼科部
謝謝您使用Seek Doctor！希望有幫助到您！Good bye~
3. 查詢主治醫生: 
U：請問青光眼要看什麼醫生?
D：眼科部青光眼的醫生有：
眼科部 醫師: 王清泓, 黃振宇, 蘇乾嘉, 楊佳靜
謝謝您使用Seek Doctor！希望有幫助到您！Good bye~
4. 查詢門診時間: 
U：請告訴我眼科的門診時刻表
D：請問您要選擇哪一個
醫生名稱：胡芳蓉, 林昌平, 何子昌, 王一中, 陳偉勵, 黃振宇, 葉伯廷, 蔡紫薰, 魏以宣, 朱筱桑, 謝易庭, 蘇乾嘉, 林昭文, 王清泓, 楊佳靜, 楊中美, 楊長豪, 賴佐庭, 施智偉, 方怡謨
U：朱筱桑
D：朱筱桑的門診時間為：
106.6.26(一) 上午, 106.6.29(四) 下午, 106.7.1(六) 上午, 106.7.3(一) 上午, 106.7.6(四) 下午
謝謝您使用Seek Doctor！希望有幫助到您！Good bye~
5. 預約掛號: 
U：我要掛號
D：好的 請給我
 疾病名稱 或 科別名稱 或 醫生名稱 ,謝謝!
U：勃起功能障礙
D：這裡有這些可以選呢！請選擇一個吧
醫生名稱：劉詩彬, 張奕凱, 謝汝敦
U：劉詩彬
D：這裡有這些可以選呢！請選擇一個吧
看診時間：106.6.30(五) 上午 .掛號. 
106.7.7(五) 上午 .掛號.
U：106.6.30
D：已經幫您預約好勃起功能障礙謝汝敦106.6.25 的門診
謝謝您使用Seek Doctor！希望有幫助到您！Good bye~

* Supported APIs
    * 影像辨識API

![](https://i.imgur.com/oVM5cck.png)

## Ontology 
### Data Sources (Using web crawler technology)
利用web crawler從[元氣網疾病表列](https://health.udn.com/disease/disease_list)爬取疾病相關資訊(如:症狀,發病部位...等)，以及從[台大醫院掛號系統](https://reg.ntuh.gov.tw/webadministration/)爬取病症掛號的資料(如:主治醫師,門診時間)
### Data Base tables (MongoDB)

| Table | Description |
| -------- | -------- |
| Disease table | 中文病名,英文病名,所屬科別,發生部位,症狀,介紹網站, with 52 Rows |
| Doctor table | 科別,中文病名,主治醫生, with 52 Rows |
| Time table (使用者有詢問才會即時爬取)     | 掛號狀態,醫師,門診時間,院區,地點,科別,門診名稱 |

Intents：
1. 打招呼
2. 查詢某疾病的症狀
3. 查詢某疾病的科別
4. 查詢某疾病或某科別的主治醫生
5. 查詢門診時間
6. 預約掛號

Slots：
1. disease疾病名稱
2. division門診科別
3. doctor醫生名稱
4. time門診時間

## Language Understanding
### Model architecture 
根據這個RNN \[1\] 的架構,結合Intent Detection and Slot Filling 這兩個Task, 對一句訓練資料同時進行訓練
### Attention-Based Recurrent Neural Network Model
![](https://i.imgur.com/ypiqMcs.png)

### Training data size 
847300 sentences

## Dialogue Management
### Model architecture

![](https://i.imgur.com/Bp4dXGl.png)

Rule Based Model 是將rule寫在Dialogue Policy裏面, 藉由歷史state和目前新輸入的semantic_frame來產生DM_frame作為下一步的指令

![](https://i.imgur.com/XARq0QR.png)

RL Model 參考Deep Learning Flappy Bird [2]架構, 使用DQN演算法, 在double-ended queue 中存放state, action, reward, 累積到定量資料, 再中取出一個batch大小的資料來訓練
Rule Based Model
RL Model

### User simulation summary 
![](https://i.imgur.com/VD7fEi9.png)

## Natural Language Generation
### Model architecture

![](https://i.imgur.com/yRITq0B.png)

參考RNNLG [3] 這個open source實作, RNNLG是為了對話系統領域的相關應用所開發的open source benchmark toolkit,使用Theano library

### Pre-trained word vector
    
使用經過joint_model fine-tune過的pre-train word vectors
Training data size
* Training data: 722 sentences

Testing data size (should come from real human)
* Testing data: 250 sentences

Performance on testing data (BLEU score, naturalness) 
* BLEU: 0.4073



## Installation

#### Python module
`sudo pip3 install -r requirement.txt`
#### apt-get module
```
sudo chmod +x setup_environment.sh
sudo ./setup_environment.sh
```
#### Document Web APIs (no need in milestone 1)
* http://localhost:8000/docs/
* Usage:
```
cd ~/DoctorBot/doctorbot
npm install
webpack
python3 manage.py check
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
```
## Run DoctorBot
```
cd ~/DoctorBot/brain/brain_libs/LU_model
python3 Doctorbot.py
```
