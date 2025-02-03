
from aldi import scrape_aldi_data
from lidl import scrape_sains_data
from tesco import scrape_Tesco_data
import subprocess


def main():
    """
    This script will run a web scraping script for Aldi, ASDA, Sainsburys, Morrisons and Tesco.

    Returns:
    Files containing the price, price per unit, name and position on the webpage of each item.
    The files are split by each supermarket and category and saved accordingly.
    """
   
    print('Started Aldi'),
    scrape_aldi_data(browser, directory)
    print('Started Tesco'), force_quit(process=process_quit)
    scrape_Tesco_data(browser, directory), force_quit(process=process_quit)
    print('Started Sainsburys'), force_quit(process=process_quit)
    scrape_sains_data(browser, directory), force_quit(process=process_quit)
    print('The Webscraping process has completed')


# The force_quit process forces chromedriver to quit on my OS.
# This is an open glitch for Seleniun Webdriver.
def force_quit(process):
    subprocess.run(['pkill', process])


# Call the function
browser = 'Chrome'
process_quit = 'chromedriver'
directory = '/Users/declanmcalinden1/PycharmProjects/uksupermarketscraping/'
main()