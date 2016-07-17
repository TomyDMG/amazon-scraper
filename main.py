import requests
import re
import ConfigParser
import random
import string
import sqlite3
from lxml import html
from google import search

db = sqlite3.connect('cache.db')


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
    if html_tree.xpath('//img[@src="https://images-na.ssl-images-amazon.com/images/G/01/error/title._TTD_.png"]'):
        status = 'BLOCKED'
        return status
    elif html_tree.xpath('//div[@id="outOfStock"]'):
        status = 'ABANDONED'
        return status
    else:
        return False


def googleCheck(asin):
    count = 0
    for url in search(asin, stop=config.getint('section', 'google_min_results')):
        count += 1
    if count != 0:
        return True
    else:
        return False


def isASINAlreadyChecked(asin):
    cur = db.cursor()
    cur.execute("SELECT * FROM amazon_items WHERE asin = '%s'" % asin)
    if cur.fetchall():
        return True
    else:
        return False


def writeASINToDB(asin):
    cur = db.cursor()
    url = 'https://www.amazon.com/dp/' + asin
    status = checkASIN(asin)
    cur.execute("INSERT INTO amazon_items VALUES ('%s', '%s', '%s')" % (asin, url, status))
    db.commit()

asin = generateASIN()
asin = 'B00ATDPHTC'
checkASIN(asin)
asin
checkUrl('https://www.amazon.com/dp/B00ATDPHTC')
checkUrl('https://www.amazon.com/dp/B00QKGAOSQ')
checkUrl('https://www.amazon.com/dp/B00GOVNISHE')
