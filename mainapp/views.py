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
import ast

import json 
import re
from fuzzywuzzy import fuzz

from mainapp.models import ScrapyItem
from mainapp.models import CrawlerModel, Comparator, ComparedData
from django.contrib import messages

from mainapp.forms import CrawlForm
from mainapp.forms import is_valid_url

from django.core.paginator import Paginator

# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')





def index(request):
    return render(request,'mainapp/index.html')

def crawlpage(request, toedit=""):
    items = ScrapyItem.objects.all()
    models = CrawlerModel.objects.all()
    try :
        jobs = scrapyd.list_jobs('default')['running']
    except:
        jobs = []

        
    if request.method == 'POST':       
        form = CrawlForm(request.POST)
        if form.is_valid():
            url = request.POST['url']
            name = request.POST['name']
            attributesJson = request.POST['xpath']  
            if toedit:         
                if CrawlerModel.objects.filter(id = int(toedit)).count():                
                    crawler = CrawlerModel.objects.get(id=toedit)                
            else:
                crawler = CrawlerModel()
            crawler.url = url
            crawler.attributesJson = attributesJson
            crawler.name = name
            crawler.save()
                
            return redirect('/crawlpage')

        return render(request, 'mainapp/crawlpage.html',  {'form' : form, 'items' : items,'models' : models,'jobs' : jobs, 'showmodal' : True })

    else:    

        if toedit:
            o = CrawlerModel.objects.get(id=toedit)
            form = CrawlForm()
            form['url'].initial = o.url
            form['name'].initial = o.name
            form['xpath'].initial = o.attributesJson

            
            return render(request, 'mainapp/crawlpage.html', {'editid' : toedit, 'form' : form, 'items' : items,'models' : models,'jobs' : jobs, 'showmodal' : True })

        else:
            form = CrawlForm()    
        return render(request, 'mainapp/crawlpage.html', {'form' : form, 'items' : items,'models' : models,'jobs' : jobs })






def comparatorpage(request):
    comparators = Comparator.objects.all()
    datas = ScrapyItem.objects.all()
    compared_data = ComparedData.objects.all()
    return render(request, 'mainapp/comparatorpage.html', {'datas': datas, 'comparators' : comparators, 'compared_data' : compared_data})

def remove_crawler(request, id):
    model = CrawlerModel.objects.get(id=id).delete()
    return redirect('/crawlpage')

def remove_comparator(request, id):
    model = Comparator.objects.get(id=id).delete()
    return redirect('/comparatorpage')

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

def remove_data(request, unique_id):
    item = ScrapyItem.objects.filter(unique_id=unique_id)
    item.delete()
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


def format_file(f):    
    f = f.replace("\\\\\\\\", "\\")    
    return f

def extract_prices(e):
    res = []
    for i in e['price']:
        i = i.replace(" ", "")
        p = re.findall("\d+", str(i))[0]
        res.append(p)
    return res

def string_sim(item1, item2, f1, f2, treshold):    
    if item1[f1] and item2[f2]:              
        ratio = fuzz.ratio(item1[f1][0], item2[f2][0])
        if (ratio > treshold):                
            return ratio
        else:
            return 0
    else:
        return 0

def price_sim(item1, item2, f1, f2, rate):    
    if item1[f1] and item2[f2]:
        prices1 = extract_prices(item1)             
        prices2 = extract_prices(item2)
        res = 0 
        nbcomp = 0
        for p1 in prices1:
            for p2 in prices2:
                if float(p1) > (float(p2) - (float(p2)*rate)) and float(p1) < (float(p2) + (float(p2)*rate)):
                    res = res + 1 
        return res/(len(prices1)*len(prices2))*100
    else:
        return 0



def compare(request):

    if request.method == 'POST':
    

        comp = Comparator.objects.get(id=request.POST['id'])
        process_list = ast.literal_eval(comp.fields)

        
        crawler1 = request.POST['data1']
        crawler2 = request.POST['data2']

        
        #[["Keyword analysis", "titre", "title"], ["Price analysis", "price", "price"]]    

        #process_list = [('titre', 'titre', 'string_sim', 70), ('price', 'price', 'price_sim', 15/100)]
        json1 = ScrapyItem.objects.get(id=crawler1)
        json2 = ScrapyItem.objects.get(id=crawler2)

        if comp.model1 != json1.crawler or comp.model2 != json2.crawler:        
            comparators = Comparator.objects.all()
            datas = ScrapyItem.objects.all()
            return render(request, 'mainapp/comparatorpage.html', {'datas': datas, 'comparators' : comparators, 'errors': 'Dataset unreadable'})
        


        #json1 = open(file1, 'r')
        #json2 = open(file2, 'r')

        data1 = ast.literal_eval(format_file(json1.data))
        data2 = ast.literal_eval(format_file(json2.data))


        bigboi = []
        i=0
        for d1 in data1:      
            item1 = ast.literal_eval(d1)    
            for d2 in data2:   
                i=i+1                 
                item2 = ast.literal_eval(d2)
                indicator = True
                to_append = {"item1" : item1, "item2": item2}   
                score = 0            
                for e in process_list:            
                    if e[0] == "string_sim":        
                        p = string_sim(item1,item2,e[1],e[2],60)                 
                        to_append[e[1]+"_"+e[2]+"_string_sim"] = p  
                        if (p == 0):                       
                            indicator = False  
                        
                        score = score + p

                    elif e[0] == "price_sim":
                        p = price_sim(item1,item2,e[1],e[2],15/100) 
                        to_append[e[1]+"_"+e[2]+"_price_sim"] = p
                        if (p == 0):                    
                            indicator = False      
                        score = score + p

                score = score/len(process_list)  
                to_append['score'] = score                        
                
                if indicator:
                    bigboi.append(to_append)
                
                print(str(i) + "/" + str(len(data1)*len(data2))) 


        sortedboi = sorted(bigboi, key=lambda k: (sum(k[e[1]+"_"+e[2]+"_"+e[0]]/len(process_list) for e in process_list)), reverse=True) 
        o = ComparedData()
        o.data = sortedboi
        o.comparator = comp
        o.item1 = json1
        o.item2 = json2
        o.save()
        request.session['cResult'] = sortedboi

    if request.method == 'GET':
        sortedboi = request.session['cResult']

    paginator = Paginator(sortedboi, 10)
    page = request.GET.get('page')
    plist = paginator.get_page(page)
    
    return render(request, 'mainapp/comparedproducts.html', {'data' : plist})



def showComp(request, id):
    c = ComparedData.objects.get(id=id)   
    paginator = Paginator(ast.literal_eval(c.data), 10)  
    page = request.GET.get('page')
    plist = paginator.get_page(page)   
    return render(request, 'mainapp/comparedproducts.html', {'data' : plist})

def removeComp(request,id):
    c = ComparedData.objects.get(id=id)  
    c.delete()
    return redirect('/comparatorpage')
    



    


    