from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.encoding import uri_to_iri
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes

from hospital_crawler.models import Movie, MovieQuery
from hospital_crawler.serializers import MovieSerializer
from hospital_crawler.yahoo_movie_crawler import YahooMovieCrawler

from hospital_crawler.division_crawler import DivisionCrawler
from hospital_crawler.disease_crawler import DiseaseCrawler
import csv

class MovieDetail(generics.ListAPIView):
    serializer_class = MovieSerializer

    def get_queryset(self):
        queryset = Movie.objects.all()
        q = uri_to_iri(self.request.query_params.get('q', None))
        MovieQuery.objects.create(
            query=q
        )
        if q:
            for word in q.split():
                queries = Q(chinese_name__icontains=word) | Q(
                    english_name__icontains=word)
                queryset = queryset.filter(queries).order_by('-id')

        return queryset


@api_view(['GET'])
def sync_movie_database_init(requests):
    ymc = YahooMovieCrawler()
    Movie.objects.all().delete()

    movies = ymc.crawl_all_yahoo_movies(1, 20)
    for movie in movies:
        Movie.objects.create(
            yahoo_id=movie['yahoo_id'],
            chinese_name=movie['chinese_name'],
            english_name=movie['english_name'],
            yahoo_poster=movie['yahoo_poster'],
            yahoo_trailer=movie['yahoo_trailer'],
            yahoo_release_data=movie['yahoo_release_data'],
            yahoo_category=movie['yahoo_category'],
            yahoo_length=movie['yahoo_length'],
            yahoo_director=movie['yahoo_director'],
            yahoo_actor=movie['yahoo_actor'],
            yahoo_company=movie['yahoo_company'],
            yahoo_official_website=movie['yahoo_official_website'],
            yahoo_description=movie['yahoo_description']
        )
    return HttpResponse('sync_movie_database_init')


@api_view(['GET'])
def clear_movie(requests):
    Movie.objects.all().delete()
    return HttpResponse('Clear movie data')


@api_view(['GET'])
def sync_division_database_init(requests):
    dc = DivisionCrawler()
    result_list = dc.crawl_search_result()
    f = open("division.csv", "w")
    w = csv.writer(f)
    w.writerows(result_list)
    f.close()
    return HttpResponse('created_division_database_csv')


@api_view(['GET'])
def sync_disease_database_init(requests):
    dc = DiseaseCrawler()
    result_list = dc.crawl_search_result()
    f = open("disease.csv", "w")
    w = csv.writer(f)
    w.writerows(result_list)
    f.close()
    return HttpResponse('created_disease_database_csv')
