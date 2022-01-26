import sys
import os
import uuid
import json

import pika
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from bs4 import BeautifulSoup
from selenium import webdriver

from crawler.SiteMatcher import SiteMatcher
from crawler.Utils import Utils

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from log.Logger import Logger

conn_timeout = 6
read_timeout = 20
chromedriver = '.\crawler\chromedriver.exe'
 
options = webdriver.ChromeOptions()
options.add_argument('headless')
browser=webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
LOGGER.setLevel(logging.WARNING)

credentials = pika.PlainCredentials("root","Ae27!6CdJc1_thEQ9")
connection = None
channel = None

def CreateAMQPConnection(conn):
    if conn is None or conn.is_closed:
        credentials = pika.PlainCredentials("root","Ae27!6CdJc1_thEQ9")
        connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.22',5672,'/', credentials))
        return connection
    return conn

def CreateSiteChannel(conn):
    if conn.is_open:
        channel = conn.channel()
        channel.queue_declare(queue='sitesQueue')
        return channel

class SiteProcessor:
    def __init__(self, sourceSite, visitedSites = {}, threadId="main"):
        self.visitedSites = visitedSites
        self.sourceSite = sourceSite
        self.sitesToVisit = []
        self.threadId = threadId
        self.logger = Logger(threadId)
        self.siteMatcher = SiteMatcher(threadId)
        self.amqpConnection = CreateAMQPConnection(connection)
        self.channel = CreateSiteChannel(self.amqpConnection)

    def Process(self, _timeout=(6, 20)):
        try:
            browser.get(self.sourceSite)
            content = browser.page_source
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find('title').string

            for link in soup.find_all(href=True):
                if link.has_attr('href'):
                    url = self.siteMatcher.GetFullSiteURL(link['href'], self.sourceSite)
                    if url is not None and url not in self.visitedSites and not Utils.isExcludedFileType(url):
                        self.sitesToVisit.append(url)
                        self.visitedSites[url] = True
            message = self.CreateSiteMessage(self.sourceSite, title)
            self.PushSiteMessage(message)
        except BaseException as ex:
            self.logger.error("Could not connect to site ["+self.sourceSite+"], Reason="+str(ex))
            
    def FlushSitesToVisit(self):
        results = self.sitesToVisit
        self.sitesToVisit = []
        return results

    def CreateSiteMessage(self, url, title):
        return json.dumps({"title": title, "url": url})
    
    def PushSiteMessage(self, message):
        try:
            self.channel.basic_publish(exchange='',
                          routing_key='sitesQueue',
                          body=message)
        except:
            self.logger.error("AMQP Channel connection failed.")