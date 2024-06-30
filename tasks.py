from celery import Celery
from celery.schedules import crontab
from scraper.tokopedia_scraper import TokopediaScraper
import pandas as pd
# import joblib
import requests
from celery import chain
from sklearn.pipeline import Pipeline
import pickle
# import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
import re
from preprocess import pipeline

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

stop_words = set(stopwords.words('indonesian'))
stemmer = StemmerFactory().create_stemmer()
non_alpha_regex = re.compile(r'[^a-zA-Z\s]')
pattern = {'gram', 'ml', 'kg', 'gr', 'pcs', 'ltr', 'liter', 'oz', 'lb', 'cc', 'pack', 'box', 'bottle', 'jar', 'can', 'piece', 'slice'}

# def preprocess_text(text):
#     tokens = word_tokenize(text)
#     tokens = [token.lower() for token in tokens if not non_alpha_regex.search(token)]
#     tokens = [stemmer.stem(token) for token in tokens if token not in stop_words and token not in pattern and not token.isdigit()]
#     return ' '.join(tokens)

# def preprocess_text_series(series):
#     return series.apply(preprocess_text)

selectors = {
    'product': ('div', 'css-bk6tzz e1nlzfl2'),
    'title': ('span', 'css-20kt3o'),
    'price': ('span', 'css-o5uqvq'),
    'sold': ('span', 'ycJITt9ym8j_SF77Kv5q'),
    'location': ('span', 'css-ywdpwd')
}


# step_names = ['preprocess', 'tfidf', 'rf']  # Replace with actual step names

# # Load each step from its file
# steps = []
# for step_name in step_names:
#     with open(f'pipelines/{step_name}.pkl', 'rb') as f:
#         step_obj = pickle.load(f)
#         steps.append((step_name, step_obj))

# Reconstruct the pipeline
# pipeline = Pipeline(steps)


DATA_PATH = 'all_category_full_0.csv'
GET_DATABASE_URL = "https://api.fadilfauzan.com/api/scraper"

def load_data_from_csv(path):
  df = pd.read_csv(path)
  return df

def load_data_from_db(url, key, idx_range):
    full_df = pd.DataFrame()
    for idx in range(0, idx_range):
        json_data = {
            "key": f'{key}_{idx}'
        }
        response = requests.get(url, json=json_data)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            full_df = full_df.append(df, ignore_index=True)
        else:
            print(f"Failed to retrieve data for index {idx}")

    return full_df

# df = load_data_from_csv(DATA_PATH)

@celery.task()
def scrape_task():
    print("Scraping started...")
    scraper = TokopediaScraper("config-scraper")
    return scraper.scrape_categories().to_dict()

@celery.task()
def classify_task(df):
    print("Classifying started...")
    df = pd.DataFrame(df)
    df['label'] = pipeline.predict(df['title'])
    df.to_csv(f'data/all_scraped_category_classified.csv', index=False)
    print(df)
    return df.to_dict()

@celery.task()
def scrape_and_classify():
    workflow = chain(scrape_task.s() | classify_task.s())
    return workflow()

celery.conf.beat_schedule = {
    'run-every-midnight': {
        'task': 'tasks.scrape_and_classify',
        'schedule': crontab(minute=0, hour=0),  # Run every midnight
    },
}

# for demo purpose only
# celery.conf.beat_schedule = {
#     'run-every-2-minutes': {
#         'task': 'tasks.scrape_and_classify',
#         'schedule': crontab(minute='*/2'),  # Run every 2 minutes
#     },
# }