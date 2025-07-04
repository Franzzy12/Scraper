"""Simple web scraper for Google or Bing Maps results using Selenium.

Usage:
    python scraper.py --query "coffee shops" --provider google

Note: This script requires the selenium package and a webdriver like ChromeDriver
available on your PATH. The page structure of map providers may change over time,
so selectors might need to be updated.
"""
import csv
import time
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Time to wait between scroll attempts when loading results
SCROLL_PAUSE = 2


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Create a Chrome WebDriver instance."""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    return driver


def search_google(driver: webdriver.Chrome, query: str):
    """Search Google Maps for the query."""
    driver.get("https://www.google.com/maps")
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)  # wait for results to load


def scroll_to_load_results(driver: webdriver.Chrome, limit: int, listing_selector: str):
    """Scroll the page until at least ``limit`` listings are loaded."""
    last_height = 0
    while True:
        listings = driver.find_elements(By.CSS_SELECTOR, listing_selector)
        if len(listings) >= limit:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def parse_google_results(driver: webdriver.Chrome, limit: int = 10):
    """Yield business info dictionaries from Google Maps results."""
    scroll_to_load_results(driver, limit, "div[role='article']")
    results = []
    listings = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
    for listing in listings[:limit]:
        try:
            listing.click()
            time.sleep(3)  # wait for details pane
            name = driver.find_element(By.CSS_SELECTOR, "h1[data-attrid='title'] span").text
        except Exception:
            continue

        info = {"name": name}
        try:
            info["phone"] = driver.find_element(By.CSS_SELECTOR, "button[data-item-id='phone'] span:nth-child(2)").text
        except Exception:
            info["phone"] = ""
        try:
            info["website"] = driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']").get_attribute("href")
        except Exception:
            info["website"] = ""
        try:
            info["address"] = driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address'] span:nth-child(2)").text
        except Exception:
            info["address"] = ""
        try:
            info["email"] = driver.find_element(By.XPATH, "//a[starts-with(@href,'mailto:')]").get_attribute("href")[7:]
        except Exception:
            info["email"] = ""

        results.append(info)
        driver.back()
        time.sleep(2)

    return results


def search_bing(driver: webdriver.Chrome, query: str):
    """Search Bing Maps for the query."""
    driver.get("https://www.bing.com/maps")
    try:
        search_box = driver.find_element(By.ID, "maps_sb")
    except Exception:
        search_box = driver.find_element(By.ID, "sb_form_q")
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)


def parse_bing_results(driver: webdriver.Chrome, limit: int = 10):
    """Yield business info dictionaries from Bing Maps results."""
    scroll_to_load_results(driver, limit, "li.entity")
    results = []
    listings = driver.find_elements(By.CSS_SELECTOR, "li.entity")
    for listing in listings[:limit]:
        try:
            listing.click()
            time.sleep(3)
            name = driver.find_element(By.CSS_SELECTOR, "h1").text
        except Exception:
            continue

        info = {"name": name}
        try:
            info["phone"] = driver.find_element(By.CSS_SELECTOR, "span[aria-label^='Phone']").text
        except Exception:
            info["phone"] = ""
        try:
            info["website"] = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Website']").get_attribute("href")
        except Exception:
            info["website"] = ""
        try:
            info["address"] = driver.find_element(By.CSS_SELECTOR, "div[data-automation-id='address']").text
        except Exception:
            info["address"] = ""
        try:
            info["email"] = driver.find_element(By.XPATH, "//a[starts-with(@href,'mailto:')]").get_attribute("href")[7:]
        except Exception:
            info["email"] = ""

        results.append(info)
        driver.back()
        time.sleep(2)

    return results


def save_to_csv(data, file_path: str):
    """Save scraped data to a CSV file."""
    if not data:
        return
    keys = data[0].keys()
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(description="Scrape map business listings")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--provider", choices=["google", "bing"], default="google")
    parser.add_argument("--limit", type=int, default=10, help="Number of results")
    parser.add_argument("--output", default="results.csv", help="Output CSV file")
    parser.add_argument("--headless", action="store_true", help="Run headless browser")

    args = parser.parse_args()
    driver = create_driver(args.headless)
    try:
        if args.provider == "google":
            search_google(driver, args.query)
            data = parse_google_results(driver, args.limit)
        elif args.provider == "bing":
            search_bing(driver, args.query)
            data = parse_bing_results(driver, args.limit)
        else:
            data = []
        save_to_csv(data, args.output)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
