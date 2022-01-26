powershell -Command "(New-Object Net.WebClient).DownloadFile('https://chromedriver.storage.googleapis.com/97.0.4692.71/chromedriver_win32.zip', 'chromedriver_win32.zip')"
powershell -Command "Expand-Archive -LiteralPath 'chromedriver_win32.zip' -DestinationPath 'chromedriver_win32'"
powershell -Command "Move-Item chromedriver_win32/chromedriver.exe crawler/chromedriver.exe"
