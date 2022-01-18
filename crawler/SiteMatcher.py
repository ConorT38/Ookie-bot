import sys
import os
import re
from crawler.Utils import Utils

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from log.Logger import Logger
from crawler.Queries import Queries

class SiteMatcher:
    def __init__(self, threadId="main"):
        self.threadId = threadId
        self.logger = Logger(threadId)

    async def GetCurrentSiteLinkMatches(self, data, sourceSite, visitedSites):
        self.logger.debug("parsing sites for "+data)
        currentSiteLinkMatches = re.findall(Queries.CURRENT_SITE_LINK, data)
        sitesToVisit = []

        for currentSiteLink in currentSiteLinkMatches:
            if sourceSite.count("/") > 2:
                siteDomainMatch = re.search(Queries.SITE_DOMAIN, sourceSite)
                site = ''.join(siteDomainMatch.groups(0))+currentSiteLink[0]
                if site not in visitedSites:
                    if not Utils.isExcludedFileType(site):
                        sitesToVisit.append(site)
                        self.logger.info("[queue]: "+site)
            else:
                site = sourceSite + "/" + currentSiteLink[0]
                if site not in visitedSites:
                    if not Utils.isExcludedFileType(site):
                        sitesToVisit.append(site)
                        self.logger.info("[queue]: "+site)
        return sitesToVisit

    async def GetFullLinkMatches(self, data, visitedSites):    
        fullLinkMatches = re.findall(Queries.FULL_LINK, data)
        sitesToVisit = []

        for fullLink in fullLinkMatches:
            site = fullLink[0]
            if site not in visitedSites:
                if not Utils.isExcludedFileType(site):
                        sitesToVisit.append(site)
                        self.logger.info("[queue]: "+site)
        return sitesToVisit
    
    async def GetSiteTitleMatch(self, data):
        titleMatch = re.search(Queries.PAGE_TITLE, data, re.IGNORECASE)

        if titleMatch is None:
            return ""

        title = titleMatch[0].replace("<title>","")
        title = title.replace("</title","")
        return title 
