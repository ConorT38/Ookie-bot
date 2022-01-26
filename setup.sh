apt upgrade && apt update && apt install unzip
wget -O chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/97.0.4692.71/chromedriver_linux64.zip

unzip chromedriver_linux64.zip chromedriver_linux64
mv chromedriver_linux64/chromedriver.exe crawler/chromedriver.exe