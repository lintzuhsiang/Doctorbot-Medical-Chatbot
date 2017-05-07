import requests
import re
import urllib
from lxml import etree
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
name = sys.argv[1]

import requests
from lxml import etree
name = urllib.parse.quote(name)
url = "https://reg.ntuh.gov.tw/webadministration/DoctorServiceQueryByDrName.aspx?HospCode=T0&QueryName=" + name
html = urlopen(url)
r = requests.get(url)

soup = BeautifulSoup(html.read(), "lxml")
html = r.content.decode('utf-8')
page = etree.HTML(html)
res=[]
result = []
#click
next = 'AdminTextShow'
#driver = webdriver.Firefox()
#driver.get(url)
timeout = 3
'''
for tag in soup.find_all(id=re.compile(next)):
    nextid = tag.get('id')
    driver.find_element_by_id(nextid).click()
    driver.current_url
'''

table = soup.find_all("table",id =re.compile('DoctorServiceList'))
for tableI in table:
    temp = []
    for item in tableI.find_all("th"):
        content = re.sub('\n', '', item.text)
        temp.append(content)
    result.append(temp)
    for row in tableI.find_all("tr"):
        temp = []
        for item in row.find_all("td"):
            content = re.sub('\n','',item.text)
            temp.append(content)
        if(temp!=[]):
            result.append(temp)
            #print(temp)
        #print(row.a)
        #add (html)
        #for tag in row.find_all(id=re.compile(next)):
         #   nextid = tag.get('id')
           # driver.find_element_by_id(nextid).click()
            #try:
             #   element_present = EC.presence_of_element_located((By.ID, 'Form1'))
              #  WebDriverWait(driver, timeout).until(element_present)
            #except TimeoutException:
             #   print ("Timed out waiting for page to load")
            #temp.append(driver.current_url)
            #driver.back()
        
#driver.quit()

#x = soup.find_all(href=re.compile("DoctorServiceQueryByDrName"))
#for division in soup.find_all('td'):
#    if division.text != '':
#        result.append(division.text)
'''
for index,division in enumerate(page.xpath("//table[@id='DoctorServiceListInSeveralDaysInput_GridViewDoctorServiceList']//tr")):
        if index == 0:

            res.append(division.xpath(".//th//text()"))
        else:
            res.append(division.xpath(".//td//span//text()"))
'''
import csv
f = open("doctor.csv","w")  
w = csv.writer(f)  
w.writerows(result)
f.close() 
