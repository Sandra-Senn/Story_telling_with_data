import pandas as pd
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import base64
import time
import subprocess

# Suppress TensorFlow Lite logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Setup Selenium WebDriver with suppressed DevTools messages
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(ChromeDriverManager().install())
    service.creationflags = subprocess.CREATE_NO_WINDOW  # Suppress console window on Windows
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Scroll down to load more images
def scroll_down(driver, scroll_pause_time=2, scroll_limit=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(scroll_limit):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Scrape all images from the page
def scrape_all_images(driver):
    try:
        images = driver.find_elements(By.TAG_NAME, 'img')
        image_urls = []
        for img in images:
            image_url = img.get_attribute('src') or img.get_attribute('data-src')
            if image_url and "data:image/gif" not in image_url:
                width = int(img.get_attribute('width') or 0)
                height = int(img.get_attribute('height') or 0)
                if width >= 100 and height >= 100:  # Filter out small images
                    image_urls.append(image_url)
        return image_urls
    except Exception as e:
        print(f"Error scraping images: {e}")
        return []

# Save the image to the specified folder
def save_image(image_url, folder_name, file_name, retry_count=3):
    try:
        file_path = os.path.join(folder_name, f"{file_name}.jpg")

        if image_url.startswith('data:image/'):  # Handle base64 images
            header, encoded = image_url.split(',', 1)
            image_data = base64.b64decode(encoded)
            with open(file_path, 'wb') as f:
                f.write(image_data)

        else:  # Handle standard HTTP/HTTPS images
            for attempt in range(retry_count):
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    break
                else:
                    print(f"Failed attempt {attempt + 1} for image: {image_url}")
                    time.sleep(2)
    except Exception as e:
        print(f"Error saving image {file_name}: {e}")

# Main scraping function
def scrape_and_save_images(base_folder, search_term: str, num_images=1):
    folder_path = os.path.join(base_folder, "img_scraper")

    # Ensure folder exists with proper permissions
    try:
        os.makedirs(folder_path, exist_ok=True)
    except PermissionError as e:
        print(f"Permission denied: {e}")
        return

    driver = create_driver()
    
    try:
        driver.get(f"https://www.google.com/search?q={search_term}&tbm=isch")
        time.sleep(5)  # Wait for page to load fully

        scroll_down(driver)  # Scroll down to load more images

        image_urls = scrape_all_images(driver)[:num_images]  # Limit to specified number of images

        for index, image_url in enumerate(image_urls, start=1):
            file_name = f'{search_term.replace(" ", "_")}_{index}'  # Replace spaces in file name with underscores
            save_image(image_url, folder_path, file_name)

        print(f"Finished scraping {len(image_urls)} images for '{search_term}'")
    
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    finally:
        driver.quit()  # Ensure browser is closed




# Read fish names from CSV and run the script
if __name__ == "__main__":
    data = pd.read_csv("../data/Fischdaten.csv")
    fish_list = data["Name wissenschaftlich"]
    
    base_folder = "img_webscrape"
    
    for fish_name in fish_list:  # Iterate over fish names correctly
        scrape_and_save_images(base_folder, search_term=fish_name.strip(), num_images=1)

