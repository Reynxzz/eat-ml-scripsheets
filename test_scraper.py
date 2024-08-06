# from scraper.tokopedia_scraper_demo import TokopediaScraperDEMO
from scraper.tokopedia_scraper import TokopediaScraper #use into this if no demo
from scraper.tokopedia_scraper_detail import TokopediaScraperDetail #use into this if no demo

# Example usage:
# config_url = 'http://your-api-endpoint/config' #use this if no demo
config_url = 'https://3k3l6hn8-5000.asse.devtunnels.ms/api/scraper/setting'

# for scraping all products by category
# scraper = TokopediaScraper(config_url)
# scraper.scrape_categories()

# for scraping detail of each product (seller)
scraper = TokopediaScraperDetail(config_url)
scraper.scrape_details()