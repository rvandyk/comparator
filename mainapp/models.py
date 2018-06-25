from django.db import models
import json
from django.utils import timezone   

# Create your models here.

class CrawlerModel(models.Model):
    name = models.TextField()
    url = models.TextField()
    attributesJson = models.TextField()
    running = models.BooleanField(default=False)
    

class ScrapyItem(models.Model):
    unique_id = models.CharField(max_length=100, null=True)
    data = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    crawler = models.OneToOneField(CrawlerModel, related_name='crawler', on_delete=models.CASCADE)

    @property
    def to_dict(self):
        data = {
            'data' : json.loads(self.data),
            'date' : self.date
        }
        return data

    def __str__(self):
        return self.unique_id


class Comparator(models.Model):
    name = models.TextField()
    model1 = models.ForeignKey(CrawlerModel, related_name="model1", on_delete=models.CASCADE)
    model2 = models.ForeignKey(CrawlerModel, related_name="model2", on_delete=models.CASCADE)
    fields = models.TextField()    
    running = models.BooleanField(default=False)

class ComparedData(models.Model):
    date = models.DateTimeField(default=timezone.now)
    data = models.TextField()
    comparator = models.OneToOneField(Comparator, on_delete=models.CASCADE)
    




