import requests
import re
import ConfigParser
import random
import string
from lxml import html
from google import search

config = ConfigParser.RawConfigParser()
config.readfp(open('defaults.cfg'))
google_scan_urls = config.getboolean('section', 'google_scan_urls')
threads_count = config.getint('section', 'threads_count')


def generateUrl():
    asin = 'B00' + \
        ''.join(random.choice(string.ascii_uppercase + string.digits)
                for _ in range(7))
    return 'https://www.amazon.com/dp' + asin


def checkUrl(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url, headers=headers)
    html_tree = html.fromstring(page.content)
    if html_tree.xpath('//img[@src="https://images-na.ssl-images-amazon.com/images/G/01/error/title._TTD_.png"]') or html_tree.xpath('//div[@id="outOfStock"]'):
        return True
    else:
        return False

generateUrl()
checkUrl(generateUrl())
checkUrl('https://www.amazon.com/dp/B00ATDPHTC')
checkUrl('https://www.amazon.com/dp/B00QKGAOSQ')
checkUrl('https://www.amazon.com/dp/B00GOVNISHE')


def googleCheck():
    for url in search(asin, stop=config.getint('section', 'google_min_results')):
        print(url)
