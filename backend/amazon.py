from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
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

def get_total_pages(browser):
    try:
        pagination = browser.find_element(By.CLASS_NAME, 's-pagination-strip')
        pages = pagination.find_elements(By.XPATH, ".//li[@class='a-disabled' or @class='a-normal']")
        if pages:
            total_pages = int(pages[-1].text)
        else:
            total_pages = 1
    except Exception as e:
        print("Error extracting total pages:", e)
        total_pages = 1
    return total_pages

def extract_product_info(product_element):
    product_info = {}
    try:
        product_info['name'] = product_element.find_element(By.XPATH, ".//span[@class='a-size-medium a-color-base a-text-normal']").text
    except:
        product_info['name'] = None

    try:
        product_info['price'] = product_element.find_element(By.XPATH, ".//span[@class='a-price-whole']").text
    except:
        product_info['price'] = None

    try:
        product_info['product_link'] = product_element.find_element(By.XPATH, ".//img").get_attribute("src")
    except:
        product_info['product_link'] = None

    try:
        rating_element = product_element.find_element(By.XPATH, ".//span[@class='a-icon-alt']")
        product_info['rating'] = rating_element.get_attribute("innerHTML")
    except:
        product_info['rating'] = None

    try:
        product_info['delivery_time'] = product_element.find_element(By.XPATH, ".//span[@class='a-color-base a-text-bold']").text
    except:
        product_info['delivery_time'] = None
    
    return product_info

def scrape_amazon(search_term):
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
    total_pages = get_total_pages(browser)

    while current_page <= total_pages:
        print(f'Scraping page {current_page} of {total_pages}')
        
        product_elements = browser.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
        for product_element in product_elements:
            products.append(extract_product_info(product_element))
        
        try:
            next_button = browser.find_element(By.CLASS_NAME, 's-pagination-next')
            if 'a-disabled' in next_button.get_attribute('class'):
                break
            
            actions = ActionChains(browser)
            actions.move_to_element(next_button).click().perform()
            sleep(random.uniform(2, 4))
            current_page += 1
        except Exception as e:
            print("Error clicking next button:", e)
            break

    df = pd.DataFrame(products)
    print(df)
    #browser.quit()
    return df

# Call the scrape_amazon function
# df = scrape_amazon("smartTV")
# df.to_csv("amazon_product_data.csv", index=False)
