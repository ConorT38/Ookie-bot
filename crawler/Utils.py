class Utils:
    def isExcludedFileType(site):
        excludedFileTypes = ['.jpg','.jpeg','.png','.mp4','.mp5','.heic','.avi','.js','.css','.tff','.ico','.favico', '.svg']
        #https://64.media.tumblr.com/a990ab5da55e4266ee1f77ff9385005a/tumblr_ofqtdi2trn1tszceio1_640.png
        for fileType in excludedFileTypes:
            if fileType in site:
                return True
        return False