import json
import logging
import os
import sys

import pika
from bs4 import BeautifulSoup

from ..crawler.SiteMatcher import SiteMatcher
from ..crawler.Utils import Utils

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from ..log.Logger import Logger

RABBITMQ_USERNAME = "pi"
RABBITMQ_PASSWORD = "raspberry"

conn_timeout = 6
read_timeout = 20

connection = None
channel = None

def CreateAMQPConnection(conn):
    if conn is None or conn.is_closed:
        credentials = pika.PlainCredentials(RABBITMQ_USERNAME,RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.20',5672,'/', credentials))
        return connection
    return conn

def CreateSiteChannel(conn):
    if conn.is_open:
        channel = conn.channel()
        channel.queue_declare(queue='sitesQueue')
        return channel

class SiteProcessor:
    def __init__(self, sourceSite, browser, visitedSites = {}, threadId="main"):
        self.visitedSites = visitedSites
        self.sourceSite = sourceSite
        self.sitesToVisit = []
        self.threadId = threadId
        self.logger = Logger(threadId)
        self.siteMatcher = SiteMatcher(threadId)
        self.amqpConnection = CreateAMQPConnection(connection)
        self.channel = CreateSiteChannel(self.amqpConnection)
        self.browser = browser

    async def Process(self, _timeout=(6, 20)):
        try:
            
            page = await self.browser.newPage()

            # Navigate to the URL
            await page.goto(self.sourceSite)

             # Wait for the page to load and execute JavaScript
            await page.waitForSelector('head')  # Replace with a suitable selector

            # Extract data from the rendered page
            content = await page.evaluate('() => document.documentElement.innerHTML')  # Replace with your data extraction logic            
            soup = BeautifulSoup(content, 'html.parser')
            
            title = soup.find('title')
            if title == None:
                return None
            
            title = title.string
            if "404" in title:
                return None

            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            unfilteredWords = [word.strip() for word in text.splitlines()]
            words = []
            for word in unfilteredWords:
                if word is None:
                    continue
                words.extend(word.split())
                
            for link in soup.find_all(href=True):
                if link.has_attr('href'):
                    url = self.siteMatcher.GetFullSiteURL(link['href'], self.sourceSite)
                    if url is not None and url not in self.visitedSites and not Utils.isExcludedFileType(url):
                        self.sitesToVisit.append(url)
                        self.visitedSites[url] = True
                        
            message = self.CreateSiteMessage(self.sourceSite, title, words)
            self.PushSiteMessage(message)
        except BaseException as ex:
            self.logger.error("Could not connect to site ["+self.sourceSite+"], Reason="+str(ex))
            raise ex
            
    def FlushSitesToVisit(self):
        results = self.sitesToVisit
        self.sitesToVisit = []
        return results

    def CreateSiteMessage(self, url, title, words):
        return json.dumps({"title": title, "url": url, "words":list(words)})
    
    def PushSiteMessage(self, message):
        try:
            self.channel.basic_publish(exchange='',
                          routing_key='sitesQueue',
                          body=message)
        except:
            self.logger.error("AMQP Channel connection failed.")
