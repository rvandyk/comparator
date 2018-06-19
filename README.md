# Comparator

## Technical details

The all system works with virtualenv, meaning you can launch it very simply from any unix environment without installing specific python dependencies.

The crawling system uses Scrapy and Scrapyd

The web application works with Django

## How does it work

### Step 1 : Creating a crawler
The crawler is the application that will go through a website and extract every information you need.
It is defined by:
* a name
* a URL
* a XPath JSON

---
#### The XPath JSON
This JSON entry actually tells your crawler what you want to be extracted, and its location on websites. It uses the official XPath language. Fields **title** and **price** are mandatory.
For instance on Axess website :
```json
{"title": "//div[@id='title']/h1/text()",
"price": "//div[@id='tarification']/p/strong/text()"}
```
---

Once a crawler is defined, you can run it and obtain a JSON-file of all the results extracted from the website. This file is stored in the database.

### Step 2 : Creating a comparator
A comparator is an application that will compare 2 crawler results. It is defined by:
* a name
* a crawler1 
* a crawler2
* a list of processing rules

---
#### Processing rules
For the moment, two rules are available:
* string_sim : compares the similarity between two texts (titles, descriptions, etc)
* price_sim : compares the similarity of prices, allowing a 15% difference
---
Once a comparator is defined, you can run it by loading 2 crawler results in it (one for crawler1 and one for crawler2), and obtain a json containing all matching entries.


