class Logger:
    @staticmethod
    def info(logId, message):
        print("[INFO]["+logId+"] "+message)
    
    @staticmethod
    def debug(logId, message):
        print("[DEBUG]["+logId+"] "+message)
    
    @staticmethod
    def error(logId, message):
        print("[ERROR]["+logId+"] "+message)