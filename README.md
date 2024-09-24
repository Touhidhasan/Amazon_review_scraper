# Amazon Review Scraper

This project is a Python-based web scraper designed to extract product reviews from Amazon. It leverages Selenium to navigate through product pages, gather information such as product details, ratings, and reviews, and save the data in a CSV file.


## Features

- Scrapes product information including:
  - Brand
  - Title
  - Capacity
  - Energy rating
  - Reviews (rating, text, and date)
- Supports pagination to scrape reviews across multiple pages
- Outputs the data to a CSV file for easy analysis

## Requirements

To run this project, you need:

- Python 3.x
- `selenium` package
- ChromeDriver (compatible with your version of Chrome)

You can install the required package using pip:

```bash
pip install selenium


