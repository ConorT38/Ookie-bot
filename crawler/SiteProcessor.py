import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from log.Logger import Logger

fullLinkQuery = r"(?i)\b((?<=href\=\")(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])(?=\"))"
currentSiteLinkQuery = r"(?i)\b((?<=href\=\"\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])(?=\"))"
siteDomainQuery = r"(https?:\/\/|www\d{0,3}[.])(.*?\/)"

startingSite = "https://bbc.co.uk"
conn_timeout = 6
read_timeout = 20

class SiteProcessor:
    def __init__(self, visitedSites = {}, numberOfThreads = 1):
        self.visitedSites = visitedSites
        self.numberOfThreads = numberOfThreads
    
    async def processLinks(source):
        print("collecting source: "+source)

        timeouts = (conn_timeout, read_timeout)
        headers = {'User- Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36' }
        
        content = requests.get(source, headers=headers, timeout=timeouts).text
        title = re.search('<\W*title\W*(.*)</title', content, re.IGNORECASE)
        Logger.debug("main", "request response - ok")

        await splitMatching(source, content, 10)
        return title

async def splitMatching(self, source, data, numThreads):
    chunkSize = len(data) // numThreads
    chunks = [data[i : i + chunkSize] for i in range(0, len(data), chunkSize)]
    for idx in range(numThreads):
        try:
            await addCurrentSiteLinkMatch(source, fullLinkQuery, chunks[idx], str(idx))
            await addFullLinkMatch(currentSiteLinkQuery, chunks[idx], str(idx))
        except BaseException as error:
            raise

async def addFullLinkMatch(self, query, data, threadId):
    Logger.debug(threadId, "data size: "+str(len(data)))
    
    fullLinkMatches = re.findall(fullLinkQuery, data)
    Logger.debug(threadId, "full link match finished")

    for fullLink in fullLinkMatches:
        site = fullLink[0]
        if site not in self.visitedSites:
            self.sitesToVisit.append(site)
            Logger.info(threadId, "[queue]: "+site)
    Logger.info(threadId, "Total number of sites matched: "+str(len(fullLinkMatches)))

async def addCurrentSiteLinkMatch(source, query, data, threadId):
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