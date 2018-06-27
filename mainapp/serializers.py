from rest_framework import serializers 
from mainapp.models import CrawlerModel, MainCrawler, Comparator, ScrapyItem, ComparedData
 
class CrawlerSerializer(serializers.ModelSerializer):
 
    class Meta: 
        model = CrawlerModel
        fields = '__all__'

class MainCrawlerSerializer(serializers.ModelSerializer):
 
    class Meta: 
        model = MainCrawler
        fields = '__all__'

class ComparatorSerializer(serializers.ModelSerializer):
 
    class Meta: 
        model = Comparator
        fields = '__all__'

class ComparedDataSerializer(serializers.ModelSerializer):
 
    class Meta: 
        model = ComparedData
        fields = '__all__'

class ScrapyItemSerializer(serializers.ModelSerializer):
 
    class Meta: 
        model = ScrapyItem
        fields = '__all__'