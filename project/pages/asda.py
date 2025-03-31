from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.error import ContentTooShortError
from urllib3.exceptions import NewConnectionError, ConnectionError, MaxRetryError
import time
import pandas as pd
import os
import datetime
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.common.exceptions import NoSuchElementException
from random import randint
from f_initiate_undetected_driver import create_undetected_headless_driver
from f_initiate_driver import create_headless_driver

# Excluded: 'christmas' 'special-offers', 'events-inspiration',
# driver.refesh()
removed_items = []


def scrape_asda_data(browser, directory):
    """
        This function scrapes location, name and price data from ASDA's website and saves it in separate CSV files
           for each product category. It handles potential errors during scraping and retries in case of failures.

        Args:
            browser (str): The name of the headless browser to use (e.g., 'chrome', 'firefox').
            directory (str): The directory path to save the scraped data.
    """
    categories_list = \
        ['vegan-vegetarian', 'dietary-lifestyle',
         'fruit', 'vegetables-potatoes', 'salads-stir-fry', 'extra-special-fruit-veg', 'raw-nuts-seeds-dried-fruit',
         'meat-poultry', 'fish-seafood',
         'cooked-meat',
         'bakery',
         # chilled-food
         'milk-butter-cream-eggs', 'cheese', 'yogurts-desserts',
         'chilled-juice-smoothies', 'ready-meals', 'pizza-pasta-garlic-bread',
         'party-food-pies-salads-dips', 'sandwiches',
         'frozen-food',
         # Food-cupboard
         'cereals-cereal-bars', 'chocolates-sweets', 'crisps-nuts-popcorn',
         'biscuits-crackers', 'tinned-food',
         'condiments-cooking-ingredients', 'cooking-sauces-meal-kits-sides', 'rice-pasta-noodles',
         'coffee-tea-hot-chocolate',
         'jams-spreads-desserts', 'noodle-pots-instant-snacks', 'home-baking', 'under-100-calories', 'world-food',
         # drinks
         'fizzy-drinks', 'squash-cordial', 'water', 'tonic-water-mixers', 'fruit-juice', 'sports-energy-drinks',
         'coffee-tea-hot-chocolate',
         # beer wine spirits
         'beer', 'wine', 'spirits', 'cider', 'prosecco-champagne', 'pre-mixed-cocktails',
         'tobacconist',
         # 'toiletries-beauty',
         "hair-care-dye-styling", "make-up-nails", "mens-toiletries", "womens-toiletries", "oral-dental-care",
         "period-products",
         "skin-care", "bath-shower-soap", 'beauty-electricals', 'sunscreen', 'bladder-weakness',
         'health-wellness', 'sun-care-tanning', "toiletries-accessories",
         "air-fresheners", "batteries", "bin-bags", "cleaning", "dishwasher", "fabric-conditioners",
         "household-accessories", "ironing",
         "kitchen-roll", "laundry", "light-bulbs", "shoe-care", "toilet-roll", "washing-powder-liquid",
         'baby-toddler-kids',
         'pets',
         # Home
         'bed-bath-home', 'kitchen', 'music-films-books', "dvds-blu-rays", "gaming", "headphones-speakers",
         "smart-home",
         "tvs-accessories", 'diy-car-care', 'toys', 'technology-electricals', 'flowers'
         ]
    # Product Names
    product_name_CSS = ('#main-content '
                        '.co-product-list__main-cntr.co-product-list__main-cntr--rest-in-shelf '
                        '.co-product__anchor')
    #  Product Prices
    product_price_CSS = ('#main-content '
                         '.co-product-list__main-cntr.co-product-list__main-cntr--rest-in-shelf '
                         '.co-product__price')
    # Product Price per KG
    product_price_per_kg_CSS = ('#main-content '
                                '.co-product-list__main-cntr.co-product-list__main-cntr--rest-in-shelf '
                                '.co-product__price-per-uom')

    product_boxes_data = '.co-item.co-item--rest-in-shelf '

    # Specify the path of the new folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    folder_path = f"{directory}ASDA_Data/{timestamp}"

    for category in categories_list:

        browser = f'{browser}'
        driver = create_headless_driver(browser=browser)
        driver.set_script_timeout(30)

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

        driver.get(f'https://groceries.asda.com/search/{category}')
        time.sleep(10)
        try:
            last_page_number = driver.find_element(By.CSS_SELECTOR,
                                                   '#main-content div.co-pagination__max-page > a').text
            print(f'The last page number for {category} is: {last_page_number}')
            if int(last_page_number) >= 20:
                last_page_number = 17
            driver.quit()
        except NoSuchElementException:
            last_page_number = 1
            print(f'The last page number for {category} is: {last_page_number}')
            driver.quit()
        except (TimeoutException, WebDriverException, ValueError,
                ConnectionError, NewConnectionError, MaxRetryError, TimeoutError, ContentTooShortError):
            driver.quit()
            driver.get(f'https://groceries.asda.com/search/{category}')
            wait = WebDriverWait(driver, 30)  # Wait for a maximum of 30 seconds
            time.sleep(10)
            last_page_number = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#main-content div.co-pagination__max-page > a'))).text
            print(f'The last page number for {category} is: {last_page_number}')
            if int(last_page_number) >= 20:
                last_page_number = 17
            driver.quit()
        page = 1
        while page <= int(last_page_number):
            browser = 'Chrome'
            driver = create_headless_driver(browser=browser)
            try:
                driver.get(f'https://groceries.asda.com/search/{category}/products?page={page}')
                time.sleep(randint(2, 5))
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

                # Use getlocation() to see where the clubcard price is relative to the other elements
                names_locations.extend([name.location for name in names])
                prices_locations.extend([price.location for price in prices])
                prices_kg_locations.extend([price_kg.location for price_kg in prices_kg])

                # Iterate up a loop
                page += 1

            except (TimeoutException, WebDriverException,
                    ConnectionError, NewConnectionError, MaxRetryError, TimeoutError, ContentTooShortError) as exc:
                print(f'Timeout error for page {page} of category {category}')
                driver.quit()
                time.sleep(30)
                driver = create_headless_driver(browser=browser)
                error_list.append(exc)
                continue  # Skip to the next page if there is an error

            driver.quit()

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