
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import random
import os
from time import sleep
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

def setup_browser():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('detach', True)
    options.add_argument("start-maximized")
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(70, 90)}.0.{random.randint(3000, 4000)}.212 Safari/537.36")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_total_pages_amazon(browser):
    try:
        pagination = browser.find_element(By.CLASS_NAME, 's-pagination-strip')
        pages = pagination.find_elements(By.XPATH, ".//li[@class='a-disabled' or @class='a-normal']")
        if pages:
            total_pages = int(pages[-1].text)
        else:
            total_pages = 1
    except Exception as e:
        logging.error("Error extracting total pages: %s", e)
        total_pages = 1
    return total_pages

def extract_product_info_amazon(product_element):
    product_info = {}
    try:
        product_info['name'] = product_element.find_element(By.XPATH, ".//span[@class='a-size-medium a-color-base a-text-normal']").text
    except Exception as e:
        logging.error("Error extracting product name: %s", e)
        product_info['name'] = None

    try:
        product_info['price'] = product_element.find_element(By.XPATH, ".//span[@class='a-price-whole']").text
    except Exception as e:
        logging.error("Error extracting product price: %s", e)
        product_info['price'] = None

    try:
        product_info['product_link'] = product_element.find_element(By.XPATH, ".//img").get_attribute("src")
    except Exception as e:
        logging.error("Error extracting product link: %s", e)
        product_info['product_link'] = None

    try:
        rating_element = product_element.find_element(By.XPATH, ".//span[@class='a-icon-alt']")
        product_info['rating'] = rating_element.get_attribute("innerHTML")
    except Exception as e:
        logging.error("Error extracting product rating: %s", e)
        product_info['rating'] = None

    try:
        product_info['delivery_time'] = product_element.find_element(By.XPATH, ".//span[@class='a-color-base a-text-bold']").text
    except Exception as e:
        logging.error("Error extracting delivery time: %s", e)
        product_info['delivery_time'] = None
    
    return product_info

def scrape_amazon(search_term):
    try:
        browser = setup_browser()
        browser.get('https://www.amazon.in/')
        sleep(random.uniform(2, 4)) 

        input_search = browser.find_element(By.ID, 'twotabsearchtextbox')
        search_button = browser.find_element(By.ID, 'nav-search-submit-button')

        input_search.send_keys(search_term)
        sleep(random.uniform(1, 2))
        search_button.click()
        sleep(random.uniform(2, 4))  

        products = []
        current_page = 1
        total_pages = get_total_pages_amazon(browser)

        while current_page <= total_pages:
            logging.info('Scraping page %d of %d', current_page, total_pages)
            
            product_elements = browser.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
            for product_element in product_elements:
                products.append(extract_product_info_amazon(product_element))
            
            try:
                next_button = browser.find_element(By.CLASS_NAME, 's-pagination-next')
                if 'a-disabled' in next_button.get_attribute('class'):
                    break
                
                actions = ActionChains(browser)
                actions.move_to_element(next_button).click().perform()
                sleep(random.uniform(2, 4))
                current_page += 1
            except Exception as e:
                logging.error("Error clicking next button: %s", e)
                break

        df = pd.DataFrame(products)
        output_file = os.path.join("output", f"{search_term}_amazon.csv")
        df.to_csv(output_file, index=False)
        browser.quit()
        return output_file
    except Exception as e:
        logging.error("Error during Amazon scraping: %s", e)
        browser.quit()
        raise e

def extract_product_info_flipkart(product_element):
    product_info = {}
    try:
        product_info['name'] = product_element.find_element(By.XPATH, ".//div[@class='KzDlHZ']").text
    except Exception as e:
        logging.error("Error extracting product name: %s", e)
        product_info['name'] = None

    try:
        product_info['price'] = product_element.find_element(By.XPATH, ".//div[@class='Nx9bqj _4b5DiR']").text
    except Exception as e:
        logging.error("Error extracting product price: %s", e)
        product_info['price'] = None

    try:
        product_info['product_link'] = product_element.find_element(By.XPATH, ".//img").get_attribute("src")
    except Exception as e:
        logging.error("Error extracting product link: %s", e)
        product_info['product_link'] = None

    try:
        rating_element = product_element.find_element(By.XPATH, ".//div[@class='XQDdHH']")
        product_info['rating'] = rating_element.text
    except Exception as e:
        logging.error("Error extracting product rating: %s", e)
        product_info['rating'] = None

    try:
        product_info['details'] = product_element.find_element(By.XPATH, ".//div[@class='_6NESgJ']").text
    except Exception as e:
        logging.error("Error extracting product details: %s", e)
        product_info['details'] = None
    
    return product_info

