class Utils:
    @staticmethod
    def isExcludedFileType(site):
        """
        Check if a given site URL is of an excluded file type.

        Args:
            site (str): The site URL to be checked.

        Returns:
            bool: True if the site URL's file type is in the list of excluded file types, False otherwise.
        """
        excludedFileTypes = ['.jpg', '.jpeg', '.png', '.mp4', '.mp5', '.heic', '.avi', '.js', '.css', '.tff', '.ico', '.favico', '.svg']

        for fileType in excludedFileTypes:
            if fileType in site:
                return True

        return False
