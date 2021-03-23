from bs4 import BeautifulSoup    
from urllib.request import urlopen
import re

url="https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card"
html=urlopen(url)
soup= BeautifulSoup(html)

#If title exists
title=soup.title()

#Get all the links in the page selecting text  within <a> </a> where href cointains an URL
links=soup.find_all('a', href=True)

#Get images from <div>
img_containers=soup.find_all("div", {"class":"item-container"})

#Get all images looking at the hierarchy of html tags
for item in img_containers:
    image=item.a.img["data-src"]
    print(image)

#After importing libraries, this code will get the info from our printer
printer_url="http://nld-printer1.safesize.com/sys_count.html"
containers=soup.find_all("table", {"class":"main"})
