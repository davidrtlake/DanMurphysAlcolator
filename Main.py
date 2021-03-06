import requests, time, csv, math
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

start = time.time()

ua = UserAgent()
userAgent = ua.random
#PROXY = "203.19.92.3"
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

def CheckOutOfStock(OOS):
    for i in OOS:
        if "Out of stock" in i.text:
            return True
    return False

def GetURLS(driver): #TODO: Check complexity of not in compared to sorting at end.
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

indentCounter = 2
def GetErrorURLS(urlCategory, p, urlSize, indentCounter):
    indentCount = indentCounter
    indentCounter += 2
    p = p*2
    urlSize = math.ceil(urlSize/2)
    llLength = len(links)
    if (urlSize/2) < 2:
        print("V " + (indentCount*" ") + "PAGE SIZE TOO SMALL")
        return True
    for i in range(0, 2):
        p += i
        lLength = len(links)
        print(str(i + 1) + (indentCount*" ") + " LOADING PAGE " + str(i + 1) + " OF SPLIT")
        driver.get("https://www.danmurphys.com.au/search?searchTerm=*&filters=variety(" + \
                   urlCategory + ")&page=" + str(p) + \
                   "&size=" + str(urlSize) + "&sort=Name")
        URL = GetURLS(driver)
        count3 = 0
        while not URL:
            URL = GetURLS(driver)
            count3 += 1
            if CheckError(driver) and count3 > ((progress*2)+100) and not URL:
                print(">>" + (indentCount*" ") + "ERROR LOADING PAGE")
                if GetErrorURLS(urlCategory, p, urlSize, indentCounter):
                    return True
                break
        print("<" + str(i + 1) + (indentCount*" ") + "LOADED", (len(links)-lLength), "URLS FROM PAGE")
    print("<<" + (indentCount*" ") + "LOADED", (len(links)-llLength), "URLS FROM ERROR")
    return False

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

