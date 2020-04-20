import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import json

print("Fetching music list")
r = requests.get("https://hsmusic.github.io/list/tracks/by-name/index.html")
soup = BeautifulSoup(r.content, "html.parser")
page = soup.find("div",attrs={"id":"content"})
music_links = ["https://hsmusic.github.io/"+x.find(href=True)['href'] for x in page.findAll("li")]
musics, flashes = {},{}
tot = len(music_links)
i=0

async def get_cards(url, session, sem):
    global i, tot
    async with sem, session.get(url) as resp:
        data = await resp.text()
        soup = BeautifulSoup(data, "html.parser")
        page = soup.find("div",attrs={"id":"content"})
        title = page.find("h1").text
        listen_link = soup.find(lambda tag:tag.name=="p" and "Listen on" in tag.text).find(href=True)['href']
        musics[title] = listen_link
        flashes_elmts = soup.find(lambda tag:tag.name=="p" and "Flashes that feature" in tag.text)
        if flashes_elmts!=None:
            flashes_elmts = flashes_elmts.findNext("ul")
            flashes_names = [x.text for x in flashes_elmts.findAll(title=True)]
            for flash in flashes_names:
                if flash in flashes:
                    flashes[flash].append(title)
                else:
                    flashes[flash] = [title]
        i+=1
        print(f"Done {i}/{tot} - {title}")


async def main():
    sem = asyncio.Semaphore(100)
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(get_cards(url, session, sem)) for url in music_links]
        results = await asyncio.gather(*tasks)
        return results


asyncio.run(main())

for key in list(flashes.keys()):
    if "==>" in key or "ACT" in key:
        flashes.pop(key)


with open("music.json","r") as f:
    _,_, aliases = json.load(f)

with open("music.json","w") as f:
    json.dump([musics, flashes, aliases], f)
