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

def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def CheckError(driver):
    for e in driver.find_elements_by_class_name("header-help-text"):
        if e.text == "Sorry, An unexpected error occured. Please, try again later.":
            return True
    return False

time.sleep(10)

more_buttons = driver.find_elements_by_class_name("show-more")
for x in range(len(more_buttons)):
  if more_buttons[x].is_displayed():
      driver.execute_script("arguments[0].click();", more_buttons[x])
      time.sleep(1)

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')

categories = soup.find_all("div", class_="accordion-item")
cats = []
delCats = []
for cat in categories:
    cats.append(cat.text)
for c in cats:
    if "Category" not in c:
        delCats.append(cats.index(c))
cnt = 0
for num in delCats:
    del cats[num - cnt]
    cnt += 1
    
allcats = cats[0]
allcats = allcats.replace('(', ',').replace(')', ',').replace('Category', ',').replace('Show less\n', ',')
cats = allcats.split(",")
delCats = []
IgnoreCategories = ["Accessories", "BarAccessories","FoodSnacks","SoftDrinks","Water",
                    "NonAlcoholicDrinks","MineralSparklingWater","Nuts","Chips","Juice",
                    "WineGlasses","BottleOpeners","PlasticCups","Chocolate","CoolerBags",
                    "BeerGlasses","StillWater","NonAlcoholicWine","WineRacks","Books",
                    "EnergyDrinks","NonAlcoholicBeer","Popcorn","PorkCrackling",
                    "Stoppers","CoconutWater","WineFridges","Corkscrews","Pretzels","Cordial",
                    "IceCubeTraysMoulds","Ice","Cherries"]
cnt = 0
for c in cats:
    if c.replace(" ", "").isalpha() == False or c.replace(" ", "") in IgnoreCategories:
        delCats.append(cnt)
        print("Category Ignored:", c.replace(" ", ""))
    if len(c) > 0 and c[-1] == " ":
        d = c[0:-1].replace(" ", "-")
        cats[cnt] = d.lower()
    cnt += 1
cnt = 0
for num in delCats:
    del cats[num - cnt]
    cnt += 1

links = []
titles = ["Best Price", "Per Amount", "Single Price", "Product Name", "Link", "Category"]
rawTitles = []
rawLinks = []
priceTexts = []
numberDict = {"one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
               "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0}
progress = 1
for cat in cats:
    print("\n" + "Scanning category:", progress, "/", len(cats))
    progress += 1
    driver.get("https://www.danmurphys.com.au/search?searchTerm=*&filters=variety(" + cat + ")&page=1&size=50&sort=Name")
    time.sleep(6)
    pcount = 1
    pagecount = driver.find_elements_by_class_name("page-count")
    for pag in pagecount:
        page = pag.text
        pagecnt = page.split(" ")
        for p in pagecnt:
            if IsNumber(p):
                pcount = int(p)
    progress2 = 1
    for p in range(1, pcount+1):
        linksLength = len(links)
        print("    Scanning page:", progress2, "/", pcount)
        progress2 += 1
        driver.get("https://www.danmurphys.com.au/search?searchTerm=*&filters=variety(" + cat + ")&page=" + str(p) + "&size=50&sort=Name")
        block = driver.find_element_by_class_name("col-xs-12")
        URL = block.find_elements_by_tag_name("a[href*=product")
        while not URL:
            if CheckError(driver):
                print("^^ ERROR LOADING PAGE ^^")
                break
            block = driver.find_element_by_class_name("col-xs-12")
            URL = block.find_elements_by_tag_name("a[href*=product")
        for u in URL:
            try:
                v = u.get_attribute("href")
            except:
                time.sleep(15)
                v = u.get_attribute("href")
            if v not in rawLinks:
                links.append([str(v), cat])
                rawLinks.append(v)
        print("        Number of URLS:", len(links))
        if (len(links)-linksLength) < 1:
            print("^^ NO ADDED LINKS ^^", "Category:", cat, "Page:", p)

data = [["","","","","",""] for j in range(len(links))]

c = 0
d = 0
progress = 1
for link in links:
    print("Scanning item:", progress, "/", len(links))
    progress += 1
    driver.get(link[0])
    time.sleep(2)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    title = soup.find_all("span", class_="item")
    value = soup.find_all("span", class_="item_value")
    prices = soup.find_all("p", class_="ng-star-inserted")
    prodTitle = soup.find("span", class_="product-name")
    try:
        print(prodTitle.text)
    except:
        print("ERROR IN PRODUCT NAME")
        
    try:
        bestPrice = 0.0
        bestPriceAmt = 0.0
        singlePrice = 0.0
        for p in prices:
            v = p.text
            if "$" in v:
                v = v.replace('$', ' $').replace(',', '')
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
            if (tmpbP < bestPrice and tmpbP > 0.0) or bestPrice == 0.0:
                bestPrice = tmpbP
                bestPriceAmt = tmpbPA
            if (tmpsP < singlePrice and tmpsP > 0.0) or singlePrice == 0.0:
                singlePrice = tmpsP
            if singlePrice < bestPrice and singlePrice > 0.0 or bestPrice == 0.0:
                bestPrice = singlePrice
                bestPriceAmt = 1
        data[d][0] = "$" + str(bestPrice)
        data[d][1] = str(bestPriceAmt)
        data[d][2] = "$" + str(singlePrice)
    except:
        print("ERROR IN PRICE")
        data[d][0] = "ERROR IN PRICE"
        data[d][1] = "ERROR IN PRICE"
        data[d][2] = "ERROR IN PRICE"
        
    try:
        data[d][3] = prodTitle.text
    except:
        data[d][3] = "ERROR IN PRODUCT NAME"
    data[d][4] = link[0]
    data[d][5] = link[1]
    
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
        d -= 1
    d += 1

with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(titles)
    for a in data:
        writer.writerow(a)