#Everything with "cat" is collecting, parsing, and sorting the categories
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
                    "NonAlcoholicDrinks","PortTawny", "BrandyCognac", "IceBuckets",
                    "MineralSparklingWater","Nuts","Chips","Juice", "Glassware",
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
rawLinks = [] #Only used to check duplicates
priceTexts = []
numberDict = {"one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
               "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0}
progress = 1
sCount = 0
for cat in newCats: #Collecting links from each category
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
            print("#   ERROR LOADING PAGECOUNT")
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
        indentCounter = 2
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
            if CheckError(driver) and count > ((progress*5)+100) and not URL:
                print(">   ERROR LOADING PAGE")
                if GetErrorURLS(urlCategory, p, urlSize, indentCounter):
                    break
        print("        Number of URLS:", len(links), "(+" + str(len(links)-linksLength) + ")")
        if (len(links)-linksLength) < 1:
            print("0   NO ADDED URLS", "Category:", cat, "Page:", p)
    sCount += 1

URLTime = (time.time()- start)/60
print("\n" + "URLS scrapped in", URLTime, "mintues \n")

#links = [["https://www.danmurphys.com.au/product/DM_ER_1000007029_10045/lawrenny-espresso-martini-cocktail-pack",
#          "fwfewfw"]]

data = [["","","","","",""] for j in range(len(links))]

c = 0
d = 0
progress = 1
for link in links: #Collecting the data for all the collected links
    print("Scanning item:", progress, "/", len(links))
    progress += 1
    driver.get(link[0])
    OOS = []
    priceTexts = []
    loadTime = time.time()
    startLoad = time.time()
    breaker = False
    while not OOS:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        title = soup.find_all("span", class_="item")
        value = soup.find_all("span", class_="item_value")
        prices = soup.find_all("p", class_="ng-star-inserted")
        prodTitle = soup.find("span", class_="product-name")
        OOS = soup.find_all("div", class_="add-to-cart-btn")
        if (time.time()-loadTime) > 60:
            statusTest = requests.get("https://www.danmurphys.com.au")
            if statusTest.status_code == 403:
                print("XXXX THEY GOT US BOYS XXXX")
                while input("Enter: ") != "c":
                    continue
                print("⟳   REFRESHING PAGE FOR RESTART")
                loadTime = time.time()
                startLoad = time.time()
                driver.get(link[0])
            else:
                print("+   PAGE TIMED OUT")
                breaker = True
                break
        if (time.time()-startLoad) > 30:
            print("⟳   REFRESHING PAGE")
            startLoad = time.time()
            driver.get(link[0])
    if breaker:
        continue
    if CheckOutOfStock(OOS):
        print("0   ITEM OUT OF STOCK")
    try:
        print("    " + prodTitle.text)
    except:
        print("*   ERROR IN PRODUCT NAME")
        
    try:
        bestPrice = 0.0
        bestPriceAmt = 0.0
        singlePrice = 0.0
        for p in prices:
            v = p.text
            if "$" in v:
                v = v.replace('$', ' $').replace(',', '').replace('(', ' ') \
                    .replace(')', ' ').replace('\n', ' ').replace(';', ' ') \
                    .replace('-', ' ').replace('+', ' ').replace('`', ' ') \
                    .replace('~', ' ').replace('_', ' ').replace('=', ' ') \
                    .replace('<', ' ').replace('>', ' ').replace('/', ' ') \
                    .replace('?', ' ').replace('|', ' ').replace('\\', ' ') \
                    .replace(']', ' ').replace('{', ' ').replace('}', ' ') \
                    .replace('[', ' ').replace(':', ' ').replace('"', ' ') \
                    .replace('\'', ' ')
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
                tmpbP = round(actualPrice/priceAmount, 2)
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
        if not prices or (bestPrice + bestPriceAmt + singlePrice == 0.0):
            print("X   NO ITEM PRICE")
            data[d][0] = "NO ITEM PRICE"
            data[d][1] = "NO ITEM PRICE"
            data[d][2] = "NO ITEM PRICE"
        else:
            data[d][0] = bestPrice
            data[d][1] = bestPriceAmt
            if singlePrice == 0.0:
                print("1   NO SINGLE PRICE")
                data[d][2] = "NO SINGLE PRICE"
            else:
                data[d][2] = singlePrice
    except:
        print("$   ERROR IN PRICE")
        data[d][0] = "ERROR IN PRICE"
        data[d][1] = "ERROR IN PRICE"
        data[d][2] = "ERROR IN PRICE"
        
    try:
        data[d][3] = prodTitle.text
    except:
        data[d][3] = "**  ERROR IN PRODUCT NAME"
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
    if 'Alcohol Volume' in titles and 'Standard Drinks' in titles:
        if (data[d][titles.index('Alcohol Volume')] == '' and \
           data[d][titles.index('Standard Drinks')] == '') or \
           data[d][titles.index('Alcohol Volume')] == '0' or \
           (IsNumber(data[d][titles.index('Alcohol Volume')]) and \
           float(data[d][titles.index('Alcohol Volume')]) > 100.00) or \
           data[d][titles.index('Alcohol Volume')] == 'N/A' or \
           (data[d][titles.index('Standard Drinks')] == 'Various' and \
           data[d][titles.index('Alcohol Volume')] == 'Various') or \
           data[d][titles.index('Alcohol Volume')] == '0%' or \
           data[d][titles.index('Standard Drinks')] == '0' or \
           (data[d][titles.index('Alcohol Volume')] == '*' and \
           data[d][titles.index('Standard Drinks')] == '*') or \
           data[d][titles.index('Alcohol Volume')] == 'NA' or \
           'mL' in data[d][titles.index('Alcohol Volume')] or \
           'ml' in data[d][titles.index('Alcohol Volume')] or \
           (data[d][titles.index('Alcohol Volume')] == 'Zero' and \
            data[d][titles.index('Standard Drinks')] == 'Zero') or \
            data[d][titles.index('Alcohol Volume')] == 'zero' or \
            data[d][titles.index('Standard Drinks')] == 'zero':
            del data[d]
            continue
    if 'Alcohol Volume' in titles:
        alcVol = data[d][titles.index('Alcohol Volume')]
        cont = 0
        numed = False
        deler = False
        for letter in data[d][titles.index('Alcohol Volume')]:
            if letter == "(":
                deler = True
            if deler and numed:
                alcVol = alcVol[:cont] + alcVol[cont+1:]
                continue
            if IsNumber(letter):
                numed = True
            elif letter != "." and letter != "-":
                alcVol = alcVol[:cont] + alcVol[cont+1:]
                continue
            cont += 1
        if alcVol == "":
            data[d][titles.index('Alcohol Volume')] = "CHECK ABV"
        else:
            try:
                data[d][titles.index('Alcohol Volume')] = float(alcVol)
            except:
                data[d][titles.index('Alcohol Volume')] = alcVol
                print("#   COULDN'T CONVERT ABV TO FLOAT")
    if 'Standard Drinks' in titles:
        stnds = data[d][titles.index('Standard Drinks')]
        cont = 0
        numed = False
        deler = False
        for letter in data[d][titles.index('Standard Drinks')]:
            if letter == "(":
                deler = True
            if deler and numed:
                stnds = stnds[:cont] + stnds[cont+1:]
                continue
            if IsNumber(letter):
                numed = True
            elif letter != ".":
                stnds = stnds[:cont] + stnds[cont+1:]
                continue
            cont += 1
        if stnds == "" or "-" in data[d][titles.index('Standard Drinks')]:
            data[d][titles.index('Standard Drinks')] = "CHECK SD"
        else:
            try:
                data[d][titles.index('Standard Drinks')] = float(stnds)
            except:
                data[d][titles.index('Standard Drinks')] = stnds
                print("#   COULDN'T CONVERT SD TO FLOAT")
    if 'Size' in titles:
        size = data[d][titles.index('Size')]
        cont = 0
        delete = True
        for letter in data[d][titles.index('Size')]:
            if "x" not in data[d][titles.index('Size')].lower():
                delete = False
            if delete:
                size = size[:cont] + size[cont+1:]
                if letter.lower == "x":
                    delete = False
                continue
            if letter != "." and not IsNumber(letter):
                size = size[:cont] + size[cont+1:]
                continue
            cont += 1
        if "ml" in data[d][titles.index('Size')].lower():
            pass
        elif "l" in data[d][titles.index('Size')].lower():
            try:
                size = round(float(size)*1000, 1)
            except:
                pass
        else:
            try:
                if float(size) < 50:
                    size = round(float(size)*1000, 1)
            except:
                pass
        if size == "":
            data[d][titles.index('Size')] = "CHECK SIZE"
        else:
            try:
                data[d][titles.index('Size')] = float(size)
            except:
                data[d][titles.index('Size')] = size
                print("#   COULDN'T CONVERT SIZE TO FLOAT")
        print(data[d][titles.index('Size')], "mL")
    d += 1

def ValConvert(val):
  if type(val).__name__ == 'unicode':
    return val.encode('utf8')
  elif type(val).__name__ == 'str':
    return val
  else:
    return str(val)

with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(titles)
    for a in data:
        if not all('' == s for s in a):
            try:
                writer.writerow(a)
            except:
                print("ERROR THROWN")
                try:
                    writer.writerow(ValConvert(a))
                except:
                    print("SECOND ERROR THROWN")
                    writer.writerow(["UnicodeEncode"])
    totalTime = (time.time()- start)/60
    writer.writerow(["URL scraping time (mins)", str(URLTime), "Total script time (mins)", str(totalTime)])
print("\n" + "Script executed in", totalTime, "mintues")
driver.quit()
