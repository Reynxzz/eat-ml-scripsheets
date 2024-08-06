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

class TokopediaScraperDetail:
    def __init__(self, config_url):
        self.config = self._fetch_config(config_url)
        self.base_url = self.config.get("base_url", "https://www.tokopedia.com/")
        self.min_delay = self.config.get("min_delay", 8)
        self.max_delay = self.config.get("max_delay", 15)
        self.scroll_step = 3
        self.min_scroll_delay = self.config.get("min_scroll_delay", 10)
        self.max_scroll_delay = self.config.get("max_scroll_delay", 14)
        self.proxy = self.config.get("proxy")
        self.selectors = {
                        'seller': ('h2', 'css-1wdzqxj-unf-heading e1qvo2ff2'),
                        }
        self.products = ['https://www.tokopedia.com/escendolelizabeth/air-daun-suji-air-perasan-daun-suji?src=topads']

    def _fetch_config(self, config_url):
        response = requests.get(config_url)
        return response.json()[0]

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

    def fetch_product_data(self, driver, product_link, headless):
        url = f"{product_link}"
        driver.get(url)
        self._delay(7, 10)

        self.scroll_page(driver)
        content = BeautifulSoup(driver.page_source, 'html.parser')

        products_data = []
        try:
            seller = content.find(*self.selectors['seller']).get_text()
            products_data.append({
                'seller': seller,
                'link': product_link
            })
        except Exception as e:
            print(f"Error processing item: {e}")
            if headless:
                driver.save_screenshot('detail_search_results_error.png')

        return pd.DataFrame(products_data)

    def scrape_details(self, headless=True, opsys='linux'):
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
        for idx, product in enumerate(self.products):
            self._delay(15, 25)
            df = self.fetch_product_data(driver, product, headless)
            all_data = pd.concat([all_data, df], ignore_index=True)
            all_data.to_csv(f'data/scraped_detail_{idx}.csv', index=False)
        print(all_data.shape)
        print(all_data)
        all_data.to_csv(f'data/all_scraped_detail.csv', index=False)
        driver.quit()

        return all_data