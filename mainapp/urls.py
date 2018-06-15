from django.urls import path

from . import views

app_name = 'mainapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('crawlpage/', views.crawlpage, name='crawlpage'),
    path('crawlpage/<int:toedit>', views.crawlpage, name='crawlpage'),
    path('api/crawl', views.crawl, name='crawl'),
    path('crawlpage/download/<str:unique_id>/', views.download_crawl, name='download_crawl'), 
    path('crawlpage/remove_data/<str:unique_id>/', views.remove_data, name='remove_data'),   
    path('crawlpage/launch_crawler/<int:id>/', views.launchCrawler, name="launch_crawler"),
    path('crawlpage/remove_crawler/<int:id>/', views.remove_crawler, name="remove_crawler"),
    path('crawlpage/edit_crawler/<int:id>/', views.editCrawler, name="edit_crawler"),

    path('comparatorpage/', views.comparatorpage, name='comparatorpage'),
    path('comparatorpage/addcomparator', views.addComparatorForm, name="add_comparator_form"),
    path('comparatorpage/launchcomparator', views.compare, name="launch_comparator"),
    path('comparatorpage/remove_comparator/<int:id>', views.remove_comparator, name="remove_comparator")



]

#SETTINGS ?
