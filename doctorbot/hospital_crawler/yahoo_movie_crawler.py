import re
import time
from multiprocessing.pool import ThreadPool
from operator import itemgetter

import requests
from bs4 import BeautifulSoup


class YahooMovieCrawler(object):
    def __init__(self):
        self.movies = []

    def crawl_search_result(self, query):
        url = 'https://tw.movies.yahoo.com/moviesearch_result.html?k={0}'.format(query)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        movies = []
        elems = []
        elems_row = soup.find_all('div', class_='clearfix row')
        elems_row_last = soup.find_all('div', class_='clearfix row_last')
        elems.extend(elems_row)
        elems.extend(elems_row_last)
        for elem in elems:
            movie = {}
            movie['chinese_name'] = elem.find('div', class_='text').find('h4').text
            movie['english_name'] = elem.find('div', class_='text').find('h5').text
            movie['yahoo_movie_link'] = elem.find('div', class_='img').find('a')['href']
            movie['yahoo_id'] = self.find_movie_id(movie['yahoo_movie_link'])
            movie['yahoo_poster'] = elem.find('div', class_='img').find('img')['src'].replace('mpost4', 'mpost')
            release_data = elem.find('div', class_='text').find('span').text
            movie['yahoo_release_data'] = self.change_time_format(release_data)
            movie['yahoo_favorite'] = elem.find('div', class_='bd').find('em').text
            movie['yahoo_description'] = elem.find('p').text.replace(u'...詳全文', '')
            movie['yahoo_trailer'] = elem.find('li', class_='trailer').find('a')['href']
            movies.append(movie)
        # for m in movies:
        #     print (m['yahoo_id'], m['chinese_name'], m['yahoo_description'])
        return movies

    def crawl_movie_thisweek_comingsoon(self, mode):
        if mode == 'movie_thisweek':
            url = 'https://tw.movies.yahoo.com/movie_thisweek.html'
        elif mode == 'movie_comingsoon':
            url = 'https://tw.movies.yahoo.com/movie_comingsoon.html'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        movies = []
        elems = []
        elems_group_date = soup.find('div', class_='group-date')
        elems_row = soup.find_all('div', class_='clearfix row')
        elems_row_last = soup.find_all('div', class_='clearfix row_last')
        elems.extend(elems_row)
        elems.extend(elems_row_last)
        for elem in elems:
            movie = {}
            movie['chinese_name'] = elem.find('div', class_='text').find('h4').text
            movie['english_name'] = elem.find('div', class_='text').find('h5').text
            movie['yahoo_movie_link'] = elem.find('div', class_='img').find('a')['href']
            movie['yahoo_id'] = self.find_movie_id(movie['yahoo_movie_link'])
            movie['yahoo_poster'] = elem.find('div', class_='img').find('img')['src'].replace('mpost4', 'mpost')
            release_data = elem.find('div', class_='text').find('span').text
            movie['yahoo_release_data'] = self.change_time_format(release_data)
            try:
                movie['yahoo_favorite'] = elem.find('div', class_='bd').find('em').text
            except AttributeError:
                movie['yahoo_favorite'] = ''
            movie['yahoo_description'] = elem.find('p').text.replace(u'...詳全文', '').replace('\n', '')
            if mode == 'movie_thisweek':
                movie['date_new_film'] = elems_group_date.text
            elif mode == 'movie_comingsoon':
                movie['date_comingsoon'] = elems_group_date.text
            movies.append(movie)

        # for m in movies:
        #     print (m['yahoo_id'], m['chinese_name'], m['yahoo_description'])
        return movies

    def crawl_movie_info(self, id):
        url = 'https://tw.movies.yahoo.com/movieinfo_main.html/id={0}'.format(id)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        if u'Yahoo奇摩電影' in soup.title.text:
            elems = soup.find_all('div', class_='item clearfix')
            yahoo_trailer = soup.find_all('li', class_='trailer')
            movie = {}
            movie['yahoo_id'] = id
            movie['chinese_name'] = elems[0].find('div', class_='text bulletin').find('h4').text
            movie['english_name'] = elems[0].find('div', class_='text bulletin').find('h5').text
            movie['yahoo_poster'] = elems[0].find('div', class_='border').find('a')['href']
            if len(yahoo_trailer) > 0:
                movie['yahoo_trailer'] = yahoo_trailer[0].find('a')['href']
            else:
                movie['yahoo_trailer'] = ''
            informations = elems[0].find_all('span', class_='dta')
            movie['yahoo_release_data'] = informations[0].text
            movie['yahoo_category'] = informations[1].text
            movie['yahoo_length'] = informations[2].text
            movie['yahoo_director'] = informations[3].text
            movie['yahoo_actor'] = informations[4].text
            movie['yahoo_company'] = informations[5].text
            movie['yahoo_official_website'] = informations[6].text
            try:
                movie['yahoo_description'] = elems[2].find('div', class_='text').text
            except AttributeError:
                movie['yahoo_description'] = elems[2].find('div', class_='text show').text
            return movie
        else:
            return None

    def crawl_taipei_box_office(self):
        url = 'https://tw.movies.yahoo.com/chart.html?cate=taipei'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        elems = []
        elems_other = soup.find_all('tr')
        elems.extend(elems_other)

        elems_time = soup.find('td', colspan='6')
        box_time = self.change_rank_time_format(elems_time.text)

        # want to detect u' '
        elems[3].find('td', class_='c1').text.replace('\n', '')
        elems[3].find('td', class_='c2').text.replace('\n', '')
        movie1 = elems[3].find('td', class_='c3').text.split('\n')
        movie1 = filter(lambda x: x is not u'' and x is not u' ', movie1)

        taipei_rank = []
        for elem in elems:
            movie_rank_info = {}
            try:
                movie_rank_info['box_time'] = box_time
                movie_rank_info['this_week_rank'] = elem.find('td', class_='c1').text.replace('\n', '')
                movie_rank_info['last_week_rank'] = elem.find('td', class_='c2').text.replace('\n', '')
                movie = elem.find('td', class_='c3').text.split('\n')
                movie = filter(lambda x: x is not u'' and x is not movie1[0], movie)
                movie_rank_info['chinese_name'] = movie[0]
                movie_rank_info['english_name'] = movie[1]
                taipei_rank.append(movie_rank_info)
            except AttributeError:
                pass
        # for t in taipei_rank:
        #     print (t['chinese_name'], t['this_week_rank'], t['last_week_rank'], t['box_time'])
        return taipei_rank

    def store_movies(self, movie):
        if movie is not None:
            self.movies.append(movie)

    def crawl_all_yahoo_movies(self, start_id, end_id):
        start_time = time.time()
        pool = ThreadPool(processes=8)
        for i in range(start_id, end_id + 1):
            pool.apply_async(self.crawl_movie_info, (i, ), callback=self.store_movies)
        pool.close()
        pool.join()
        movies = sorted(self.movies, key=itemgetter('yahoo_id'))
        for m in movies:
            try:
                pass
                print (m['yahoo_id'], m['chinese_name'], m['yahoo_director'])
            except TypeError:
                print ('The movie not found')
        end_time = time.time()
        print ("The execution time takes %s seconds." % (end_time - start_time))
        return movies

    def change_time_format(self, release_data):
        pat_time = '\d+-\d+-\d+'
        match = re.search(pat_time, release_data)
        if match is None:
            return release_data
        else:
            return match.group(0)

    def change_rank_time_format(self, rank_time):
        # 2016-12-31 ~ 2017-01-01
        # 2017-01-07 ~ 01-08
        pat_time = '\d+-\d+-\d+ ~ \d+-\d+-\d+'
        match = re.search(pat_time, rank_time)
        if match is None:
            return rank_time
        else:
            rank_time = match.group(0).split()
            return rank_time[0] + ' ' + rank_time[2]

    def find_movie_id(self, url):
        pat_id = '/id=\d+'
        match = re.search(pat_id, url)
        if match is None:
            return url
        else:
            return match.group(0).replace('/id=', '')


def main():
    ymc = YahooMovieCrawler()
    # ymc.crawl_search_result('刺客')
    # ymc.crawl_movie_thisweek_comingsoon('movie_thisweek')
    #ymc.crawl_movie_thisweek_comingsoon('movie_comingsoon')
    # m = ymc.crawl_movie_info(6530)
    # print m['chinese_name'], m['yahoo_release_data'], m['yahoo_description'], m['yahoo_trailer']
    ymc.crawl_all_yahoo_movies(1, 10)
    # ymc.crawl_taipei_box_office()
    # ymc.change_time_format('上映日期：2013-04-30')
    # a, b = ymc.change_rank_time_format('統計時間：2016-12-31 ~ 2017-01-01')


if __name__ == '__main__':
    main()
