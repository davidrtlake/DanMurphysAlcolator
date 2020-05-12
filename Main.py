import requests, time, csv
from bs4 import BeautifulSoup
from selenium import webdriver

options = webdriver.ChromeOptions()
options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe";
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(r"C:\Users\david\Documents\Personal\Projects\chromedriver.exe")
driver.get("https://www.danmurphys.com.au/search?searchTerm=*&size=30&sort=Name")

time.sleep(6.5)

links = []
titles = []
rawTitles = []


count = 0
URL = driver.find_elements_by_tag_name("a[href*=product")
for u in URL:
    v = u.get_attribute('href')
    if v not in links and count < 30:
        count += 1
        links.append(v)

data = [[] for j in range(len(links))]

c = 0
d = 0
for link in links:
    driver.get(str(link))
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    title = soup.find_all("span", class_="item")
    value = soup.find_all("span", class_="item_value")
    for t in title:
        p = t.text
        rawTitles.append(p)
        if p not in titles:
            titles.append(p)
            for n in data:
                n.append("")
    for v in value:
        data[d][titles.index(rawTitles[c])] = v.text
        c += 1
    if data[d][titles.index('Alcohol Volume')] == '' \
               or data[d][titles.index('Alcohol Volume')] == '0':
        del data[d]
        #del prices[d]
        d -= 1
    d += 1

with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(titles)
    for a in data:
        writer.writerow(a)
