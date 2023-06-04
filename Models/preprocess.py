import re
import nltk
nltk.download('stopwords')

input_str = open("fake_or_real_news_test.csv")

noNewLines = re.sub("\n", "", input_str.read())
noNewLines = re.sub("title,text", "title,text\n", noNewLines)
noNewLines = re.sub(",FAKE", ",FAKE\n", noNewLines)
noNewLines = re.sub(",REAL", ",REAL\n", noNewLines)
lines = noNewLines.split('\n')

def removeComma(g):
  t = g.groups()
  t = [t[0], t[1].replace(',', ' |'), t[2], t[3]]
  return "".join(t)

betweenQuotes = lambda line: re.sub(r'(.*,")(.*)(",)(.*)', lambda x: removeComma(x), line)

secondCol = lambda line: re.sub(r'^([0-9]+,)(.*,.*)(,\")(.*)$', lambda x: removeComma(x), line, 1)


lines = [betweenQuotes(l) for l in lines]
lines = [secondCol(l) for l in lines]

finalString = '\n'.join(lines)


file = open('fake_or_real_news_test_CLEANED.csv', 'w')
file.write(finalString)
file.close()