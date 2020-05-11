import requests, time, csv
from bs4 import BeautifulSoup
from selenium import webdriver

options = webdriver.ChromeOptions()
options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe";
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(r"C:\Users\david\Documents\Personal\Projects\chromedriver.exe")
driver.get("https://www.danmurphys.com.au/search?searchTerm=*&size=120&sort=Name")

time.sleep(6.5)

links = []

URL = driver.find_elements_by_tag_name("a[href*=product")
for u in URL:
    v = u.get_attribute('href')
    if v not in links:
        links.append(v)

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')

##with open("\output.csv", "w") as f:
##    writer = csv.writer(f)
    #for item_property_list in collected_items:
    #    writer.writerow(item_property_list)
