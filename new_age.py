from selenium import webdriver
import time
driver = webdriver.Firefox()
url = "https://sebpearce.com/bullshit/"
driver.get(url)


def get_bs():
    bs = driver.find_element_by_id("third-heading").text
    bs = [bs] + [x.text for x in driver.find_elements_by_class_name("bs-paragraph")]
    driver.find_element_by_xpath("//button[contains(.,'Reionize electrons')]").click()
    return '\n'.join(bs)


quotes = []
while len(quotes)<30000:
    print(len(quotes))
    quote = get_bs()
    if quote not in quotes:
        quotes.append(quote)
    time.sleep(0.3)

quotes.pop(0)

print("Generated quotes")
for i, quote in enumerate(quotes):
    print(quote)