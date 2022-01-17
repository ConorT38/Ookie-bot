import sys
import os
import uuid
import json

import pika
import asyncio
import requests

from crawler.SiteMatcher import SiteMatcher

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from log.Logger import Logger

conn_timeout = 6
read_timeout = 20
credentials = pika.PlainCredentials("root","Ae27!6CdJc1_thEQ9")
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.22',5672,'/', credentials))
channel = connection.channel()
channel.queue_declare(queue='sitesQueue')

class SiteProcessor:
    def __init__(self, sourceSite, visitedSites = {}, threadId="main"):
        self.visitedSites = visitedSites
        self.sourceSite = sourceSite
        self.sitesToVisit = []
        self.threadId = threadId
        self.logger = Logger(threadId)
        self.siteMatcher = SiteMatcher(threadId)

    async def Process(self, _timeout=(6, 20)):
        content = requests.get(self.sourceSite, timeout=_timeout).text

        tmpFilePath = self.CreateFileFromResponse(content)
        
        title = ""
        # we need to read the tmpFile line-by-line and check for urls, title, etc.
        for line in open(tmpFilePath, "r", encoding="utf-8", newline="\n").readlines():
            if not title:
                title = await self.siteMatcher.GetSiteTitleMatch(line)
            await self.GetUrlMatches(line)
        
        queueMessage = json.dumps({"title": title, "url": self.sourceSite})
        channel.basic_publish(exchange='',
                      routing_key='sitesQueue',
                      body=queueMessage)
            
        os.remove(tmpFilePath)

    async def FlushSitesToVisit(self):
        results = self.sitesToVisit
        self.sitesToVisit = []
        return results

    async def GetUrlMatches(self, data):
        try:
            currentSiteMatches = await self.siteMatcher.GetCurrentSiteLinkMatches(data, self.sourceSite, self.visitedSites)
            fullLinkMatches = await self.siteMatcher.GetFullLinkMatches(data, self.visitedSites)

            self.sitesToVisit.extend(currentSiteMatches)
            self.sitesToVisit.extend(fullLinkMatches)
        except BaseException as error:
            raise

    def CreateFileFromResponse(self, data):
        # write html response to a file (to be read line-by-line)
        # this will be multi-threaded so we need different file name each time
        # to avoid locking etc.
        tmpFileName = str(uuid.uuid4())+".html"
        with open(tmpFileName, "w", encoding="utf-8", newline="\n") as tmpFile:
            for line in data:
                tmpFile.write(line)
        return tmpFileName