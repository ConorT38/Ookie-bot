import json
import os
import sys

import pika
from bs4 import BeautifulSoup

# Import your local modules and dependencies here
from ..crawler.SiteMatcher import SiteMatcher
from ..crawler.Utils import Utils

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from ..log.Logger import Logger

# Constants for RabbitMQ connection
RABBITMQ_USERNAME = "pi"
RABBITMQ_PASSWORD = "raspberry"

# Timeouts for connection and reading
conn_timeout = 6
read_timeout = 20

# Initialize RabbitMQ connection and channel
connection = None
channel = None

def CreateAMQPConnection(conn):
    """
    Create and return an AMQP connection if it is closed or doesn't exist.

    Args:
        conn: An existing AMQP connection, if any.

    Returns:
        pika.BlockingConnection: The AMQP connection.
    """
    if conn is None or conn.is_closed:
        credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq.home.lan', 5672, '/', credentials))
        return connection
    return conn

def CreateSiteChannel(conn):
    """
    Create a channel for the AMQP connection.

    Args:
        conn: An AMQP connection.

    Returns:
        pika.channel.Channel: The created channel.
    """
    if conn.is_open:
        channel = conn.channel()
        channel.queue_declare(queue='sitesQueue')
        return channel

class SiteProcessor:
    """
    SiteProcessor is a class for processing and scraping websites.

    Attributes:
        visitedSites (dict): A dictionary of visited sites.
        sourceSite (str): The source site URL.
        sitesToVisit (list): A list of sites to visit.
        threadId (str): A string representing the thread ID.
        logger (Logger): An instance of the Logger class for logging.
        siteMatcher (SiteMatcher): An instance of the SiteMatcher class.
        amqpConnection (pika.BlockingConnection): An AMQP connection for message publishing.
        channel (pika.channel.Channel): An AMQP channel for message publishing.
        browser: The web browser object for web scraping.
    """
    def __init__(self, sourceSite, browser, visitedSites={}, threadId="main"):
        """
        Initialize a SiteProcessor object.

        Args:
            sourceSite (str): The source site to start processing.
            browser: The web browser object for web scraping.
            visitedSites (dict): A dictionary of visited sites (default is an empty dictionary).
            threadId (str): A string representing the thread ID (default is "main").
        """
        self.visitedSites = visitedSites
        self.sourceSite = sourceSite
        self.sitesToVisit = []
        self.threadId = threadId
        self.logger = Logger(threadId)
        self.siteMatcher = SiteMatcher(threadId)
        self.amqpConnection = CreateAMQPConnection(connection)
        self.channel = CreateSiteChannel(self.amqpConnection)
        self.browser = browser

    async def Process(self, _timeout=(6, 20)):
        """
        Process the source site, extract content, and push messages to RabbitMQ.

        Args:
            _timeout (tuple): A tuple containing connection and read timeouts (default is (6, 20)).
        """
        try:
            page = await self.browser.newPage()

            # Navigate to the URL
            await page.goto(self.sourceSite)

            # Wait for the page to load and execute JavaScript
            await page.waitForSelector('head')  # Replace with a suitable selector

            # Extract data from the rendered page
            content = await page.evaluate('() => document.documentElement.innerHTML')  # Replace with your data extraction logic
            soup = BeautifulSoup(content, 'html.parser')

            self.logger.debug("closing page ["+self.sourceSite+"]")
            await page.close()

            title = soup.find('title')
            if title is None:
                return None

            title = title.string
            if "404" in title:
                return None

            # Kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            unfilteredWords = [word.strip() for word in text.splitlines()]
            words = []
            for word in unfilteredWords:
                if word is None:
                    continue
                words.extend(word.split())

            for link in soup.find_all(href=True):
                if link.has_attr('href'):
                    url = self.siteMatcher.GetFullSiteURL(link['href'], self.sourceSite)
                    if url is not None and url not in self.visitedSites and not Utils.isExcludedFileType(url):
                        self.sitesToVisit.append(url)
                        self.visitedSites[url] = True

            message = self.CreateSiteMessage(self.sourceSite, title, words)
            self.PushSiteMessage(message)
        except BaseException as ex:
            self.logger.error("Could not connect to site ["+self.sourceSite+"], Reason="+str(ex))
            raise ex

    def FlushSitesToVisit(self):
        """
        Flush the list of sites to visit.

        Returns:
            list: The list of sites to visit.
        """
        results = self.sitesToVisit
        self.sitesToVisit = []
        return results

    def CreateSiteMessage(self, url, title, words):
        """
        Create a JSON message containing site information.

        Args:
            url (str): The site URL.
            title (str): The site title.
            words (list): A list of words from the site content.

        Returns:
            str: The JSON message.
        """
        return json.dumps({"title": title, "url": url, "words": list(words)})

    def PushSiteMessage(self, message):
        """
        Push a site message to RabbitMQ.

        Args:
            message (str): The message to push to the message queue.
        """
        try:
            self.channel.basic_publish(exchange='',
                routing_key='sitesQueue',
                body=message)
        except:
            self.logger.error("AMQP Channel connection failed.")
