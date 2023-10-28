from datetime import datetime

class Logger:
    def __init__(self, threadId="main"):
        self.threadId=threadId
        
    def info(self, message, logId=""):
        if not logId:
            logId = self.threadId
        print(self.getTimeStamp() + "[INFO]["+logId+"] "+message)
    
    def debug(self, message, logId=""):
        if not logId:
            logId = self.threadId
        print(self.getTimeStamp() + "[DEBUG]["+logId+"] "+message)
    
    def error(self, message, logId=""):
        if not logId:
            logId = self.threadId
        print(self.getTimeStamp() + "[ERROR]["+logId+"] "+message)
    
    def getTimeStamp(self):
        return "["+str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))+"]"