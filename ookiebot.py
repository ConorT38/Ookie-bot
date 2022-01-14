import requests
import re
import time
import asyncio
import uuid
from log.Logger import Logger

fullLinkQuery = r"(?i)\b((?<=href\=\")(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])(?=\"))"
currentSiteLinkQuery = r"(?i)\b((?<=href\=\"\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])(?=\"))"
siteDomainQuery = r"(https?:\/\/|www\d{0,3}[.])(.*?\/)"

startingSite = "https://en.wikipedia.org"
conn_timeout = 6
read_timeout = 20

visitedSites = {}
sitesToVisit = [startingSite]

async def processLinks(source):
    # get html
    # load html into file line-by-line
    # read new file line by line
    # check for url on each line
    # site name | seen_online| url_safety 
    # facebook.com | 1,000,000 | facebook.com/search/q?=hi
    # facebook.com/user/conor.thompson | 4
    # spacebook.com 

    # search = facebook.com 
    # result:
    #       https://facebook.com (because it's )
    #       
    Logger.debug("main", "collecting source: "+source)

    timeouts = (conn_timeout, read_timeout)
    #headers = {'User- Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36' }
    
    # grab html content from web page
    content = requests.get(source, timeout=timeouts).text
    
    #Logger.debug("main", content)
    # write html response to a file (to be read line-by-line)
    # this will be multi-threaded so we need different file name each time
    # to avoid locking etc.
    threadFileName = str(uuid.uuid4())+".html"
    with open(threadFileName, "w", encoding="utf-8", newline="\n") as tmpFile:
        for line in content:
            tmpFile.write(line)
    
    title = ""
    # we need to read the tmpFile line-by-line and check for urls, title, etc.
    for line in open(threadFileName, "r", encoding="utf-8", newline="\n").readlines():
        if not title:
            title = re.search('<\W*title\W*(.*)</title', line, re.IGNORECASE)
        await getUrlMatches(source, line, "mainThreadWillChangeLater")
    return title

# for each line in the file, we need to check if it has a url
async def getUrlMatches(source, line, threadId):
    try:
        await addCurrentSiteLinkMatch(source,  line, threadId)
        await addFullLinkMatch(line, threadId)
    except BaseException as error:
        raise

async def addFullLinkMatch( data, threadId):
    Logger.debug(threadId, "data size: "+str(len(data)))
    
    fullLinkMatches = re.findall(fullLinkQuery, data)
    Logger.debug(threadId, "full link match finished")

    for fullLink in fullLinkMatches:
        site = fullLink[0]
        if site not in visitedSites:
            sitesToVisit.append(site)
            Logger.info(threadId, "[queue]: "+site)
    Logger.info(threadId, "Total number of sites matched: "+str(len(fullLinkMatches)))

async def addCurrentSiteLinkMatch(source,  data, threadId):
    Logger.debug(threadId, "data size: "+str(len(data)))

    currentSiteLinkMatches = re.findall(currentSiteLinkQuery, data)
    Logger.debug(threadId, source + " current link match finished")

    for currentSiteLink in currentSiteLinkMatches:
        if source.count("/") > 2:
            siteDomainMatch = re.search(siteDomainQuery, source)
            site = ''.join(siteDomainMatch.groups(0))+currentSiteLink[0]
            if site not in visitedSites:
                sitesToVisit.append(site)
                Logger.info(threadId, "[queue]: "+site)
        else:
            site = source+"/"+currentSiteLink[0]
            if site not in visitedSites:
                sitesToVisit.append(site)
                Logger.info(threadId, "[queue]: "+site)
    Logger.info(threadId, "Total number of sites matched: "+str(len(currentSiteLinkMatches)))

def addToVisitedSites(site, title):
    if site in visitedSites:
        visitedSites[site]["count"] = visitedSites[site]["count"] + 1
    else:
        visitedSites[site] = {"title": title, "count": 1}


def isExcludedFileType(site):
    excludedFileTypes = ['.jpg','.jpeg','.png','.mp4','.mp5','.heic','.avi','.js','.css','.tff','.ico','.favico', '.svg']

    for fileType in excludedFileTypes:
        if fileType in site:
            return True
    return False

async def main():
    sitesVisited = 0
    while sitesVisited < 300:
        if not sitesToVisit:
            continue

        startTime = time.time()
        site = sitesToVisit.pop(0)

        if isExcludedFileType(site):
            continue
        
        title = await processLinks(site)
        addToVisitedSites(site, title)

        sitesVisited += 1
        Logger.info("main", "Site: "+site+"\nSitesVisited: "+str(sitesVisited)+", Total Time: "+str(time.time()-startTime))
    Logger.info("main", "Finished...")
    print(visitedSites)

asyncio.run(main())

    
    
