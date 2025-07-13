import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import random
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import csv
from datetime import datetime
import os


class WebScraper:
    def __init__(self, delay_range=(1, 3), user_agent=None):
        """
        Initialize web scraper with rate limiting and user agent
        """
        self.session = requests.Session()
        self.delay_range = delay_range

        # Set user agent
        if user_agent:
            self.session.headers.update({'User-Agent': user_agent})
        else:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

    def get_page(self, url, retries=3):
        """Get webpage content with error handling and retries"""
        for attempt in range(retries):
            try:
                # Random delay to be respectful
                time.sleep(random.uniform(*self.delay_range))

                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response

            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

    def scrape_basic_data(self, url, selectors):
        """
        Scrape basic data using CSS selectors
        selectors: dict of {field_name: css_selector}
        """
        try:
            response = self.get_page(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            data = {}
            for field, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    if len(elements) == 1:
                        data[field] = elements[0].get_text(strip=True)
                    else:
                        data[field] = [el.get_text(strip=True) for el in elements]
                else:
                    data[field] = None

            return data

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def scrape_table(self, url, table_selector="table"):
        """Scrape HTML tables and convert to pandas DataFrame"""
        try:
            response = self.get_page(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.select_one(table_selector)
            if not table:
                print("No table found with the specified selector")
                return None

            # Extract headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

            # Extract data rows
            rows = []
            for row in table.find_all('tr')[1:]:  # Skip header row
                row_data = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                if row_data:
                    rows.append(row_data)

            # Create DataFrame
            if headers and rows:
                df = pd.DataFrame(rows, columns=headers)
                return df
            else:
                print("No data found in table")
                return None

        except Exception as e:
            print(f"Error scraping table from {url}: {e}")
            return None

    def scrape_links(self, url, link_selector="a", base_url=None):
        """Extract all links from a page"""
        try:
            response = self.get_page(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            links = []
            for link in soup.select(link_selector):
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if base_url:
                        href = urljoin(base_url, href)

                    links.append({
                        'url': href,
                        'text': link.get_text(strip=True),
                        'title': link.get('title', '')
                    })

            return links

        except Exception as e:
            print(f"Error scraping links from {url}: {e}")
            return []


class AdvancedScraper:
    def __init__(self, headless=True):
        """Initialize Selenium-based scraper for JavaScript-heavy sites"""
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        # Note: You need to install ChromeDriver and add it to PATH
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def scrape_dynamic_content(self, url, wait_selector, data_selectors):
        """Scrape content that loads dynamically with JavaScript"""
        if not self.driver:
            self.setup_driver()

        try:
            self.driver.get(url)

            # Wait for content to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))

            data = {}
            for field, selector in data_selectors.items():
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        if len(elements) == 1:
                            data[field] = elements[0].text
                        else:
                            data[field] = [el.text for el in elements]
                    else:
                        data[field] = None
                except Exception as e:
                    print(f"Error getting {field}: {e}")
                    data[field] = None

            return data

        except Exception as e:
            print(f"Error scraping dynamic content from {url}: {e}")
            return None

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()


class ScrapingPipeline:
    def __init__(self, output_dir="scraped_data"):
        """Initialize scraping pipeline with data storage"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.results = []

    def scrape_multiple_pages(self, urls, scraper_func, **kwargs):
        """Scrape multiple pages and collect results"""
        results = []

        for i, url in enumerate(urls, 1):
            print(f"Scraping {i}/{len(urls)}: {url}")

            try:
                data = scraper_func(url, **kwargs)
                if data:
                    data['scraped_url'] = url
                    data['scraped_at'] = datetime.now().isoformat()
                    results.append(data)

            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue

        self.results.extend(results)
        return results

    def save_to_csv(self, filename, data=None):
        """Save scraped data to CSV"""
        if data is None:
            data = self.results

        if not data:
            print("No data to save")
            return

        filepath = os.path.join(self.output_dir, filename)

        # Convert list of dicts to DataFrame
        if isinstance(data[0], dict):
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
        else:
            # Handle other data types
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in data:
                    writer.writerow(row)

        print(f"Data saved to {filepath}")

    def save_to_json(self, filename, data=None):
        """Save scraped data to JSON"""
        if data is None:
            data = self.results

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Data saved to {filepath}")


# Example scraping functions
def scrape_news_headlines():
    """Example: Scrape news headlines"""
    scraper = WebScraper()

    # Example selectors for a news site (adjust for actual sites)
    selectors = {
        'headlines': 'h2.headline',
        'summaries': '.article-summary',
        'authors': '.author-name',
        'dates': '.publish-date'
    }

    # This is a placeholder URL - replace with actual news site
    url = "https://example-news-site.com"

    data = scraper.scrape_basic_data(url, selectors)
    return data


def scrape_product_prices():
    """Example: Scrape product prices for comparison"""
    scraper = WebScraper()
    pipeline = ScrapingPipeline()

    # Example product URLs (replace with actual e-commerce sites)
    product_urls = [
        "https://example-store1.com/product/123",
        "https://example-store2.com/product/456"
    ]

    price_selectors = {
        'product_name': '.product-title',
        'price': '.price',
        'availability': '.stock-status',
        'rating': '.rating-score'
    }

    def scrape_product(url):
        return scraper.scrape_basic_data(url, price_selectors)

    results = pipeline.scrape_multiple_pages(product_urls, scrape_product)
    pipeline.save_to_csv('product_prices.csv')
    pipeline.save_to_json('product_prices.json')

    return results


def scrape_job_listings():
    """Example: Scrape job listings"""
    scraper = WebScraper()

    # Job site selectors (example)
    job_selectors = {
        'job_titles': '.job-title',
        'companies': '.company-name',
        'locations': '.job-location',
        'salaries': '.salary-range',
        'descriptions': '.job-description'
    }

    url = "https://example-job-site.com/search?q=python"
    data = scraper.scrape_basic_data(url, job_selectors)
    return data


def monitor_price_changes():
    """Example: Monitor price changes and send email alerts"""
    from email_automation import EmailAutomation  # Assuming the email script is imported

    scraper = WebScraper()

    # Products to monitor
    products = [
        {
            'name': 'Python Course',
            'url': 'https://example-store.com/python-course',
            'price_selector': '.price',
            'target_price': 50.00
        }
    ]

    # Email setup
    email_bot = EmailAutomation("smtp.gmail.com", 587, "your_email@gmail.com", "your_password")

    for product in products:
        try:
            data = scraper.scrape_basic_data(product['url'], {'price': product['price_selector']})
            if data and data.get('price'):
                # Extract numeric price (you'll need to adjust parsing based on format)
                price_text = data['price']
                current_price = float(price_text.replace('$', '').replace(',', ''))

                if current_price <= product['target_price']:
                    # Send alert email
                    subject = f"Price Alert: {product['name']}"
                    message = f"""
                    Good news! The price for {product['name']} has dropped!

                    Current Price: ${current_price}
                    Target Price: ${product['target_price']}
                    URL: {product['url']}

                    Happy shopping!
                    """

                    email_bot.send_simple_email("your_email@gmail.com", subject, message)
                    print(f"Price alert sent for {product['name']}")

        except Exception as e:
            print(f"Error monitoring {product['name']}: {e}")


def scrape_social_media_posts():
    """Example: Scrape social media posts (requires dynamic scraping)"""
    scraper = AdvancedScraper(headless=True)

    try:
        # This is a placeholder - actual social media scraping requires
        # handling authentication and respecting terms of service
        data_selectors = {
            'posts': '.post-content',
            'likes': '.like-count',
            'shares': '.share-count',
            'comments': '.comment-count'
        }

        url = "https://example-social-site.com/hashtag/python"
        data = scraper.scrape_dynamic_content(url, '.post-content', data_selectors)
        return data

    finally:
        scraper.close()


if __name__ == "__main__":
    print("Web Scraping Examples")
    print("Note: Replace example URLs with actual websites")
    print("Always respect robots.txt and terms of service!")

    # Uncomment to run examples:
    # scrape_news_headlines()
    # scrape_product_prices()
    # scrape_job_listings()