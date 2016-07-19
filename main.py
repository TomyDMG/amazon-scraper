import requests
import ConfigParser
import random
import string
import sqlite3
import threading
import zipfile
from lxml import html
from google import search
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class myHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Description', 'File Transfer')
        self.send_header('Content-type', 'application/octet-stream')
        self.send_header('Content-Disposition',
                         'attachment; filename=amazon_bad_items.zip')
        self.send_header('Content-Transfer-Encoding', 'binary')
        self.send_header('Expires', '0')
        self.send_header('Cache-Control', 'must-revalidate')
        self.send_header('Pragma', 'public')
        self.end_headers()
        db = sqlite3.connect('cache.db')
        cur = db.cursor()
        allDB = cur.execute('SELECT * FROM amazon_items').fetchall()
        dbLenght = allDB.__len__()
        textFile = open('amazon.txt', 'w')
        for i in range(0, dbLenght):
            textFile.write(allDB[i].__str__() + '\n')
        textFile.close()
        db.close()
        with zipfile.ZipFile('amazon.zip', 'w') as zip:
            zip.write('amazon.txt')
        self.wfile.write(open('amazon.zip').read())
        return


config = ConfigParser.RawConfigParser()
config.readfp(open('defaults.cfg'))
google_scan_urls = config.getboolean('section', 'google_scan_urls')
google_min_results = config.getint('section', 'google_min_results')
threads_count = config.getint('section', 'threads_count')
PORT = config.getint('section', 'PORT_NUMBER')


def generateASIN():
    asin = 'B00' + \
        ''.join(random.choice(string.ascii_uppercase + string.digits)
                for _ in range(7))
    return asin


def checkASIN(asin):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
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
    try:
        count = 0
        for url in search(asin, tld='ru', stop=google_min_results, pause=20.0):
            count += 1
        if count >= google_min_results - 1:
            return True
        else:
            print 'no one result in google search for %s' % asin
            return False
    except Exception:
        print 'Bad response from google'
        return False


def isASINAlreadyChecked(asin):
    db = sqlite3.connect('cache.db')
    cur = db.cursor()
    cur.execute("SELECT * FROM amazon_items WHERE asin = '%s'" % asin)
    if cur.fetchall():
        db.close()
        return True
    else:
        db.close()
        return False


def writeASINToDB(asin):
    db = sqlite3.connect('cache.db')
    cur = db.cursor()
    url = 'https://www.amazon.com/dp/' + asin
    status = checkASIN(asin)
    cur.execute("INSERT INTO amazon_items VALUES ('%s', '%s', '%s')" %
                (asin, url, status))
    db.commit()
    db.close()


def runServer():
    try:
        server = HTTPServer(('', PORT), myHandler)
        # Wait forever for incoming htto requests
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()


def scraper():
    while 1:
        asin = generateASIN()
        if not isASINAlreadyChecked(asin):
            if googleCheck(asin):
                checkASIN(asin)
                writeASINToDB(asin)
                print '%s in da base. %s' % (asin, checkASIN(asin))
            # else: print 'no one result in google search for %s' % asin
        else:
            print '%s already in base ' % asin


def main():
    for i in range(0, threads_count):
        t = threading.Thread(target=scraper)
        t.start()

    httpServThread = threading.Thread(target=runServer)
    httpServThread.start()


if __name__ == "__main__":
    main()
