from http.client import HTTPResponse
from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
from django.http import HttpResponse
import json
import requests


from mainapp.models import ScrapyItem
from mainapp.models import CrawlerModel, Comparator

# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')





def index(request):
    return render(request,'mainapp/index.html')

def crawlpage(request):
    items = ScrapyItem.objects.all()
    models = CrawlerModel.objects.all()
    try :
        jobs = scrapyd.list_jobs('default')['running']
    except:
        jobs = []
    return render(request, 'mainapp/crawlpage.html', {'items' : items,'models' : models,'jobs' : jobs })

def comparatorpage(request):
    comparators = Comparator.objects.all()
    return render(request, 'mainapp/comparatorpage.html', {'comparators' : comparators})

def remove_crawler(request, id):
    model = CrawlerModel.objects.get(id=id).delete()
    return redirect('/crawlpage')

def addComparatorForm(request):
    if 'crawler1' in request.POST and 'crawler2' in request.POST:
        crawlersOk = True
        crawler1 = CrawlerModel.objects.get(name=request.POST['crawler1'])
        crawler2 = CrawlerModel.objects.get(name=request.POST['crawler2'])
        attributes1 = json.loads(crawler1.attributesJson)
        attributes2 = json.loads(crawler2.attributesJson)
    elif 'count' in request.POST:
        relations = []
        count = request.POST['count']
        name = request.POST['name']
        crawler1 = CrawlerModel.objects.get(id=request.POST['crawler1id'])
        crawler2 = CrawlerModel.objects.get(id=request.POST['crawler2id'])
        for i in range(0,int(count)+1):
            if 'typeselect'+str(i) in request.POST:
                relations.append((request.POST['typeselect'+str(i)],request.POST['crawlerselect1'+str(i)],request.POST['crawlerselect2'+str(i)]))

        comparator = Comparator()
        comparator.name = name
        comparator.model1 = crawler1
        comparator.model2 = crawler2
        comparator.fields = json.dumps(relations)
        comparator.save()
        return redirect('/comparatorpage')

    else:
        crawler1 = ''
        crawler2 = ''
        crawlersOk = False
        attributes1 = []
        attributes2 = []

    crawlers = CrawlerModel.objects.all()
    return render(request, 'mainapp/addcomparator.html', {'attributes1' : attributes1, 'attributes2' : attributes2,
                                                          'crawlers' : crawlers, 'crawlersOK': crawlersOk,
                                                          'crawler1':crawler1, 'crawler2' : crawler2})

def download_crawl(request, unique_id):
    item = ScrapyItem.objects.filter(unique_id=unique_id).values()
    response = HttpResponse(item, content_type = 'application/json')
    response['Content-Disposition'] = 'attachment; filename=export.json'
    return response

def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True

def is_valid_json(jsonfile):
    try :
        json.loads(jsonfile)
    except ValueError as e:
        return False

    return True

@require_http_methods(['POST'])
def addCrawler(request):

        url = request.POST['url_sitemap']
        name = request.POST['name']
        attributesJson = request.POST['attributesJson']
        print(url)
        print(name)
        print(attributesJson)

        if (not is_valid_url(url)) or (not is_valid_json(attributesJson)):
            print(str(is_valid_json(attributesJson)))
            print(str(is_valid_url(url)))
            print('error')
            return redirect('/crawlpage')

        crawler = CrawlerModel()
        crawler.url = url
        crawler.attributesJson = attributesJson
        crawler.name = name
        crawler.save()
        print('saved')
        return redirect('/crawlpage')


@require_http_methods(['POST'])
def editCrawler(request, id):

        url = request.POST['url_sitemap']
        name = request.POST['name']
        attributesJson = request.POST['attributesJson']
        print(url)
        print(name)
        print(attributesJson)

        if (not is_valid_url(url)) or (not is_valid_json(attributesJson)):
            print(str(is_valid_json(attributesJson)))
            print(str(is_valid_url(url)))
            print('error')
            return redirect('/crawlpage')

        crawler = CrawlerModel.objects.get(id=id)
        crawler.url = url
        crawler.attributesJson = attributesJson
        crawler.name = name
        crawler.save()
        print('saved')
        return redirect('/crawlpage')

def launchCrawler(request, id):
    model = CrawlerModel.objects.get(id=id)
    post_data = {'url': model.url, 'attributesJson' : model.attributesJson, 'id' : id}
    requests.post('http://localhost:8000/api/crawl', data=post_data)
    model.running = True
    model.save()
    return redirect('/crawlpage')

@csrf_exempt
@require_http_methods(['POST', 'GET'])  # only get and post
def crawl(request):
    # Post requests are for new crawling tasks
    if request.method == 'POST':

        url = request.POST.get('url', None)  # take url comes from client. (From an input may be?)
        attributesJson = request.POST.get('attributesJson')
        id = request.POST.get('id')


        if not url:
            return JsonResponse({'error': 'Missing  args'})

        if not is_valid_url(url):
            return JsonResponse({'error': 'URL is invalid'})

        domain = urlparse(url).netloc  # parse the url and extract the domain
        unique_id = str(uuid4())  # create a unique ID.

        # This is the custom settings for scrapy spider.
        # We can send anything we want to use it inside spiders and pipelines.
        # I mean, anything
        settings = {
            'unique_id': unique_id,  # unique ID for each record for DB
            'crawler_id': id,
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        # Here we schedule a new crawling task from scrapyd.
        # Notice that settings is a special argument name.
        # But we can pass other arguments, though.
        # This returns a ID which belongs and will be belong to this task
        # We are goint to use that to check task's status.
        task = scrapyd.schedule('default', 'icrawler',
                                settings=settings, url=url, domain=domain, attributesJson=attributesJson)

        return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})

    # Get requests are for getting result of a specific crawling task
    elif request.method == 'GET':
        # We were passed these from past request above. Remember ?
        # They were trying to survive in client side.
        # Now they are here again, thankfully. <3
        # We passed them back to here to check the status of crawling
        # And if crawling is completed, we respond back with a crawled data.
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        # Here we check status of crawling that just started a few seconds ago.
        # If it is finished, we can query from database and get results
        # If it is not finished we can return active status
        # Possible results are -> pending, running, finished
        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                # this is the unique_id that we created even before crawling started.
                item = ScrapyItem.objects.get(unique_id=unique_id)
                return JsonResponse({'data': item.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})
