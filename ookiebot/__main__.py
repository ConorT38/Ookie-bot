from multiprocessing import Pool
import time
from .crawler.SiteProcessor import SiteProcessor
from .log.Logger import Logger
import sys
from urllib.parse import urlparse

visitedSites = {}
def StartProcessing(startingSite, threadId):
    sitesToVisit = [startingSite]
    sitesVisited = 0
    while sitesToVisit:
        if not sitesToVisit:
            continue

        startTime = time.time()
        site = sitesToVisit.pop(0)

        siteProcessor = SiteProcessor(site, visitedSites, threadId)
        siteProcessor.Process()
    
        sitesToVisit.extend(siteProcessor.FlushSitesToVisit())
        sitesVisited += 1
        
        Logger(threadId).info("Site: "+site+"\nSitesVisited: "+str(sitesVisited)+", Total Time: "+str(time.time()-startTime))    

def main(startingSites):
    pool = Pool(len(startingSites))
    try:
        for i in range(len(startingSites)):
            pool.apply_async(StartProcessing(startingSites[i], "thread-" + str(i)))
    except KeyboardInterrupt:
        pool.terminate()
        sys.exit(1)

    Logger().info("Finished...")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("Inavlid argument. Usage: ookiebot.py <url>")
    for arg in sys.argv[1:]:
        parsedUrl = urlparse(str(arg))
        if not all([parsedUrl.scheme, parsedUrl.netloc]):
            raise Exception("Inavlid argument. Usage: ookiebot.py <url>")

    main(sys.argv[1:])
    
