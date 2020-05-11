import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver

options = webdriver.ChromeOptions()
options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe";
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(r"C:\Users\david\Documents\Personal\Projects\chromedriver.exe")
driver.get("https://www.danmurphys.com.au/search?searchTerm=*&size=120&sort=Name")
time.sleep(6)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
prices = soup.find_all('span', class_='value')
for price in prices:
    print(price.text)
