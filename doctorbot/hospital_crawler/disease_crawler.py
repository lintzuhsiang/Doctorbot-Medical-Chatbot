
# coding: utf-8

import requests
from bs4 import BeautifulSoup

class DiseaseCrawler(object):
    def __init__(self):
        self.disease = []

    def subPage(self, href):
        subres = requests.get(href)
        subres.encoding = 'utf-8'
        output = []
        subsoup = BeautifulSoup(subres.text)
        story = subsoup.select('#story_art_title')
        story_name = story[0].text[:len(story[0].text) - 10]
        print(story_name)
        output.append(story_name)  # append disease name
        card = subsoup.select('ul')
        for item in card[0].select('li'):
            title = item.select('span')[0]
            content = item.select('h3')[0]
            print(title.text, content.text)  # 英文名稱,就診科別,身體部位
            new_list = []
            for text in content.text.split(','):
                new_list.append(text)
            output.append(new_list)
        section = subsoup.select('section')
        sympton = section[0].select('h4')[1].findNext('p').text
        output.append(sympton.split('．'))  # append sympton
        output.append(href)  # append disease webpage
        return output

    def crawl_search_result(self):
        res = requests.get("https://health.udn.com/disease/disease_list")
        soup = BeautifulSoup(res.text)
        body = soup.select('#diagnosis_body')
        bodytext = str(body)
        start = 0
        result_list = []
        for i in range(bodytext.count("/disease/sole/")):
            indexStart = bodytext.find("/disease/sole/", start)
            indexEnd = bodytext.find('">', indexStart)
            href = "https://health.udn.com" + bodytext[indexStart:indexEnd]
            start = indexEnd + 2
            result_list.append(DiseaseCrawler.subPage(self, href))
        return result_list


def main():
    dc = DiseaseCrawler()
    dc.crawl_search_result()

if __name__ == '__main__':
    main()
