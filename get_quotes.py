from selenium import webdriver
driver = webdriver.Firefox()
url = "https://www.bgreco.net/hsquote/10225"
driver.get(url)

def get_quote():
    next = driver.find_element_by_id("submit")
    quote = driver.find_element_by_id("quote").text.split("\nSource: ")[0]
    next.click()
    return quote
#
quotes = []
for i in range(500):
    print(i)
    quote = get_quote()
    quote = quote.replace("[","")
    quote = quote.replace("]","")
    if quote not in quotes:
        quotes.append(quote)
    else:
        print("Repeat, skipping")

for i, quote in enumerate(quotes):
    print(quote)