from rest_framework import serializers

from hospital_crawler.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = (
            'yahoo_id',
            'chinese_name',
            'english_name',
            'yahoo_poster',
            'yahoo_trailer',
            'yahoo_release_data',
            'yahoo_category',
            'yahoo_length',
            'yahoo_director',
            'yahoo_actor',
            'yahoo_company',
            'yahoo_official_website',
            'yahoo_description'
        )