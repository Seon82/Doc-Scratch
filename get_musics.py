import requests
from bs4 import BeautifulSoup
import json
page = requests.get("https://homestuck.bandcamp.com/")
soup = BeautifulSoup(page.content, 'html.parser')
discography = soup.find(attrs = {"id":"discography"})
albums = [x.find(href=True)['href'] for x in discography.find_all(attrs = {"class":"trackTitle"})]
res = {}
for album_link in albums:
    print("Getting album", "https://homestuck.bandcamp.com"+album_link)
    page = requests.get("https://homestuck.bandcamp.com"+album_link)
    print("Got it")
    soup = BeautifulSoup(page.content, 'html.parser')
    titles = soup.find_all(attrs = {"class":"title-col"})
    for title in titles:
        key = title.find('span').text
        val = "https://homestuck.bandcamp.com"+title.find(href=True)['href']
        res[key]=val
print("Done")

json.dump(res, open("Music.json","w"))
print("Saved")