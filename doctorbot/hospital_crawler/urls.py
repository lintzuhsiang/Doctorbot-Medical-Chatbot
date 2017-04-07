from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from hospital_crawler import views

urlpatterns = [
    url(r'^movies/sync_disease_database_init$', views.movie_view.sync_disease_database_init),
    url(r'^movies/sync_division_database_init$', views.movie_view.sync_division_database_init),
    url(r'^movies/sync_movie_database_init$', views.movie_view.sync_movie_database_init),
    url(r'^movies/clear_movie$', views.movie_view.clear_movie),
    url(r'^movies/$', views.movie_view.MovieDetail.as_view()),
]   

urlpatterns = format_suffix_patterns(urlpatterns)
