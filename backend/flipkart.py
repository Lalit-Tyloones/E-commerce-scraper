from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas as pd
import random

def setup_browser():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('detach', True)
    options.add_argument("start-maximized")
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(70, 90)}.0.{random.randint(3000, 4000)}.212 Safari/537.36")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_product_info(product_element):
    product_info = {}
    try:
        product_info['name'] = product_element.find_element(By.XPATH, ".//div[@class='KzDlHZ']").text
    except:
        product_info['name'] = None

    try:
        product_info['price'] = product_element.find_element(By.XPATH, ".//div[@class='Nx9bqj _4b5DiR']").text
    except:
        product_info['price'] = None

    try:
        product_info['product_link'] = product_element.find_element(By.XPATH, ".//img").get_attribute("src")
    except:
        product_info['product_link'] = None

    try:
        rating_element = product_element.find_element(By.XPATH, ".//div[@class='XQDdHH']")
        product_info['rating'] = rating_element.text
    except:
        product_info['rating'] = None

    try:
        product_info['details'] = product_element.find_element(By.XPATH, ".//div[@class='_6NESgJ']").text
    except:
        product_info['details'] = None
    
    return product_info

def scrape_flipkart(search_term):
    browser = setup_browser()
    browser.get('https://www.flipkart.com/')
    sleep(random.uniform(2, 4)) 

    input_search = browser.find_element(By.NAME, 'q')
    search_button = browser.find_element(By.XPATH, ".//button[@class='_2iLD__']")

    input_search.send_keys(search_term)
    sleep(random.uniform(1, 2))
    search_button.click()
    sleep(random.uniform(2, 4))  

    products = []
    
    # Scraping products only from the first page
    product_elements = browser.find_elements(By.XPATH, ".//div[@class='cPHDOP col-12-12']")
    for product_element in product_elements:
        products.append(extract_product_info(product_element))

    df = pd.DataFrame(products)
    print(df)
    #browser.quit()
    return df

# Call the scrape_flipkart function
# df = scrape_flipkart("Smartwatches")
# df.to_csv("flipkart_product_data.csv", index=False)
