from django.contrib import admin
from hospital_crawler.models import Movie

# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    list_display = ('yahoo_id', 'chinese_name', 'english_name', 'yahoo_release_data')
    search_fields = ('yahoo_id', 'chinese_name', 'english_name', 'yahoo_release_data')

admin.site.register(Movie, MovieAdmin)
