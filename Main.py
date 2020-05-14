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

def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

links = []
titles = ["Best Price", "Per Amount", "Single Price"]
rawTitles = []
priceTexts = []
numberDict = {"one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
               "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0}


count = 0
URL = driver.find_elements_by_tag_name("a[href*=product")
for u in URL:
    v = u.get_attribute('href')
    if v not in links and count < 30:
        count += 1
        links.append(v)

data = [["","",""] for j in range(len(links))]

c = 0
d = 0
for link in links:
    driver.get(str(link))
    #driver.get("https://www.danmurphys.com.au/product/DM_904212/oyster-bay-sauvignon-blanc")
    time.sleep(1)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    title = soup.find_all("span", class_="item")
    value = soup.find_all("span", class_="item_value")
    price = soup.find_all("p", class_="ng-star-inserted")
    bestPrice = 0.0
    bestPriceAmt = 0.0
    singlePrice = 0.0
    for p in price: #Best price, per single, per no.
        v = p.text
        if "$" in v:
            priceSplit = v.split(" ")
            for word in priceSplit:
                if IsNumber(word):
                    priceSplit[priceSplit.index(word)] = float(word)
                for x in numberDict:
                    if word == x:
                        priceSplit[priceSplit.index(word)] = numberDict[x]       
            priceTexts.append(priceSplit)
    for price in priceTexts:
        actualPrice = 0.0
        priceAmount = 0.0
        package = False
        tmpbP = 0.0
        tmpbPA = 0.0
        tmpsP = 0.0
        for pr in price:
            if IsNumber(pr) == False and "$" in pr:
                newpr = pr.replace("$", "")
                actualPrice = float(newpr)
                priceTexts[priceTexts.index(price)][price.index(pr)] = float(newpr)
            elif IsNumber(pr) == True:
                priceAmount = int(pr)
                package = True
        if "per" in price and package == True:
            tmpbP = actualPrice/priceAmount
            tmpbPA = priceAmount
        elif ("in" in price and package == True) or package == False:
            tmpsP = actualPrice
        if tmpbP > bestPrice:
            bestPrice = tmpbP
        if tmpbPA > bestPriceAmt:
            bestPriceAmt = tmpbPA
        if tmpsP > singlePrice:
            singlePrice = tmpsP
        if singlePrice > bestPrice:
            bestPrice = singlePrice
            bestPriceAmt = 1
    data[d][0] = "$" + str(bestPrice)
    data[d][1] = str(bestPriceAmt)
    data[d][2] = "$" + str(singlePrice)
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
