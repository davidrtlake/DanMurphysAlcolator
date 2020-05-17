import requests, time, csv, math
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

start = time.time()

ua = UserAgent()
userAgent = ua.random
#PROXY = "111.220.90.41:40938"
print(userAgent)

options = Options()
options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe";
options.add_argument('--ignore-certificate-errors')
#options.add_argument('--incognito')
options.add_argument('--lang=en_US')
options.add_argument(f'user-agent={userAgent}')
#options.add_argument('--proxy-server=%s' % PROXY)
driver_path = r"C:\Users\david\Documents\Personal\Projects\chromedriver.exe"
driver = webdriver.Chrome(driver_path, options=options)
driver.get("https://www.danmurphys.com.au/search?searchTerm=*&size=1&sort=Name")

def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def CheckError(d):
    header = []
    while not header: #To prevent stale errors
        try:
            header = d.find_elements_by_class_name("header-help-text")
            for e in header:
                if e.text == "Sorry, An unexpected error occured. Please, try again later." or \
                   "Sorry, 0 results found for *":
                    return True
        except:
            header = []
    return False

def CheckNoPageCount(d):
    header = []
    while not header: #To prevent stale errors
        try:
            header = d.find_elements_by_class_name("header-help-text")
            for cout in header:
                for i in cout.text.split(" "):
                    if IsNumber(i) and int(i) <= 50 and int(i) > 0:
                        return True
        except:
            header = []
    return False

def CheckOutOfStock(soup):
    OOS = soup.find_all("div", class_="add-to-cart-btn")
    for i in OOS:
        if i.text == " Out of stock ":
            return True
    return False

def GetURLS(driver):
    block = driver.find_element_by_class_name("col-xs-12")
    URL = block.find_elements_by_tag_name("a[href*=product")
    for u in URL:
        try:
            v = u.get_attribute("href")
        except:
            print('StaleElementReferenceException while getting URL, trying to find element again')
            URL = []
            break
        if v not in rawLinks:
            links.append([str(v), cat])
            rawLinks.append(v)
    return URL

def GetErrorURLS(urlCategory, p, urlSize):
    p = p*2
    urlSize = urlSize/2
    if (urlSize/2) < 1:
        print("    PAGE SIZE TOO SMALL")
        return
    for i in range(0, 2):
        driver.get("https://www.danmurphys.com.au/search?searchTerm=*&filters=variety(" + \
                   urlCategory + ")&page=" + str(p+i) + \
                   "&size=" + str(urlSize) + "&sort=Name")
        URL = GetURLS(driver)
        count = 0
        while not URL:
            URL = GetURLS(driver)
            count += 1
            if CheckError(driver) and count > ((progress*10)+100) and not URL:
                print("    ERROR LOADING PAGE ^^")
                GetErrorURLS(urlCategory, p, urlSize)
                break

categories = []
while not categories:
    clicked = False
    more_buttons = driver.find_elements_by_class_name("show-more")
    for x in range(len(more_buttons)):
      if more_buttons[x].is_displayed():
          driver.execute_script("arguments[0].click();", more_buttons[x])
          clicked = True
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    if clicked:
        print("CLICKED - SLEEPING FOR 10 SECONDS")
        time.sleep(10)
        categories = soup.find_all("div", class_="accordion-item")

print("LOADED CATEGORIES")
driver.quit()
options.add_argument('--headless')
driver = webdriver.Chrome(driver_path, options=options)

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
keepCats = []
keepNums = []
IgnoreCategories = ["Accessories", "BarAccessories","FoodSnacks","SoftDrinks","Water",
                    "NonAlcoholicDrinks","MineralSparklingWater","Nuts","Chips","Juice",
                    "WineGlasses","BottleOpeners","PlasticCups","Chocolate","CoolerBags",
                    "BeerGlasses","StillWater","NonAlcoholicWine","WineRacks","Books",
                    "EnergyDrinks","NonAlcoholicBeer","Popcorn","PorkCrackling",
                    "Stoppers","CoconutWater","WineFridges","Corkscrews","Pretzels","Cordial",
                    "IceCubeTraysMoulds","Ice","Cherries"]
