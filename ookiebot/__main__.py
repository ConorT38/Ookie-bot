from multiprocessing import Pool
import time
from .crawler.SiteProcessor import SiteProcessor
from .log.Logger import Logger
import sys
import os
from pyppeteer import launch
import asyncio
from urllib.parse import urlparse

visitedSites = {}
async def StartProcessing(startingSite, threadId):
    sitesToVisit = [startingSite]
    sitesVisited = 0
    
    # check if it's windows or linux
    if os.name == 'nt': 
        browser = await launch()
    elif os.name == 'posix':
        browser = await launch(executablePath='/usr/lib/chromium-browser/chromedriver')
    else:
        raise Exception("OS Error: Ookiebot only runs on 'nt' or 'posix' systems.")

    while sitesToVisit:
        if not sitesToVisit:
            continue

        startTime = time.time()
        site = sitesToVisit.pop(0)

        siteProcessor = SiteProcessor(site,browser, visitedSites, threadId)
        await siteProcessor.Process()
    
        sitesToVisit.extend(siteProcessor.FlushSitesToVisit())
        sitesVisited += 1
        
        Logger(threadId).info("Site: "+site+"\nSitesVisited: "+str(sitesVisited)+", Total Time: "+str(time.time()-startTime))    
    await browser.close()
async def main(startingSites):
    pool = Pool(len(startingSites))    
    try:
        for i in range(len(startingSites)):
            pool.apply_async(await StartProcessing(startingSites[i], "thread-" + str(i)))
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

    asyncio.run(main(sys.argv[1:]))
    