def scrape_flipkart(search_term):
    try:
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
        
        product_elements = browser.find_elements(By.XPATH, ".//div[@class='cPHDOP col-12-12']")
        for product_element in product_elements:
            products.append(extract_product_info_flipkart(product_element))

        df = pd.DataFrame(products)
        output_file = os.path.join("output", f"{search_term}_flipkart.csv")
        df.to_csv(output_file, index=False)
        browser.quit()
        return output_file
    except Exception as e:
        logging.error("Error during Flipkart scraping: %s", e)
        browser.quit()
        raise e


def extract_product_info_myntra(product_element):
    product_info = {}
   
    try:
        product_info['name'] = product_element.find_element(By.XPATH, ".//h4[@class='product-product']").text
    except Exception as e:
        logging.error("Error extracting name: %s", e)
        product_info['name'] = None

    try:
        product_info['brand'] = product_element.find_element(By.XPATH, ".//h3[@class='product-brand']").text
    except Exception as e:
        logging.error("Error extracting product brand: %s", e)
        product_info['brand'] = None

    try:
        product_info['price'] = product_element.find_element(By.XPATH, ".//div[@class='product-price']").text
    except Exception as e:
        logging.error("Error extracting product price: %s", e)
        product_info['price'] = None

    try:
        product_info['product_link'] = product_element.find_element(By.XPATH, ".//a").get_attribute("href")
    except Exception as e:
        logging.error("Error extracting product link: %s", e)
        product_info['product_link'] = None

    try:
        rating_element = product_element.find_element(By.XPATH, ".//div[@class='product-ratingsContainer']")
        rating_value = rating_element.find_element(By.TAG_NAME, 'span').text
        product_info['rating'] = rating_value
    except Exception as e:
        logging.error("Error extracting product rating: %s", e)
        product_info['rating'] = None

    return product_info

def scrape_myntra(search_term):
    try:
        browser = setup_browser()
        browser.get('https://www.myntra.com/')
        sleep(random.uniform(2, 4)) 

        input_search = browser.find_element(By.XPATH, ".//input[@class='desktop-searchBar']")
        search_button = browser.find_element(By.XPATH, ".//a[@class='desktop-submit']")

        input_search.send_keys(search_term)
        sleep(random.uniform(1, 2))
        search_button.click()
        sleep(random.uniform(2, 4))  

        products = []
        current_page = 1
        total_pages = 3  # You can adjust this based on the actual total pages
        
        while current_page <= total_pages:
            logging.info('Scraping page %d of %d', current_page, total_pages)
            
            product_elements = browser.find_elements(By.XPATH, "//li[@class='product-base']")
            for product_element in product_elements:
                products.append(extract_product_info_myntra(product_element))
            
            try:
                next_button = browser.find_element(By.XPATH, "//li[@class='pagination-next']/a")
                actions = ActionChains(browser)
                actions.move_to_element(next_button).click().perform()
                sleep(random.uniform(2, 4))
                current_page += 1
            except Exception as e:
                logging.error("Error clicking next button: %s", e)
                break

        df = pd.DataFrame(products)
        output_file = os.path.join("output", f"{search_term}_myntra.csv")
        df.to_csv(output_file, index=False)
        browser.quit()
        return output_file
    except Exception as e:
        logging.error("Error during myntra scraping: %s", e)
        browser.quit()
        raise e



@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    search_term = data.get('keyword')
    site = data.get('site')
    
    if not search_term or not site:
        logging.error("Keyword and site are required")
        return jsonify({"error": "Keyword and site are required"}), 400

    try:
        if site == 'amazon':
            output_file = scrape_amazon(search_term)
        elif site == 'flipkart':
            output_file = scrape_flipkart(search_term)
        elif site == 'myntra':
            output_file = scrape_myntra(search_term)            
        else:
            logging.error("Invalid site")
            return jsonify({"error": "Invalid site"}), 400
        
        logging.info("Scraping successful, returning file")
        return send_file(output_file, as_attachment=True)
    except Exception as e:
        logging.error("Error during scraping: %s", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists("output"):
        os.makedirs("output")
    app.run(debug=True)
