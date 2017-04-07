


import requests
import re
from lxml import etree
from urllib.request import urlopen
from bs4 import BeautifulSoup


class DivisionCrawler(object):
    def __init__(self):
        self.division = []



    def crawl_search_result(self):
        #url = "https://www.ntuh.gov.tw/MedicalTeams/%E9%86%AB%E5%B8%AB%E6%9F%A5%E8%A9%A2_table.aspx"
        #r = requests.get(url)
        #html = r.content.decode('utf-8')
        #page = etree.HTML(html)
        html = urlopen("https://www.ntuh.gov.tw/MedicalTeams/%E9%86%AB%E5%B8%AB%E6%9F%A5%E8%A9%A2_table.aspx")
        soup = BeautifulSoup(html.read(), "lxml")

        result = []
        for division in soup.find_all('tr'):
            result.append(division.text)

        # Preprocessing doctor cloumn
        # Making list with url
        doctor_name = []
        x = soup.find_all(href=re.compile("DoctorServiceQueryByDrName"))
        for doctor in x:
            tempdoc = doctor.text
            tempdoc = re.sub('、', '', tempdoc)
            tempdoc = re.sub('\u3000', '', tempdoc)
            tempdoc = re.sub('\xa0', '', tempdoc)
            tempdoc = re.sub('\u200b', '', tempdoc)
            tempdoc = re.sub('n', '', tempdoc)
            tempdoc = re.sub('\r', '', tempdoc)
            tempdoc = re.sub(' ', '', tempdoc)
            if len(tempdoc)==6:
                tempdoc=tempdoc[:3]
            if tempdoc!='':
                doctor_name.append(tempdoc)
        #result = []
        #for division in page.xpath("//tr"):
        #    result.append(division.xpath(".//text()"))

        ts = []
        global d
        d = 0
        def textclean(ts):
            ts = "".join(ts)
            ts = re.sub('\n+',' ',ts)
            ts = re.sub(' +', ' ', ts)
            ts = re.sub('、', ' ',ts)
            ts = re.sub('\u3000', ' ',ts)
            ts = re.sub('\xa0', ' ', ts)
            ts = re.sub('\u200b', '',ts )
            ts = re.sub('兼任：', ' ', ts)
            ts = re.sub('任：', '',ts)
            ts = re.sub('\r','',ts)
            #ts = re.sub(r'\(.*\)', '', ts)
            ts = re.sub('（', ' ', ts)
            ts = re.sub('）', ' ', ts)
            ts = re.sub('請', ' ', ts)
            ts = re.sub('\(', ' ', ts)
            ts = re.sub('\)', ' ', ts)
            #ts = bytes(ts,"UTF-8")
            #ts = ts.decode("ascii","ignore")
            ts = ts.split(' ')
            cleants =[]
            global d
            for item in ts:
                if(len(item)>1):
                    cleants.append(item)
            ts =[]
            urlts = []
            last_index = 0

            while (doctor_name[d] in cleants and not(doctor_name[d] in ts) or doctor_name[d]=='楊湘'
                   or doctor_name[d]=='敬淳'):
                urltemp = doctor_name[d]
                ts.append(urltemp)
                d = d + 1
                if  d >= len(doctor_name):
                    break
                '''
            for i in range(1,len(cleants)+1): #+1 for 1 error
                if doctor_name[d] in cleants:
                    urltemp = doctor_name[d]
                    ts.append(urltemp)
                    d = d + 1'''
            return ts
        c = 0
        fs= []
        ss= [] 
        inin = []
        res = []

        for row in result:
            i = False
            temp = "".join(row)
            if(temp.find('部')!=-1 or temp.find('中心')!=-1 or temp.find('醫院')!=-1):
                newrow = 0
                if (ts != []):
                    newrow=1
                ts = textclean(ts)
                inin = [fs,ss,ts]
                if(newrow==1):
                    res.append(inin)
                fs= []
                ss= [] 
                ts = []
                inin = []
                if(temp.find('部')!=-1):
                    a = temp.index('部')
                elif(temp.find('中心')!=-1):
                    a = temp.index('中心')+1
                else:
                    a = temp.index('院')
                fs = temp[0:a+1]
                if(temp.find('專')!=-1):	
                    b = temp.index('專')
                    ss = temp[a+1:b]
                    ts = temp[b+1:]
                elif(temp.find('兼')!=-1):
                    b = temp.index('兼')
                    ss = temp[a + 1:b]
                    ts = temp[b + 1:]
                elif (temp.find('翁') != -1):
                    b = temp.index('翁')
                    ss = temp[a + 1:b]
                    ts = temp[b :]
                elif (temp.find('李') != -1):
                    b = temp.index('李')
                    ss = temp[a + 1:b]
                    ts = temp[b :]
                elif (temp.find('廖') != -1):
                    b = temp.index('廖')
                    ss = temp[a + 1:b]
                    ts = temp[b:]
                elif (temp.find('梁') != -1):
                    b = temp.index('梁')
                    ss = temp[a + 1:b]
                    ts = temp[b:]
            else:
                tempts = [ts,temp]
                ts = "".join(ts)
        ts = textclean(ts)
        inin = [fs,ss,ts]
        res.append(inin)	


        # Preprocessing disease cloumn

        parse_list = []
        #first_row = ["division", "disease", "doctor"]
        #parse_list.append(first_row)

        for index, row in enumerate(res):
            if index != 0:
                new_row = []
                for i, col in enumerate(row):
                    if i != 1:
                        new_row.append(col)
                    else:
                        splited_list = col.split("、")
                        clean_list = []
                        for item in splited_list:
                            clean_list.extend(re.split('（|\(|\)|）', item))
                        new_row.append(list(filter(None, clean_list)))
                parse_list.append(new_row)

        return parse_list

def main():
    dc = DivisionCrawler()
    dc.crawl_search_result()

if __name__ == '__main__':
    main()
