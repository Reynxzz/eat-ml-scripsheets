from scraper.tokopedia_scraper_demo import TokopediaScraper
# from scraper.tokopedia_scraper import TokopediaScraper #use into this if no demo

# Example usage:
# config_url = 'http://your-api-endpoint/config' #use this if no demo
config_url = 'config-scraper'
scraper = TokopediaScraper(config_url)
scraper.scrape_categories()