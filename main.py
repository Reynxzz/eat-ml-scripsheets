# from scraper.tokopedia_scraper_demo import TokopediaScraperDEMO
from scraper.tokopedia_scraper import TokopediaScraper
from scraper.tokopedia_scraper_detail import TokopediaScraperDetail
import pandas as pd
import joblib
from preprocess import *
from utils import load_data_from_csv, df_to_db, classify_task, extract_keywords
from utils import SCRAPER_SETTING_URL, CAT_SCRAPED_OUTPUT_DIR, DETAIL_SCRAPED_OUTPUT_DIR, SEND_PRODUCT_URL, SEND_KEYWORD_URL

# for scraping all products by category
scraper_cat = TokopediaScraper(SCRAPER_SETTING_URL)
scraper_cat.scrape_categories()
prod_df = load_data_from_csv(CAT_SCRAPED_OUTPUT_DIR)

# for scraping detail of each product (seller)
prod_list = prod_df['link'].to_list()
scraper_detail = TokopediaScraperDetail(SCRAPER_SETTING_URL, prod_list)
scraper_detail.scrape_details()
detail_df = load_data_from_csv(DETAIL_SCRAPED_OUTPUT_DIR)

#get full scraped data
scraped = pd.merge(prod_df, detail_df, on='link', how='left')
scraped['label'] = 'Legal'

df_to_db(scraped, SEND_PRODUCT_URL)

#prediction
pipeline = joblib.load('pipelines/pipeline.joblib')
df_pred = classify_task(scraped, pipeline)
df_pred['label'] = df_pred['label'].map({0: 'Legal', 1: 'Illegal'})
print(df_pred)

df_to_db(df_pred, SEND_PRODUCT_URL)

# keywords database
df_kwrd = extract_keywords(df_pred, 'title')
df_to_db(df_kwrd, SEND_KEYWORD_URL)