import nltk
import re, json
import random
from nltk.util import ngrams
quotes = json.load(open("REPLIES"))
s = "".join(quotes)
s = s.lower()
s=re.sub("[^A-Za-z]", " ",s)
s=re.sub("  ", " ", s)
tokens = nltk.word_tokenize(s)
from collections import Counter

res = Counter(ngrams(tokens, 3)).most_common(100)

for x,i in res:
    print(' '.join(x), '-', i)


regex = 'humankind'
replacements =\
["humankind", "trollkind", "paradox space"]
for i,t in enumerate(quotes):
    quotes[i] = re.sub(regex, lambda x: random.choice(replacements), t)


for x in quotes[:500]:
    i = x.find('we are')
    if i!=-1:
        print(x[i-30:i+35])


# json.dump(quotes, open("REPLIES", "w"))