from multiprocessing import Pool
import time
from .crawler.SiteProcessor import SiteProcessor
from .log.Logger import Logger
import sys
import os
from pyppeteer import launch
import asyncio
from urllib.parse import urlparse
from pyppeteer.errors import PageError

visitedSites = {}

async def StartProcessing(startingSite, threadId, sitesToVisit=[]):
    """
    Start the web scraping process for a given starting site and its child sites.

    Args:
        startingSite (str): The starting site URL.
        threadId (str): A string representing the thread ID.
        sitesToVisit (list): A list of sites to visit (default is an empty list).
    """
    if not sitesToVisit:
        sitesToVisit = [startingSite]
    sitesVisited = 0
    browser = None

    # Check if it's Windows or Linux for launching the browser
    if os.name == 'nt':
        browser = await launch()
    elif os.name == 'posix':
        browser = await launch(headless=True, executablePath="/usr/bin/chromium", args=['--no-sandbox'])
    else:
        raise Exception("OS Error: Ookiebot only runs on 'nt' or 'posix' systems.")

    while sitesToVisit:
        try:
            if not sitesToVisit:
                continue

            startTime = time.time()
            site = sitesToVisit.pop(0)

            siteProcessor = SiteProcessor(site, browser, visitedSites, threadId)
            await siteProcessor.Process()

            sitesToVisit.extend(siteProcessor.FlushSitesToVisit())
            sitesVisited += 1

            Logger(threadId).info("Site: "+site+"\nSitesVisited: "+str(sitesVisited)+", Total Time: "+str(time.time()-startTime))
        except BaseException as ex:
            await browser.close()
            if type(ex) is TimeoutError or type(ex) is PageError:
                await StartProcessing(sitesToVisit.pop(), threadId, sitesToVisit)
            else:
                raise ex

    await browser.close()

async def main(startingSites):
    """
    Main entry point for starting the web scraping process.

    Args:
        startingSites (list): A list of starting site URLs.
    """
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
        raise Exception("Invalid argument. Usage: ookiebot.py <url>")
    for arg in sys.argv[1:]:
        parsedUrl = urlparse(str(arg))
        if not all([parsedUrl.scheme, parsedUrl.netloc]):
            raise Exception("Invalid argument. Usage: ookiebot.py <url>")

    asyncio.run(main(sys.argv[1:]))
