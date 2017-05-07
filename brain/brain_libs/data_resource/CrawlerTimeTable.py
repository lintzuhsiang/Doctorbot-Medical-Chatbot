import re
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from lxml import etree
import csv


class Timetable(object):
    def __init__(self, name):
        self.result = []
        name = urllib.parse.quote(name)
        url = "https://reg.ntuh.gov.tw/webadministration/DoctorServiceQueryByDrName.aspx?HospCode=T0&QueryName=" + name
        html = urlopen(url)
        r = requests.get(url)

        soup = BeautifulSoup(html.read(), "lxml")
        html = r.content.decode('utf-8')
        page = etree.HTML(html)
        res=[]
        next = 'AdminTextShow'
        timeout = 3

        table = soup.find_all("table",id =re.compile('DoctorServiceList'))
        for tableI in table:
            temp = []
            for item in tableI.find_all("th"):
                content = re.sub('\n', '', item.text)
                temp.append(content)
            self.result.append(temp)
            for row in tableI.find_all("tr"):
                temp = []
                for item in row.find_all("td"):
                    content = re.sub('\n', '', item.text)
                    temp.append(content)
                if(temp!=[]):
                    self.result.append(temp)
            self.result.pop(0)

    def get_time(self):
        time_list = []
        for col in self.result:
            time_list.append(col[2])
        return time_list

    def save_csv(self):
        f = open("../data_resource/doctor.csv", "w")
        w = csv.writer(f)
        w.writerows(self.result[1:])
        f.close()


def main():
    name = input('Doctor name: ')
    time = Timetable(name)
    print(time.get_time())


if __name__ == '__main__':
    main()
