import os
import time
import random
import pickle
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from undetected_chromedriver import Chrome, ChromeOptions
import requests

# for demo only
from deta import Deta
deta = Deta("c0ds9umrakg_hGsYySDnQ1mNTAcqK39pQUKqwPtXFuJD")

class TokopediaScraperDEMO:
    def __init__(self, config_db_name):
        self.config = self._fetch_config_db(config_db_name)
        self.base_url = self.config.get("base_url", "https://www.tokopedia.com/")
        self.min_delay = self.config.get("min_delay", 8)
        self.max_delay = self.config.get("max_delay", 15)
        self.scroll_step = self.config.get("scroll_step", 7)
        self.min_scroll_delay = self.config.get("min_scroll_delay", 10)
        self.max_scroll_delay = self.config.get("max_scroll_delay", 14)
        self.proxy = self.config.get("proxy")
        self.selectors = self.config.get("selectors", {})
        self.categories = self.config.get("categories", [])

    def _fetch_config(self, config_url):
        response = requests.get(config_url)
        response.raise_for_status()
        return response.json()
    
    def _fetch_config_db(self, config_db_name):
        db = deta.Base(config_db_name)
        db_labeled = db.fetch().items
        return db_labeled[0]

    def _delay(self, min_delay=None, max_delay=None):
        min_delay = min_delay if min_delay is not None else self.min_delay
        max_delay = max_delay if max_delay is not None else self.max_delay
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def _save_cookies(self, driver, file_path="cookies/cookies.pkl"):
        cookies = driver.get_cookies()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump(cookies, f)
        print("Cookies saved successfully.")
    
    def _load_cookies(self, driver, file_path="cookies/cookies.pkl"):
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print("Cookies loaded successfully.")

    def scroll_page(self, driver, steps=None, min_scroll_delay=None, max_scroll_delay=None):
        steps = steps if steps is not None else self.scroll_step
        min_scroll_delay = min_scroll_delay if min_scroll_delay is not None else self.min_scroll_delay
        max_scroll_delay = max_scroll_delay if max_scroll_delay is not None else self.max_scroll_delay
        for _ in tqdm(range(steps), desc="Scrolling"):
            driver.execute_script("window.scrollBy(0, 1000);")
            self._delay(min_scroll_delay, max_scroll_delay)

    def fetch_category_data(self, driver, category_link, headless):
        url = f"{category_link}"
        driver.get(url)
        self._delay(7, 10)

        self.scroll_page(driver)
        content = BeautifulSoup(driver.page_source, 'html.parser')

        products_data = []
        for area in tqdm(content.find_all(*self.selectors['product']), desc="Processing Items"):
            try:
                title = area.find(*self.selectors['title']).get_text()
                price = area.find(*self.selectors['price']).get_text()
                link = area.find('a')['href']
                sold = area.find(*self.selectors['sold'])
                sold = sold.get_text() if sold else None
                location = area.find(*self.selectors['location']).get_text()

                products_data.append({
                    'title': title,
                    'price': price,
                    'link': link,
                    'sold': sold,
                    'location': location,
                    'category': category_link
                })
            except Exception as e:
                print(f"Error processing item: {e}")
                if headless:
                    driver.save_screenshot('category_search_results_error.png')

        return pd.DataFrame(products_data)

    def scrape_categories(self, headless=True, opsys='linux'):
        user_agent = UserAgent(browsers='chrome', os=opsys).random
        options = ChromeOptions()
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--no-sandbox")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-blink-features=AutomationControlled")
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        if headless:
            options.add_argument("--headless")

        driver = Chrome(options=options)
        # driver = webdriver.Chrome(options=options)

        print("WebDriver initialized.")

        all_data = pd.DataFrame()
        for idx, category in enumerate(self.categories):
            self._delay(15, 25)
            df = self.fetch_category_data(driver, category, headless)
            all_data = pd.concat([all_data, df], ignore_index=True)
            all_data.to_csv(f'data/scraped_category_{idx}.csv', index=False)
        print(all_data.shape)
        print(all_data)
        all_data.to_csv(f'data/all_scraped_category.csv', index=False)
        driver.quit()

        return all_data