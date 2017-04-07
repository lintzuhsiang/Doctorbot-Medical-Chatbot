from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.encoding import uri_to_iri
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes

#from hospital_crawler.models import Movie, MovieQuery
#from hospital_crawler.serializers import MovieSerializer
from doctorbot.hospital_crawler.division_crawler import DivisionCrawler
import csv

@api_view(['GET'])
def sync_division_database_init(requests):
	dc = DivisionCrawler()
	result_list = dc.crawl_search_result()
	f = open("division.csv","w")  
	w = csv.writer(f)  
	w.writerows(result_list)  
	f.close()
	return HttpResponse('creat_division_database_csv')

