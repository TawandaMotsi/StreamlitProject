from selenium.webdriver.common.by import By
from urllib.error import ContentTooShortError
from urllib3.exceptions import NewConnectionError, ConnectionError, MaxRetryError
import time
import pandas as pd
import os
import datetime
from f_initiate_driver import create_headless_driver
from selenium.common.exceptions import (TimeoutException, WebDriverException, NoSuchElementException,
                                        StaleElementReferenceException)
import signal
import subprocess

# , 'new---trending', 'price-lock-', 'new-years-party',
#    '355372', '488855', '350369',

removed_items = []
removed_identifiers = []


def scrape_sains_data(browser, directory):
    """
        This function scrapes location, name and price data from Sainsbury's website and saves it in separate CSV files
           for each product category. It handles potential errors during scraping and retries in case of failures.

        Args:
            browser (str): The name of the headless browser to use (e.g., 'chrome', 'firefox').
            directory (str): The directory path to save the scraped data.
    """
    categories_list = ['dietary-and-lifestyle', 'fruit-veg', 'meat-fish', 'dairy-eggs-and-chilled', 'bakery', 'frozen-',
                       'food-cupboard', 'drinks', 'household', 'beauty-and-cosmetics', 'health-beauty',
                       'home', 'baby-toddler-products', 'pet'
                       ]

    categories_code = ['453878', '12518', '13343', '428866', '12320', '218831',
                       '12422', '12192', '12564', '448352', '12448', '281806', '11651', '12298'
                       ]

    dictionary = dict(zip(categories_list, categories_code))
    print(dictionary)
    # Product Names
    product_name_CSS = '#productLister > ul div > div.productInfo > div > h3 > a'
    #  Product Prices
    product_price_CSS = '.pricing .pricePerUnit'
    # Product Price per KG
    product_price_per_kg_CSS = '.pricing .pricePerMeasure'
    # Product boxes data
    product_boxes_data = '#productLister .gridItem'

    # Specify the path of the new folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    folder_path = f"{directory}Sains_Data/{timestamp}"

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
    driver = create_headless_driver(browser=browser)
    driver.set_script_timeout(30)

    for categories_list, categories_code in dictionary.items():
        print(f'{categories_list} and {categories_code}')
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
        error_list = []

        try:
            driver.get(f'https://www.sainsburys.co.uk/shop/CategorySeeAllView?'
                       f'listId=&catalogId=10241&searchTerm=&beginIndex='
                       f'0&pageSize=60&orderBy=FAVOURITES_FIRST'
                       f'&top_category=&langId=44&storeId=10151&categoryId='
                       f'{categories_code}&promotionId=&parent_category_rn=')
            last_page_number = driver.find_element(By.CSS_SELECTOR,
                                                   f'#productLister > div:nth-child(2) > ul.pages > li:nth-child(8) > '
                                                   f'a > span:nth-child(2)').text
            print(f'The last page number for {categories_list} is: {last_page_number}')
        except (NoSuchElementException, ConnectionError, NewConnectionError, MaxRetryError,
                StaleElementReferenceException, TimeoutError, ValueError, IndexError):
            # If the initial attempt fails, reload the page and try again
            driver.refresh()
            time.sleep(10)
            last_page_number = driver.find_element(By.CSS_SELECTOR,
                                                   f'#productLister > div:nth-child(2) > ul.pages > li:nth-child(8) '
                                                   f'> a > span:nth-child(2)').text
            print(f'The last page number for {categories_list} is: {last_page_number}')
            continue
        page = 1
        while page <= int(last_page_number):
            beginIndex = (page - 1) * 60 or 0
            try:

                # Set the timeout for the page request
                signal.alarm(30)  # Set the timeout to 30 seconds

                driver.get(f'https://www.sainsburys.co.uk/shop/CategorySeeAllView?'
                           f'listId=&catalogId=10241&searchTerm=&beginIndex='
                           f'{beginIndex}&pageSize=60&orderBy=FAVOURITES_FIRST'
                           f'&top_category=&langId=44&storeId=10151&categoryId='
                           f'{categories_code}&promotionId=&parent_category_rn=')

                time.sleep(2)

                names = driver.find_elements(By.CSS_SELECTOR, product_name_CSS)

                # Check if the lengths are the same
                names_text_temp = []
                names_locations_temp = []
                names_text_temp.extend([name.text for name in names])
                names_locations_temp.extend([name.location for name in names])
                if len(names_text_temp) != len(names_locations_temp):
                    # If lengths are not the same, re-run the code to collect the data again
                    continue  # This will restart the loop and try to collect the data again

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

                # Use getlocation() to see the relative location
                names_locations.extend([name.location for name in names])
                prices_locations.extend([price.location for price in prices])
                prices_kg_locations.extend([price_kg.location for price_kg in prices_kg])

                # Reset the alarm after a successful page request
                signal.alarm(0)

                # Iterate up a loop
                page += 1

            except (TimedOut, TimeoutException, WebDriverException, ConnectionError,
                    StaleElementReferenceException,
                    NewConnectionError, MaxRetryError, TimeoutError, ContentTooShortError):
                print(f'Request error for page {page} of category {categories_list}')
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
        df_names.to_csv(f'{folder_path}/df_names_{categories_list}_{timestamp}.txt',
                        header=True, index=False, sep='\t')

        df_prices.to_csv(f'{folder_path}/df_prices_{categories_list}_{timestamp}.txt',
                         header=True, index=False, sep='\t')

        df_prices_kg.to_csv(f'{folder_path}/df_prices_kg_{categories_list}_{timestamp}.txt',
                            header=True, index=False, sep='\t')

        # Save the Dict DataFrame to a CSV file
        df_boxes.to_csv(f'{folder_path}/df_positions_{categories_list}_{timestamp}.txt', index=False)

    driver.quit()
    print('done')