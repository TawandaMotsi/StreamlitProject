import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Ensure the module path is added
import sys
from pathlib import Path

# Adjust this path to where the 'F_check_last_page_number.py' module is located
module_path = Path("/Users/tawandamotsi/Downloads/ProjectStreamlit/project/pages/Scrapping")
sys.path.append(str(module_path))

try:
    from F_check_last_page_number import get_last_page_number
except ModuleNotFoundError:
    print("Error: 'F_check_last_page_number' module not found. Ensure it is in the correct path.")
    sys.exit(1)

# Define headers to avoid blocking by the website
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
}

# URL of Tesco
url = "https://www.tesco.ie/groceries/en-IE/shop/fresh-food/all"

# Set up retry logic
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

try:
    print("Fetching data from Tesco...")
    response = session.get(url, headers=headers, timeout=30)
    response.raise_for_status()  # Raise an error for HTTP issues
    print("Response received successfully!")

    # Example of using the imported function (adjust based on your project logic)
    last_page = get_last_page_number(response.text)
    print(f"Last page number: {last_page}")

except requests.exceptions.Timeout:
    print("Error: The request timed out. Try increasing the timeout or checking your network.")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
