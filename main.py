from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import csv


class AmazonScraper:
    def __init__(self, driver_path, input_file, output_file):
        # Configure Chrome options to disable JavaScript and images
        chrome_options = Options()
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')

        # Initialize the Chrome WebDriver with the specified options
        self.driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        self.input_file = input_file
        self.output_file = output_file

    def scrape_product_info(self, url):
        # Navigate to the product page
        self.driver.get(url)
        time.sleep(3)

        # Scrape the brand of the product
        try:
            brand = self.driver.find_element(By.XPATH, '//tr[@class="a-spacing-small po-brand"]/td[2]/span').text
        except:
            brand = ""

        # Scrape the product title
        try:
            title = self.driver.find_element(By.XPATH, '//span[@id="productTitle"]').text
        except:
            title = ""

        # Scrape the product capacity
        try:
            capacity = self.driver.find_element(By.XPATH, '//tr[@class="a-spacing-small po-capacity"]/td[2]/span').text
        except:
            capacity = ""

        # Get the energy rating of the product
        energy_rating = self.get_energy_rating()

        # Scrape reviews for the product
        self.scrape_reviews(url, title, brand, energy_rating, capacity)

    def get_energy_rating(self):
        try:
            energy_rating = self.driver.find_element(By.XPATH,
                                                     '//tr[@class="a-spacing-small po-energy_star"]/td[2]/span').text
            return energy_rating.replace(" Star", "")
        except:
            # If not found, search using regex patterns
            all_text = self.driver.find_element(By.TAG_NAME, "body").text
            patterns = [r"Energy Rating:\s*(\d+)", r"Energy Rating :\s*(\d+)", r"Energy Star Rating:\s*(\d+)"]

            for pattern in patterns:
                match = re.search(pattern, all_text)
                if match:
                    return match.group(1)  # Return the first captured group
            return ""

    def scrape_reviews(self, url, title, brand, energy_rating, capacity):
        # Attempt to click the button to view all reviews
        try:
            self.driver.find_element(By.XPATH, '//a[@class="a-link-emphasis a-text-bold"]').click()
            time.sleep(4)  # Wait for the reviews page to load
        except:
            # If the button is not found, write the product data to CSV and exit
            self.write_to_csv([url, title, brand, "", "", "", energy_rating, capacity])
            return

        # Continuously scrape reviews until no more pages are available
        while True:
            review_roots = self.driver.find_elements(By.XPATH, '//div[@id="cm_cr-review_list"]/div')
            for review_root in review_roots:
                r_rating = self.get_review_rating(review_root)
                r_review = self.get_review_text(review_root)
                r_date = self.get_review_date(review_root)

                # Write the scraped data to the CSV file
                self.write_to_csv([url, title, brand, r_rating, r_review, r_date, energy_rating, capacity])

            # Navigate to the next page of reviews
            if not self.go_to_next_page():
                break

    def get_review_rating(self, review_root):
        # Extract the rating
        try:
            r_rating = review_root.find_element(By.XPATH, './/i[@data-hook="review-star-rating"]').get_attribute(
                "class")
            match = re.findall(r"-(\d+)", r_rating)
            return match[0] if match else ""
        except:
            return ""

    def get_review_text(self, review_root):
        # Extract the text of the review
        try:
            return review_root.find_element(By.XPATH, './/span[@data-hook="review-body"]/span').text
        except:
            return ""

    def get_review_date(self, review_root):
        # Extract the date of the review
        try:
            r_date = review_root.find_element(By.XPATH, './/span[@data-hook="review-date"]').text
            return r_date.replace("Reviewed in India on ", "")
        except:
            return ""

    def go_to_next_page(self):
        # Click the next page button to load more reviews
        try:
            next_page = self.driver.find_element(By.XPATH, '//li[@class="a-last"]/a')
            next_page.click()
            time.sleep(1.5)
            return True
        except:
            return False

    def write_to_csv(self, data):
        # Append the scraped data to the output CSV file
        with open(self.output_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(data)

    def start_scraping(self):
        # Initialize the CSV file with headers
        self.setup_csv()
        # Read the input CSV file containing URLs to scrape
        with open(self.input_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for sl, row in enumerate(reader, 1):
                url = row[0]
                print(f"Scraping {sl}: {url}")
                self.scrape_product_info(url)

        print("Scraping Complete!")  # Indicate that scraping is finished
        time.sleep(5)

    def setup_csv(self):
        # Create the output CSV file with headers
        with open(self.output_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['URL', 'Product Name', 'Brand', 'Rating', 'Review', 'Review Date', 'Energy Star', 'Capacity'])


if __name__ == "__main__":
    driver_path = "chromedriver.exe"  # Path to the ChromeDriver
    input_file = 'products_input.csv'  # Input file with product URLs
    output_file = 'output.csv'  # Output file for scraped data

    # Create an instance of the AmazonScraper class and start scraping
    scraper = AmazonScraper(driver_path, input_file, output_file)
    scraper.start_scraping()
