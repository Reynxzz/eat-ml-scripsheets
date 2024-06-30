from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
import re
import pickle

stop_words = set(stopwords.words('indonesian'))
stemmer = StemmerFactory().create_stemmer()
non_alpha_regex = re.compile(r'[^a-zA-Z\s]')
pattern = {'gram', 'ml', 'kg', 'gr', 'pcs', 'ltr', 'liter', 'oz', 'lb', 'cc', 'pack', 'box', 'bottle', 'jar', 'can', 'piece', 'slice'}

def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [token.lower() for token in tokens if not non_alpha_regex.search(token)]
    tokens = [stemmer.stem(token) for token in tokens if token not in stop_words and token not in pattern and not token.isdigit()]
    return ' '.join(tokens)

def preprocess_text_series(series):
    return series.apply(preprocess_text)
from tasks import scrape_and_classify

result = scrape_and_classify.delay(['https://www.tokopedia.com/p/makanan-minuman/makanan-ringan'])
print(result.get())