cnt = 0
cnt2 = 0
catSize = []
for c in cats:
    if c.replace(" ", "").isalpha() and c.replace(" ", "") not in IgnoreCategories:
        keepCats.append(cnt)
        keepNums.append(cnt2)
        print("Category Accepted:", c.replace(" ", ""))
    elif IsNumber(c):
        catSize.append(int(c))
    if c.replace(" ", "").isalpha():
        cnt2 += 1
    if len(c) > 0 and c[-1] == " ":
        cats[cnt] = c[0:-1]
    cnt += 1
    
newCats = []
for num in keepCats:
    newCats.append(cats[num])
print(newCats)
    
newSizes = []
for num in keepNums:
    newSizes.append(catSize[num])
print(newSizes)

newSizes.reverse()
newCats.reverse()

links = []
titles = ["Best Price", "Per Amount", "Single Price", "Product Name", "Link", "Category"]
rawTitles = []
rawLinks = []
priceTexts = []
numberDict = {"one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
               "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0}
progress = 1
sCount = 0
for cat in newCats: #For each category
    print("\n" + "Scanning category:", cat, progress, "/", len(newCats))
    progress += 1
    urlCategory = cat.replace(" ", "-").lower()
    urlSize = math.ceil(newSizes[sCount]/4)
    if urlSize < 1:
        urlSize = 1
    print("CATEGORY SIZE:", newSizes[sCount], "PAGE SIZE:", urlSize)
    driver.get("https://www.danmurphys.com.au/search?searchTerm=*&filters=variety(" + \
               urlCategory \
               + ")&page=1&size=" + str(urlSize) + "&sort=Name")
    pcount = 4
    pagecount = []
    count = 0
    while not pagecount: #Get the total page count
        pagecount = driver.find_elements_by_class_name("page-count")
        if (CheckNoPageCount(driver) or CheckError(driver)) and count > 150 and not pagecount:
            print("    ERROR LOADING PAGECOUNT ^^")
            break
        count += 1
    for pag in pagecount:
        page = pag.text
        pagecnt = page.split(" ")
        for p in pagecnt:
            if IsNumber(p):
                pcount = int(p)
    progress2 = 1
    for p in range(1, pcount+1): #Iterate through all the pages
        linksLength = len(links)
        print("    Scanning page:", progress2, "/", pcount)
        progress2 += 1
        if p > 1: #Only load for second+ pages
            driver.get("https://www.danmurphys.com.au/search?searchTerm=*&filters=variety(" + \
                       urlCategory + ")&page=" + str(p) + \
                       "&size=" + str(urlSize) + "&sort=Name")
        URL = GetURLS(driver)
        count = 0
        while not URL:
            URL = GetURLS(driver)
            count += 1
            if CheckError(driver) and count > ((progress*10)+100) and not URL:
                print("^^ ERROR LOADING PAGE ^^")
                GetErrorURLS(urlCategory, p, urlSize)
                break
        print("        Number of URLS:", len(links), "(+" + str(len(links)-linksLength) + ")")
        if (len(links)-linksLength) < 1:
            print("    NO ADDED URLS ^^", "Category:", cat, "Page:", p)
    sCount += 1

print("\n" + "URLS scrapped in", (time.time()- start), "seconds")

data = [["","","","","",""] for j in range(len(links))]

c = 0
d = 0
progress = 1
for link in links:
    print("Scanning item:", progress, "/", len(links))
    progress += 1
    driver.get(link[0])
    time.sleep(1)
    prices = []
    cnt = 0
    while not prices:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        title = soup.find_all("span", class_="item")
        value = soup.find_all("span", class_="item_value")
        prices = soup.find_all("p", class_="ng-star-inserted")
        prodTitle = soup.find("span", class_="product-name")
        if CheckOutOfStock(soup) and cnt > 100:
            print("ITEM OUT OF STOCK")
            break
        cnt += 1
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
                v = v.replace('$', ' $').replace(',', '').replace('(', ' ').replace(')', ' ')
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
        if not prices:
            print("ITEM OUT OF STOCK")
            data[d][0] = "NO ITEM PRICE"
            data[d][1] = "NO ITEM PRICE"
            data[d][2] = "NO ITEM PRICE"
        else:
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
print("\n" + "Script executed in", (time.time()- start), "seconds")
