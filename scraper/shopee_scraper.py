import os
import time
import random
import pickle
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from undetected_chromedriver import Chrome, ChromeOptions

class ShopeeScraper:
    def __init__(self, base_url="https://shopee.co.id"):
        self.base_url = base_url

    def _delay(self, min_delay=8, max_delay=15):
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

    def login_and_save_cookies(self, driver, email, password):
        driver.get(f"{self.base_url}/buyer/login")
        wait = WebDriverWait(driver, 45)
        wait.until(EC.element_to_be_clickable((By.NAME, 'loginKey'))).send_keys(email)
        self._delay(8, 20)
        wait.until(EC.element_to_be_clickable((By.NAME, 'password'))).send_keys(password)
        self._delay(5, 15)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Log in']"))).click()
        time.sleep(5)
        self._save_cookies(driver)
        print("Login successful.")

    def scroll_page(self, driver, steps=7, min_scroll_delay=10, max_scroll_delay=14):
        for _ in tqdm(range(steps), desc="Scrolling"):
            driver.execute_script("window.scrollBy(0, 1000);")
            self._delay(min_scroll_delay, max_scroll_delay)

    def fetch_category_data(self, driver, email, password , category_link, page, selectors, login_alert="Login sekarang untuk mulai berbelanja!"):
        url = f"{category_link}?page={page}"
        driver.get(url)
        self._delay(7, 10)

        if login_alert in driver.page_source:
            print("Login required")
            self.login_and_save_cookies(driver, email, password)
            driver.get(url)
            self._delay(7, 10)

        self.scroll_page(driver)
        content = BeautifulSoup(driver.page_source, 'html.parser')

        products_data = []
        for area in tqdm(content.find_all(*selectors['product']), desc="Processing Items"):
            try:
                title = area.find(*selectors['title']).get_text()
                price = area.find(*selectors['price']).get_text()
                link = self.base_url + area.find('a')['href']
                sold = area.find(*selectors['sold'])
                sold = sold.get_text() if sold else None
                location = area.find(*selectors['location']).get_text()

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
                driver.save_screenshot('category_search_results_error.png')

        return pd.DataFrame(products_data)

    def scrape_categories(self, email, password, category_links, selectors, login_alert, proxy=None, headless=False, os='linux'):
        user_agent = UserAgent(browsers='chrome', os=os).random
        options = ChromeOptions()
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--no-sandbox")
        options.add_argument( '--auto-open-devtools-for-tabs' )
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        if headless:
            options.add_argument("--headless")

        driver = Chrome(options=options, version_main=119)
        print("WebDriver initialized.")

        all_data = pd.DataFrame()
        for idx, category in enumerate(category_links):
            self._delay(10, 25)
            for page in range(9):
                self._delay(15, 25)
                df = self.fetch_category_data(driver, email, password, category, page, selectors, login_alert)
                if len(df) < 60:
                    print(f"WARNING: only {len(df)} products scraped")
                    driver.save_screenshot(f'only_{len(df)}_products_scraped.png')
                all_data = pd.concat([all_data, df], ignore_index=True)

            all_data.to_csv(f"data/all_category_full_{idx}.csv", index=False)
        driver.quit()

# Example usage:
selectors = {
    'product': ('li', 'col-xs-2-4 shopee-search-item-result__item'),
    'title': ('div', 'DgXDzJ rolr6k Zvjf4O'),
    'price': ('span', 'k9JZlv'),
    'sold': ('div', 'OwmBnn eumuJJ'),
    'location': ('div', 'JVW3E2')
}
login_alert = "Login sekarang untuk mulai berbelanja!"

scraper = ShopeeScraper()
scraper.scrape_categories('luthfirey258','zcxfzxxzShopee', 
    ['https://shopee.co.id/Makanan-Minuman-cat.11043451'],
    selectors=selectors,
    login_alert=login_alert
)