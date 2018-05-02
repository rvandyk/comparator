from django.urls import path

from . import views

app_name = 'mainapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('crawlpage/', views.crawlpage, name='crawlpage'),
    path('api/crawl', views.crawl, name='crawl'),
    path('crawlpage/download/<str:unique_id>/', views.download_crawl, name='download_crawl'),
    path('crawlpage/add_crawler', views.addCrawler, name="add_crawler")
]

#SETTINGS ?
