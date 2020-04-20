import aiohttp
from google import google
from bs4 import BeautifulSoup
from rank_bm25 import BM25Okapi

async def get_wiki_link(query):
    search_results = google.search(query+" site:https://mspaintadventures.fandom.com")
    if search_results!=[]:
        return search_results[0].link
    return None

async def get_best_paragraph(query, paragraphs):
    tokenized_corpus = [par.lower().split(" ") for par in paragraphs]
    query = query.lower().replace("?", "")
    tokenized_query = query.split(" ")
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25.get_top_n(tokenized_query, paragraphs, n=1)[0]

async def get_webpage(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def get_paragraphs(wiki_page_link):
    r = await get_webpage(wiki_page_link)
    soup = BeautifulSoup(r, 'lxml')
    wiki_page = soup.find("div", attrs = {'id':'WikiaArticle'})
    tags = ['figure','aside', 'table']
    for t in tags:
        [s.extract() for s in wiki_page(t)]
    [x.extract() for x in wiki_page.findAll(attrs={"class":"mspaNotice"})]
    paragraphs = wiki_page.find_all("p")
    return [p.text for p in paragraphs]

async def get_wiki(query):
    link = await get_wiki_link(query)
    # paragraphs = await get_paragraphs(link)
    # best_p = await get_best_paragraph(query, paragraphs)
    if link!=None:
        return link
    return "I couldn't find the page you're looking for."

