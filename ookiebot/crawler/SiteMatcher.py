import sys
import os

# Add the parent directory to the sys.path so that you can import Logger
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from ..log.Logger import Logger

class SiteMatcher:
    """
    SiteMatcher is a class for manipulating and matching website URLs.

    Attributes:
        threadId (str): A string representing the thread ID.
        logger (Logger): An instance of the Logger class for logging.
    """
    def __init__(self, threadId="main"):
        """
        Initialize a SiteMatcher object.

        Args:
            threadId (str): A string representing the thread ID (default is "main").
        """
        self.threadId = threadId
        self.logger = Logger(threadId)

    def GetFullSiteURL(self, href, sourceSite):
        """
        Get the full URL of a site based on the provided href and source site.

        Args:
            href (str): The href to be matched.
            sourceSite (str): The source site to use as a base URL.

        Returns:
            str: The full URL resulting from matching the href to the source site.
        """
        if not href or not sourceSite or href[0] == "#":
            return sourceSite
        href = href.strip()
        siteDomain = sourceSite.strip()
        if siteDomain.count('/') >  2:
            siteDomainArr = sourceSite.split("/", 3)
            if siteDomainArr[0].lower() not in ["http:", "https:"]:
                self.logger.debug("this is not a website -- "+siteDomainArr[0])
                return

            siteDomain = siteDomainArr[0] + "//" + siteDomainArr[2].strip()
        
        # absolute url path (e.g. https://google.com/source/link, "/about/project" -> https://google.com/about/project)
        if href[0] == '/':
            if len(href) > 1 and href[1] == '/':
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