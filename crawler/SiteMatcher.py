import sys
import os
import re

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from log.Logger import Logger

class SiteMatcher:
    def __init__(self, threadId="main"):
        self.threadId = threadId
        self.logger = Logger(threadId)

    def GetFullSiteURL(self, href, sourceSite):
        if not href or href[0] == "#":
            return sourceSite
        href = href.strip()
        siteDomain = sourceSite.strip()
        if siteDomain.count('/') >  2:
            siteDomainArr = sourceSite.split("/",3)
            if siteDomainArr[0].lower() not in ["http:", "https:"]:
                self.logger.debug("this is not a website -- "+siteDomainArr[0])
                return
            siteDomain = siteDomainArr[0] + "//" + siteDomainArr[2].strip()
        
        # absolute url path (e.g. https://google.com/source/link, "/about/project" -> https://google.com/about/project)
        if href[0] == '/':
            if href[1] == '/':
                return "https://" + href[2:]
            if siteDomain[-1] == '/':
                return siteDomain + href[1:]
            return siteDomain + href

        # relative url path (e.g. https://google.com/source/link, "/about/" -> https://google.com/source/link/about/)
        if href[:4] != "http":
            if sourceSite[-1] == '/':
                return sourceSite + href
            return sourceSite + "/" + href

        return href
        