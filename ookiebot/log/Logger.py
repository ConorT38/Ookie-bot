from datetime import datetime

class Logger:
    def __init__(self, threadId="main"):
        """
        Initialize a Logger object.

        Args:
            threadId (str): A string representing the thread ID (default is "main").
        """
        self.threadId = threadId

    def info(self, message, logId=""):
        """
        Log an informational message.

        Args:
            message (str): The message to be logged.
            logId (str): An optional log ID (default is empty).
        """
        if not logId:
            logId = self.threadId
        print(self.getTimeStamp() + "[INFO][" + logId + "] " + message)

    def debug(self, message, logId=""):
        """
        Log a debug message.

        Args:
            message (str): The debug message to be logged.
            logId (str): An optional log ID (default is empty).
        """
        if not logId:
            logId = self.threadId
        print(self.getTimeStamp() + "[DEBUG][" + logId + "] " + message)

    def error(self, message, logId=""):
        """
        Log an error message.

        Args:
            message (str): The error message to be logged.
            logId (str): An optional log ID (default is empty).
        """
        if not logId:
            logId = self.threadId
        print(self.getTimeStamp() + "[ERROR][" + logId + "] " + message)

    def getTimeStamp(self):
        """
        Get the current timestamp.

        Returns:
            str: A formatted timestamp.
        """
        return "[" + str(datetime.now().strftime('%d-%m-%Y %H:%M:%S')) + "]"
