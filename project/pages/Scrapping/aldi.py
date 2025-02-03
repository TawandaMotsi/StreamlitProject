from selenium.webdriver.common.by import By
from urllib.error import ContentTooShortError
from urllib3.exceptions import NewConnectionError, ConnectionError, MaxRetryError
import time
import pandas as pd
import os
import datetime
from f_initiate_driver import create_headless_driver
import re
from selenium.common.exceptions import (TimeoutException, WebDriverException, NoSuchElementException,
                                        StaleElementReferenceException)
import signal
import subprocess

removed_items = []


def scrape_aldi_data(browser, directory):
    """
        This function scrapes location, name and price data from Aldi's website and saves it in separate CSV files
           for each product category. It handles potential errors during scraping and retries in case of failures.

        Args:
            browser (str): The name of the headless browser to use (e.g., 'chrome', 'firefox').
            directory (str): The directory path to save the scraped data.
    """
    # removed categories: 'specially-selected',
    categories_list = ['vegan-range', 'bakery', 'fresh-food', 'drinks', 'food-cupboard',
                       'frozen', 'chilled-food', 'baby-toddler', 'health-beauty', 'household', 'pet-care']
    # Product Names
    product_name_CSS = '#vueSearchResults .p.text-default-font'
    #  Product Prices
    product_price_CSS = '#vueSearchResults div.product-tile-price.text-center > div > span > span'
    # Product Price per unit
    product_price_per_kg_CSS = '#vueSearchResults div.product-tile-price.text-center > div > div > p > small > span'
    # Product Boxes
    product_boxes_data = '#vueSearchResults .col-6.col-md-4.col-xl-3'

    # Specify the path of the new folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    folder_path = f"{directory}Aldi_Data/{timestamp}"

    class TimedOut(Exception):
        print('The custom error TimedOut has been raised')
        pass

    # Define a signal handler function for the timeout
    def signal_handler(signum, frame):
        raise TimedOut("Timeout occurred")

    def force_quit(process):
        subprocess.run(['pkill', process])

    # Register the signal handler for the SIGALRM signal
    signal.signal(signal.SIGALRM, signal_handler)

    # Initialise the browser outside the function
    browser = f'{browser}'
    driver = create_headless_driver(browser=browser)
    driver.set_script_timeout(30)

    for category in categories_list:
        names_text = []
        names_locations = []
        prices_text = []
        prices_locations = []
        prices_kg_text = []
        prices_kg_locations = []
        boxes_rect = []
        page_numbers_names = []
        page_numbers_prices = []
        page_numbers_prices_kg = []
        page_numbers_boxes = []
        last_page_number = []
        error_list = []
        try:
            driver.get(f'https://groceries.aldi.co.uk/en-GB/{category}')
            time.sleep(3)
            last_page_numbers = driver.find_elements(By.CSS_SELECTOR, f'ul .d-flex-inline.pt-2')
            last_page_number.extend([number.text for number in last_page_numbers])
            last_page_number = last_page_number[1]
            last_page_number = re.sub(r'\D', '', last_page_number)  # Remove non-digit characters
            print(f'The last page number for {category} is: {last_page_number}')
            check = int(last_page_number)
            check.is_integer()
        except (NoSuchElementException, ConnectionError, NewConnectionError, MaxRetryError,
                StaleElementReferenceException, WebDriverException, TimeoutError, ValueError, IndexError):
            # If the initial attempt fails, reload the page and try again
            driver.quit()
            time.sleep(10)
            driver.get(f'https://groceries.aldi.co.uk/en-GB/{category}')
            last_page_numbers = driver.find_elements(By.CSS_SELECTOR, f'ul .d-flex-inline.pt-2')
            last_page_number.extend([number.text for number in last_page_numbers])
            last_page_number = last_page_number[1]
            last_page_number = re.sub(r'\D', '', last_page_number)  # Remove non-digit characters
            print(f'The last page number for {category} is: {last_page_number}')
        page = 1
        while page <= int(last_page_number):
            try:

                # Set the timeout for the page request
                signal.alarm(30)  # Set the timeout to 30 seconds

                driver.get(f'https://groceries.aldi.co.uk/en-GB/{category}?&page={page}')
                time.sleep(3)

                names = driver.find_elements(By.CSS_SELECTOR, product_name_CSS)
                names_text.extend([name.text for name in names])
                page_numbers_names.extend([page] * len(names))

                prices = driver.find_elements(By.CSS_SELECTOR, product_price_CSS)
                prices_text.extend([price.text for price in prices])
                page_numbers_prices.extend([page] * len(prices))

                prices_kg = driver.find_elements(By.CSS_SELECTOR, product_price_per_kg_CSS)
                prices_kg_text.extend([price_kg.text for price_kg in prices_kg])
                page_numbers_prices_kg.extend([page] * len(prices_kg))

                # Use rect to get the rectangles that hold each piece of information
                boxes = driver.find_elements(By.CSS_SELECTOR, product_boxes_data)
                boxes_rect.extend([box.rect for box in boxes])
                page_numbers_boxes.extend([page] * len(boxes))

                # Use getlocation() to see where the price is relative to the other elements
                names_locations.extend([name.location for name in names])
                prices_locations.extend([price.location for price in prices])
                prices_kg_locations.extend([price_kg.location for price_kg in prices_kg])

                # Reset the alarm after a successful page request
                signal.alarm(0)

                # Iterate up a loop
                page += 1

            except (TimedOut, TimeoutException, WebDriverException, ConnectionError, StaleElementReferenceException,
                    NewConnectionError, MaxRetryError, TimeoutError, ContentTooShortError):
                print(f'Request error for page {page} of category {category}')
                # force_quit(process='chromedriver')
                driver.quit()
                time.sleep(30)
                driver = create_headless_driver(browser=browser)
                continue  # Skip to the next page if there is an error

        names_data = {
            'names': names_text,
            'names_locations': names_locations,
            'page_number': page_numbers_names  # Add page numbers list
        }

        df_names = pd.DataFrame(names_data)

        prices_data = {
            'prices': prices_text,
            'prices_locations': prices_locations,
            'page_number': page_numbers_prices  # Add page numbers list
        }

        df_prices = pd.DataFrame(prices_data)

        prices_kg_data = {
            'prices_kg': prices_kg_text,
            'prices_kg_locations': prices_kg_locations,
            'page_number': page_numbers_prices_kg  # Add page numbers list
        }

        df_prices_kg = pd.DataFrame(prices_kg_data)

        boxes_data = {
            'box': boxes_rect,
            'page_number': page_numbers_boxes
        }

        df_boxes = pd.DataFrame(boxes_data)

        # Create the new folder if it doesn't exist
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)

        # Save the modified dataframes to a new CSV file
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        df_names.to_csv(f'{folder_path}/df_names_{category}_{timestamp}.txt',
                        header=True, index=False, sep='\t')

        df_prices.to_csv(f'{folder_path}/df_prices_{category}_{timestamp}.txt',
                         header=True, index=False, sep='\t')

        df_prices_kg.to_csv(f'{folder_path}/df_prices_kg_{category}_{timestamp}.txt',
                            header=True, index=False, sep='\t')

        # Save the Dict DataFrame to a CSV file
        df_boxes.to_csv(f'{folder_path}/df_positions_{category}_{timestamp}.txt', index=False)

    driver.quit()
    print('done')