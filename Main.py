import requests
from bs4 import BeautifulSoup
result = requests.get("https://www.danmurphys.com.au/search?searchTerm=*&sort=PriceDesc")
#result = requests.get("https://www.google.com.au/")
#print(result.status_code)
#print(result.headers)
src = result.content
soup = BeautifulSoup(src, 'lxml')
links = soup("a")
print(links)
