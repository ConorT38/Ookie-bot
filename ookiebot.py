import threading
import time
from crawler.SiteProcessor import SiteProcessor
from crawler.Utils import Utils
from log.Logger import Logger
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

startingSites = ["https://www.quantstart.com/","https://reddit.com","https://en.wikipedia.org"]

visitedSites = {}
async def StartProcessing(startingSite, threadId):
    sitesToVisit = [startingSite]
    sitesVisited = 0
    while sitesVisited < 300 or len(sitesToVisit) > 0:
        if not sitesToVisit:
            continue

        startTime = time.time()
        site = sitesToVisit.pop(0)

        if Utils.isExcludedFileType(site):
            Logger(threadId).error(site)
            continue
        
        siteProcessor = SiteProcessor(site, visitedSites,threadId)
        await siteProcessor.Process()
    
        sitesToVisit.extend(await siteProcessor.FlushSitesToVisit())
        sitesVisited += 1
        
        Logger(threadId).info("Site: "+site+"\nSitesVisited: "+str(sitesVisited)+", Total Time: "+str(time.time()-startTime))
    

async def main():
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=4)
    siteEnum = enumerate(startingSites)

    futures = [loop.run_in_executor(executor, asyncio.ensure_future(StartProcessing(site, "thread-" + str(id))), id) for id, site in siteEnum]
    
    await asyncio.gather(futures)
    Logger().info("Finished...")

asyncio.run(main())

    
    
