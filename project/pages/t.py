from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Initialize WebDriver
driver = webdriver.Chrome()
driver.get("https://www.lidl.ie/products")

# Scroll down to load all products
for _ in range(50):  # Adjust scroll depth as needed
    driver.find_element_by_tag_name("body").send_keys(Keys.END)
    time.sleep(1)

# Extract product details
html = driver.page_source
# Process HTML using BeautifulSoup
