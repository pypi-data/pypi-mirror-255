# https://detail.1688.com/offer/715593582127.html
import random
import time
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import shutil
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import pyautogui
import re     

def getSKUInfo(url):
    chromedriver_autoinstaller.install()
    chrome_path = shutil.which("chromedriver")
    # print(chrome_path)
    service = Service(executable_path=chrome_path)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument("--disable-javascript")

    driver = webdriver.Chrome(options=chrome_options,service=service)
    # driver = webdriver.Firefox()


    # driver.get("http://www.google.com")
    # driver.get("http://www.python.org")
    # driver.get("https://bot.sannysoft.com/")
    driver.implicitly_wait(10)
    # driver.set_window_size(1920, 1080)
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(0.2, 1.2))
    # driver.execute_script("window.scrollBy(0,500)　")
    # time.sleep(1)
    detailElm = driver.find_element(By.CLASS_NAME,"od-pc-layout-detail-tab-container")
    driver.execute_script("arguments[0].scrollIntoView();",detailElm)
    time.sleep(random.uniform(0.2, 1.2))
    h = random.uniform(500, 1000)
    driver.execute_script("window.scrollBy(0,-500)".format(h))
    time.sleep(random.uniform(0.2, 1.2))
    actions = ActionChains(driver)
    try:
        sku_expend = driver.find_element(By.CLASS_NAME,"sku-wrapper-expend-button")
        
        actions.move_to_element(sku_expend)
        actions.click(sku_expend)
        actions.perform()
    except:
        print('no sku_expend button')

    
    colorList = []
    sku_items = driver.find_elements(By.CLASS_NAME,"prop-item")
    # print(sku_items)
    for skus_item in sku_items:
        styleStr = 'no img'
        try:
          styleStr = skus_item.find_element(By.CLASS_NAME,"prop-img").get_attribute("style")
        except:
            print("NO image")
            
        url = 'no img url'
        if styleStr != 'no img':
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', styleStr)
            if type(urls) == list:
                url = urls[0]
        title = skus_item.find_element(By.CLASS_NAME,"prop-name").get_attribute("title")
        # print(title , url)
        colorList.append({"title":title,"url":url})    
    # print(colorList)
    
    sku_sizes = driver.find_elements(By.CLASS_NAME,"sku-item-wrapper")
    
    sizeList = []
    for sku_size in sku_sizes:
        size_text = sku_size.find_element(By.CLASS_NAME,"sku-item-name").text
        sizeList.append(size_text)
        
    # print(sizeList)
    # driver.quit()

    return colorList,sizeList


    
