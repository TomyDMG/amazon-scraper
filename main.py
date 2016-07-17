import requests
import re
import ConfigParser
import random
import string
import anydbm
from lxml import html
from google import search

#db = anydbm.open('cache', 'n')
config = ConfigParser.RawConfigParser()
config.readfp(open('defaults.cfg'))
google_scan_urls = config.getboolean('section', 'google_scan_urls')
threads_count = config.getint('section', 'threads_count')


def generateASIN():
    asin = 'B00' + \
        ''.join(random.choice(string.ascii_uppercase + string.digits)
                for _ in range(7))
    return asin


def checkASIN(asin):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    url = 'https://www.amazon.com/dp/' + asin
    page = requests.get(url, headers=headers)
    html_tree = html.fromstring(page.content)
    if html_tree.xpath('//img[@src="https://images-na.ssl-images-amazon.com/images/G/01/error/title._TTD_.png"]') or html_tree.xpath('//div[@id="outOfStock"]'):
        return True
    else:
        return False


def googleCheck():
    count = 0
    for url in search(generateASIN(), stop=config.getint('section', 'google_min_results')):
        print (url)
        count += 1
        print count


asin = generateASIN()
checkUrl(asin)
asin
checkUrl('https://www.amazon.com/dp/B00ATDPHTC')
checkUrl('https://www.amazon.com/dp/B00QKGAOSQ')
checkUrl('https://www.amazon.com/dp/B00GOVNISHE')
